"""
Main UI Traps Analyzer - Claude API Integration

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

This software is provided exclusively to authorized subscribers.
Unauthorized reproduction, distribution, or use is prohibited.
"""
import os
import base64
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from anthropic import Anthropic

try:
    from .validators import validate_file_format, validate_context, is_figma_url
    from .prompts import build_system_prompt, build_user_message, build_figma_message
    from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
    from .schema import get_ui_analysis_schema
except ImportError:
    # Fallback for direct script execution
    from validators import validate_file_format, validate_context, is_figma_url
    from prompts import build_system_prompt, build_user_message, build_figma_message
    from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
    from schema import get_ui_analysis_schema


class UITrapsAnalyzer:
    """
    Main analyzer class for UI Tenets & Traps evaluation.

    Usage:
        analyzer = UITrapsAnalyzer(api_key="your-key")
        report = analyzer.analyze_design(
            design_file="path/to/image.png",
            user_context={
                "users": "Professional designers and PMs",
                "tasks": "Creating projects, reviewing designs",
                "format": "PNG screenshot"
            }
        )
    """

    def __init__(self, api_key: Optional[str] = None, use_caching: bool = True):
        """
        Initialize the analyzer.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            use_caching: Use prompt caching to reduce costs (recommended for production)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Either pass api_key parameter or "
                "set ANTHROPIC_API_KEY environment variable."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.use_caching = use_caching
        self.model = "claude-sonnet-4-5-20250929"  # Latest Sonnet 4.5

    def analyze_design(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        user_id: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a UI design using the UI Tenets & Traps framework.

        Args:
            design_file: Path to image/video file or Figma URL
            user_context: Dict with 'users', 'tasks', 'format' keys
            timeout: Maximum time to wait for response (seconds)
            user_id: Optional user ID for tracking
            page_context: Optional dict for multi-page analysis context:
                - page_role: Classified page type (homepage, product, etc.)
                - page_title: Title of this page
                - page_url: URL of this page
                - site_pages: List of other page titles on the site
                - relevant_tasks: Tasks appropriate for this page type

        Returns:
            Dictionary containing:
                - report: Parsed report with all findings
                - metadata: Analysis metadata (tokens, cost, duration)
                - markdown: Formatted markdown report
                - statistics: Report statistics

        Raises:
            ValueError: If validation fails
            Exception: If API call fails
        """
        start_time = time.time()

        # Step 1: Validate inputs
        is_valid_context, context_msg = validate_context(user_context)
        if not is_valid_context:
            raise ValueError(f"Invalid context: {context_msg}")

        is_valid_file, file_msg = validate_file_format(design_file)
        if not is_valid_file:
            raise ValueError(f"Invalid file: {file_msg}")

        # Step 2: Build prompts
        system_prompt = build_system_prompt(use_caching=self.use_caching)

        # Step 3: Handle different file types
        if is_figma_url(design_file):
            # For Figma URLs, we need special handling
            # In production, you'd either:
            # 1. Use Figma API to fetch images
            # 2. Ask user to export PNG
            # For now, we'll provide guidance
            user_message = build_figma_message(user_context, design_file)
            raise NotImplementedError(
                "Figma URL support requires additional implementation. "
                "Please export your Figma design as PNG/JPG and upload the image file. "
                "Alternatively, integrate Figma API to fetch design images automatically."
            )
        else:
            # Load image and convert to base64 for Claude
            image_data = self._load_image(design_file)
            user_message = build_user_message(user_context, image_data, page_context)

        # Step 4: Call Claude API with structured output
        # Use tool forcing to ensure structured JSON output
        schema = get_ui_analysis_schema()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,  # Enough for detailed reports
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                tools=[
                    {
                        "name": "ui_analysis_report",
                        "description": "Submit the complete UI Tenets & Traps analysis report",
                        "input_schema": schema
                    }
                ],
                tool_choice={"type": "tool", "name": "ui_analysis_report"},
                timeout=timeout
            )
        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")

        # Step 5: Parse response from tool use
        # With tool forcing, response will be in tool_use content block
        try:
            tool_use_block = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if not tool_use_block:
                # Fallback to text parsing if tool use not found
                response_text = response.content[0].text
                report = parse_claude_response(response_text)
            else:
                # Extract structured data directly from tool input
                report = tool_use_block.input

                # Validate required fields are present
                required_fields = [
                    'summary', 'critical_issues', 'moderate_issues',
                    'minor_issues', 'positive_observations', 'potential_issues', 'traps_checked_not_found'
                ]
                for field in required_fields:
                    if field not in report:
                        raise ValueError(f"Missing required field in response: {field}")

                # Validate and fix data types
                # Summary must be an array of strings
                if isinstance(report['summary'], str):
                    # Claude returned a string instead of array - wrap it
                    report['summary'] = [report['summary']]
                elif not isinstance(report['summary'], list):
                    raise ValueError(f"Summary must be an array, got {type(report['summary'])}")

                # Ensure issue arrays are actually arrays
                for issue_field in ['critical_issues', 'moderate_issues', 'minor_issues']:
                    if not isinstance(report[issue_field], list):
                        raise ValueError(f"{issue_field} must be an array, got {type(report[issue_field])}")

                # Ensure positive observations, potential issues, and traps not found are arrays
                if not isinstance(report['positive_observations'], list):
                    report['positive_observations'] = []
                if not isinstance(report['potential_issues'], list):
                    report['potential_issues'] = []
                if not isinstance(report['traps_checked_not_found'], list):
                    report['traps_checked_not_found'] = []

        except Exception as e:
            raise ValueError(
                f"Failed to parse Claude's response: {e}\n\n"
                f"Response content: {response.content}"
            )

        # Step 6: Calculate metadata
        duration = time.time() - start_time

        metadata = {
            "model": self.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "cache_creation_tokens": getattr(response.usage, 'cache_creation_input_tokens', 0),
            "cache_read_tokens": getattr(response.usage, 'cache_read_input_tokens', 0),
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "duration_seconds": round(duration, 2),
            "estimated_cost": self._estimate_cost(response.usage),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id
        }

        # Step 7: Generate outputs
        markdown_report = format_report_as_markdown(report, user_context)
        html_report = format_report_as_html(report, user_context)
        statistics = get_report_statistics(report)

        return {
            "report": report,
            "metadata": metadata,
            "markdown": markdown_report,
            "html": html_report,
            "statistics": statistics,
            "status": "success"
        }

    def _load_image(self, image_path: str) -> Dict[str, Any]:
        """
        Load image file and prepare for Claude vision API.

        Args:
            image_path: Path to image file

        Returns:
            Image data dict for Claude API
        """
        # Determine media type
        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }

        media_type = media_type_map.get(ext)
        if not media_type:
            raise ValueError(f"Unsupported image format: {ext}")

        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }

    def _estimate_cost(self, usage) -> float:
        """
        Estimate API cost based on token usage.

        Claude Sonnet 4.5 pricing (as of Jan 2025):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        - Cache writes: $3.75 per million tokens
        - Cache reads: $0.30 per million tokens

        Args:
            usage: Usage object from Claude API response

        Returns:
            Estimated cost in USD
        """
        input_cost = (usage.input_tokens / 1_000_000) * 3.0
        output_cost = (usage.output_tokens / 1_000_000) * 15.0

        cache_write_cost = 0
        cache_read_cost = 0

        if hasattr(usage, 'cache_creation_input_tokens'):
            cache_write_cost = (usage.cache_creation_input_tokens / 1_000_000) * 3.75

        if hasattr(usage, 'cache_read_input_tokens'):
            cache_read_cost = (usage.cache_read_input_tokens / 1_000_000) * 0.30

        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        return round(total_cost, 4)

    def analyze_design_stream(
        self,
        design_file: str,
        user_context: Dict[str, str],
        callback=None
    ):
        """
        Analyze design with streaming response (for real-time UI updates).

        Args:
            design_file: Path to image/video file
            user_context: Dict with 'users', 'tasks', 'format' keys
            callback: Optional function to call with each chunk of response

        Yields:
            Chunks of the analysis as they're generated

        Note: This is a placeholder for future streaming implementation.
        Claude API supports streaming, which can provide better UX.
        """
        raise NotImplementedError(
            "Streaming analysis not yet implemented. "
            "Use analyze_design() for now."
        )


# Convenience function for simple usage
def analyze_design(
    design_file: str,
    user_context: Dict[str, str],
    api_key: Optional[str] = None,
    use_caching: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to analyze a design without creating analyzer instance.

    Args:
        design_file: Path to image/video file or Figma URL
        user_context: Dict with 'users', 'tasks', 'format' keys
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        use_caching: Use prompt caching to reduce costs

    Returns:
        Analysis results dictionary

    Example:
        result = analyze_design(
            design_file="screenshot.png",
            user_context={
                "users": "Software developers and testers",
                "tasks": "Running tests, viewing results",
                "format": "PNG"
            }
        )
        print(result['markdown'])
    """
    analyzer = UITrapsAnalyzer(api_key=api_key, use_caching=use_caching)
    return analyzer.analyze_design(design_file, user_context)
