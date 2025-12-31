"""
Font detection module for PDF editing system.

This module provides functionality to detect and analyze font properties
in PDF documents.
"""
import fitz  # PyMuPDF
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class FontInfo:
    """Represents font information extracted from a PDF."""
    name: str
    size: float
    flags: int
    is_bold: bool
    is_italic: bool
    is_monospace: bool
    is_serif: bool
    color: tuple
    
    @classmethod
    def from_span(cls, span: Dict) -> 'FontInfo':
        """
        Create FontInfo from a PyMuPDF span dictionary.
        
        Args:
            span: Span dictionary from PyMuPDF
            
        Returns:
            FontInfo object
        """
        flags = span.get("flags", 0)
        return cls(
            name=span.get("font", "Unknown"),
            size=span.get("size", 12.0),
            flags=flags,
            is_bold=bool(flags & 2**4),  # Bold flag
            is_italic=bool(flags & 2**1),  # Italic flag
            is_monospace=bool(flags & 2**0),  # Monospace flag
            is_serif=bool(flags & 2**3),  # Serif flag
            color=span.get("color", (0, 0, 0))
        )


class FontDetector:
    """Detect and analyze fonts in PDF documents."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the font detector.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.document: Optional[fitz.Document] = None
        
    def __enter__(self):
        """Context manager entry."""
        self.document = fitz.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.document:
            self.document.close()
            
    def get_fonts_on_page(self, page_number: int) -> List[FontInfo]:
        """
        Get all fonts used on a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of FontInfo objects
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        page = self.document[page_number]
        fonts = []
        
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        for block in blocks.get("blocks", []):
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_info = FontInfo.from_span(span)
                        fonts.append(font_info)
                        
        return fonts
    
    def get_unique_fonts(self, page_number: Optional[int] = None) -> List[FontInfo]:
        """
        Get unique fonts in the document or on a specific page.
        
        Args:
            page_number: Specific page number (0-indexed), None for all pages
            
        Returns:
            List of unique FontInfo objects
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        fonts_set = set()
        unique_fonts = []
        
        pages = [self.document[page_number]] if page_number is not None else self.document
        
        for page in pages:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            for block in blocks.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            font_key = (
                                span.get("font", "Unknown"),
                                span.get("size", 12.0),
                                span.get("flags", 0)
                            )
                            if font_key not in fonts_set:
                                fonts_set.add(font_key)
                                unique_fonts.append(FontInfo.from_span(span))
                                
        return unique_fonts
    
    def get_font_at_position(self, page_number: int, x: float, y: float) -> Optional[FontInfo]:
        """
        Get font information at a specific position on a page.
        
        Args:
            page_number: Page number (0-indexed)
            x: X coordinate
            y: Y coordinate
            
        Returns:
            FontInfo object if text found at position, None otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        page = self.document[page_number]
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        for block in blocks.get("blocks", []):
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                            return FontInfo.from_span(span)
                            
        return None
    
    def get_dominant_font(self, page_number: Optional[int] = None) -> Optional[FontInfo]:
        """
        Get the most frequently used font in the document or page.
        
        Args:
            page_number: Specific page number (0-indexed), None for all pages
            
        Returns:
            FontInfo object of the dominant font, None if no text found
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        font_counts = {}
        
        pages = [self.document[page_number]] if page_number is not None else self.document
        
        for page in pages:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            for block in blocks.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            font_key = (
                                span.get("font", "Unknown"),
                                span.get("size", 12.0),
                                span.get("flags", 0)
                            )
                            if font_key not in font_counts:
                                font_counts[font_key] = {
                                    "count": 0,
                                    "info": FontInfo.from_span(span)
                                }
                            font_counts[font_key]["count"] += len(span.get("text", ""))
                            
        if not font_counts:
            return None
            
        dominant = max(font_counts.items(), key=lambda x: x[1]["count"])
        return dominant[1]["info"]


def detect_fonts_in_pdf(pdf_path: str, page_number: Optional[int] = None) -> List[FontInfo]:
    """
    Convenience function to detect unique fonts in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Specific page number (0-indexed), None for all pages
        
    Returns:
        List of unique FontInfo objects
    """
    with FontDetector(pdf_path) as detector:
        return detector.get_unique_fonts(page_number)
