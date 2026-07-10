"""
Main UI Traps Analyzer - Claude API Integration

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

This software is provided exclusively to authorized subscribers.
Unauthorized reproduction, distribution, or use is prohibited.
"""
import os
import ast
import base64
import hashlib
import json
import logging
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Floor for the per-request API timeout on an analysis pass. A heavy two-pass adjudication
# (many matched traps → many chunks loaded + up to 8,000 output tokens) can take several
# minutes to generate; the old 120s default timed out mid-generation and forced SDK retries
# that wasted the whole attempt. 600s lets a single attempt finish. (Anthropic recommends
# streaming for high max_tokens; this floor is the low-risk fix pending that.)
_ANALYSIS_API_TIMEOUT_S = 600

# Multi-screen (flow) analysis sends all screens in ONE call; the output ceiling and cross-screen
# reasoning are tuned for short flows. Hard-cap the screen count — a clear stop beats silent
# output truncation or the model self-limiting. Revisit if longer flows are genuinely needed.
MAX_FLOW_SCREENS = 12


def resolve_artifact_class(input_type: Optional[str], n_files: int) -> str:
    """Which rung of the observability scale the SUBMITTED artifact sits on — a mechanical fact about
    the input medium (tool-owned, like screen count). The KB owns the per-Trap floors on this scale
    (Ledger 26 ASSESSABILITY-DIGEST); the disposition gate compares this class against those floors.
    Conservative by construction: a medium is mapped to a rung only when it genuinely exposes that
    rung's evidence, and ties break DOWN — over-claiming a class would wrongly license "Not present"
    verdicts the artifact can't support, the exact error the gate exists to stop. Scale order:
    static-screenshot < disconnected-screens < flow < live < code. The video→live and
    flow_diagram→flow mappings are tool-owned tuning, re-rulable if the medium's real coverage differs.
    """
    it = (input_type or "").strip().lower()
    if it == "video":
        return "live"                 # a recording exposes real-time feedback / timing / activation
    if it == "flow_diagram":
        return "flow"                 # a flow shows the screen-to-screen transitions in one artifact
    if it in ("multi_image", "multi-image", "multi_screen") or n_files > 1:
        return "disconnected-screens"  # separate stills, no wired transitions between them
    return "static-screenshot"        # a single still — the most restrictive, default rung

# Stream generations at/above this max_tokens ceiling. Streaming is the Anthropic-recommended path
# for high-max_tokens calls: it keeps the HTTP connection active so a multi-minute generation can't
# trip the idle timeout and force an SDK retry that re-runs the entire attempt. The final Message is
# identical to messages.create()'s, so downstream parsing is unchanged.
_STREAM_MIN_TOKENS = 8000

# Public list price per 1M tokens (USD): (input, output, cache_write, cache_read).
# Used only for the estimated-cost line in the report header — not billing.
_MODEL_PRICING = {
    "claude-sonnet-4-6":          (3.0, 15.0, 3.75, 0.30),
    "claude-haiku-4-5-20251001":  (1.0,  5.0, 1.25, 0.10),
    "claude-haiku-4-5":           (1.0,  5.0, 1.25, 0.10),
}


def _usage_from_response(response, model: str):
    """Token usage + estimated USD cost from an API response's usage block (None if absent)."""
    u = getattr(response, "usage", None)
    if u is None:
        return None
    inp = getattr(u, "input_tokens", 0) or 0
    out = getattr(u, "output_tokens", 0) or 0
    cr = getattr(u, "cache_read_input_tokens", 0) or 0
    cw = getattr(u, "cache_creation_input_tokens", 0) or 0
    pin, pout, pcw, pcr = _MODEL_PRICING.get(model, _MODEL_PRICING["claude-sonnet-4-6"])
    cost = (inp * pin + out * pout + cw * pcw + cr * pcr) / 1_000_000
    return {"input": inp, "output": out, "cache_read": cr, "cache_creation": cw, "cost": cost}


def _sum_usage(*usages):
    """Sum any number of _usage dicts (None-safe) into one, for multi-call passes."""
    total = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "cost": 0.0}
    seen = False
    for u in usages:
        if not u:
            continue
        seen = True
        for k in total:
            total[k] += u.get(k, 0) or 0
    return total if seen else None

try:
    from .validators import validate_file_format, validate_context, is_figma_url
    from .prompts import (
        build_system_prompt, build_user_message, build_figma_message, build_multi_screen_blocks,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message,
    )
    try:
        from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_bytrap_report_as_html
    except ImportError:
        from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
        format_bytrap_report_as_html = None
    from .schema import get_ui_analysis_schema, get_interaction_analysis_schema, get_user_issues_schema, is_new_kb, normalize_relationship
    from .knowledge_extractor import collect_found_trap_names, extract_trap_sections, extract_trap_images
    from .knowledge_base import get_chunks_for_traps
    from . import pack_generator
    from . import run_logger
