"""
PDF Editing System

A production-grade PDF editing system for text extraction,
spell checking, modification, and re-rendering.
"""
from .pdf_editor import PDFEditor
from .extraction import TextBlock, TextExtractor
from .font import FontInfo, FontDetector
from .layout import LayoutMapper, LayoutRegion, Alignment
from .utils import SpellChecker, TextModifier
from .rendering import PDFRenderer, RenderOptions

__version__ = "1.0.0"

__all__ = [
    "PDFEditor",
    "TextBlock",
    "TextExtractor",
    "FontInfo",
    "FontDetector",
    "LayoutMapper",
    "LayoutRegion",
    "Alignment",
    "SpellChecker",
    "TextModifier",
    "PDFRenderer",
    "RenderOptions",
]
