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
    from .prompts import (
        build_system_prompt, build_user_message, build_figma_message,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message
    )
    from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
    from .schema import get_ui_analysis_schema, get_interaction_analysis_schema
    from .knowledge_extractor import collect_found_trap_names, extract_trap_sections
except ImportError:
    # Fallback for direct script execution
    from validators import validate_file_format, validate_context, is_figma_url
    from prompts import (
        build_system_prompt, build_user_message, build_figma_message,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message
    )
    from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
    from schema import get_ui_analysis_schema, get_interaction_analysis_schema
    from knowledge_extractor import collect_found_trap_names, extract_trap_sections


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

                # Reconcile summary with actual structured counts to prevent contradictions
                # (Claude's free-form summary text can diverge from the structured issue arrays)
                n_critical = len(report['critical_issues'])
                n_moderate = len(report['moderate_issues'])
                n_minor = len(report['minor_issues'])
                n_total = n_critical + n_moderate + n_minor
                if n_total > 0:
                    parts = []
                    if n_critical:
                        parts.append(f"{n_critical} critical")
                    if n_moderate:
                        parts.append(f"{n_moderate} moderate")
                    if n_minor:
                        parts.append(f"{n_minor} minor")
                    count_bullet = f"{n_total} issue{'s' if n_total != 1 else ''} identified: {', '.join(parts)}."
                else:
                    count_bullet = "No confirmed issues identified in this design."
                if report['summary']:
                    report['summary'][0] = count_bullet
                else:
                    report['summary'] = [count_bullet]

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

        # Step 7: Pass 2 — Enrich findings using full book sections
        try:
            report = self._enrich_report(report, timeout=timeout)
        except Exception as e:
            # Enrichment failure is non-fatal — use Pass 1 report as-is
            print(f"[UITraps] Pass 2 enrichment skipped (non-fatal): {e}")

        # Step 8: Generate outputs
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

    def _enrich_report(self, pass1_report: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        """
        Pass 2: Enrich Pass 1 findings using full book sections for found traps.

        Extracts the relevant book sections for each trap identified in Pass 1,
        then calls Claude to rewrite the problem descriptions and recommendations
        with richer, more educational content.

        Args:
            pass1_report: Structured report from Pass 1 detection
            timeout: API call timeout in seconds

        Returns:
            Enriched report (same schema as Pass 1, with enhanced text fields).
            Falls back to pass1_report unchanged if no traps were found.
        """
        # Collect trap names found in Pass 1
        found_trap_names = collect_found_trap_names(pass1_report)

        # If nothing was found, no enrichment needed
        if not found_trap_names:
            return pass1_report

        # Extract the relevant book sections
        trap_sections = extract_trap_sections(found_trap_names)

        # Build Pass 2 prompts
        system_prompt = build_enrichment_system_prompt()
        user_message = build_enrichment_user_message(pass1_report, trap_sections)
        schema = get_ui_analysis_schema()

        print(f"[UITraps] Pass 2: enriching {len(found_trap_names)} trap(s): {', '.join(found_trap_names)}")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=[
                {
                    "name": "ui_analysis_report",
                    "description": "Submit the enriched UI Tenets & Traps analysis report",
                    "input_schema": schema
                }
            ],
            tool_choice={"type": "tool", "name": "ui_analysis_report"},
            timeout=timeout
        )

        # Parse enriched report
        tool_use_block = next(
            (block for block in response.content if block.type == "tool_use"),
            None
        )

        if not tool_use_block:
            print("[UITraps] Pass 2: no tool use block in response, using Pass 1 report")
            return pass1_report

        enriched = tool_use_block.input

        # Preserve Pass 1 fields that Pass 2 might not return
        for field in ("bugs_detected", "incomplete_flow_findings", "flagged_for_human_review"):
            if field in pass1_report and field not in enriched:
                enriched[field] = pass1_report[field]

        # Re-apply the count reconciliation on the enriched summary
        n_critical = len(enriched.get("critical_issues", []))
        n_moderate = len(enriched.get("moderate_issues", []))
        n_minor = len(enriched.get("minor_issues", []))
        n_total = n_critical + n_moderate + n_minor
        if n_total > 0:
            parts = []
            if n_critical:
                parts.append(f"{n_critical} critical")
            if n_moderate:
                parts.append(f"{n_moderate} moderate")
            if n_minor:
                parts.append(f"{n_minor} minor")
            count_bullet = f"{n_total} issue{'s' if n_total != 1 else ''} identified: {', '.join(parts)}."
        else:
            count_bullet = "No confirmed issues identified in this design."

        if enriched.get("summary"):
            enriched["summary"][0] = count_bullet
        else:
            enriched["summary"] = [count_bullet]

        print(f"[UITraps] Pass 2: enrichment complete ({response.usage.input_tokens} input tokens)")
        return enriched

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

    def analyze_interaction_sequence(
        self,
        images: list,
        interaction_type: str,
        element_description: str,
        labels: list,
        user_context: Optional[Dict[str, str]] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Analyze a UI interaction sequence using multi-image analysis.

        This method analyzes screenshot sequences captured during user interactions
        (hover, click, form validation, scroll, responsive) to detect interaction-specific
        UI Traps like FEEDBACK FAILURE, ACCIDENTAL ACTIVATION, etc.

        Args:
            images: List of image dicts (base64 encoded) in sequence order
                   Each dict should have: {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}
            interaction_type: Type of interaction ("hover", "click", "form", "scroll", "responsive")
            element_description: Description of the element being interacted with
            labels: List of labels for each screenshot (e.g., ["before_hover", "during_hover"])
            user_context: Optional user context dict with 'users', 'tasks' keys
            timeout: Maximum time to wait for response (seconds)

        Returns:
            Dictionary containing:
                - analysis: Structured interaction analysis result
                - metadata: Analysis metadata (tokens, cost, duration)

        Raises:
            ValueError: If inputs are invalid
            Exception: If API call fails
        """
        start_time = time.time()

        # Validate inputs
        if not images:
            raise ValueError("At least one image is required")
        if len(images) != len(labels):
            raise ValueError(f"Number of images ({len(images)}) must match number of labels ({len(labels)})")
        if interaction_type not in ["hover", "click", "form", "scroll", "responsive"]:
            raise ValueError(f"Invalid interaction type: {interaction_type}")

        # Build message with images
        user_message = build_interaction_message(
            images=images,
            interaction_type=interaction_type,
            element_description=element_description,
            labels=labels,
            user_context=user_context
        )

        # Get interaction analysis schema
        schema = get_interaction_analysis_schema()

        # Build system prompt for interaction analysis
        system_prompt = [
            {
                "type": "text",
                "text": INTERACTION_ANALYSIS_SYSTEM_PROMPT
            }
        ]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                tools=[
                    {
                        "name": "interaction_analysis_report",
                        "description": "Submit the interaction analysis report",
                        "input_schema": schema
                    }
                ],
                tool_choice={"type": "tool", "name": "interaction_analysis_report"},
                timeout=timeout
            )
        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")

        # Parse response
        try:
            tool_use_block = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if not tool_use_block:
                raise ValueError("No tool use found in response")

            analysis = tool_use_block.input

            # Validate required fields
            required_fields = [
                'interaction_type', 'element_analyzed', 'feedback_quality',
                'state_transition', 'traps_detected', 'overall_assessment', 'summary'
            ]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure arrays are arrays
            if not isinstance(analysis.get('traps_detected'), list):
                analysis['traps_detected'] = []
            if not isinstance(analysis.get('accessibility_concerns'), list):
                analysis['accessibility_concerns'] = []
            if not isinstance(analysis.get('positive_observations'), list):
                analysis['positive_observations'] = []

        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}")

        # Calculate metadata
        duration = time.time() - start_time

        metadata = {
            "model": self.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "duration_seconds": round(duration, 2),
            "estimated_cost": self._estimate_cost(response.usage),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "interaction_type": interaction_type,
            "image_count": len(images)
        }

        return {
            "analysis": analysis,
            "metadata": metadata,
            "status": "success"
        }

    def analyze_all_interactions(
        self,
        interactions: list,
        user_context: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple interaction sequences and aggregate results.

        Args:
            interactions: List of interaction dicts, each containing:
                - images: List of base64 image dicts
                - interaction_type: Type of interaction
                - element_description: Description of element
                - labels: List of labels for screenshots
            user_context: Optional user context
            progress_callback: Optional callback(current, total, message)

        Returns:
            Dictionary containing:
                - individual_analyses: List of individual analysis results
                - summary: Aggregated summary of all interactions
                - statistics: Aggregate statistics
                - metadata: Combined metadata
        """
        if not interactions:
            return {
                "individual_analyses": [],
                "summary": {"message": "No interactions to analyze"},
                "statistics": {},
                "metadata": {}
            }

        start_time = time.time()
        individual_analyses = []
        total_cost = 0
        total_tokens = 0

        for i, interaction in enumerate(interactions):
            if progress_callback:
                progress_callback(
                    i + 1,
                    len(interactions),
                    f"Analyzing {interaction.get('interaction_type', 'unknown')} interaction..."
                )

            try:
                result = self.analyze_interaction_sequence(
                    images=interaction.get('images', []),
                    interaction_type=interaction.get('interaction_type', 'click'),
                    element_description=interaction.get('element_description', 'Unknown element'),
                    labels=interaction.get('labels', []),
                    user_context=user_context
                )
                individual_analyses.append({
                    "success": True,
                    "interaction_type": interaction.get('interaction_type'),
                    "element": interaction.get('element_description'),
                    "analysis": result.get('analysis'),
                    "metadata": result.get('metadata')
                })
                total_cost += result.get('metadata', {}).get('estimated_cost', 0)
                total_tokens += result.get('metadata', {}).get('total_tokens', 0)

            except Exception as e:
                individual_analyses.append({
                    "success": False,
                    "interaction_type": interaction.get('interaction_type'),
                    "element": interaction.get('element_description'),
                    "error": str(e)
                })

        # Generate aggregate statistics
        successful = [a for a in individual_analyses if a.get('success')]
        statistics = {
            "total_analyzed": len(interactions),
            "successful": len(successful),
            "failed": len(interactions) - len(successful),
            "by_type": {},
            "issues_found": {
                "critical": 0,
                "moderate": 0,
                "minor": 0
            }
        }

        # Count by type and collect issues
        all_traps = []
        for analysis in successful:
            itype = analysis.get('interaction_type', 'unknown')
            if itype not in statistics['by_type']:
                statistics['by_type'][itype] = {"count": 0, "issues": 0}
            statistics['by_type'][itype]['count'] += 1

            traps = analysis.get('analysis', {}).get('traps_detected', [])
            for trap in traps:
                severity = trap.get('severity', 'minor')
                statistics['issues_found'][severity] = statistics['issues_found'].get(severity, 0) + 1
                statistics['by_type'][itype]['issues'] += 1
                all_traps.append({
                    **trap,
                    'interaction_type': itype,
                    'element': analysis.get('element')
                })

        # Generate summary
        summary = {
            "total_interactions": len(interactions),
            "overall_assessment": self._determine_overall_assessment(statistics),
            "critical_findings": [t for t in all_traps if t.get('severity') == 'critical'],
            "all_issues": all_traps
        }

        duration = time.time() - start_time

        return {
            "individual_analyses": individual_analyses,
            "summary": summary,
            "statistics": statistics,
            "metadata": {
                "total_duration_seconds": round(duration, 2),
                "total_estimated_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def _determine_overall_assessment(self, statistics: dict) -> str:
        """Determine overall assessment based on issues found."""
        issues = statistics.get('issues_found', {})
        if issues.get('critical', 0) > 0:
            return "poor"
        elif issues.get('moderate', 0) > 2:
            return "needs_improvement"
        elif issues.get('moderate', 0) > 0 or issues.get('minor', 0) > 3:
            return "acceptable"
        else:
            return "good"


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