except ImportError:
    # Fallback for direct script execution
    from validators import validate_file_format, validate_context, is_figma_url
    from prompts import (
        build_system_prompt, build_user_message, build_figma_message, build_multi_screen_blocks,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message,
    )
    try:
        from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_bytrap_report_as_html
    except ImportError:
        from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics
        format_bytrap_report_as_html = None
    from schema import get_ui_analysis_schema, get_interaction_analysis_schema, get_user_issues_schema, is_new_kb, normalize_relationship
    from knowledge_extractor import collect_found_trap_names, extract_trap_sections, extract_trap_images
    from knowledge_base import get_chunks_for_traps
    import pack_generator
    import run_logger


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
        additional_design_files: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        chat_context: Optional[str] = None,
        kb_version: str = "v2",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        thorough_mode: bool = False,
        report_style: str = "trap",
        mode: str = "single",
        profile: str = "default",
        frame_notice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a UI design using the UI Tenets & Traps framework.

        frame_notice: optional disclosure banner rendered at the top of the report (e.g. the
        Figma flow path truncating a large file to the first MAX_FLOW_SCREENS frames). Reflects
        reality in the report itself so a truncation-caused miss is never misread as a KB gap.

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
            thorough_mode: Deprecated/ignored. The legacy tenet-parallel pipeline was removed;
                accepted only for API backward-compatibility.
            report_style: "trap" (default) for per-Trap HTML report; "issues" for user-centric issues synthesis.

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

        # Sonnet-only (Haiku dropped). Hard-reject any non-Sonnet model instead of silently
        # falling back — a report's config line must never claim a model the run did not use, so a
        # silent fallback would make that line lie. None defaults to Sonnet; "sonnet" is explicit;
        # anything else (stale client, saved config, hand-edited payload) is rejected here, the
        # single chokepoint every call path (image, flow, multi-screen) passes through.
        if pass1_model is not None and str(pass1_model).strip().lower() not in ("", "sonnet"):
            raise ValueError(f"model not available: {pass1_model!r} — only Sonnet is available.")

        # The By-Issue report style is retired — every run renders By Trap. Pinning here forces the
        # by-trap schema/prompt/formatter for ALL profiles (including self-serve, 1D) and makes the
        # legacy issue-mode branches below inert. The `report_style` param is kept for API/signature
        # compatibility but no longer selects a rendering.
        report_style = "trap"

        # Self-serve (raw-KB) profile: single-pass, by-trap, rev6 template, with the harness's
        # minimal prompt + relaxed schema — regardless of KB lineage. This is an experimental
        # condition; the output contract is harness-provided and identical in kind to the other
        # conditions, and the minimal prompt is deliberately NOT strengthened.
        _self_serve = (profile == "self-serve")
        if _self_serve:
            # Self-serve is always ONE call against the raw KB — force single-pass and off
            # thorough (a separate legacy pipeline that would bypass the self-serve
            # prompt/schema). report_style is honored: 'issues' → bare issues schema, 'trap' →
            # bare per-trap schema; both use the minimal KB-only prompt, no coaching, no
            # enrichment pass. This keeps the KB-only condition clean for either report style.
            mode = "single"
            thorough_mode = False

        # Multi-screen (flow) analysis: load ALL screens and pack them into one labeled
        # image_data_list so the model reasons across the whole flow in a SINGLE call
        # (flow-aware, per KB G7) rather than per-screen in isolation. Single-image runs keep
        # preloaded_images=None and behave exactly as before.
        _design_files = [design_file] + [p for p in (additional_design_files or []) if p]
        if len(_design_files) > MAX_FLOW_SCREENS:
            raise ValueError(
                f"Multi-screen flow analysis supports at most {MAX_FLOW_SCREENS} screens in one "
                f"analysis; received {len(_design_files)}. Please submit {MAX_FLOW_SCREENS} or fewer."
            )
        preloaded_images = None
        if len(_design_files) > 1:
            _image_dicts = [self._load_image(p) for p in _design_files]
            preloaded_images = build_multi_screen_blocks(_image_dicts)

        # Steps 2–5: Pass 1 visual analysis. Mode selects the architecture:
        #   "twopass" — detection→adjudication over sliced packs (new KBs only)
        #   "single"  — one call with the whole KB
        if mode == "twopass" and is_new_kb(kb_version):
            report = self._twopass(
                design_file=design_file,
                user_context=user_context,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
                page_context=page_context,
                preloaded_images=preloaded_images,
                report_style=report_style,
                profile=profile,
            )
        elif mode == "twopass":
            # Guard: twopass is unsupported for legacy KBs — fall back to single, loudly.
            print(f"[UITraps] twopass mode requested for legacy KB {kb_version!r}; falling back to single-pass")
            report = self._pass1(
                design_file=design_file,
                user_context=user_context,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
                page_context=page_context,
                report_style=report_style,
            )
        else:
            # Single-pass. The Thorough coverage option (the legacy tenet-parallel pipeline)
            # is deprecated and removed; `thorough_mode` is still accepted for API
            # compatibility but is ignored for every supported config.
            report = self._pass1(
                design_file=design_file,
                user_context=user_context,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
                page_context=page_context,
                preloaded_images=preloaded_images,
                report_style=report_style,
                profile=profile,
            )

        report["_design_file"] = design_file
        report["_design_files"] = _design_files
        # Token usage / estimated cost across all passes (read-only telemetry for the
        # report header). Each API pass attaches "_usage_last"; accrue and pop it here.
        _usage_total = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "cost": 0.0}

        def _accrue_usage(rep):
            u = rep.pop("_usage_last", None) if isinstance(rep, dict) else None
            if not u:
                return
            for _k in _usage_total:
                _usage_total[_k] += u.get(_k, 0) or 0

        _accrue_usage(report)

        # Step 6: Calculate metadata
        duration = time.time() - start_time
        # Report the model actually used for pass 1 (pass1_model="haiku" routes to enrich_model).
        _effective_model = {"sonnet": self.model, "haiku": self.enrich_model}.get(pass1_model or "", self.model)
        metadata = {
            "model": _effective_model,
            "duration_seconds": round(duration, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
        }

        if _self_serve:
            # Self-serve BY-TRAP: the single call already produced the per-trap report. This is
            # the KB-only condition, so there is NO enrichment pass (that would be a second call
            # carrying legacy guidance) and NO legacy completeness backfill. The tool fills only
            # presentation the model was never asked for: the tenet for each finding's pill
            # (derived from its trap name) and the coverage complement (traps not reported).
            # Keep only dict findings — the bare schema is permissive, and a stray non-dict
            # item (string/None) would crash the formatter's per-finding reads. traps_checked
            # is derived below (overwritten); positives are strings.
            for _opt in ('critical_issues', 'moderate_issues', 'minor_issues'):
                report[_opt] = [f for f in (report.get(_opt) or []) if isinstance(f, dict)]
            for _opt in ('positive_observations', 'traps_checked_not_found'):
                if not isinstance(report.get(_opt), list):
                    report[_opt] = []
            self._fill_selfserve_trap_tenets(report, kb_version)
            self._derive_selfserve_trap_coverage(report, kb_version)
            self._crop_issue_regions(report, _design_files)
        else:
            # Step 7: Pass 2 — Enrich findings using full book sections (per-trap path)
            try:
                report = self._enrich_report(report, timeout=timeout, kb_version=kb_version, verbosity=verbosity)
            except Exception as e:
                # Enrichment failure is non-fatal — use Pass 1 report as-is
                print(f"[UITraps] Pass 2 enrichment skipped (non-fatal): {e}")
            _accrue_usage(report)

            # Step 8: Generate outputs
            # Normalize optional fields after enrichment — Pass 2 may omit fields that were
            # present in Pass 1, causing formatter KeyErrors.
            for _opt in ['critical_issues', 'moderate_issues', 'minor_issues',
                         'positive_observations', 'potential_issues', 'traps_checked_not_found',
                         'flagged_for_human_review', 'incomplete_flow_findings']:
                if not isinstance(report.get(_opt), list):
                    report[_opt] = []
            # Drop any non-dict finding element — the formatter reads .get() per finding and a
            # stray string/None would crash the whole render (positives are strings, so skip them).
            for _opt in ('critical_issues', 'moderate_issues', 'minor_issues',
                         'potential_issues', 'flagged_for_human_review', 'incomplete_flow_findings'):
                report[_opt] = [f for f in report[_opt] if isinstance(f, dict)]

            # Retain the additive issue-level substrate (issue_groups, KB ledger 22): normalize to
            # a list of dicts and canonicalize each bound trap's G3 relationship. This renders
            # nothing in the report body; the Emergent Patterns synthesis section reads it.
            _ig = report.get("issue_groups")
            if isinstance(_ig, str):
                # The model occasionally JSON-encodes an array field as a string (the same failure
                # the per-finding arrays above recover from). Recover it so the substrate isn't
                # silently dropped → Emergent Patterns / disposition attribution would go blank.
                for _loader in (json.loads, ast.literal_eval):
                    try:
                        _ig = _loader(_ig)
                        break
                    except Exception:
                        continue
            report["issue_groups"] = [g for g in _ig if isinstance(g, dict)] if isinstance(_ig, list) else []
            for _g in report["issue_groups"]:
                _gt = _g.get("traps")
                _g["traps"] = [t for t in _gt if isinstance(t, dict)] if isinstance(_gt, list) else []
                for _t in _g["traps"]:
                    _t["relationship"] = normalize_relationship(_t.get("relationship"))

            # Guarantee report completeness across KB versions: backfill the per-trap
            # "Could Not Evaluate" breakdown. This makes v1 and v2 reports symmetric.
            self._normalize_report_completeness(report, kb_version=kb_version)
            self._crop_issue_regions(report, _design_files)

        if chat_context and chat_context.strip():
            user_context = dict(user_context)
            user_context['chat_context_used'] = True
            user_context['chat_context_content'] = chat_context.strip()
        _elapsed = time.time() - start_time
        _twopass_meta = report.pop('_twopass_meta', None)
        _pass_metrics = report.pop('_pass_metrics', None)  # single-pass latency/stop_reason/tokens
        _truncated = bool(report.pop('_truncated', False))
        _analysis_settings = {
            'verbosity': verbosity,
            'pass1_model': pass1_model,
            'kb_version': kb_version,
            'elapsed_seconds': _elapsed,
            'thorough_mode': thorough_mode,
            'report_style': report_style,
            'mode': mode,
            'profile': profile,
            'truncated': _truncated,
            'frame_notice': frame_notice,
            'usage': dict(_usage_total),
            # Observability rung of the submitted artifact — the disposition gate (Ledger 26) compares
            # this against each Trap's KB-owned floor to decide whether a "Not present" verdict is even
            # eligible. Derived from the declared input medium + screen count (tool mechanics).
            'artifact_class': resolve_artifact_class(user_context.get('input_type'), len(_design_files)),
        }
        metadata['usage'] = dict(_usage_total)
        metadata['estimated_cost'] = round(_usage_total['cost'], 4)
        metadata['mode'] = mode
        metadata['profile'] = profile
        metadata['truncated'] = _truncated
        if _self_serve:
            # The output contract (tool schema + minimal instruction) is harness-provided and
            # identical in kind across all conditions — the KB material supplies content, not
            # the output shape. Recorded so comparative runs can attest the contract was fixed.
            _ss_tool = 'ui_analysis_report'  # By-Trap is the sole self-serve output (By-Issue retired).
            metadata['output_contract'] = f'harness-provided (self-serve): minimal instruction + {_ss_tool} schema; KB injected verbatim, no evaluation guidance'
        if _truncated:
            logger.error("[UITraps] Analysis returned with truncated output (max_tokens) — report is incomplete.")
        if _twopass_meta is not None:
            metadata['twopass'] = _twopass_meta
        # Apply the disposition gate ONCE to the source report (self-guards to v2-coached only) so the
        # markdown export, the statistics, and the returned report object all agree with the HTML — the
        # HTML formatter re-runs it on its escaped copy idempotently. Runs after the run-log counts are
        # unaffected (it changes coverage_status labels, not counts).
        try:
            from .formatters import _apply_disposition_gate
        except ImportError:
            from formatters import _apply_disposition_gate
        _apply_disposition_gate(report, _analysis_settings)
        markdown_report = format_report_as_markdown(report, user_context, kb_version=kb_version)
        # rev6 BY-TRAP report for new-KB / self-serve; the legacy formatter is the fallback for any
        # other lineage. The public entry escapes settings at the boundary.
        if (is_new_kb(kb_version) or _self_serve) and format_bytrap_report_as_html is not None:
            html_report = format_bytrap_report_as_html(report, user_context, analysis_settings=_analysis_settings)
        else:
            html_report = format_report_as_html(report, user_context, analysis_settings=_analysis_settings)
        statistics = get_report_statistics(report)

        # ── Run log (Phase 4) — one JSONL record per analysis; best-effort, never fatal ──
        try:
            # Self-serve records the sha of the RAW KB file on disk (the exact bytes injected,
            # pre-stripping) so the condition is reproducible from the file; other profiles use
            # the standard master/training hash.
            _kb_hash = self._raw_kb_file_sha(kb_version) if _self_serve else self._current_kb_hash(kb_version)
            metadata['kb_hash'] = _kb_hash
            # Count issues whenever an issues report was produced (new-KB or legacy synthesis).
            _n_issues = None
            _n_findings = sum(
                len(report.get(f, [])) for f in ('critical_issues', 'moderate_issues', 'minor_issues'))
            run_logger.log_run({
                "timestamp": metadata.get("timestamp"),
                "kb_version": kb_version,
                "kb_hash": _kb_hash,
                "mode": mode,
                "profile": profile,
                "report_style": report_style,
                "thorough_mode": bool(thorough_mode),
                "verbosity": verbosity,
                "pass1_model": pass1_model,
                "model": metadata.get("model"),
                "duration_seconds": metadata.get("duration_seconds"),
                "tokens": dict(_usage_total),
                "estimated_cost": metadata.get("estimated_cost"),
                "truncated": _truncated,
                "n_findings": _n_findings,
                "n_issues": _n_issues,
                "design_name": (user_context or {}).get("design_name"),
                "user_id": user_id,
                "twopass": _twopass_meta,
                # Per-pass breakdown (latency/stop_reason/input/output/cache_read/cost):
                # detection+adjudication for two-pass, the single pass otherwise.
                "passes": (_twopass_meta.get("passes") if isinstance(_twopass_meta, dict) and _twopass_meta.get("passes")
                           else ([_pass_metrics] if _pass_metrics else None)),
            })
        except Exception as _log_err:
            print(f"[UITraps] run-log skipped: {_log_err}")

        return {
            "report": report,
            "metadata": metadata,
            "markdown": markdown_report,
            "html": html_report,
            "statistics": statistics,
            "status": "success"
        }

    def _crop_findings_regions(self, findings, image_paths) -> None:
        """Crop every finding's regions[] against the screen each box names (0-based
        screen_index) and attach the base64 PNG to that region entry as region['image_b64'].
        `image_paths` is a list of screen paths (index 0 = first/only screen). Screens are opened
        once and reused across all findings/boxes."""
        try:
            from PIL import Image
        except Exception as e:
            print(f"[UITraps] Region crop unavailable: {e}")
            return
        cache: Dict[int, Any] = {}
        def _screen(idx):
            if idx not in cache:
                cache[idx] = None
                if 0 <= idx < len(image_paths):
                    try:
                        im = Image.open(image_paths[idx])
                        cache[idx] = (im, im.size[0], im.size[1])
                    except Exception as e:
                        print(f"[UITraps] screen {idx} unavailable for crop: {e}")
            return cache[idx]
        try:
            for f in findings:
                if not isinstance(f, dict):
                    continue
                for region in (f.get('regions') or []):
                    if not isinstance(region, dict):
                        continue
                    try:
                        idx = int(region.get('screen_index', 0) or 0)
                    except (TypeError, ValueError):
                        idx = 0
                    got = _screen(idx)
                    if not got:
                        continue
                    b64 = self._crop_one_region(got[0], got[1], got[2], region)
                    if b64:
                        region['image_b64'] = b64
        finally:
            for v in cache.values():
                if v:
                    try:
                        v[0].close()
                    except Exception:
                        pass

    def _crop_issue_regions(self, report: Dict[str, Any], image_paths) -> None:
        """By-Trap: crop each finding's regions[] (across all severities). `image_paths` may be a
        single path (single-screen) or a list of screen paths (multi-screen flow)."""
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        findings = []
        for severity in ('critical_issues', 'moderate_issues', 'minor_issues'):
            findings += [f for f in (report.get(severity) or []) if isinstance(f, dict)]
        self._crop_findings_regions(findings, image_paths)

    def _crop_one_region(self, img, img_w, img_h, region) -> Optional[str]:
        """Crop a single normalized region (15% padding, clamped) → base64 PNG, or None."""
        import io
        try:
            x = max(0.0, min(1.0, float(region.get('x', 0))))
            y = max(0.0, min(1.0, float(region.get('y', 0))))
            w = max(0.01, min(1.0 - x, float(region.get('width', 0))))
            h = max(0.01, min(1.0 - y, float(region.get('height', 0))))
            pad_x, pad_y = w * 0.15, h * 0.15
            x1, y1 = max(0, int((x - pad_x) * img_w)), max(0, int((y - pad_y) * img_h))
            x2, y2 = min(img_w, int((x + w + pad_x) * img_w)), min(img_h, int((y + h + pad_y) * img_h))
            if x2 > x1 and y2 > y1:
                crop = img.crop((x1, y1, x2, y2))
                # Skip near-blank crops — a uniform dark/empty region (e.g. a coordinate over
                # a plain hero background) renders as a black box that adds no visual evidence.
                try:
                    lo, hi = crop.convert("L").getextrema()
                    if (hi - lo) < 12:
                        return None
                except Exception:
                    pass
                buf = io.BytesIO()
                crop.save(buf, format='PNG', optimize=True)
                return base64.standard_b64encode(buf.getvalue()).decode('utf-8')
        except Exception as crop_err:
            print(f"[UITraps] Region crop skipped: {crop_err}")
        return None

    def _fill_selfserve_trap_tenets(self, report: Dict[str, Any], kb_version: str = None) -> None:
        """Self-serve BY-TRAP: the bare KB-only schema does not require `tenet`, but the by-trap
        formatter needs it for each finding's pill. Derive a missing/blank tenet from the trap
        name (the coached formatters get it from the model), using the version's OWN taxonomy —
        v1 findings get v1 Tenets (the frozen v1.0 card-deck map), not the v2 table. Fills only
        when absent; leaves any tenet the model did provide untouched. Tolerates non-dict findings."""
        try:
            from .formatters import _tenet_for
        except ImportError:
            from formatters import _tenet_for
        for _sev in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for _f in (report.get(_sev) or []):
                if isinstance(_f, dict) and not (_f.get('tenet') or '').strip():
                    _t = _tenet_for(_f.get('trap_name', ''), version=kb_version)
                    if _t:
                        _f['tenet'] = _t

    def _derive_selfserve_trap_coverage(self, report: Dict[str, Any], kb_version: str) -> None:
        """By-Trap self-serve coverage: coverage = every trap in the KB's set NOT named in a
        critical/moderate/minor finding. ALWAYS replaces any coverage the model
        emitted (the KB-only condition is never shown coverage vocabulary). Marked not_present
        ('Did not find')."""
        try:
            from .schema import _valid_trap_names
        except ImportError:
            from schema import _valid_trap_names
        _nz = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
        reported = set()
        for _arr in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for f in report.get(_arr, []):
                if isinstance(f, dict) and f.get('trap_name'):
                    reported.add(_nz(f['trap_name']))
        all_traps = _valid_trap_names(kb_version) or []
        # Emit BOTH coverage vocabularies so the entry renders correctly regardless of the KB
        # lineage the legacy formatter branches on: new-KB reads `coverage_status`, legacy
        # (v1/v2) reads the `testable` boolean. testable=True ⇒ "evaluated, not present".
        report["traps_checked_not_found"] = [
            {"trap_name": name, "coverage_status": "not_present", "testable": True}
            for name in all_traps if _nz(name) not in reported
        ]

    def _raw_kb_file_sha(self, kb_version: str) -> Optional[str]:
        """sha256 of the RAW KB file on disk for this version (the exact bytes, pre-stripping).
        Used by the self-serve profile so the condition is reproducible from the file itself."""
        try:
            try:
                from .knowledge_base import _KB_PATHS
            except ImportError:
                from knowledge_base import _KB_PATHS
            p = _KB_PATHS.get(kb_version)
            if p and p.exists():
                return hashlib.sha256(p.read_bytes()).hexdigest()
        except Exception:
            pass
        return None

    def _current_kb_hash(self, kb_version: str) -> Optional[str]:
        """sha256 of the KB the run used — the master file for new KBs (matches the pack
        manifest's master_sha256), else the loaded training content for legacy versions."""
        try:
            if is_new_kb(kb_version):
                return pack_generator.master_hash(kb_version)
        except Exception:
            pass
        try:
            from .prompts import load_training_content
        except ImportError:
            from prompts import load_training_content
        try:
            return hashlib.sha256(load_training_content(version=kb_version).encode("utf-8")).hexdigest()
        except Exception:
            return None

    def analyze_flow_diagram(
        self,
        frames: List[Dict],
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = "v2",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        profile: str = "default",
        report_style: str = "trap",
        mode: str = "single",
        chat_context: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        total_frames: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze Figma frames as ONE cross-screen flow — full parity with the image path.

        The exported frames (already capped/ordered by the caller) are handed to analyze_design
        as a single multi-screen artifact (design_file + additional_design_files), so the whole
        flow goes to the model in ONE call with [SCREEN i] labels and the model reasons across
        screens (KB G7) exactly as a multi-screenshot run does — NOT N stitched per-frame
        reports. This delegates to the shared evaluation engine, so every config axis is honored
        identically: profile (coaching lock: v1 → self-serve, so no deprecation-guard trip),
        mode (one-pass via _pass1 vs two-pass via _twopass), verbosity, model, chat/page
        context, the MAX_FLOW_SCREENS
        ceiling, and the rev6 renderer. There is no flow-specific prompt, schema, pass structure,
        text-injected flow context, or formatter — the previous per-frame-loop + separate
        flow-pass + _merge_reports + legacy-enrichment architecture is retired.
        """
        valid_frames = [f for f in frames if f.get('image_path')]
        if not valid_frames:
            raise ValueError("No exportable frames found")
        _paths = [f['image_path'] for f in valid_frames]
        # Truncate-with-notice: the caller exports/passes only the first MAX_FLOW_SCREENS frames
        # (Figma document order). When the source file had more, disclose BOTH counts in the
        # report so a trap that lived on an un-analyzed frame reads as a truncation artifact, not
        # a KB miss. total_frames is the full pre-truncation count (analyze_figma_file.total_frames).
        _analyzed = len(valid_frames)
        _frame_notice = None
        if total_frames and total_frames > _analyzed:
            _skipped = total_frames - _analyzed
            _frame_notice = (
                f"Analyzed {_analyzed} of {total_frames} frames in this file; "
                f"{_skipped} frame{'s' if _skipped != 1 else ''} {'were' if _skipped != 1 else 'was'} "
                f"not analyzed."
            )
        return self.analyze_design(
            design_file=_paths[0],
            additional_design_files=_paths[1:],
            user_context=user_context,
            timeout=timeout,
            chat_context=chat_context,
            page_context=page_context,
            kb_version=kb_version,
            verbosity=verbosity,
            pass1_model=pass1_model,
            report_style=report_style,
            mode=mode,
            profile=profile,
            frame_notice=_frame_notice,
        )

    def _create_message(self, **kwargs):
        """Call the Messages API, STREAMING when the requested max_tokens is large.

        Streaming keeps the connection active so a long generation can't trip the idle timeout and
        force an SDK retry that re-runs the whole attempt. `stream().get_final_message()` returns the
        same Message object `create()` would, so callers read `.content`/`.stop_reason`/`.usage`
        unchanged. Falls back to `create()` when max_tokens is small, when the client's `stream` is
        not a real context manager (e.g. a test Mock), or if streaming rejects a kwarg — so behaviour
        (and the create-mocking test suite) degrades safely to the previous path.
        """
        if kwargs.get("max_tokens", 0) >= _STREAM_MIN_TOKENS:
            _stream = getattr(self.client.messages, "stream", None)
            if callable(_stream):
                # Guard ONLY the construction + capability probe. Once we've decided to stream, a
                # failure inside get_final_message() must propagate — NOT fall through to create(),
                # which would re-run the whole (multi-minute, billed) generation.
                _cm = None
                try:
                    _cm = _stream(**kwargs)
                    # Real SDK yields a context manager; a bare Mock's type has no __enter__, so
                    # tests (and a stream() that rejects a kwarg) fall through to create().
                    _streamable = getattr(type(_cm), "__enter__", None) is not None
                except (TypeError, AttributeError):
                    _streamable = False
                if _streamable:
                    with _cm as _s:
                        return _s.get_final_message()
        return self.client.messages.create(**kwargs)

    def _pass1(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = "v2",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        chat_context: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        preloaded_image: Optional[Dict[str, Any]] = None,
        preloaded_images: Optional[list] = None,
        max_tokens_override: Optional[int] = None,
        system_prompt_override: Optional[list] = None,
        extra_user_blocks: Optional[list] = None,
        report_style: str = "trap",
        profile: str = "default",
    ) -> Dict[str, Any]:
        """Run Pass 1 visual analysis and return the raw report dict.

        preloaded_images (multi-screen flow): a pre-built content list of interleaved SCREEN
        labels + image blocks (see prompts.build_multi_screen_blocks). When provided it takes
        precedence over preloaded_image / design_file and all screens go to the model in ONE call.

        Emits the per-trap report (ui_analysis_report tool); By-Issue rendering is retired.

        system_prompt_override / extra_user_blocks let twopass mode reuse this call's
        parse+normalize machinery for its adjudication pass: the system prompt carries
        the sliced packs (core + flagged chunks) and the extra blocks carry the Pass-1
        candidate list."""
        _model_map = {"sonnet": self.model, "haiku": self.enrich_model}
        effective_model = _model_map.get(pass1_model or "", self.model)
        # Multi-screen (flow) analysis sends N screens in ONE call; count them for the output
        # ceiling and for build_system_prompt's multi-screen note (screen_index reinforcement).
        _n_screens = (sum(1 for b in preloaded_images if isinstance(b, dict) and b.get("type") == "image")
                      if preloaded_images else 1)
        # New-KB single mode does the whole analysis in this one call, so its output ceiling
        # must clear the KB's ≥8,000-token floor — truncation drops the coverage section and
        # can cut off adjudication (a run error, not a formatting artifact). Legacy v1/v2 keep
        # their prior caps (Pass 2 rewrites their final report). Thorough sub-calls pass an
        # explicit override and are unaffected.
        if max_tokens_override:
            pass1_max_tokens = max_tokens_override
        elif is_new_kb(kb_version) or profile == "self-serve":
            # COMPLETENESS OVER SPEED (author-ruled): a truncated report is an incomplete
            # evaluation = a reliability failure, so give the KB report a HIGH ceiling a full report
            # (all findings + coverage + Emergent Patterns + disposition index) never reaches.
            # max_tokens is a CEILING, not a target — a short report stops early, so raising it costs
            # nothing except letting a long report complete (accepted: slower/costlier when it does).
            # Stays ≥ _STREAM_MIN_TOKENS so it streams; scales with screen count for multi-screen.
            pass1_max_tokens = min(24000 + max(0, _n_screens - 1) * 4000, 32000)
        else:
            pass1_max_tokens = 3000 if verbosity == "brief" else 5000

        _self_serve = (profile == "self-serve")

        if system_prompt_override is not None:
            system_prompt = system_prompt_override
        else:
            system_prompt = build_system_prompt(
                use_caching=self.use_caching, version=kb_version, image_count=_n_screens,
                report_style=report_style, profile=profile,
            )

        # NOTE: page_context is passed by KEYWORD below. It was previously passed positionally
        # as the 3rd arg, which binds to build_user_message's `image_data_list` slot — a latent
        # bug (benign only because page_context was None on this path).
        if preloaded_images is not None:
            # Multi-screen flow: labeled SCREEN blocks + images already built upstream.
            user_message = build_user_message(
                user_context, image_data_list=preloaded_images, page_context=page_context,
                verbosity=verbosity, version=kb_version, profile=profile,
            )
        else:
            if preloaded_image is not None:
                image_data = preloaded_image
            else:
                if is_figma_url(design_file):
                    raise NotImplementedError(
                        "Figma URL support requires additional implementation. "
                        "Please export your Figma design as PNG/JPG and upload the image file."
                    )
                image_data = self._load_image(design_file)
            user_message = build_user_message(
                user_context, image_data, page_context=page_context, verbosity=verbosity,
                version=kb_version, profile=profile,
            )

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

        if extra_user_blocks:
            user_message = list(extra_user_blocks) + list(user_message)

        # self_serve here means By-Trap KB-only: the BARE per-trap schema (no enums, no
        # guidance). Default keeps the full trap schema.
        schema = get_ui_analysis_schema(version=kb_version, self_serve=_self_serve)
        tool_name = "ui_analysis_report"
        tool_desc = "Submit the complete UI Tenets & Traps analysis report"
        _t_call = time.time()
        try:
            response = self._create_message(
                model=effective_model,
                max_tokens=pass1_max_tokens,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                tools=[{
                    "name": tool_name,
                    "description": tool_desc,
                    "input_schema": schema
                }],
                tool_choice={"type": "tool", "name": tool_name},
                # Give a heavy generation room to finish in one attempt rather than timing out
                # mid-stream and burning retries; honor a caller that explicitly asked for more.
                timeout=max(timeout or 0, _ANALYSIS_API_TIMEOUT_S),
            )
        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")
        _pass_latency_s = round(time.time() - _t_call, 2)  # wall-clock incl. any SDK retries

        if getattr(response, "stop_reason", None) == "max_tokens":
            logger.error(
                "[UITraps] Pass-1 hit max_tokens (%s) — output truncated. This is a RUN ERROR: "
                "the report (coverage notes, and possibly adjudication) is incomplete.",
                pass1_max_tokens,
            )
            print(f"[UITraps][RUN ERROR] Pass-1 truncated at max_tokens={pass1_max_tokens}")

        try:
            tool_use_block = next(
                (block for block in response.content if block.type == "tool_use"), None
            )
            if not tool_use_block:
                report = parse_claude_response(response.content[0].text)
            else:
                report = tool_use_block.input
                # Truncation (stop_reason == max_tokens) can return a PARTIAL dict missing later
                # required fields. Coerce missing keys to safe defaults instead of raising — the
                # by-issue path already tolerates this, and the _truncated banner marks the report
                # incomplete downstream, so we degrade gracefully rather than 500 on exactly the
                # runs that hit the length ceiling.
                for field in ['summary_headline', 'summary_narrative']:
                    report.setdefault(field, '')
                for field in ['critical_issues', 'moderate_issues', 'minor_issues']:
                    report.setdefault(field, [])
                if not isinstance(report.get('summary_headline'), str):
                    report['summary_headline'] = ''
                if not isinstance(report.get('summary_narrative'), str):
                    report['summary_narrative'] = ''
                for issue_field in ['critical_issues', 'moderate_issues', 'minor_issues']:
                    val = report.get(issue_field)
                    if isinstance(val, str):
                        # Claude sometimes JSON-encodes array fields as strings.
                        # Try json.loads first, then ast.literal_eval as fallback.
                        parsed = None
                        try:
                            parsed = json.loads(val)
                        except (json.JSONDecodeError, ValueError):
                            try:
                                parsed = ast.literal_eval(val)
                            except (ValueError, SyntaxError):
                                logger.warning(
                                    f"Could not parse {issue_field} as JSON or literal; "
                                    f"treating as empty. First 300 chars: {val[:300]!r}"
                                )
                        report[issue_field] = parsed if isinstance(parsed, list) else []
                    elif not isinstance(val, list):
                        report[issue_field] = []
                for opt_field in ['positive_observations', 'potential_issues',
                                  'traps_checked_not_found', 'flagged_for_human_review',
                                  'incomplete_flow_findings']:
                    val = report.get(opt_field)
                    if isinstance(val, str):
                        parsed = None
                        try:
                            parsed = json.loads(val)
                        except (json.JSONDecodeError, ValueError):
                            try:
                                parsed = ast.literal_eval(val)
                            except (ValueError, SyntaxError):
                                pass
                        report[opt_field] = parsed if isinstance(parsed, list) else []
                    elif not isinstance(val, list):
                        report[opt_field] = []
        except Exception as e:
            raise ValueError(
                f"Failed to parse Claude's response: {e}\n\nResponse content: {response.content}"
            )

        _u = _usage_from_response(response, effective_model)
        if _u:
            report["_usage_last"] = _u
        _stop = getattr(response, "stop_reason", None)
        if _stop == "max_tokens":
            # Surface truncation to the caller — the report is incomplete, not a clean success.
            report["_truncated"] = True
        # Per-pass metrics (latency + stop_reason + token breakdown incl. cache_read) for the
        # run log — completes the per-pass logging spec. Caller (_twopass / analyze_design) reads it.
        report["_pass_metrics"] = {
            "latency_s": _pass_latency_s,
            "stop_reason": _stop,
            "model": effective_model,
            **({} if not _u else {k: _u.get(k) for k in ("input", "output", "cache_read", "cache_creation", "cost")}),
        }
        return report

    def _twopass(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = "v2",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        chat_context: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        preloaded_image: Optional[Dict[str, Any]] = None,
        preloaded_images: Optional[list] = None,
        report_style: str = "trap",
        profile: str = "default",
    ) -> Dict[str, Any]:
        """
        Two-pass analysis for the new (v2-lineage) KBs.

        preloaded_images (multi-screen flow): interleaved SCREEN-labeled image blocks sent to
        BOTH passes in one call each; takes precedence over preloaded_image / design_file.

        Pass 1 (detection): the whole master's detection procedures are injected and the
        model emits a recall-oriented candidate list — no adjudication. We match those
        candidates against the manifest (tolerantly), load the full chunk for each matched
        trap, and hand only those chunks + the always-loaded core pack to Pass 2.

        Pass 2 (adjudication): reuses _pass1's call/parse/normalize machinery, but with the
        sliced KB in the system prompt and the Pass-1 candidate list in the user turn, so
        every candidate is confirmed/dismissed/reclassified with full definitions and the
        coverage pass runs over all traps.

        The staleness guard (pack_generator.ensure_current) regenerates the packs if the
        master hash has moved — twopass never runs against stale packs.
        """
        if not is_new_kb(kb_version):
            raise ValueError(
                f"two-pass mode is only supported for new KBs (v1.1, v2); got {kb_version!r}"
            )

        # Staleness guard: regenerate derived packs if the master changed. Automatic swap.
        manifest = pack_generator.ensure_current(kb_version)

        # Load the artifact once and reuse across both passes. Multi-screen flow: the labeled
        # SCREEN blocks (image_data_list) are the artifact; image_data stays None.
        image_data = None
        _n_screens = 1
        if preloaded_images is not None:
            _n_screens = sum(1 for b in preloaded_images if isinstance(b, dict) and b.get("type") == "image")
        elif preloaded_image is not None:
            image_data = preloaded_image
        elif is_figma_url(design_file):
            raise NotImplementedError(
                "Figma URL support requires additional implementation. "
                "Please export your Figma design as PNG/JPG and upload the image file."
            )
        else:
            image_data = self._load_image(design_file)

        _model_map = {"sonnet": self.model, "haiku": self.enrich_model}
        effective_model = _model_map.get(pass1_model or "", self.model)

        # ── Pass 1: detection (candidate list, no tool) ─────────────────────────
        detection_system = build_system_prompt(
            use_caching=self.use_caching, version=kb_version, image_count=_n_screens,
            training_override=pack_generator.load_pack(kb_version, "pass1"), mode="detect",
        )
        # page_context passed by KEYWORD (was positionally in the image_data_list slot — a bug).
        if preloaded_images is not None:
            detection_user = build_user_message(
                user_context, image_data_list=preloaded_images, page_context=page_context,
                verbosity=verbosity, version=kb_version, mode="detect",
            )
        else:
            detection_user = build_user_message(
                user_context, image_data, page_context=page_context,
                verbosity=verbosity, version=kb_version, mode="detect",
            )
        if chat_context and chat_context.strip():
            detection_user = [{
                "type": "text",
                "text": (
                    "CRITICAL OVERRIDE — UPDATED CONTEXT FROM USER:\n"
                    f"{chat_context.strip()}\n\n"
                    "--- END OF USER CORRECTIONS — use these when scanning ---\n"
                )
            }] + list(detection_user)

        # A truncated candidate list loses recall. Scale the ceiling with screen count — a
        # multi-screen flow surfaces candidates on every screen, so a fixed 4000 would clip the
        # tail (and the tail is exactly the cross-screen traps this rebuild exists to catch).
        _detection_max_tokens = min(8000 + max(0, _n_screens - 1) * 2000, 16000)
        _t_det = time.time()
        try:
            det_response = self._create_message(
                model=effective_model,
                max_tokens=_detection_max_tokens,
                temperature=0,
                system=detection_system,
                messages=[{"role": "user", "content": detection_user}],
                timeout=max(timeout or 0, _ANALYSIS_API_TIMEOUT_S),
            )
        except Exception as e:
            raise Exception(f"Claude API call failed (detection pass): {e}")
        _det_latency_s = round(time.time() - _t_det, 2)
        _det_stop = getattr(det_response, "stop_reason", None)

        if _det_stop == "max_tokens":
            print(f"[UITraps][twopass][RUN ERROR] Detection pass truncated at max_tokens={_detection_max_tokens} — candidate list may be incomplete (lost recall)")

        raw_candidates = "".join(
            b.text for b in det_response.content if getattr(b, "type", None) == "text"
        )
        det_usage = _usage_from_response(det_response, effective_model)

        # ── Match candidates → flagged traps → load their chunks ────────────────
        matched, unmatched = pack_generator.match_candidates(raw_candidates, manifest)
        print(f"[UITraps][twopass] detection surfaced {len(matched)} matched trap(s), "
              f"{len(unmatched)} unmatched line(s)")
        if unmatched:
            # Surface, never silently drop — the KB Claude's "no silent caps" rule.
            print(f"[UITraps][twopass] unmatched candidate lines: {unmatched[:20]}")

        chunks_text = pack_generator.load_chunks(kb_version, matched, manifest=manifest) if matched else ""
        if matched and not chunks_text.strip():
            print("[UITraps][twopass][RUN ERROR] candidates matched but no chunk text loaded — "
                  "adjudication will run on the core pack only")
        core_pack = pack_generator.load_pack(kb_version, "pass2")

        # ── Pass-1 candidates for the adjudication turn ──────────────────────────
        # Forward the detection pass's RAW output verbatim, not just the matched names: it
        # carries each candidate's screen/element/condition observation (context the
        # adjudicator would otherwise re-derive) and preserves any candidate whose name did
        # not normalize to a canonical trap, so nothing is silently dropped. The note tells
        # the adjudicator which traps arrived with full definitions loaded.
        raw_block = raw_candidates.strip() or "(the detection pass returned no candidate lines)"
        if matched:
            loaded_note = "Full definitions are loaded below for these matched traps: " + ", ".join(matched) + "."
        else:
            loaded_note = "No candidate matched a canonical trap name; adjudicate from the core pack."
        candidate_block = {
            "type": "text",
            "text": (
                "PASS-1 CANDIDATES (raw detection output) — a recall-oriented starting list, "
                "NOT confirmed findings. Each line is one observed candidate in the form "
                "TRAP | screen | element | condition. For EACH candidate, run its full "
                "detection procedure and adjudication rules and decide where it belongs: an "
                "Issue, a Worth-a-closer-look entry, or a Coverage note. Then run the coverage "
                "pass over EVERY remaining trap in the framework — the candidate list is a "
                "floor for recall, not a ceiling.\n\n"
                f"{raw_block}\n\n--- END CANDIDATES ---\n"
                f"{loaded_note}\n"
            ),
        }

        # ── Pass 2: adjudication (reuse _pass1 machinery, sliced KB) ─────────────
        # core_pack is the stable cached prefix; the variable flagged-trap chunks go in the
        # uncached extra_training slot so the core pack keeps hitting cache across runs.
        adjudication_system = build_system_prompt(
            use_caching=self.use_caching, version=kb_version, image_count=_n_screens,
            training_override=core_pack,
            extra_training=(chunks_text if chunks_text.strip() else None),
            mode="report", report_style=report_style, profile=profile,
        )
        report = self._pass1(
            design_file=design_file,
            user_context=user_context,
            timeout=timeout,
            kb_version=kb_version,
            verbosity=verbosity,
            pass1_model=pass1_model,
            report_style=report_style,
            chat_context=chat_context,
            page_context=page_context,
            preloaded_image=image_data,
            preloaded_images=preloaded_images,
            system_prompt_override=adjudication_system,
            extra_user_blocks=[candidate_block],
        )

        # Per-pass metrics for the run log — latency / stop_reason / token breakdown incl.
        # cache_read — completing the per-pass logging spec. Capture the adjudication usage
        # BEFORE folding it into the combined total below.
        _adj_metrics = report.pop("_pass_metrics", {}) or {}
        _adj_usage = report.get("_usage_last")
        report["_usage_last"] = _sum_usage(det_usage, _adj_usage)

        _det_pass = {"pass": "detection", "latency_s": _det_latency_s, "stop_reason": _det_stop,
                     "model": effective_model, "max_tokens": _detection_max_tokens}
        for _k in ("input", "output", "cache_read", "cache_creation", "cost"):
            _det_pass[_k] = (det_usage or {}).get(_k)
        _adj_pass = {"pass": "adjudication"}
        for _k in ("latency_s", "stop_reason", "model", "input", "output", "cache_read", "cache_creation", "cost"):
            _adj_pass[_k] = _adj_metrics.get(_k)

        report["_twopass_meta"] = {
            "candidates_matched": matched,
            "candidates_unmatched": unmatched,
            "chunks_loaded": len(matched),
            "kb_master_sha256": manifest.get("master_sha256"),
            "passes": [_det_pass, _adj_pass],
        }
        # A truncated detection pass drops candidates (lost recall) — surface it as an
        # incomplete run just like an adjudication truncation.
        if _det_stop == "max_tokens":
            report["_truncated"] = True
        return report

    def _enrich_report(self, pass1_report: Dict[str, Any], timeout: int = 120, kb_version: str = "v2", verbosity: str = "standard") -> Dict[str, Any]:
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
        # New-KB (v2-lineage) versions are self-instructing and use the new output
        # vocabulary (Confirmed/Probable/Flagged, coverage_status). The legacy Pass-2
        # enrichment prompt speaks the old vocabulary (high/medium/low, testable) and
        # would conflict with the new schema, so skip enrichment — Pass 1 output stands.
        if is_new_kb(kb_version):
            print(f"[UITraps] Pass 2 enrichment skipped for new KB ({kb_version}) — Pass 1 output is authoritative")
            return pass1_report

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
            pass1_report, trap_sections, trap_images, knowledge_chunks=knowledge_chunks, verbosity=verbosity
        )
        schema = get_ui_analysis_schema()

        print(f"[UITraps] Pass 2: enriching {len(found_trap_names)} trap(s): {', '.join(found_trap_names)}")

        pass2_max_tokens = 2200 if verbosity == "brief" else 3500
        response = self._create_message(
            model=self.enrich_model,
            max_tokens=pass2_max_tokens,
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
            timeout=max(timeout or 0, _ANALYSIS_API_TIMEOUT_S),
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
            "critical_issues", "moderate_issues", "minor_issues",
            "potential_issues", "bugs_detected",
            "incomplete_flow_findings", "flagged_for_human_review",
        ):
            if field in pass1_report and field not in enriched:
                enriched[field] = pass1_report[field]



        print(f"[UITraps] Pass 2: enrichment complete ({response.usage.input_tokens} input tokens)")
        _u = _usage_from_response(response, self.enrich_model)
        if _u:
            enriched["_usage_last"] = _u
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
        # New-KB versions own coverage via the G4 `coverage_status` labels the model
        # emits directly. The legacy testable-based rebuild below would clobber them.
        if is_new_kb(kb_version):
            if not isinstance(report.get("traps_checked_not_found"), list):
                report["traps_checked_not_found"] = []
            return

        try:
            from .prompts import _TRAP_NAMES_V1, _TRAP_NAMES_V2
            from .formatters import _normalize_trap_name
        except ImportError:
            from prompts import _TRAP_NAMES_V1, _TRAP_NAMES_V2
            from formatters import _normalize_trap_name

        src = _TRAP_NAMES_V1 if kb_version == "v1" else _TRAP_NAMES_V2
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

        new_tcnf = []
        for canonical in canonical_traps:
            norm = _normalize_trap_name(canonical)
            if norm in confirmed_norm:
                continue
            existing = existing_by_norm.get(norm)
            if existing is not None:
                item = dict(existing)
                item.pop("reason", None)
                if norm in testable_always_false_norm:
                    item["testable"] = False
                elif norm in testable_true_norm:
                    item.setdefault("testable", True)
                new_tcnf.append(item)
            else:
                if norm in testable_true_norm:
                    new_tcnf.append({"trap_name": canonical, "testable": True})
                else:
                    new_tcnf.append({"trap_name": canonical, "testable": False})

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
                # No optimize= on the PNG upload encode: it runs a slow extra compression pass for a
                # marginally smaller payload that does NOT change Claude's vision token count (the image
                # is re-processed server-side regardless). Saves encode CPU per screen per analysis.
                img.save(buf, format='PNG')
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
                timeout=max(timeout or 0, _ANALYSIS_API_TIMEOUT_S),
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
