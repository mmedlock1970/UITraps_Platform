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
    from .knowledge_extractor import collect_found_trap_names, extract_trap_sections, extract_trap_images
    from .knowledge_base import get_chunks_for_traps
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
    from knowledge_extractor import collect_found_trap_names, extract_trap_sections, extract_trap_images
    from knowledge_base import get_chunks_for_traps


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

        self.client = Anthropic(api_key=self.api_key, max_retries=3)
        self.use_caching = use_caching
        self.model = "claude-sonnet-4-6"                    # Pass 1: full visual analysis
        self.enrich_model = "claude-haiku-4-5-20251001"    # Pass 2: text enrichment only

    def analyze_design(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        user_id: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        chat_context: Optional[str] = None,
        kb_version: str = "v2",
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
        system_prompt = build_system_prompt(use_caching=self.use_caching, version=kb_version, image_count=1)

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

        # Prepend chat context if provided (from a prior discussion about this design)
        if chat_context and chat_context.strip():
            context_block = {
                "type": "text",
                "text": (
                    "CRITICAL OVERRIDE — UPDATED CONTEXT FROM USER:\n"
                    "The user has provided corrections or clarifications in a prior conversation. "
                    "These corrections OVERRIDE any conflicting values in the structured context "
                    "that follows (users, tasks, format, etc.). "
                    "If the user corrected the user group, tasks, or any other context field, "
                    "use their corrected values and DISREGARD the original values below.\n\n"
                    f"{chat_context.strip()}\n\n"
                    "--- END OF USER CORRECTIONS — use these when analyzing ---\n"
                )
            }
            user_message = [context_block] + list(user_message)

        # Step 4: Call Claude API with structured output
        # Use tool forcing to ensure structured JSON output
        schema = get_ui_analysis_schema()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                temperature=0,
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

                # Validate truly required fields (core structure)
                for field in ['summary_headline', 'summary_narrative', 'critical_issues', 'moderate_issues', 'minor_issues']:
                    if field not in report:
                        raise ValueError(f"Missing required field in response: {field}")

                # Ensure summary fields are strings
                if not isinstance(report.get('summary_headline'), str):
                    report['summary_headline'] = ''
                if not isinstance(report.get('summary_narrative'), str):
                    report['summary_narrative'] = ''

                # Ensure issue arrays are actually arrays
                for issue_field in ['critical_issues', 'moderate_issues', 'minor_issues']:
                    if not isinstance(report[issue_field], list):
                        raise ValueError(f"{issue_field} must be an array, got {type(report[issue_field])}")

                # Default optional array fields if absent or wrong type
                for opt_field in ['positive_observations', 'potential_issues', 'traps_checked_not_found',
                                  'flagged_for_human_review', 'incomplete_flow_findings']:
                    if not isinstance(report.get(opt_field), list):
                        report[opt_field] = []

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
            report = self._enrich_report(report, timeout=timeout, kb_version=kb_version)
        except Exception as e:
            # Enrichment failure is non-fatal — use Pass 1 report as-is
            print(f"[UITraps] Pass 2 enrichment skipped (non-fatal): {e}")

        # Step 8: Generate outputs
        # Normalize optional fields after enrichment — Pass 2 may omit fields that were
        # present in Pass 1, causing formatter KeyErrors.
        for _opt in ['positive_observations', 'potential_issues', 'traps_checked_not_found',
                     'flagged_for_human_review', 'incomplete_flow_findings']:
            if not isinstance(report.get(_opt), list):
                report[_opt] = []

        # Guarantee report completeness across KB versions: backfill the per-trap
        # "Could Not Evaluate" breakdown. This makes v1 and v2 reports symmetric.
        self._normalize_report_completeness(report, kb_version=kb_version)

        if chat_context and chat_context.strip():
            user_context = dict(user_context)
            user_context['chat_context_used'] = True
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

    def _enrich_report(self, pass1_report: Dict[str, Any], timeout: int = 120, kb_version: str = "v2") -> Dict[str, Any]:
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

        # Load structured knowledge base chunks for the found traps
        knowledge_chunks = get_chunks_for_traps(found_trap_names, version=kb_version) or None
        if knowledge_chunks:
            print(f"[UITraps] Pass 2: loaded {kb_version} KB chunks for {len(found_trap_names)} trap(s)")

        # Fall back to extracted book sections if KB chunks unavailable
        trap_sections = {} if knowledge_chunks else extract_trap_sections(found_trap_names)

        # Only fetch book illustration images when KB text chunks are unavailable —
        # images are redundant and expensive (input tokens) when text chunks already
        # supply the same knowledge for enrichment.
        if not knowledge_chunks:
            trap_images = extract_trap_images(found_trap_names, version=kb_version)
            if kb_version == "v1":
                trap_images = {k: v[:1] for k, v in trap_images.items()}
            if trap_images:
                n_imgs = sum(len(v) for v in trap_images.values())
                print(f"[UITraps] Pass 2: including {n_imgs} book illustration(s) for {len(trap_images)} trap(s)")
        else:
            trap_images = {}
            print(f"[UITraps] Pass 2: skipping book images — KB text chunks sufficient")

        # Build Pass 2 prompts
        system_prompt = build_enrichment_system_prompt()
        user_message = build_enrichment_user_message(
            pass1_report, trap_sections, trap_images, knowledge_chunks=knowledge_chunks
        )
        schema = get_ui_analysis_schema()

        print(f"[UITraps] Pass 2: enriching {len(found_trap_names)} trap(s): {', '.join(found_trap_names)}")

        response = self.client.messages.create(
            model=self.enrich_model,
            max_tokens=3500,
            temperature=0,
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

        # Always restore traps_checked_not_found from Pass 1 — Pass 2 regenerates
        # this field with all testable:true, overwriting the correct testable:false
        # values set by Pass 1 based on the detectability rules.
        enriched['traps_checked_not_found'] = pass1_report.get('traps_checked_not_found', [])

        # Preserve other Pass 1 fields that Pass 2 might omit
        for field in (
            "potential_issues", "bugs_detected",
            "incomplete_flow_findings", "flagged_for_human_review",
        ):
            if field in pass1_report and field not in enriched:
                enriched[field] = pass1_report[field]



        print(f"[UITraps] Pass 2: enrichment complete ({response.usage.input_tokens} input tokens)")
        return enriched

    def _normalize_report_completeness(self, report: Dict[str, Any], kb_version: str = "v2") -> None:
        """
        Make v1 and v2 reports structurally symmetric. Mutates report in place.

        Two model-output gaps that this fixes:
        1. `traps_checked_not_found` sometimes ships with items missing the
           `testable` flag, missing a `reason`, or not covering every trap in
           the version's canonical list. We backfill every non-confirmed trap
           with the right testable flag and a default reason when needed.
        2. `traps_checked_not_found` entries are normalised here to ensure
           were confirmed. We synthesize a single fallback user_issue from the
           confirmed traps in that case so the section always renders.
        """
        try:
            from .prompts import _TRAP_NAMES_V1, _TRAP_NAMES_V2
            from .formatters import _UNTESTABLE_REASON_DEFAULTS, _normalize_trap_name
        except ImportError:
            from prompts import _TRAP_NAMES_V1, _TRAP_NAMES_V2
            from formatters import _UNTESTABLE_REASON_DEFAULTS, _normalize_trap_name

        src = _TRAP_NAMES_V2 if kb_version == "v2" else _TRAP_NAMES_V1
        canonical_traps = [t.strip() for t in src.split(",") if t.strip()]

        # Traps that are always evaluable from a single screenshot — default testable:true.
        testable_true_norm = {
            "POOR GROUPING", "FORCED SYNTAX", "INFORMATION OVERLOAD",
            "UNNECESSARY STEP(S)", "UNNECESSARY STEP", "UNNECESSARY STEPS",
            "GRATUITOUS REDUNDANCY",
            "INCORRECT INFORMATION", "INCORRECT INFO",
            "BAD PREDICTION",
        }
        # Traps that are never evaluable from a static artifact — force testable:false always,
        # regardless of what the model output.
        testable_always_false_norm = {
            "SLOW OR NO RESPONSE",
            "POOR AESTHETIC", "UNATTRACTIVE APPEARANCE",
        }

        confirmed_norm = set()
        for sev_field in ("critical_issues", "moderate_issues", "minor_issues"):
            for issue in report.get(sev_field, []):
                tn = (issue or {}).get("trap_name", "")
                if tn:
                    confirmed_norm.add(_normalize_trap_name(tn))

        existing_by_norm: Dict[str, Dict[str, Any]] = {}
        for item in report.get("traps_checked_not_found", []) or []:
            if isinstance(item, dict):
                tn = item.get("trap_name", "")
                if tn:
                    existing_by_norm[_normalize_trap_name(tn)] = item
            elif isinstance(item, str) and item.strip():
                existing_by_norm[_normalize_trap_name(item)] = {
                    "trap_name": item, "testable": True
                }

        def _default_reason(norm: str) -> str:
            return _UNTESTABLE_REASON_DEFAULTS.get(
                norm,
                "Requires additional screenshots, interaction data, or live testing to evaluate."
            )

        new_tcnf = []
        for canonical in canonical_traps:
            norm = _normalize_trap_name(canonical)
            if norm in confirmed_norm:
                continue
            existing = existing_by_norm.get(norm)
            if existing is not None:
                item = dict(existing)
                if norm in testable_always_false_norm:
                    # Never evaluable — force false regardless of model output
                    item["testable"] = False
                    if not (item.get("reason") or "").strip():
                        item["reason"] = _default_reason(norm)
                elif norm in testable_true_norm:
                    # Always evaluable — accept true, fill default if missing
                    item.setdefault("testable", True)
                else:
                    # Conditional trap — respect model's judgment; add reason if false
                    if not item.get("testable", True):
                        if not (item.get("reason") or "").strip():
                            item["reason"] = _default_reason(norm)
                new_tcnf.append(item)
            else:
                if norm in testable_true_norm:
                    new_tcnf.append({"trap_name": canonical, "testable": True})
                else:
                    # Not output by model — default to not-evaluated with standard reason
                    new_tcnf.append({
                        "trap_name": canonical,
                        "testable": False,
                        "reason": _default_reason(norm),
                    })

        report["traps_checked_not_found"] = new_tcnf


    def _load_image(self, image_path: str) -> Dict[str, Any]:
        """
        Load image file and prepare for Claude vision API.

        Resizes to 1568px max on the longest side before encoding.
        Claude Vision scales images to this limit internally anyway, so
        pre-resizing reduces upload payload and token count without any
        loss in what Claude can perceive.
        """
        import io
        from PIL import Image

        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        media_type = media_type_map.get(ext)
        if not media_type:
            raise ValueError(f"Unsupported image format: {ext}")

        MAX_SIDE = 1568
        try:
            img = Image.open(image_path)
            w, h = img.size
            if max(w, h) > MAX_SIDE:
                scale = MAX_SIDE / max(w, h)
                new_w, new_h = int(w * scale), int(h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                print(f"[UITraps] Image resized {w}×{h} → {new_w}×{new_h}")

            buf = io.BytesIO()
            if media_type == 'image/jpeg':
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(buf, format='JPEG', quality=92, optimize=True)
            else:
                img.save(buf, format='PNG', optimize=True)
            img.close()
            image_data = base64.standard_b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"[UITraps] Image resize failed ({e}), using raw file")
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

        Claude Sonnet 4.6 pricing:
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
                temperature=0,
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
