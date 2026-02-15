"""
PDF Analyzer for UI Traps Platform.

Converts PDF pages to images and analyzes them for UI/document usability issues.

Requires: pip install pymupdf (imported as fitz)

Copyright (c) 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def is_pymupdf_available() -> bool:
    """Check if PyMuPDF is installed."""
    try:
        import fitz
        return True
    except ImportError:
        return False


class PdfAnalyzer:
    """
    Analyzes PDF documents by converting pages to images.

    Converts each PDF page to a PNG image, then uses the existing
    multi-image analysis pipeline to detect UI/document traps.
    """

    # Maximum pages to analyze (cost control)
    MAX_PAGES = 20

    # Render resolution (2x for clarity)
    RENDER_SCALE = 2.0

    def __init__(self):
        """Initialize the PDF analyzer."""
        if not is_pymupdf_available():
            raise RuntimeError(
                "PyMuPDF not installed. Install with: pip install pymupdf"
            )

    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with page_count, title, author, etc.
        """
        import fitz

        doc = fitz.open(pdf_path)
        try:
            metadata = doc.metadata or {}
            return {
                "page_count": len(doc),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "file_size": os.path.getsize(pdf_path),
            }
        finally:
            doc.close()

    def convert_pages_to_images(
        self,
        pdf_path: str,
        output_dir: str = None,
        max_pages: int = None,
        start_page: int = 0
    ) -> List[Tuple[str, str]]:
        """
        Convert PDF pages to PNG images.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for output images (temp if None)
            max_pages: Maximum pages to convert
            start_page: First page to convert (0-indexed)

        Returns:
            List of (image_path, page_label) tuples
        """
        import fitz

        max_pages = max_pages or self.MAX_PAGES

        # Validate input
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if pdf_path.suffix.lower() != '.pdf':
            raise ValueError(f"Not a PDF file: {pdf_path.suffix}")

        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='uitraps_pdf_')
        else:
            os.makedirs(output_dir, exist_ok=True)

        doc = fitz.open(str(pdf_path))
        images = []

        try:
            total_pages = len(doc)
            end_page = min(start_page + max_pages, total_pages)

            for page_num in range(start_page, end_page):
                page = doc[page_num]

                # Render at 2x resolution for clarity
                mat = fitz.Matrix(self.RENDER_SCALE, self.RENDER_SCALE)
                pix = page.get_pixmap(matrix=mat)

                # Save as PNG
                output_path = os.path.join(output_dir, f'page_{page_num + 1:04d}.png')
                pix.save(output_path)

                # Create label
                label = f"Page {page_num + 1} of {total_pages}"
                images.append((output_path, label))

                logger.debug(f"Converted PDF page {page_num + 1} to {output_path}")
        finally:
            doc.close()

        return images

    def analyze(
        self,
        pdf_path: str,
        user_context: dict,
        max_pages: int = None
    ) -> dict:
        """
        Full analysis pipeline for PDF documents.

        Converts PDF to images and runs multi-image analysis.

        Args:
            pdf_path: Path to PDF file
            user_context: Dict with users, tasks, format, content_type
            max_pages: Maximum pages to analyze

        Returns:
            Analysis result dict with html, markdown, statistics
        """
        from .multi_analyzer import MultiAnalyzer
        from .analyzer import UITrapsAnalyzer

        max_pages = max_pages or self.MAX_PAGES

        # Get PDF info
        pdf_info = self.get_pdf_info(pdf_path)

        # Create temp directory for page images
        with tempfile.TemporaryDirectory(prefix='uitraps_pdf_') as tmp_dir:
            # Convert pages to images
            page_images = self.convert_pages_to_images(
                pdf_path,
                output_dir=tmp_dir,
                max_pages=max_pages
            )

            if not page_images:
                raise ValueError("No pages could be extracted from PDF")

            # Extract just the paths for multi-analyzer
            image_paths = [path for path, _ in page_images]

            # Update user context for PDF analysis
            pdf_context = user_context.copy()
            if not pdf_context.get('content_type'):
                pdf_context['content_type'] = 'pdf_document'

            # Add PDF-specific format info
            original_format = pdf_context.get('format', '')
            pdf_context['format'] = (
                f"{original_format}\n"
                f"PDF Document: {pdf_info.get('title') or Path(pdf_path).stem}\n"
                f"Pages: {len(page_images)} of {pdf_info['page_count']} total"
            ).strip()

            # Run multi-image analysis
            base_analyzer = UITrapsAnalyzer()
            multi_analyzer = MultiAnalyzer(base_analyzer)

            result = multi_analyzer.analyze_images(image_paths, pdf_context)

            # Add PDF-specific metadata
            result['pdf_info'] = pdf_info
            result['pages_analyzed'] = len(page_images)
            result['analysis_type'] = 'pdf'

            return result

    def cleanup_images(self, image_paths: List[str]) -> None:
        """
        Clean up extracted page images.

        Args:
            image_paths: List of image file paths to delete
        """
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass

        # Try to remove parent temp directory if empty
        if image_paths:
            parent_dir = os.path.dirname(image_paths[0])
            if parent_dir and 'uitraps_pdf_' in parent_dir:
                try:
                    os.rmdir(parent_dir)
                except Exception:
                    pass


def get_pdf_page_count(pdf_path: str) -> int:
    """Quick helper to get PDF page count."""
    import fitz
    doc = fitz.open(pdf_path)
    try:
        return len(doc)
    finally:
        doc.close()
