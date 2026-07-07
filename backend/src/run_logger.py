"""
Lightweight per-analysis run log.

Appends one JSON object per analysis run to backend/logs/analysis_runs.jsonl so questions
like "what kb_hash / mode / model did run N use?" are answerable after the fact. Writes are
best-effort and never raise into the request path.
"""
import json
import threading
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_PATH = _LOG_DIR / "analysis_runs.jsonl"
_LOCK = threading.Lock()


def log_run(record: dict) -> None:
    """Append one run record to the JSONL log. Best-effort — logs a warning on failure."""
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, default=str)
        with _LOCK:
            with open(_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception as e:  # never break an analysis over telemetry
        print(f"[UITraps] run-log write skipped: {e}")


def read_runs(limit: int = 50) -> list:
    """Return up to the last `limit` run records (oldest→newest). Empty on any error."""
    try:
        if not _LOG_PATH.exists():
            return []
        lines = _LOG_PATH.read_text(encoding="utf-8").splitlines()
        out = []
        for ln in lines[-limit:] if limit else lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
        return out
    except Exception:
        return []
