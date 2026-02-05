"""
Multi-Image and Video Analysis for UI Traps Analyzer

Handles analysis of multiple screenshots or video frames,
aggregating results into a cohesive report.

Two-pass frame selection for video:
1. Extract more frames than needed (2x target)
2. Use lightweight AI call to filter out bad frames (loading, blank, mid-transition)
3. Analyze only the good frames

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import base64
import tempfile
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .analyzer import UITrapsAnalyzer


# Frame quality classification prompt (lightweight, fast)
FRAME_QUALITY_PROMPT = """Classify each video frame for UI analysis suitability.
For each frame, respond with EXACTLY this JSON format:
{
  "frames": [
    {"index": 1, "quality": "good|loading|blank|transition|duplicate", "reason": "brief reason"}
  ]
}

Quality classifications:
- "good": Complete UI visible, stable, suitable for analysis
- "loading": Loading spinner, progress bar, or "loading" text visible
- "blank": Mostly empty screen, solid color, or no meaningful content
- "transition": Mid-animation, blurry, or partial UI (elements moving/fading)
- "duplicate": Nearly identical to previous frame (skip if consecutive)

IMPORTANT: Be strict. If you see ANY loading indicator, progress animation, or partially rendered UI, mark as loading/transition.
A blank screen with no visible UI elements should be marked as "blank" even without explicit loading text.

