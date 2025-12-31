"""Text extraction module for PDF editing system."""
from .text_extractor import (
    TextBlock,
    TextExtractor,
    extract_text_from_pdf,
    extract_text_blocks_from_pdf
)

__all__ = [
    "TextBlock",
    "TextExtractor",
    "extract_text_from_pdf",
    "extract_text_blocks_from_pdf"
]
