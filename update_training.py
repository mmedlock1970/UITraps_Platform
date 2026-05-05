"""
Update the training content from the book manuscript and push to the repo.

Supports both a local PDF path and a Google Drive share URL as the source.
After updating, commits backend/data/UI_Tenets_Traps.txt and
backend/data/book_images/ then pushes to origin/master so Michael can git pull.

Usage:
    python update_training.py                              # uses .env settings
    python update_training.py "C:\\path\\to\\book.pdf"    # override with local PDF
    python update_training.py "https://drive.google.com/file/d/..."  # Drive URL
"""
import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Add backend/src to path so we can import the extractor directly
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from knowledge_extractor import extract_and_save_book, _download_google_drive, _BOOK_CACHE_PDF

REPO_ROOT = Path(__file__).parent
TRAINING_FILE = REPO_ROOT / "backend" / "data" / "UI_Tenets_Traps.txt"
IMAGES_DIR = REPO_ROOT / "backend" / "data" / "book_images"


def resolve_source(arg: str) -> Path:
    """Resolve a CLI argument (local path or Drive URL) to a local PDF path."""
    if arg.startswith("http://") or arg.startswith("https://"):
        print(f"Downloading from Drive: {arg[:60]}…")
        if not _download_google_drive(arg, _BOOK_CACHE_PDF):
            print("ERROR: Failed to download PDF from Drive URL")
            sys.exit(1)
        return _BOOK_CACHE_PDF
    return Path(arg)


def git_push(source_label: str):
    training_rel = str(TRAINING_FILE.relative_to(REPO_ROOT))
    images_rel = str(IMAGES_DIR.relative_to(REPO_ROOT))
    msg = f"Update training content and book images from '{source_label}'"

    cmds = [
        ["git", "add", training_rel, images_rel],
        ["git", "commit", "-m", msg],
        ["git", "push", "origin", "master"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"  git error: {result.stderr.strip() or result.stdout.strip()}")
            return
    print("  Pushed to origin/master — Michael can git pull to get the update.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        source_pdf = resolve_source(sys.argv[1])
        source_label = sys.argv[1]
    else:
        # Try URL first, then local path
        source_url = os.environ.get("BOOK_SOURCE_URL", "").strip()
        source_path = os.environ.get("BOOK_SOURCE_PATH", "").strip()

        if source_url:
            source_pdf = resolve_source(source_url)
            source_label = source_url
        elif source_path:
            source_pdf = Path(source_path)
            source_label = source_path
        else:
            print("ERROR: No source given. Set BOOK_SOURCE_URL or BOOK_SOURCE_PATH in backend/.env")
            sys.exit(1)

    if extract_and_save_book(source_pdf):
        print(f"  Written to {TRAINING_FILE.relative_to(REPO_ROOT)}")
        git_push(Path(source_label).name if not source_label.startswith("http") else source_label[:60])
