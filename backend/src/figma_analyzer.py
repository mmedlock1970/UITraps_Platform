"""
UI Traps Analyzer - Figma Integration

Copyright © 2009-present UI Traps LLC. All Rights Reserved.

CONFIDENTIAL AND PROPRIETARY
This code contains proprietary UI Tenets & Traps framework logic.
Unauthorized use, reproduction, or distribution is strictly prohibited.

This module enables direct analysis of Figma design files by:
1. Accepting Figma file URLs
2. Fetching file data via Figma REST API
3. Exporting frames as images
4. Analyzing prototype flows for multi-screen traps
"""

import os
import re
import base64
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class FigmaAnalyzer:
    """
    Analyzes Figma design files for UI Traps.

    Requires a Figma Personal Access Token.
    Get yours at: https://www.figma.com/developers/api#access-tokens
    """

    def __init__(self, figma_token: Optional[str] = None):
        """
        Initialize Figma analyzer.

        Args:
            figma_token: Figma Personal Access Token. If not provided,
                        will look for FIGMA_TOKEN environment variable.
        """
        self.figma_token = figma_token or os.getenv('FIGMA_TOKEN')
        if not self.figma_token:
            raise ValueError(
                "Figma token required. Either pass figma_token parameter or "
                "set FIGMA_TOKEN environment variable. "
                "Get your token at: https://www.figma.com/developers/api#access-tokens"
            )

        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.figma_token
        }

    def parse_figma_url(self, url: str) -> Tuple[str, Optional[str]]:
        """
        Extract file_key and optional node_id from Figma URL.

        Supports:
        - https://www.figma.com/file/{file_key}/{title}
        - https://www.figma.com/file/{file_key}/{title}?node-id={node_id}
        - https://www.figma.com/design/{file_key}/{title}
        - https://www.figma.com/proto/{file_key}/{title}

        Args:
            url: Figma file URL

        Returns:
            Tuple of (file_key, node_id)

        Raises:
            ValueError: If URL format is invalid
        """
        # Pattern matches: /file/, /design/, or /proto/ followed by file key
        pattern = r'figma\.com/(?:file|design|proto)/([a-zA-Z0-9]+)'
        match = re.search(pattern, url)

        if not match:
            raise ValueError(
                f"Invalid Figma URL format. Expected format: "
                f"https://www.figma.com/file/{{file_key}}/{{title}}\n"
                f"Got: {url}"
            )

        file_key = match.group(1)

        # Check for node-id parameter
        node_id = None
        node_match = re.search(r'node-id=([^&]+)', url)
        if node_match:
            node_id = node_match.group(1)

        return file_key, node_id

    def get_file_data(self, file_key: str, max_retries: int = 3) -> Dict:
        """
        Fetch file data from Figma API with retry on rate limits.

        Args:
            file_key: Figma file key
            max_retries: Maximum number of retries on rate limit (429)

        Returns:
            Dictionary containing file metadata and structure

        Raises:
            requests.HTTPError: If API request fails after retries
        """
        import time as time_module
        url = f"{self.base_url}/files/{file_key}"

        for attempt in range(max_retries + 1):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 429:  # Rate limited
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                    print(f"Rate limited by Figma API. Waiting {wait_time}s before retry...")
                    time_module.sleep(wait_time)
                    continue

            response.raise_for_status()
            return response.json()

        # Should not reach here, but just in case
        response.raise_for_status()
        return response.json()

    def get_all_frames(self, file_data: Dict) -> List[Dict]:
        """
        Extract all frames/screens from file data.

        Args:
            file_data: File data from get_file_data()

        Returns:
            List of frame objects with metadata
        """
        frames = []

        def traverse_node(node, page_name=""):
            """Recursively traverse node tree to find frames."""
            if not node:
                return
            node_type = node.get('type', '')

            # Frames are the top-level containers for designs
            if node_type == 'FRAME':
                bounding_box = node.get('absoluteBoundingBox') or {}
                frames.append({
                    'id': node.get('id', ''),
                    'name': node.get('name', 'Unnamed'),
                    'page': page_name,
                    'width': bounding_box.get('width', 0),
                    'height': bounding_box.get('height', 0)
                })

            # Recurse into children
            for child in node.get('children') or []:
                traverse_node(child, page_name)

        # Traverse all pages
        document = file_data.get('document') or {}
        for page in document.get('children') or []:
            page_name = page.get('name', 'Unnamed Page') if page else 'Unnamed Page'
            traverse_node(page, page_name)

        return frames

    def export_frame_as_image(
        self,
        file_key: str,
        node_id: str,
        scale: int = 2,
        format: str = 'png',
        max_retries: int = 3
    ) -> bytes:
        """
        Export a specific frame as an image with retry on rate limits.

        Args:
            file_key: Figma file key
            node_id: Node ID to export
            scale: Export scale (1-4). 2 = 2x resolution
            format: Image format ('png', 'jpg', 'svg', 'pdf')
            max_retries: Maximum number of retries on rate limit (429)

        Returns:
            Image data as bytes

        Raises:
            requests.HTTPError: If API request fails after retries
        """
        import time as time_module

        # Request image export URL
        url = f"{self.base_url}/images/{file_key}"
        params = {
            'ids': node_id,
            'scale': scale,
            'format': format
        }

        for attempt in range(max_retries + 1):
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 429:  # Rate limited
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                    print(f"Rate limited by Figma API. Waiting {wait_time}s...")
                    time_module.sleep(wait_time)
                    continue

            response.raise_for_status()
            break

        result = response.json()

        # Get the image URL
        images = result.get('images') or {}
        image_url = images.get(node_id)
        if not image_url:
            raise ValueError(f"Failed to get image URL for node {node_id}")

        # Download the actual image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        return image_response.content

    def get_prototype_flows(self, file_data: Dict) -> List[Dict]:
        """
        Extract prototype navigation flows from file data.

        Figma prototypes define interactions between frames.
        This helps identify multi-screen traps like AMBIGUOUS HOME.

        Args:
            file_data: File data from get_file_data()

        Returns:
            List of flow connections: [{'from': node_id, 'to': node_id, 'action': ...}]
        """
        flows = []

        def traverse_for_interactions(node):
            """Find all prototype interactions in the node tree."""
            if not node:
                return
            # Check for interactions on this node
            interactions = node.get('interactions') or []
            for interaction in interactions:
                if not interaction:
                    continue
                actions = interaction.get('actions') or [{}]
                action = actions[0] if actions else {}
                if not action:
                    action = {}
                destination_id = action.get('destinationId')

                if destination_id:
                    trigger = interaction.get('trigger') or {}
                    flows.append({
                        'from_node': node.get('id', ''),
                        'from_name': node.get('name', 'Unnamed'),
                        'to_node': destination_id,
                        'trigger': trigger.get('type', 'UNKNOWN')
                    })

            # Recurse into children
            for child in node.get('children') or []:
                traverse_for_interactions(child)

        # Traverse all pages
        document = file_data.get('document') or {}
        for page in document.get('children') or []:
            traverse_for_interactions(page)

        return flows

    def analyze_figma_file(
        self,
        figma_url: str,
        output_dir: Optional[str] = None,
        cached_file_data: Optional[Dict] = None
    ) -> Dict:
        """
        Complete analysis workflow for a Figma file.

        1. Parse URL to get file_key
        2. Fetch file data (or use cached)
        3. Export all frames as images
        4. Detect prototype flows
        5. Prepare for UI Traps analysis

        Args:
            figma_url: Figma file URL
            output_dir: Directory to save exported images (optional)
            cached_file_data: Pre-fetched file data to avoid API call (optional)

        Returns:
            Dictionary containing:
            - file_info: Basic file metadata
            - frames: List of frames with image paths
            - flows: Prototype navigation structure
        """
        print(f"Parsing Figma URL...")
        file_key, node_id = self.parse_figma_url(figma_url)

        if cached_file_data:
            print(f"Using cached file data...")
            file_data = cached_file_data
        else:
            print(f"Fetching file data from Figma API...")
            file_data = self.get_file_data(file_key)

        # Extract file info
        file_info = {
            'name': file_data.get('name', 'Untitled'),
            'key': file_key,
            'version': file_data.get('version', 'unknown'),
            'last_modified': file_data.get('lastModified', 'unknown')
        }

        print(f"File: {file_info['name']}")
        print(f"Version: {file_info['version']}")

        # Get all frames
        print(f"Extracting frames...")
        frames = self.get_all_frames(file_data)
        print(f"Found {len(frames)} frames")

        # Get prototype flows
        print(f"Analyzing prototype flows...")
        flows = self.get_prototype_flows(file_data)
        print(f"Found {len(flows)} prototype connections")

        # Export images if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            print(f"Exporting frame images to {output_dir}...")
            for i, frame in enumerate(frames, 1):
                try:
                    print(f"  [{i}/{len(frames)}] Exporting: {frame['name']}")

                    # Export frame
                    image_data = self.export_frame_as_image(file_key, frame['id'])

                    # Save to file
                    safe_name = re.sub(r'[^\w\-_]', '_', frame['name'])
                    image_path = output_path / f"{safe_name}.png"
                    image_path.write_bytes(image_data)

                    frame['image_path'] = str(image_path)

                except Exception as e:
                    print(f"    Warning: Failed to export {frame['name']}: {e}")
                    frame['image_path'] = None

        return {
            'file_info': file_info,
            'frames': frames,
            'flows': flows
        }


def main():
    """Example usage of FigmaAnalyzer."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python figma_analyzer.py <figma_url> [output_dir]")
        print("\nExample:")
        print("  python figma_analyzer.py https://www.figma.com/file/abc123/MyDesign ./exports")
        print("\nMake sure to set FIGMA_TOKEN environment variable first!")
        sys.exit(1)

    figma_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./figma_exports"

    try:
        analyzer = FigmaAnalyzer()
        result = analyzer.analyze_figma_file(figma_url, output_dir)

        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nFile: {result['file_info']['name']}")
        print(f"Frames: {len(result['frames'])}")
        print(f"Flows: {len(result['flows'])}")

        if result['flows']:
            print("\nPrototype Navigation:")
            for flow in result['flows'][:5]:  # Show first 5
                print(f"  {flow['from_name']} → {flow['trigger']} → {flow['to_node']}")

        print(f"\nImages saved to: {output_dir}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
