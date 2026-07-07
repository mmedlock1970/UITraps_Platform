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
        build_system_prompt, build_user_message, build_figma_message,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message,
        build_synthesis_system_prompt, build_synthesis_user_message,
    )
    try:
        from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_issues_report_as_html, format_new_kb_issues_markdown
    except ImportError:
        from .formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_new_kb_issues_markdown
        format_issues_report_as_html = None
    from .schema import get_ui_analysis_schema, get_interaction_analysis_schema, get_user_issues_schema, get_ui_issues_schema, is_new_kb, normalize_relationship
    from .knowledge_extractor import collect_found_trap_names, extract_trap_sections, extract_trap_images
    from .knowledge_base import get_chunks_for_traps
    from . import pack_generator
    from . import run_logger
except ImportError:
    # Fallback for direct script execution
    from validators import validate_file_format, validate_context, is_figma_url
    from prompts import (
        build_system_prompt, build_user_message, build_figma_message,
        INTERACTION_ANALYSIS_SYSTEM_PROMPT, build_interaction_message,
        build_enrichment_system_prompt, build_enrichment_user_message,
        build_synthesis_system_prompt, build_synthesis_user_message,
    )
    try:
        from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_issues_report_as_html, format_new_kb_issues_markdown
    except ImportError:
        from formatters import parse_claude_response, format_report_as_markdown, format_report_as_html, get_report_statistics, format_new_kb_issues_markdown
        format_issues_report_as_html = None
    from schema import get_ui_analysis_schema, get_interaction_analysis_schema, get_user_issues_schema, get_ui_issues_schema, is_new_kb, normalize_relationship
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
            thorough_mode: Run one _pass1 per tenet group in parallel for deeper coverage.
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

        # Self-serve (raw-KB) profile: single-pass, by-issue, rev6 template, with the harness's
        # minimal prompt + relaxed schema — regardless of KB lineage. This is an experimental
        # condition; the output contract is harness-provided and identical in kind to the other
        # conditions, and the minimal prompt is deliberately NOT strengthened.
        _self_serve = (profile == "self-serve")
        if _self_serve:
            mode = "single"
            report_style = "issues"
            # thorough (tenet-parallel) is a separate legacy pipeline that would bypass the
            # self-serve prompt/schema and emit trap-shaped output — force it off so self-serve
            # always takes the single-pass issues path.
            thorough_mode = False

        # Steps 2–5: Pass 1 visual analysis. Mode selects the architecture:
        #   "twopass" — detection→adjudication over sliced packs (new KBs only)
        #   "single"  — one call with the whole KB (thorough_mode fans out per tenet group)
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
                report_style=report_style,
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
        elif thorough_mode and not is_new_kb(kb_version):
            report = self._run_tenet_parallel(
                design_file=design_file,
                user_context=user_context,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
            )
        else:
            # Single-pass. New-KB + thorough lands here too: the legacy tenet-parallel merge
            # speaks the old vocabulary (counts, critical/moderate/minor, `testable`) and would
            # corrupt new-KB output, so thorough is not supported for new KBs.
            if thorough_mode and is_new_kb(kb_version):
                print(f"[UITraps] thorough_mode is not supported for new KB {kb_version!r}; running single-pass")
            report = self._pass1_issues_retry(
                design_file=design_file,
                user_context=user_context,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
                page_context=page_context,
                report_style=report_style,
                profile=profile,
            )

        report["_design_file"] = design_file
        # Did the pass emit the issue-grouped structure directly (Option A / self-serve)?
        _is_new_kb_issues = (
            (is_new_kb(kb_version) or _self_serve) and report_style == "issues"
            and report.get("_report_style") == "issues"
        )

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

        issues_report = None
        if _is_new_kb_issues:
            # Option A: the adjudication already produced the issue-grouped report. Attach the
            # verbatim definition to each aligned trap (from the manifest, case-insensitive),
            # crop each issue's region, and hand it straight to the by-issue formatter.
            self._inject_issue_trap_definitions(report, kb_version)
            if _self_serve:
                # The minimal self-serve prompt produces no coverage notes, so derive the
                # "not reported" list = the KB's full trap set minus the traps named in issues.
                self._derive_selfserve_coverage(report, kb_version)
            self._crop_issues_report_regions(report, design_file)
            issues_report = report
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

            # Guarantee report completeness across KB versions: backfill the per-trap
            # "Could Not Evaluate" breakdown. This makes v1 and v2 reports symmetric.
            self._normalize_report_completeness(report, kb_version=kb_version)
            self._crop_issue_regions(report, design_file)

            # Pass 3 — legacy synthesis into user-issues format (only when requested).
            # New KBs never reach here: they emit the issue structure directly above.
            if report_style == "issues" and is_new_kb(kb_version):
                print(f"[UITraps] issues requested for new KB {kb_version!r} but the adjudication "
                      f"did not emit an issue structure; returning the per-trap report")
            elif report_style == "issues":
                try:
                    issues_report = self._synthesize_issues(report, timeout=timeout)
                except Exception as e:
                    print(f"[UITraps] Pass 3 synthesis skipped (non-fatal): {e}")
        _accrue_usage(issues_report)

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
            'usage': dict(_usage_total),
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
            metadata['output_contract'] = 'harness-provided (self-serve): minimal instruction + ui_issues_report schema; KB injected verbatim, no evaluation guidance'
        if _truncated:
            logger.error("[UITraps] Analysis returned with truncated output (max_tokens) — report is incomplete.")
        if _twopass_meta is not None:
            metadata['twopass'] = _twopass_meta
        if _is_new_kb_issues:
            markdown_report = format_new_kb_issues_markdown(issues_report)
        else:
            markdown_report = format_report_as_markdown(report, user_context, kb_version=kb_version)
        if issues_report is not None and format_issues_report_as_html is not None:
            html_report = format_issues_report_as_html(issues_report, user_context, analysis_settings=_analysis_settings)
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
            _n_issues = len(issues_report.get('issues', [])) if isinstance(issues_report, dict) else None
            _n_findings = None if _is_new_kb_issues else sum(
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

    def _crop_issue_regions(self, report: Dict[str, Any], image_path: str) -> None:
        """Crop region screenshots from the source image and attach as base64 to each issue."""
        try:
            from PIL import Image
            import io
            img = Image.open(image_path)
            img_w, img_h = img.size
            for severity in ['critical_issues', 'moderate_issues', 'minor_issues']:
                for issue in report.get(severity, []):
                    region = issue.get('region')
                    if not region:
                        continue
                    try:
                        x = max(0.0, min(1.0, float(region.get('x', 0))))
                        y = max(0.0, min(1.0, float(region.get('y', 0))))
                        w = max(0.01, min(1.0 - x, float(region.get('width', 0))))
                        h = max(0.01, min(1.0 - y, float(region.get('height', 0))))
                        # 15% padding on each side, clamped to image bounds
                        pad_x, pad_y = w * 0.15, h * 0.15
                        x1 = max(0, int((x - pad_x) * img_w))
                        y1 = max(0, int((y - pad_y) * img_h))
                        x2 = min(img_w, int((x + w + pad_x) * img_w))
                        y2 = min(img_h, int((y + h + pad_y) * img_h))
                        if x2 > x1 and y2 > y1:
                            crop = img.crop((x1, y1, x2, y2))
                            # Skip near-blank crops (uniform dark/empty region → black box).
                            _lo, _hi = crop.convert("L").getextrema()
                            if (_hi - _lo) < 12:
                                continue
                            buf = io.BytesIO()
                            crop.save(buf, format='PNG', optimize=True)
                            issue['region_image_b64'] = base64.standard_b64encode(buf.getvalue()).decode('utf-8')
                    except Exception as crop_err:
                        print(f"[UITraps] Region crop skipped ({issue.get('trap_name', '?')}): {crop_err}")
            img.close()
        except Exception as e:
            print(f"[UITraps] Region crop unavailable: {e}")

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

    def _crop_issues_report_regions(self, report: Dict[str, Any], image_path: str) -> None:
        """Crop each by-issue entry's region → issue['region_image_b64']."""
        try:
            from PIL import Image
            img = Image.open(image_path)
            img_w, img_h = img.size
            for issue in report.get('issues', []):
                if isinstance(issue, dict) and issue.get('region'):
                    b64 = self._crop_one_region(img, img_w, img_h, issue['region'])
                    if b64:
                        issue['region_image_b64'] = b64
            img.close()
        except Exception as e:
            print(f"[UITraps] Region crop unavailable (issues): {e}")

    def _inject_issue_trap_definitions(self, report: Dict[str, Any], kb_version: str) -> None:
        """Attach each aligned trap's verbatim definition (from the pack manifest) to the
        by-issue structure — case-insensitively, since report names are ALL-CAPS and the
        manifest keys are Title-Case. The model does not transcribe defs; the tool owns them.

        Legacy KBs (v1/v2, e.g. self-serve) have no manifest of their own; fall back to the
        same-lineage new KB's manifest (v1→v1.1, v2→v2.1), which carries the identical trap
        set's verbatim definitions."""
        _def_version = {"v1": "v1.1", "v2": "v2.1"}.get(kb_version, kb_version)
        try:
            manifest = pack_generator.ensure_current(_def_version)
            by_upper = {k.upper(): v for k, v in (manifest.get('verbatim_definitions') or {}).items()}
        except Exception as e:
            print(f"[UITraps] verbatim-definition injection skipped: {e}")
            return
        for issue in report.get('issues', []):
            if not isinstance(issue, dict):
                continue
            for t in issue.get('traps', []):
                if isinstance(t, dict) and t.get('trap_name'):
                    d = by_upper.get(str(t['trap_name']).upper())
                    if d:
                        t['definition'] = d

    def _derive_selfserve_coverage(self, report: Dict[str, Any], kb_version: str) -> None:
        """Self-serve is never shown the coverage vocabulary, so coverage is derived here: every
        trap in the KB's trap set that was NOT named in an issue. This ALWAYS replaces any
        coverage the model may have emitted — the derived complement is the only coverage the
        KB-only condition reports. Each entry is marked not_present ('Did not find' bucket)."""
        try:
            from .schema import _valid_trap_names
        except ImportError:
            from schema import _valid_trap_names
        _nz = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
        reported = set()
        for issue in report.get("issues", []):
            if isinstance(issue, dict):
                for t in issue.get("traps", []):
                    if isinstance(t, dict) and t.get("trap_name"):
                        reported.add(_nz(t["trap_name"]))
        all_traps = _valid_trap_names(kb_version) or []
        report["traps_checked_not_found"] = [
            {"trap_name": name, "coverage_status": "not_present"}
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

    # Analysis groups for thorough_mode=True.
    # UNDERSTANDABLE and HABITUATING are split by sub-tenet; no group exceeds 5 traps.
    _ANALYSIS_GROUPS = [
        # UNDERSTANDABLE — 3 sub-tenet groups
        {'label': 'UNDERSTANDABLE/Noticeable',
         'traps': ['INVISIBLE ELEMENT', 'EFFECTIVELY INVISIBLE ELEMENT', 'DISTRACTION']},
        {'label': 'UNDERSTANDABLE/Comprehensible',
         'traps': ['UNCOMPREHENDED ELEMENT', 'INVITING DEAD END', 'POOR GROUPING',
                   'FORCED SYNTAX', 'MEMORY CHALLENGE']},
        {'label': 'UNDERSTANDABLE/Confirmatory',
         'traps': ['FEEDBACK FAILURE']},
        # Full tenets
        {'label': 'COMFORTABLE',  'tenet': 'COMFORTABLE'},
        {'label': 'RESPONSIVE',   'tenet': 'RESPONSIVE'},
        {'label': 'EFFICIENT',    'tenet': 'EFFICIENT'},
        {'label': 'ACCURATE',     'tenet': 'ACCURATE'},
        {'label': 'PROTECTIVE',   'tenet': 'PROTECTIVE'},
        # HABITUATING — 3 sub-tenet groups
        {'label': 'HABITUATING/Non-Redundant',
         'traps': ['GRATUITOUS REDUNDANCY']},
        {'label': 'HABITUATING/Consistent-with-Expectations',
         'traps': ['VARIABLE OUTCOME', 'WANDERING ELEMENT', 'INCONSISTENT APPEARANCE']},
        {'label': 'HABITUATING/Oriented',
         'traps': ['AMBIGUOUS HOME']},
        # Full tenet
        {'label': 'BEAUTIFUL',    'tenet': 'BEAUTIFUL'},
    ]

    def _run_tenet_parallel(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = "v2",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        chat_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run one _pass1 per analysis group concurrently, return merged report."""
        import concurrent.futures
        from copy import deepcopy

        groups = list(self._ANALYSIS_GROUPS)
        print(f"[UITraps] Thorough mode: running {len(groups)} parallel sub-analyses")

        # Pre-load image once — avoids 12 concurrent PIL decode/resize operations
        preloaded_image = self._load_image(design_file)
        # Narrower token budget per sub-call (1-5 traps scope, not 27)
        sub_max_tokens = 1500 if verbosity == "brief" else 2500

        def analyze_one(group: dict) -> Dict[str, Any]:
            ctx = deepcopy(user_context)
            if 'traps' in group:
                ctx['trap_filter'] = group['traps']
                ctx.pop('tenet_filter', None)
            else:
                ctx['tenet_filter'] = [group['tenet']]
                ctx.pop('trap_filter', None)
            return self._pass1(
                design_file=design_file,
                user_context=ctx,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
                chat_context=chat_context,
                preloaded_image=preloaded_image,
                max_tokens_override=sub_max_tokens,
            )

        reports = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(groups)) as executor:
            future_to_group = {executor.submit(analyze_one, g): g for g in groups}
            for future in concurrent.futures.as_completed(future_to_group):
                label = future_to_group[future]['label']
                try:
                    reports.append(future.result())
                    print(f"[UITraps] Group complete: {label}")
                except Exception as e:
                    print(f"[UITraps] Group failed ({label}): {e}")

        if not reports:
            raise Exception("All parallel sub-analyses failed")

        return self._merge_reports(reports)

    @staticmethod
    def _merge_reports(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple tenet/sub-tenet Pass 1 reports into one deduplicated report."""
        try:
            from .formatters import _normalize_trap_name
        except ImportError:
            from formatters import _normalize_trap_name

        merged: Dict[str, Any] = {
            'critical_issues': [],
            'moderate_issues': [],
            'minor_issues': [],
            'positive_observations': [],
            'potential_issues': [],
            'traps_checked_not_found': [],
            'flagged_for_human_review': [],
            'incomplete_flow_findings': [],
            'bugs_detected': [],
        }

        seen_traps: set = set()
        for report in reports:
            for severity in ('critical_issues', 'moderate_issues', 'minor_issues'):
                for issue in report.get(severity) or []:
                    norm = _normalize_trap_name(issue.get('trap_name', '') or '')
                    if norm and norm not in seen_traps:
                        seen_traps.add(norm)
                        merged[severity].append(issue)

        seen_pos: set = set()
        for report in reports:
            for pos in report.get('positive_observations') or []:
                if pos and pos not in seen_pos:
                    seen_pos.add(pos)
                    merged['positive_observations'].append(pos)

        # Merge traps_checked_not_found across all sub-reports, deduplicating by trap_name
        seen_tcnf: set = set()
        for report in reports:
            for item in report.get('traps_checked_not_found') or []:
                if isinstance(item, dict):
                    norm = _normalize_trap_name(item.get('trap_name', '') or '')
                    if norm and norm not in seen_traps and norm not in seen_tcnf:
                        seen_tcnf.add(norm)
                        merged['traps_checked_not_found'].append(item)
                elif isinstance(item, str) and item.strip():
                    norm = _normalize_trap_name(item)
                    if norm and norm not in seen_traps and norm not in seen_tcnf:
                        seen_tcnf.add(norm)
                        merged['traps_checked_not_found'].append({'trap_name': item, 'testable': True})

        for field in ('potential_issues', 'flagged_for_human_review',
                      'incomplete_flow_findings', 'bugs_detected'):
            for report in reports:
                items = report.get(field) or []
                if items:
                    merged[field] = items
                    break

        n_crit = len(merged['critical_issues'])
        n_mod = len(merged['moderate_issues'])
        n_min = len(merged['minor_issues'])
        total = n_crit + n_mod + n_min

        if total == 0:
            merged['summary_headline'] = "No UI Traps detected"
            merged['summary_narrative'] = (
                "Thorough tenet-by-tenet analysis found no usability issues."
            )
        else:
            parts = (
                ([f"{n_crit} critical"] if n_crit else []) +
                ([f"{n_mod} moderate"] if n_mod else []) +
                ([f"{n_min} minor"] if n_min else [])
            )
            merged['summary_headline'] = (
                f"{total} UI Trap{'s' if total != 1 else ''} found: {', '.join(parts)}"
            )
            merged['summary_narrative'] = (
                f"Thorough tenet-by-tenet analysis identified {total} "
                f"issue{'s' if total != 1 else ''} across the full framework "
                f"({', '.join(parts)})."
            )

        return merged

    def analyze_flow_diagram(
        self,
        frames: List[Dict],
        flow_map: Dict,
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = 'v2',
        verbosity: str = 'standard',
        pass1_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze Figma frames with flow-aware context.

        Always runs both passes and merges with deduplication:
        - Screen pass: one _pass1 per frame with per-frame flow context.
          Produces per-screen findings with region crops.
        - Flow pass: single _pass1 on first frame with full flow summary.
          Catches journey-level traps that span multiple screens.
        Screen findings are processed first so they win deduplication and
        retain their region crops when the same trap is found by both passes.
        """
        try:
            from .prompts import build_flow_context_section
        except ImportError:
            from prompts import build_flow_context_section

        from concurrent.futures import ThreadPoolExecutor

        valid_frames = [f for f in frames if f.get('image_path')]
        if not valid_frames:
            raise ValueError("No exportable frames found")

        # Build per-frame contexts for screen pass
        screen_tasks: List[tuple] = []
        for frame in valid_frames:
            ctx = dict(user_context)
            per_frame_ctx = flow_map.get('per_frame', {}).get(frame['id'])
            if per_frame_ctx:
                flow_section = build_flow_context_section(
                    flow_context=per_frame_ctx, mode='screen'
                )
                existing_extra = ctx.get('extra_context', '')
                ctx['extra_context'] = (
                    flow_section
                    + ('\n' + existing_extra if existing_extra else '')
                ).strip()
            screen_tasks.append((frame, ctx))

        # Build flow pass context
        flow_ctx = dict(user_context)
        flow_section = build_flow_context_section(
            flow_summary=flow_map.get('summary', ''),
            mode='flow',
        )
        frames_list = '\n'.join(f"  - {f['name']}" for f in valid_frames)
        existing_extra = flow_ctx.get('extra_context', '')
        flow_ctx['extra_context'] = (
            flow_section
            + f"\nFrames included in this flow:\n{frames_list}"
            + ('\n' + existing_extra if existing_extra else '')
        ).strip()

        def _run_screen(args: tuple) -> Dict[str, Any]:
            frame, ctx = args
            report = self._pass1(
                design_file=frame['image_path'],
                user_context=ctx,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
            )
            self._crop_issue_regions(report, frame['image_path'])
            return report

        def _run_flow(_: None = None) -> Dict[str, Any]:
            report = self._pass1(
                design_file=valid_frames[0]['image_path'],
                user_context=flow_ctx,
                timeout=timeout,
                kb_version=kb_version,
                verbosity=verbosity,
                pass1_model=pass1_model,
            )
            self._crop_issue_regions(report, valid_frames[0]['image_path'])
            return report

        # Run all passes in parallel — screen pass tasks + flow pass task
        n_workers = len(screen_tasks) + 1
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            screen_futures = [executor.submit(_run_screen, task) for task in screen_tasks]
            flow_future = executor.submit(_run_flow)
            # Collect screen results in original frame order
            screen_reports = [f.result() for f in screen_futures]
            flow_report = flow_future.result()

        # Screen findings first so they win dedup over flow findings
        merged = self._merge_reports(screen_reports + [flow_report])

        for _opt in ['critical_issues', 'moderate_issues', 'minor_issues',
                     'positive_observations', 'potential_issues', 'traps_checked_not_found',
                     'flagged_for_human_review', 'incomplete_flow_findings']:
            if not isinstance(merged.get(_opt), list):
                merged[_opt] = []

        self._normalize_report_completeness(merged, kb_version=kb_version)

        # Save region crops before enrichment — Pass 2 rewrites findings from scratch
        # and drops region_image_b64. Keyed by (trap_name, location) so we can restore
        # them after enrichment.
        _saved_crops: dict = {}
        for _sev in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for _issue in merged.get(_sev, []):
                if _issue.get('region_image_b64'):
                    _key = (_issue.get('trap_name', ''), _issue.get('location', ''))
                    _saved_crops[_key] = _issue['region_image_b64']

        try:
            merged = self._enrich_report(merged, timeout=timeout, kb_version=kb_version, verbosity=verbosity)
        except Exception as e:
            print(f"[UITraps] Flow analysis Pass 2 enrichment skipped (non-fatal): {e}")

        # Restore crops that Pass 2 stripped
        if _saved_crops:
            for _sev in ('critical_issues', 'moderate_issues', 'minor_issues'):
                for _issue in merged.get(_sev, []):
                    if not _issue.get('region_image_b64'):
                        _key = (_issue.get('trap_name', ''), _issue.get('location', ''))
                        if _key in _saved_crops:
                            _issue['region_image_b64'] = _saved_crops[_key]

        return merged

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
        max_tokens_override: Optional[int] = None,
        system_prompt_override: Optional[list] = None,
        extra_user_blocks: Optional[list] = None,
        report_style: str = "trap",
        profile: str = "default",
    ) -> Dict[str, Any]:
        """Run Pass 1 visual analysis and return the raw report dict.

        For new KBs with report_style='issues' this emits the issue-grouped output
        (ui_issues_report tool) directly (Option A); otherwise the per-trap report.

        system_prompt_override / extra_user_blocks let twopass mode reuse this call's
        parse+normalize machinery for its adjudication pass: the system prompt carries
        the sliced packs (core + flagged chunks) and the extra blocks carry the Pass-1
        candidate list."""
        _model_map = {"sonnet": self.model, "haiku": self.enrich_model}
        effective_model = _model_map.get(pass1_model or "", self.model)
        # New-KB single mode does the whole analysis in this one call, so its output ceiling
        # must clear the KB's ≥8,000-token floor — truncation drops the coverage section and
        # can cut off adjudication (a run error, not a formatting artifact). Legacy v1/v2 keep
        # their prior caps (Pass 2 rewrites their final report). Thorough sub-calls pass an
        # explicit override and are unaffected.
        if max_tokens_override:
            pass1_max_tokens = max_tokens_override
        elif is_new_kb(kb_version) or profile == "self-serve":
            # New KBs and the self-serve profile emit the verbose by-issue report — a legacy
            # 3–5K cap truncates it. Give them the full ceiling.
            pass1_max_tokens = 8000
        else:
            pass1_max_tokens = 3000 if verbosity == "brief" else 5000

        # New-KB by-issue emits the issue-grouped structure directly (Option A).
        _self_serve = (profile == "self-serve")
        _issues_mode = (is_new_kb(kb_version) or _self_serve) and report_style == "issues"

        if system_prompt_override is not None:
            system_prompt = system_prompt_override
        else:
            system_prompt = build_system_prompt(
                use_caching=self.use_caching, version=kb_version, image_count=1,
                report_style=report_style, profile=profile,
            )

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
            user_context, image_data, page_context, verbosity=verbosity, version=kb_version,
            profile=profile,
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

        if _issues_mode:
            schema = get_ui_issues_schema(version=kb_version, self_serve=_self_serve)
            tool_name = "ui_issues_report"
            tool_desc = "Submit the complete UI Tenets & Traps BY-ISSUE report"
        else:
            schema = get_ui_analysis_schema(version=kb_version)
            tool_name = "ui_analysis_report"
            tool_desc = "Submit the complete UI Tenets & Traps analysis report"
        _t_call = time.time()
        try:
            response = self.client.messages.create(
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
                timeout=timeout
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
            elif _issues_mode:
                # By-issue structure: normalize the issue list + each trap's relationship.
                report = tool_use_block.input
                report["_report_style"] = "issues"
                for field in ("summary_headline", "summary_narrative"):
                    if not isinstance(report.get(field), str):
                        report[field] = ""

                # Coerce each array field to a real list. The model occasionally JSON-encodes an
                # array as a string (sometimes wrapped in ```json fences) instead of a native
                # array; recover it rather than silently rendering an empty report.
                def _coerce_list(v):
                    if isinstance(v, list):
                        return v
                    if isinstance(v, str):
                        s = v.strip()
                        if s.startswith("```"):
                            s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s)
                            s = re.sub(r"\s*```$", "", s).strip()
                        for _loader in (json.loads, ast.literal_eval):
                            try:
                                p = _loader(s)
                                if isinstance(p, list):
                                    return p
                            except Exception:
                                pass
                    return []

                _issues_raw = report.get("issues")
                for list_field in ("issues", "positive_observations", "traps_checked_not_found"):
                    report[list_field] = _coerce_list(report.get(list_field))

                # Safety net: the by-issue report exists to surface issues[]. If it came back
                # empty while the model produced a full report, that is a RUN ERROR, not "clean
                # design" — surface it loudly and dump the raw tool input for inspection instead
                # of shipping a misleading "No issues" report.
                if not report["issues"]:
                    logger.error(
                        "[UITraps][RUN ERROR] by-issue adjudication returned NO issues "
                        "(issues field was %s). This usually means a malformed tool call, not a "
                        "clean design. Dumping raw tool input.", type(_issues_raw).__name__,
                    )
                    try:
                        _dbg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                        os.makedirs(_dbg_dir, exist_ok=True)
                        _dbg_path = os.path.join(_dbg_dir, f"empty_issues_{time.strftime('%Y%m%d_%H%M%S')}.json")
                        with open(_dbg_path, "w", encoding="utf-8") as _df:
                            json.dump(dict(report), _df, ensure_ascii=False, indent=2, default=str)
                        print(f"[UITraps][RUN ERROR] by-issue returned NO issues — raw dumped to {_dbg_path}")
                    except Exception as _de:
                        print(f"[UITraps][RUN ERROR] empty-issues dump failed: {_de}")
                for _issue in report["issues"]:
                    if not isinstance(_issue, dict):
                        continue
                    _traps = _issue.get("traps")
                    if not isinstance(_traps, list):
                        _issue["traps"] = _traps = []
                    for _t in _traps:
                        if isinstance(_t, dict):
                            _t["relationship"] = normalize_relationship(_t.get("relationship"))
            else:
                report = tool_use_block.input
                for field in ['summary_headline', 'summary_narrative',
                              'critical_issues', 'moderate_issues', 'minor_issues']:
                    if field not in report:
                        raise ValueError(f"Missing required field in response: {field}")
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

    def _pass1_issues_retry(self, **kwargs):
        """Run _pass1 and, for a BY-ISSUE call that comes back with ZERO issues (a rare
        malformed tool call — not a clean design), retry once. A retry at temperature 0 almost
        always yields a well-formed issues[]. The discarded attempt's token usage is folded into
        the returned report so cost/token logging stays honest. Non-by-issue calls pass through
        untouched."""
        report = self._pass1(**kwargs)
        _by_issue = ((is_new_kb(kwargs.get("kb_version")) or kwargs.get("profile") == "self-serve")
                     and kwargs.get("report_style") == "issues")
        if _by_issue and not report.get("issues"):
            print("[UITraps] by-issue adjudication returned 0 issues — retrying once "
                  "(temperature 0 usually self-corrects a malformed tool call)...")
            logger.warning("[UITraps] by-issue returned 0 issues; retrying adjudication once.")
            _wasted = report.get("_usage_last")
            report = self._pass1(**kwargs)
            if _wasted:
                report["_usage_last"] = _sum_usage(_wasted, report.get("_usage_last"))
        return report

    def _twopass(
        self,
        design_file: str,
        user_context: Dict[str, str],
        timeout: int = 120,
        kb_version: str = "v2.1",
        verbosity: str = "standard",
        pass1_model: Optional[str] = None,
        chat_context: Optional[str] = None,
        page_context: Optional[Dict[str, Any]] = None,
        preloaded_image: Optional[Dict[str, Any]] = None,
        report_style: str = "trap",
    ) -> Dict[str, Any]:
        """
        Two-pass analysis for the new (v2.1-lineage) KBs.

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
                f"two-pass mode is only supported for new KBs (v1.1, v2.1); got {kb_version!r}"
            )

        # Staleness guard: regenerate derived packs if the master changed. Automatic swap.
        manifest = pack_generator.ensure_current(kb_version)

        # Load the artifact once and reuse across both passes.
        if preloaded_image is not None:
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
            use_caching=self.use_caching, version=kb_version, image_count=1,
            training_override=pack_generator.load_pack(kb_version, "pass1"), mode="detect",
        )
        detection_user = build_user_message(
            user_context, image_data, page_context,
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

        _t_det = time.time()
        try:
            det_response = self.client.messages.create(
                model=effective_model,
                max_tokens=4000,                 # detection floor — a truncated list loses recall
                temperature=0,
                system=detection_system,
                messages=[{"role": "user", "content": detection_user}],
                timeout=timeout,
            )
        except Exception as e:
            raise Exception(f"Claude API call failed (detection pass): {e}")
        _det_latency_s = round(time.time() - _t_det, 2)
        _det_stop = getattr(det_response, "stop_reason", None)

        if _det_stop == "max_tokens":
            print("[UITraps][twopass][RUN ERROR] Detection pass truncated at max_tokens=4000 — candidate list may be incomplete (lost recall)")

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
            use_caching=self.use_caching, version=kb_version, image_count=1,
            training_override=core_pack,
            extra_training=(chunks_text if chunks_text.strip() else None),
            mode="report", report_style=report_style,
        )
        report = self._pass1_issues_retry(
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
                     "model": effective_model, "max_tokens": 4000}
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
        # New-KB (v2.1-lineage) versions are self-instructing and use the new output
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
        response = self.client.messages.create(
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

    def _synthesize_issues(
        self,
        enriched_report: Dict[str, Any],
        timeout: int = 120,
    ) -> Optional[Dict[str, Any]]:
        """
        Pass 3: Synthesise enriched per-Trap findings into user-centric issues.

        Groups Traps that share a common design element or root cause into a
        single user-facing issue. Grounds all synthesis in the confirmed Trap
        findings — does not introduce new problems.

        Unlike Pass 2, this pass does not use prompt caching (short context, single-use).

        Args:
            enriched_report: Pass 1+2 report (per-Trap findings).
            timeout: API call timeout in seconds.

        Returns:
            User-issues report matching USER_ISSUES_SCHEMA, or None if no
            confirmed findings exist or the API call fails.
        """
        total = sum(
            len(enriched_report.get(k, []))
            for k in ("critical_issues", "moderate_issues", "minor_issues")
        )
        if total == 0:
            return None

        system_prompt = build_synthesis_system_prompt()
        kb_version = enriched_report.get("_meta", {}).get("kb_version", "v2")
        user_message = build_synthesis_user_message(enriched_report, kb_version=kb_version)
        schema = get_user_issues_schema()

        print(f"[UITraps] Pass 3: synthesising {total} Trap finding(s) into user issues")

        response = self.client.messages.create(
            model=self.enrich_model,
            max_tokens=4096,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=[
                {
                    "name": "ui_issues_report",
                    "description": "Submit the synthesised user-issues report",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": "ui_issues_report"},
            timeout=timeout,
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "ui_issues_report":
                result = block.input
                # Pass-through Pass 1 fields that the formatter needs but
                # the synthesis schema does not produce.
                result['traps_checked_not_found'] = enriched_report.get('traps_checked_not_found', [])
                # Build trap_name → crop lookup so the formatter can attach
                # the Pass 1 screenshot crop to the matching issue card.
                region_by_trap: dict[str, dict] = {}
                for _sev in ("critical_issues", "moderate_issues", "minor_issues"):
                    for _f in enriched_report.get(_sev, []) or []:
                        _name = (_f.get("trap_name") or "").upper().strip()
                        _b64 = _f.get("region_image_b64")
                        if _name and _b64:
                            _caption = (_f.get("region") or {}).get("caption") or _f.get("location", "")
                            region_by_trap[_name] = {"b64": _b64, "caption": _caption}
                result['_region_by_trap'] = region_by_trap
                _u = _usage_from_response(response, self.enrich_model)
                if _u:
                    result["_usage_last"] = _u
                return result

        print("[UITraps] Pass 3: no tool-use block in response, synthesis skipped")
        return None

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
