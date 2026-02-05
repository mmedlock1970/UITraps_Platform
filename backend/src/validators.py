"""
File format validation for UI Traps Analyzer
"""
import os
from typing import Tuple
from urllib.parse import urlparse


SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg'}
SUPPORTED_VIDEO_FORMATS = {'.mp4'}
SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_VIDEO_FORMATS


def validate_file_format(file_path: str) -> Tuple[bool, str]:
    """
    Validate if file format is supported.

    Args:
        file_path: Path to file or Figma URL

    Returns:
        Tuple of (is_valid, message)
    """
    # Check if it's a Figma URL
    if is_figma_url(file_path):
        return True, "Figma URL detected"

    # Check file extension first (before existence check)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in SUPPORTED_FORMATS:
        return False, (
            f"Unsupported format: {ext}. "
            f"Supported formats are PNG, JPG, MP4, and Figma links. "
            f"Please convert your file to one of these formats."
        )

    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    # File exists and format is valid
    if ext in SUPPORTED_IMAGE_FORMATS:
        return True, f"Valid image format: {ext}"
    elif ext in SUPPORTED_VIDEO_FORMATS:
        return True, f"Valid video format: {ext}"
    else:
        return True, f"Valid format: {ext}"


def is_figma_url(url: str) -> bool:
    """
    Check if string is a Figma URL.

    Args:
        url: String to check

    Returns:
        True if valid Figma URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc in ['figma.com', 'www.figma.com'] and '/file/' in parsed.path
    except:
        return False


def validate_context(user_context: dict) -> Tuple[bool, str]:
    """
    Validate that required context information is provided.

    Args:
        user_context: Dict with 'users', 'tasks', 'format' keys

    Returns:
        Tuple of (is_valid, message)
    """
    required_fields = ['users', 'tasks', 'format']

    for field in required_fields:
        if field not in user_context:
            return False, f"Missing required field: {field}"

        value = user_context[field]
        if not value or not isinstance(value, str):
            return False, f"Field '{field}' must be a non-empty string"

        # Check minimum length (avoid vague answers)
        if len(value.strip()) < 10:
            return False, (
                f"Field '{field}' is too short. Please provide more detail "
                f"(at least 10 characters). Examples and suggestions should be "
                f"shown to the user if their answer is unclear."
            )

    return True, "Context is valid"


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes
    """
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path)


def get_format_conversion_help(current_format: str) -> str:
    """
    Provide help message for converting unsupported formats.

    Args:
        current_format: The unsupported format (e.g., '.psd')

    Returns:
        Help message with conversion suggestions
    """
    conversion_map = {
        '.psd': "You can export your Photoshop file as PNG or JPG via File > Export > Export As",
        '.sketch': "You can export your Sketch file as PNG or JPG via File > Export",
        '.xd': "You can export your Adobe XD file as PNG or JPG via File > Export",
        '.fig': "You can upload your design to Figma and share the link",
        '.pdf': "You can convert PDF to PNG using online tools or save screenshots of each page",
    }

    help_text = conversion_map.get(current_format.lower(),
        "You can save a screenshot of your design as PNG or JPG"
    )

    return (
        f"Sorry, {current_format} files are not currently supported. "
        f"Supported formats are PNG, JPG, MP4, and Figma links.\n\n"
        f"Suggestion: {help_text}"
    )
