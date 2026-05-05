"""
Update the training content from the book manuscript and push to the repo.

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

import pypdf

REPO_ROOT = Path(__file__).parent
TRAINING_FILE = REPO_ROOT / "backend" / "data" / "UI_Tenets_Traps.txt"
SKIP_PAGES = {"[page intentionally blank]", "[COVER PAGE]", "[FRONT MATTER]"}


def extract_pdf(pdf_path: Path) -> str:
    print(f"Extracting: {pdf_path.name}")
    reader = pypdf.PdfReader(str(pdf_path))
    pages = [
        t for page in reader.pages
        if (t := page.extract_text().strip()) not in SKIP_PAGES and len(t) > 10
    ]
    text = "\n\n".join(pages)
    bib = text.find("\nBibliography\n")
    if bib != -1:
        text = text[:bib].rstrip()
    print(f"  {len(reader.pages)} pages → {len(text):,} chars extracted")
    return text


def update_training_file(pdf_path: Path) -> bool:
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return False

    pdf_text = extract_pdf(pdf_path)

    # Preserve existing confidentiality header
    header = ""
    if TRAINING_FILE.exists():
        existing = TRAINING_FILE.read_text(encoding="utf-8")
        kb_idx = existing.find("## KNOWLEDGE BASE")
        if kb_idx != -1:
            header = existing[:kb_idx].rstrip() + "\n\n"

    new_content = header + "## KNOWLEDGE BASE\n\n" + pdf_text + "\n"
    TRAINING_FILE.write_text(new_content, encoding="utf-8")
    print(f"  Written to {TRAINING_FILE.relative_to(REPO_ROOT)}")
    return True


def git_push(pdf_name: str):
    relative = str(TRAINING_FILE.relative_to(REPO_ROOT))
    msg = f"Update training content from '{pdf_name}'"
    cmds = [
        ["git", "add", relative],
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

    if update_training_file(source):
        git_push(source.name)
