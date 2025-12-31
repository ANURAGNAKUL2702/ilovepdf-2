"""Font detection module for PDF editing system."""
from .font_detector import (
    FontInfo,
    FontDetector,
    detect_fonts_in_pdf
)

__all__ = [
    "FontInfo",
    "FontDetector",
    "detect_fonts_in_pdf"
]