Analyze these frames:"""


def _load_image_as_base64(image_path: str) -> Optional[str]:
    """Load an image file and return as base64 string."""
    try:
        # Normalize path for Windows compatibility
        path = Path(image_path).resolve()

        # Check if file exists
        if not path.exists():
            print(f"[UITraps DEBUG] Image file does not exist: {path}")
            return None

        ext = path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        media_type = media_type_map.get(ext, 'image/png')

        # Read file
        file_size = path.stat().st_size
        if file_size == 0:
            print(f"[UITraps DEBUG] Image file is empty: {path}")
            return None

        # Read binary data
        with open(str(path), 'rb') as f:
            raw_data = f.read()

        if not raw_data:
            print(f"[UITraps DEBUG] Failed to read image data from: {path}")
            return None

        # Encode to base64
        data = base64.standard_b64encode(raw_data).decode('utf-8')

        if not data:
            print(f"[UITraps DEBUG] Base64 encoding failed for: {path}")
            return None

        result = f"data:{media_type};base64,{data}"
        print(f"[UITraps DEBUG] Successfully loaded image ({file_size} bytes, {len(data)} chars base64): {path.name}")
        return result

    except PermissionError as e:
        print(f"[UITraps DEBUG] Permission error reading {image_path}: {e}")
        return None
    except Exception as e:
        print(f"[UITraps DEBUG] Error loading image {image_path}: {type(e).__name__}: {e}")
        return None
from .video_processor import VideoProcessor, is_ffmpeg_available
from .formatters import format_report_as_html, format_report_as_markdown, get_report_statistics


class MultiAnalyzer:
    """
    Analyzes multiple images or video frames.

    Runs individual analyses and aggregates findings,
    detecting cross-frame issues like WANDERING ELEMENT.
    """

    def __init__(self, analyzer: UITrapsAnalyzer = None):
        """
        Initialize the multi-analyzer.

        Args:
            analyzer: Existing UITrapsAnalyzer instance (creates new if None)
        """
        self.analyzer = analyzer or UITrapsAnalyzer()
        self.video_processor = None

    def _get_video_processor(self) -> VideoProcessor:
        """Lazy-load video processor."""
        if self.video_processor is None:
            self.video_processor = VideoProcessor()
        return self.video_processor

    def _filter_frames_with_ai(
        self,
        frames: List[Tuple[str, float]],
        max_good_frames: int = 15,
        progress_callback: callable = None
    ) -> Tuple[List[Tuple[str, float]], List[Dict]]:
        """
        Use AI to filter out bad frames (loading, blank, transitions).

        Two-pass approach:
        1. Send all frame thumbnails to AI for quality classification
        2. Keep only "good" frames up to max_good_frames

        Args:
            frames: List of (frame_path, timestamp) tuples
            max_good_frames: Maximum good frames to return
            progress_callback: Optional progress callback

        Returns:
            Tuple of (good_frames, quality_notes)
            - good_frames: Filtered list of (path, timestamp) tuples
            - quality_notes: List of quality issues for report
        """
        if not frames:
            return [], []

        if progress_callback:
            progress_callback(0, 1, "Filtering frames for quality...")

        # Build images for classification (use thumbnails to reduce cost)
        images = []
        for i, (frame_path, timestamp) in enumerate(frames):
            image_data = _load_image_as_base64(frame_path)
            if image_data:
                images.append({
                    'index': i + 1,
                    'timestamp': timestamp,
                    'image_data': image_data,
                    'path': frame_path
                })

        if not images:
            print("[UITraps] No valid images for frame filtering, using all frames")
            return frames, []

        # Build the API request for frame classification
        try:
            # Use the analyzer's Claude client for the classification
            from anthropic import Anthropic
            client = Anthropic()

            # Build content with all frame images
            content = [{"type": "text", "text": FRAME_QUALITY_PROMPT}]

            for img in images:
                # Add image
                img_data = img['image_data']
                if img_data.startswith('data:'):
                    # Extract base64 from data URL
                    parts = img_data.split(',', 1)
                    if len(parts) == 2:
                        media_type = parts[0].split(':')[1].split(';')[0]
                        base64_data = parts[1]
                    else:
                        continue
                else:
                    media_type = "image/png"
                    base64_data = img_data

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_data
                    }
                })
                content.append({
                    "type": "text",
                    "text": f"Frame {img['index']} (at {img['timestamp']:.1f}s)"
                })

            # Make fast classification request (use haiku for speed/cost)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",  # Fast model for classification
                max_tokens=2000,
                messages=[{"role": "user", "content": content}]
            )

            # Parse response
            response_text = response.content[0].text

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                classification = json.loads(json_match.group(0))
            else:
                print(f"[UITraps] Could not parse frame classification, using all frames")
                return frames, []

            # Filter to good frames only
            good_frames = []
            quality_notes = []

            frame_classifications = {f['index']: f for f in classification.get('frames', [])}

            for img in images:
                idx = img['index']
                fc = frame_classifications.get(idx, {})
                quality = fc.get('quality', 'good')
                reason = fc.get('reason', '')

                if quality == 'good':
                    good_frames.append((img['path'], img['timestamp']))
                else:
                    # Record quality note for report
                    issue_map = {
                        'loading': 'loading_state',
                        'blank': 'blank_screen',
                        'transition': 'mid_transition',
                        'duplicate': 'duplicate'
                    }
                    quality_notes.append({
                        'frame_index': idx,
                        'issue': issue_map.get(quality, 'low_quality'),
                        'description': reason or f"Frame classified as {quality}",
                        'should_skip': True,
                        'timestamp': img['timestamp']
                    })
                    print(f"[UITraps] Skipping frame {idx} ({img['timestamp']:.1f}s): {quality} - {reason}")

                # Stop if we have enough good frames
                if len(good_frames) >= max_good_frames:
                    break

            # If we filtered out too many, add some back
            if len(good_frames) < 3 and len(frames) >= 3:
                print(f"[UITraps] Only {len(good_frames)} good frames found, using all frames")
                return frames, quality_notes

            print(f"[UITraps] Frame filtering: {len(good_frames)}/{len(frames)} frames passed quality check")
            return good_frames, quality_notes

        except Exception as e:
            print(f"[UITraps] Frame filtering failed: {e}, using all frames")
            return frames, []

    def analyze_images(
        self,
        image_paths: List[str],
        user_context: Dict[str, str],
        progress_callback: callable = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple images and aggregate results.

        Args:
            image_paths: List of image file paths
            user_context: Dict with 'users', 'tasks', 'format' keys
            progress_callback: Optional callback(current, total, message)

        Returns:
            Aggregated analysis result with HTML and markdown reports
        """
        results = []
        total = len(image_paths)

        for i, path in enumerate(image_paths):
            if progress_callback:
                progress_callback(i + 1, total, f"Analyzing image {i + 1} of {total}")

            # Load image as base64 for embedding in report
            image_data = _load_image_as_base64(path)

            try:
                result = self.analyzer.analyze_design(
                    design_file=path,
                    user_context=user_context
                )
                results.append({
                    'path': path,
                    'filename': os.path.basename(path),
                    'index': i + 1,
                    'result': result,
                    'error': None,
                    'image_data': image_data
                })
            except Exception as e:
                results.append({
                    'path': path,
                    'filename': os.path.basename(path),
                    'index': i + 1,
                    'result': None,
                    'error': str(e),
                    'image_data': image_data
                })

        # Aggregate results
        return self._aggregate_results(results, 'multi_image')

    def analyze_video(
        self,
        video_path: str,
        user_context: Dict[str, str],
        max_frames: int = 15,
        progress_callback: callable = None,
        enable_frame_filtering: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a video by extracting and analyzing frames.

        Uses two-pass frame selection when enabled:
        1. Extract 2x more frames than needed
        2. Use AI to filter out loading screens, blank screens, and transitions
        3. Analyze only the good frames

        Args:
            video_path: Path to video file
            user_context: Dict with 'users', 'tasks', 'format' keys
            max_frames: Maximum frames to analyze
            progress_callback: Optional callback(current, total, message)
            enable_frame_filtering: Use AI to filter bad frames (default: True)

        Returns:
            Aggregated analysis result with HTML and markdown reports
        """
        if not is_ffmpeg_available():
            raise RuntimeError(
                "FFmpeg is required for video analysis but not installed. "
                "Please install FFmpeg and try again."
            )

        processor = self._get_video_processor()

        # Get video info
        if progress_callback:
            progress_callback(0, 1, "Reading video metadata...")

        video_info = processor.get_video_info(video_path)

        # Extract frames - get 2x more than needed if filtering is enabled
        if progress_callback:
            progress_callback(0, 1, "Extracting frames from video...")

        extraction_count = max_frames * 2 if enable_frame_filtering else max_frames
        frames = processor.extract_frames(
            video_path,
            max_frames=extraction_count
        )

        if not frames:
            raise ValueError("No frames could be extracted from video")

        # Two-pass frame selection: filter out bad frames
        quality_notes = []
        if enable_frame_filtering and len(frames) > max_frames:
            if progress_callback:
                progress_callback(0, 1, f"Filtering {len(frames)} frames for quality...")

            frames, quality_notes = self._filter_frames_with_ai(
                frames,
                max_good_frames=max_frames,
                progress_callback=progress_callback
            )

            if progress_callback:
                progress_callback(0, 1, f"Selected {len(frames)} quality frames for analysis")

        # Analyze each frame
        results = []
        total = len(frames)

        for i, (frame_path, timestamp) in enumerate(frames):
            if progress_callback:
                progress_callback(
                    i + 1, total,
                    f"Analyzing frame {i + 1} of {total} ({timestamp:.1f}s)"
                )

            # Load frame image as base64 BEFORE analysis (in case of error)
            image_data = _load_image_as_base64(frame_path)

            try:
                result = self.analyzer.analyze_design(
                    design_file=frame_path,
                    user_context=user_context
                )
                results.append({
                    'path': frame_path,
                    'filename': f"Frame at {timestamp:.1f}s",
                    'timestamp': timestamp,
                    'index': i + 1,
                    'result': result,
                    'error': None,
                    'image_data': image_data
                })
            except Exception as e:
                results.append({
                    'path': frame_path,
                    'filename': f"Frame at {timestamp:.1f}s",
                    'timestamp': timestamp,
                    'index': i + 1,
                    'result': None,
                    'error': str(e),
                    'image_data': image_data
                })

        # Clean up all extracted frame files
        all_frame_paths = [f[0] for f in frames]
        processor.cleanup_frames(all_frame_paths)

        # Aggregate results
        aggregated = self._aggregate_results(results, 'video')
        aggregated['video_info'] = video_info

        # Include frame quality notes in the report
        if quality_notes:
            aggregated['raw']['frame_quality_notes'] = quality_notes

        return aggregated

    def _aggregate_results(
        self,
        results: List[Dict],
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Aggregate multiple analysis results into a single report.

        Args:
            results: List of individual analysis results
            analysis_type: 'multi_image' or 'video'

        Returns:
            Aggregated result dict
        """
        # Collect all issues across frames
        all_critical = []
        all_moderate = []
        all_minor = []
        all_positive = []
        all_potential = []
        all_checked_not_found = set()

        # Build frame images lookup: frame_index -> image_data
        frame_images = {}

        successful_count = 0
        failed_count = 0

        for item in results:
            # Always capture frame image, even if analysis failed
            if item.get('image_data'):
                frame_images[item['index']] = {
                    'image_data': item['image_data'],
                    'filename': item['filename'],
                    'timestamp': item.get('timestamp')
                }

            if item['error']:
                failed_count += 1
                continue

            successful_count += 1
            result = item['result']
            # Note: analyzer.py returns data under 'report' key, not 'raw'
            raw = result.get('report', {}) or result.get('raw', {})
            frame_label = item['filename']

            # Add frame context to each issue
            for issue in raw.get('critical_issues', []):
                issue['frame'] = frame_label
                issue['frame_index'] = item['index']
                all_critical.append(issue)

            for issue in raw.get('moderate_issues', []):
                issue['frame'] = frame_label
                issue['frame_index'] = item['index']
                all_moderate.append(issue)

            for issue in raw.get('minor_issues', []):
                issue['frame'] = frame_label
                issue['frame_index'] = item['index']
                all_minor.append(issue)

            for obs in raw.get('positive_observations', []):
                all_positive.append(f"[{frame_label}] {obs}")

            for issue in raw.get('potential_issues', []):
                issue['frame'] = frame_label
                issue['frame_index'] = item['index']
                all_potential.append(issue)

            for trap in raw.get('traps_checked_not_found', []):
                all_checked_not_found.add(trap)

        # Deduplicate similar issues (same trap at same location)
        critical_deduped = self._deduplicate_issues(all_critical)
        moderate_deduped = self._deduplicate_issues(all_moderate)
        minor_deduped = self._deduplicate_issues(all_minor)

        # Detect cross-frame issues
        cross_frame_issues = self._detect_cross_frame_issues(results)

        # Build aggregated raw result
        aggregated_raw = {
            'summary': self._generate_summary(
                critical_deduped, moderate_deduped, minor_deduped,
                successful_count, failed_count, analysis_type
            ),
            'critical_issues': critical_deduped,
            'moderate_issues': moderate_deduped,
            'minor_issues': minor_deduped,
            'positive_observations': list(set(all_positive))[:10],
            'potential_issues': all_potential,
            'traps_checked_not_found': list(all_checked_not_found),
            'cross_frame_issues': cross_frame_issues,
            'frame_images': frame_images,  # Include frame images for report embedding
        }

        # Format reports
        html = self._format_multi_html(aggregated_raw, results, analysis_type, frame_images)
        markdown = self._format_multi_markdown(aggregated_raw, results, analysis_type, frame_images)
        statistics = get_report_statistics(aggregated_raw)

        return {
            'html': html,
            'markdown': markdown,
            'raw': aggregated_raw,
            'statistics': statistics,
            'analysis_type': analysis_type,
            'frame_count': len(results),
            'successful_count': successful_count,
            'failed_count': failed_count,
            'individual_results': results
        }

    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Deduplicate issues that appear in multiple frames.

        Groups by trap_name + location, keeps highest confidence.
        """
        seen = {}

        for issue in issues:
            key = (issue.get('trap_name', ''), issue.get('location', ''))
            if key not in seen:
                # First occurrence - add frame list and index list
                issue['frames'] = [issue.get('frame', 'Unknown')]
                issue['frame_indices'] = [issue.get('frame_index', 0)]
                seen[key] = issue
            else:
                # Duplicate - add to frame list and index list
                seen[key]['frames'].append(issue.get('frame', 'Unknown'))
                if issue.get('frame_index'):
                    seen[key]['frame_indices'].append(issue.get('frame_index'))
                # Keep higher confidence
                if issue.get('confidence') == 'high':
                    seen[key]['confidence'] = 'high'

        # Convert back to list
        result = list(seen.values())

        # Format frame info for display
        for issue in result:
            frames = issue.get('frames', [])
            frame_indices = issue.get('frame_indices', [])
            if len(frames) > 1:
                issue['frame'] = f"{len(frames)} frames"
                issue['appears_in'] = frames
                # Keep first frame_index for single reference, full list for multi
                if frame_indices:
                    issue['frame_indices'] = sorted(set(frame_indices))
            elif frames:
                issue['frame'] = frames[0]
                # Keep single frame_index
                if frame_indices:
                    issue['frame_index'] = frame_indices[0]

        return result

    def _normalize_location(self, raw_location: str) -> str:
        """
        Normalize a natural language location description to a standard region.

        Args:
            raw_location: e.g., "upper right corner of the navigation bar"

        Returns:
            Normalized region: e.g., "top-right:header"
        """
        if not raw_location:
            return "unknown"

        location_lower = raw_location.lower()

        # Step 1: Determine vertical position
        vertical = 'middle'
        if any(term in location_lower for term in ['top', 'upper', 'above', 'header']):
            vertical = 'top'
        elif any(term in location_lower for term in ['bottom', 'lower', 'below', 'footer']):
            vertical = 'bottom'

        # Step 2: Determine horizontal position
        horizontal = 'center'
        if any(term in location_lower for term in ['left', 'west', 'start']):
            horizontal = 'left'
        elif any(term in location_lower for term in ['right', 'east', 'end']):
            horizontal = 'right'

        # Step 3: Detect UI region context
        region_context = ''
        if any(term in location_lower for term in ['header', 'navigation', 'nav bar', 'top bar', 'navbar', 'menu bar']):
            region_context = ':header'
        elif any(term in location_lower for term in ['footer', 'bottom bar', 'page footer']):
            region_context = ':footer'
        elif any(term in location_lower for term in ['sidebar', 'side panel', 'side bar', 'side menu']):
            region_context = ':sidebar'
        elif any(term in location_lower for term in ['toolbar', 'tool bar', 'action bar']):
            region_context = ':toolbar'
        elif any(term in location_lower for term in ['modal', 'dialog', 'popup', 'overlay']):
            region_context = ':modal'

        # Step 4: Combine into normalized location
        if vertical == 'middle' and horizontal == 'center':
            return f'center{region_context}'
        elif vertical == 'middle':
            return f'{horizontal}{region_context}'
        elif horizontal == 'center':
            return f'{vertical}-center{region_context}'
        else:
            return f'{vertical}-{horizontal}{region_context}'

    def _extract_element_identity(self, issue: Dict) -> Tuple[str, str]:
        """
        Extract element identity from issue description.

        Returns (element_type, element_name) tuple for grouping similar elements.
        """
        location = (issue.get('location', '') or '').lower()
        problem = (issue.get('problem', '') or '').lower()
        combined = f"{location} {problem}"

        # Extract element type
        element_types = [
            ('button', ['button', 'btn', 'cta']),
            ('link', ['link', 'anchor', 'href']),
            ('icon', ['icon', 'symbol', 'glyph']),
            ('menu', ['menu', 'dropdown', 'nav', 'navigation']),
            ('field', ['field', 'input', 'textbox', 'text box', 'form field']),
            ('toggle', ['toggle', 'switch', 'checkbox', 'check box']),
            ('search', ['search', 'find', 'lookup']),
            ('tab', ['tab', 'tabs']),
            ('label', ['label', 'text', 'heading', 'title']),
            ('image', ['image', 'img', 'photo', 'picture', 'logo']),
        ]

        element_type = 'element'
        for type_name, keywords in element_types:
            if any(kw in combined for kw in keywords):
                element_type = type_name
                break

        # Extract element name/function (common UI actions/purposes)
        element_names = [
            ('search', ['search', 'find', 'lookup', 'magnifying']),
            ('login', ['login', 'log in', 'sign in', 'signin']),
            ('logout', ['logout', 'log out', 'sign out', 'signout']),
            ('settings', ['settings', 'preferences', 'config', 'gear', 'cog']),
            ('profile', ['profile', 'account', 'user', 'avatar']),
            ('home', ['home', 'main', 'dashboard', 'start']),
            ('back', ['back', 'return', 'previous']),
            ('close', ['close', 'dismiss', 'cancel', 'x button']),
            ('menu', ['menu', 'hamburger', 'three lines', '≡']),
            ('cart', ['cart', 'basket', 'shopping', 'bag']),
            ('help', ['help', 'support', 'faq', 'question']),
            ('notification', ['notification', 'alert', 'bell', 'notify']),
            ('filter', ['filter', 'sort', 'refine']),
            ('edit', ['edit', 'modify', 'change', 'pencil']),
            ('delete', ['delete', 'remove', 'trash', 'bin']),
            ('add', ['add', 'new', 'create', 'plus', '+']),
            ('save', ['save', 'submit', 'confirm', 'done']),
            ('share', ['share', 'send', 'export']),
            ('refresh', ['refresh', 'reload', 'update']),
        ]

        element_name = 'unknown'
        for name, keywords in element_names:
            if any(kw in combined for kw in keywords):
                element_name = name
                break

        # If no name found, try to extract from location directly
        if element_name == 'unknown':
            # Look for quoted text or specific element mentions
            import re
            # Match patterns like "the X button" or "X icon"
            pattern = r'(?:the\s+)?(\w+)\s+(?:button|icon|link|control|element)'
            match = re.search(pattern, combined)
            if match:
                element_name = match.group(1)

        return (element_type, element_name)

    def _detect_cross_frame_issues(self, results: List[Dict]) -> List[Dict]:
        """
        Detect issues that span multiple frames.

        Specifically detects WANDERING ELEMENT: when the same UI element
        appears in different locations across frames.

        Algorithm:
        1. Collect all UI elements mentioned across all frames
        2. Group by element identity (type + name)
        3. For each element appearing in 2+ frames, compare normalized locations
        4. If same element has different locations, report as WANDERING ELEMENT
        """
        from collections import defaultdict

        cross_issues = []

        # Build element registry: element_id -> list of occurrences
        element_registry = defaultdict(list)

        for item in results:
            if item.get('error'):
                continue

            frame_idx = item.get('index', 0)
            timestamp = item.get('timestamp')
            result = item.get('result', {})

            # Get report data (analyzer returns under 'report' key)
            report = result.get('report', {}) or result.get('raw', {})

            # Check all issue types for element mentions
            issue_types = ['critical_issues', 'moderate_issues', 'minor_issues', 'potential_issues']

            for issue_type in issue_types:
                for issue in report.get(issue_type, []):
                    # Extract element identity
                    element_id = self._extract_element_identity(issue)

                    # Skip if we couldn't identify the element
                    if element_id[1] == 'unknown':
                        continue

                    raw_location = issue.get('location', '')
                    normalized_location = self._normalize_location(raw_location)

                    element_registry[element_id].append({
                        'frame_index': frame_idx,
                        'timestamp': timestamp,
                        'normalized_location': normalized_location,
                        'raw_location': raw_location,
                        'trap_name': issue.get('trap_name'),
                        'issue_type': issue_type,
                    })

        # Find elements with position changes across frames
        for element_id, occurrences in element_registry.items():
            if len(occurrences) < 2:
                continue

            # Get unique normalized locations
            unique_locations = set(o['normalized_location'] for o in occurrences)

            # If same element appears in multiple different locations
            if len(unique_locations) > 1:
                element_type, element_name = element_id

                # Build frame occurrence details
                frame_details = []
                for occ in sorted(occurrences, key=lambda x: x['frame_index']):
                    detail = {
                        'frame_index': occ['frame_index'],
                        'location': occ['normalized_location'],
                        'raw_location': occ['raw_location'],
                    }
                    if occ['timestamp'] is not None:
                        detail['timestamp'] = occ['timestamp']
                    frame_details.append(detail)

                # Determine confidence based on how many different locations
                confidence = 'high' if len(unique_locations) >= 3 else 'medium'

                # Create descriptive element name
                element_desc = f"{element_name} {element_type}".strip()
                if element_desc == 'unknown element':
                    element_desc = 'UI element'

                cross_issues.append({
                    'trap_name': 'WANDERING ELEMENT (Cross-Frame)',
                    'tenet': 'HABITUATING',
                    'element_description': element_desc,
                    'locations_found': list(unique_locations),
                    'frame_occurrences': frame_details,
                    'problem': f"The {element_desc} appears in {len(unique_locations)} different locations across {len(occurrences)} frames: {', '.join(sorted(unique_locations))}. This inconsistent placement impedes user habituation.",
                    'recommendation': 'Maintain consistent element placement across all screens and states to support user muscle memory and habituation.',
                    'confidence': confidence,
                    'severity': 'moderate',
                })

        return cross_issues

    def _generate_summary(
        self,
        critical: List, moderate: List, minor: List,
        successful: int, failed: int, analysis_type: str
    ) -> List[str]:
        """Generate summary bullet points."""
        total_issues = len(critical) + len(moderate) + len(minor)
        type_label = "screenshots" if analysis_type == 'multi_image' else "video frames"

        summary = [
            f"Analyzed {successful} {type_label}" +
            (f" ({failed} failed)" if failed else ""),
            f"Found {total_issues} total issues: {len(critical)} critical, "
            f"{len(moderate)} moderate, {len(minor)} minor",
        ]

        if critical:
            trap_names = list(set(i.get('trap_name', 'Unknown') for i in critical))[:3]
            summary.append(
                f"Critical issues include: {', '.join(trap_names)}"
            )

        if moderate:
            trap_names = list(set(i.get('trap_name', 'Unknown') for i in moderate))[:3]
            summary.append(
                f"Moderate issues include: {', '.join(trap_names)}"
            )

        return summary[:7]  # Max 7 bullets

    def _format_multi_html(
        self,
        aggregated: Dict,
        results: List[Dict],
        analysis_type: str,
        frame_images: Dict[int, Dict] = None
    ) -> str:
        """Format aggregated results as HTML with embedded frame images."""
        # Use existing formatter with aggregated data
        base_html = format_report_as_html(aggregated)

        # Add multi-frame header
        type_label = "Multi-Screenshot" if analysis_type == 'multi_image' else "Video"
        frame_count = len([r for r in results if not r['error']])

        header = f"""
        <div class="multi-analysis-header" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            text-align: center;
        ">
            <h2 style="margin: 0; font-size: 1.25rem;">
                {type_label} Analysis
            </h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                {frame_count} {'screenshots' if analysis_type == 'multi_image' else 'frames'} analyzed
            </p>
        </div>
        """

        # Build frames gallery if we have frame images
        frames_gallery = ""
        if frame_images:
            # Build JavaScript array of image data (to avoid huge inline attributes)
            js_image_array = "var frameImages = {\n"
            js_labels_array = "var frameLabels = {\n"

            for frame_index in sorted(frame_images.keys()):
                frame_data = frame_images[frame_index]
                image_data = frame_data.get('image_data') or ''
                filename = frame_data.get('filename', f'Frame {frame_index}')
                timestamp = frame_data.get('timestamp')

                if timestamp is not None:
                    label = f"Frame {frame_index} ({timestamp:.1f}s)"
                else:
                    label = f"Frame {frame_index}: {filename}"

                # Escape for JavaScript string
                label_escaped = label.replace("'", "\\'").replace('"', '\\"')

                if image_data and image_data.startswith('data:image'):
                    js_image_array += f'  {frame_index}: "{image_data}",\n'
                else:
                    js_image_array += f'  {frame_index}: "",\n'
                js_labels_array += f'  {frame_index}: "{label_escaped}",\n'

            js_image_array += "};\n"
            js_labels_array += "};\n"

            # Add lightbox modal, styles, and JavaScript with image data
            frames_gallery = f"""
            <style>
                .frame-lightbox {{
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.9);
                    z-index: 10000;
                    justify-content: center;
                    align-items: center;
                    cursor: pointer;
                }}
                .frame-lightbox.active {{
                    display: flex;
                }}
                .frame-lightbox img {{
                    max-width: 90%;
                    max-height: 85%;
                    object-fit: contain;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                }}
                .frame-lightbox .lightbox-label {{
                    position: absolute;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    color: white;
                    background: rgba(0,0,0,0.7);
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }}
                .frame-lightbox .close-btn {{
                    position: absolute;
                    top: 20px;
                    right: 30px;
                    color: white;
                    font-size: 30px;
                    font-weight: bold;
                    cursor: pointer;
                }}
                .gallery-frame-card {{
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                .gallery-frame-card:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
                }}
            </style>
            <div id="frameLightbox" class="frame-lightbox" onclick="closeLightbox()">
                <span class="close-btn">&times;</span>
                <img id="lightboxImg" src="" alt="">
                <div class="lightbox-label" id="lightboxLabel"></div>
            </div>
            <script>
                {js_image_array}
                {js_labels_array}
                function openLightbox(frameIdx) {{
                    var imgSrc = frameImages[frameIdx] || '';
                    var label = frameLabels[frameIdx] || 'Frame ' + frameIdx;
                    if (imgSrc) {{
                        document.getElementById('lightboxImg').src = imgSrc;
                        document.getElementById('lightboxLabel').textContent = label;
                        document.getElementById('frameLightbox').classList.add('active');
                    }}
                }}
                function closeLightbox() {{
                    document.getElementById('frameLightbox').classList.remove('active');
                }}
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') closeLightbox();
                }});
                function getFrameImage(frameIdx) {{
                    return frameImages[frameIdx] || '';
                }}
            </script>
            <div class="frames-gallery" style="
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 2rem;
            ">
                <h2 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px;">
                    📸 Frames Analyzed
                </h2>
                <p style="color: #7f8c8d; margin-bottom: 1rem;">
                    Click any frame to view larger. Issues below reference these frames by number.
                </p>
                <div class="frames-grid" style="
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 1rem;
                ">
            """

            # Sort frames by index and generate gallery cards
            for frame_index in sorted(frame_images.keys()):
                frame_data = frame_images[frame_index]
                image_data = frame_data.get('image_data') or ''
                filename = frame_data.get('filename', f'Frame {frame_index}')
                timestamp = frame_data.get('timestamp')

                # Frame label
                if timestamp is not None:
                    label = f"Frame {frame_index} ({timestamp:.1f}s)"
                else:
                    label = f"Frame {frame_index}: {filename}"

                # Check if we have actual image data
                if image_data and image_data.startswith('data:image'):
                    # Put base64 directly in src attribute (works in both web view and download)
                    frames_gallery += f"""
                        <div class="gallery-frame-card" id="frame-{frame_index}">
                            <img id="gallery-img-{frame_index}" src="{image_data}" alt="{label}" style="
                                width: 100%;
                                height: 180px;
                                object-fit: cover;
                                display: block;
                            ">
                            <div style="
                                padding: 10px;
                                text-align: center;
                                font-weight: 600;
                                color: #2c3e50;
                                font-size: 0.9rem;
                                background: #f0f0f0;
                            ">
                                {label}
                                <div style="font-size: 0.75rem; color: #7f8c8d; font-weight: normal; margin-top: 4px;">
                                    Click to enlarge
                                </div>
                            </div>
                        </div>
                    """
                else:
                    # No image - show placeholder with timestamp
                    frames_gallery += f"""
                        <div class="gallery-frame-card" id="frame-{frame_index}" style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        ">
                            <div style="
                                width: 100%;
                                height: 180px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 1.5rem;
                            ">
                                🎬
                            </div>
                            <div style="
                                padding: 10px;
                                text-align: center;
                                font-weight: 600;
                                color: white;
                                font-size: 0.9rem;
                                background: rgba(0,0,0,0.2);
                            ">
                                {label}
                                <div style="font-size: 0.75rem; opacity: 0.8; font-weight: normal; margin-top: 4px;">
                                    Image not available
                                </div>
                            </div>
                        </div>
                    """

            # Close grid and gallery, then add script to load images from JS array
            frames_gallery += """
                </div>
            </div>
            <script>
                // Function to load all images from JS array
                function loadFrameImages() {
                    for (var frameIdx in frameImages) {
                        // Load gallery images
                        var img = document.getElementById('gallery-img-' + frameIdx);
                        if (img && frameImages[frameIdx]) {
                            img.src = frameImages[frameIdx];
                        }
                        // Load thumbnail images in issue cards (may be multiple per frame)
                        var thumbs = document.querySelectorAll('.thumb-img-' + frameIdx);
                        for (var i = 0; i < thumbs.length; i++) {
                            if (frameImages[frameIdx]) {
                                thumbs[i].src = frameImages[frameIdx];
                            }
                        }
                    }
                }
                // Load images after DOM is ready
                document.addEventListener('DOMContentLoaded', loadFrameImages);
                // Also try immediately in case DOMContentLoaded already fired
                loadFrameImages();
            </script>
            """

        # Insert header and frames gallery after opening body/container
        # Note: HTML uses single quotes for class attributes
        insert_content = header + frames_gallery
        if "<div class='ui-traps-report'>" in base_html:
            base_html = base_html.replace(
                "<div class='ui-traps-report'>",
                f"<div class='ui-traps-report'>{insert_content}"
            )
        elif '<div class="ui-traps-report">' in base_html:
            base_html = base_html.replace(
                '<div class="ui-traps-report">',
                f'<div class="ui-traps-report">{insert_content}'
            )
        elif "<div class='report-container'>" in base_html:
            base_html = base_html.replace(
                "<div class='report-container'>",
                f"<div class='report-container'>{insert_content}"
            )

        return base_html

    def _format_multi_markdown(
        self,
        aggregated: Dict,
        results: List[Dict],
        analysis_type: str,
        frame_images: Dict[int, Dict] = None
    ) -> str:
        """Format aggregated results as Markdown."""
        type_label = "Multi-Screenshot" if analysis_type == 'multi_image' else "Video"
        frame_count = len([r for r in results if not r['error']])

        md = [
            f"# {type_label} UI Traps Analysis",
            f"",
            f"**{frame_count} {'screenshots' if analysis_type == 'multi_image' else 'frames'} analyzed**",
            f"",
        ]

        # Add frame index/reference section
        if frame_images:
            md.append("## 📸 Frames Analyzed")
            md.append("")
            md.append("*Reference these frames when reviewing issues below:*")
            md.append("")
            for frame_index in sorted(frame_images.keys()):
                frame_data = frame_images[frame_index]
                filename = frame_data.get('filename', f'Frame {frame_index}')
                timestamp = frame_data.get('timestamp')
                if timestamp is not None:
                    md.append(f"- **Frame {frame_index}**: {timestamp:.1f}s into video")
                else:
                    md.append(f"- **Frame {frame_index}**: {filename}")
            md.append("")
            md.append("---")
            md.append("")

        # Add base markdown
        base_md = format_report_as_markdown(aggregated)
        md.append(base_md)

        return '\n'.join(md)
