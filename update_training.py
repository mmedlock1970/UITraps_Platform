"""
Update the training content from the book manuscript and push to the repo.
Run this whenever you have a new version of the book PDF.

Usage:
    python update_training.py
    python update_training.py "C:\\path\\to\\new_book.pdf"   # override source path
"""
import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from knowledge_extractor import extract_and_save_book

REPO_ROOT = Path(__file__).parent
TRAINING_FILE = REPO_ROOT / "backend" / "data" / "UI_Tenets_Traps.txt"
IMAGES_DIR = REPO_ROOT / "backend" / "data" / "book_images"


def git_push(pdf_name: str):
    training_rel = str(TRAINING_FILE.relative_to(REPO_ROOT))
    images_rel = str(IMAGES_DIR.relative_to(REPO_ROOT))
    msg = f"Update training content and book images from '{pdf_name}'"
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
        source = Path(sys.argv[1])
    else:
        source_env = os.environ.get("BOOK_SOURCE_PATH", "").strip()
        if not source_env:
            print("ERROR: No PDF path given and BOOK_SOURCE_PATH not set in backend/.env")
            sys.exit(1)
        source = Path(source_env)

    if extract_and_save_book(source):
        print(f"  Written to {TRAINING_FILE.relative_to(REPO_ROOT)}")
        git_push(source.name)
