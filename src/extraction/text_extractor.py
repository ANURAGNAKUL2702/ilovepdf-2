"""
Text extraction module for PDF editing system.

This module provides functionality to extract text from PDFs with detailed
metadata including coordinates, font information, and layout details.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a block of text extracted from a PDF."""
    text: str
    x0: float  # Left coordinate
    y0: float  # Top coordinate
    x1: float  # Right coordinate
    y1: float  # Bottom coordinate
    font_name: str
    font_size: float
    font_flags: int
    color: Tuple[float, float, float]
    page_number: int
    block_number: int
    line_number: int
    
    @property
    def width(self) -> float:
        """Calculate the width of the text block."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Calculate the height of the text block."""
        return self.y1 - self.y0
    
    @property
    def position(self) -> Tuple[float, float]:
        """Return the top-left position of the text block."""
        return (self.x0, self.y0)


class TextExtractor:
    """Extract text from PDF with layout and font information."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the text extractor.
        
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
            
    def extract_text_blocks(self, page_number: Optional[int] = None) -> List[TextBlock]:
        """
        Extract text blocks from PDF with detailed metadata.
        
        Args:
            page_number: Specific page to extract from (0-indexed), None for all pages
            
        Returns:
            List of TextBlock objects containing text and metadata
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager or call open().")
            
        text_blocks = []
        
        pages = [self.document[page_number]] if page_number is not None else self.document
        
        for page_idx, page in enumerate(pages):
            actual_page_num = page_number if page_number is not None else page_idx
            
            # Extract text with detailed information
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            
            for block_idx, block in enumerate(blocks.get("blocks", [])):
                if block.get("type") == 0:  # Text block
                    for line_idx, line in enumerate(block.get("lines", [])):
                        for span in line.get("spans", []):
                            text_block = TextBlock(
                                text=span.get("text", ""),
                                x0=span.get("bbox")[0],
                                y0=span.get("bbox")[1],
                                x1=span.get("bbox")[2],
                                y1=span.get("bbox")[3],
                                font_name=span.get("font", "Unknown"),
                                font_size=span.get("size", 12.0),
                                font_flags=span.get("flags", 0),
                                color=span.get("color", (0, 0, 0)),
                                page_number=actual_page_num,
                                block_number=block_idx,
                                line_number=line_idx
                            )
                            text_blocks.append(text_block)
                            
        return text_blocks
    
    def extract_text(self, page_number: Optional[int] = None) -> str:
        """
        Extract plain text from PDF.
        
        Args:
            page_number: Specific page to extract from (0-indexed), None for all pages
            
        Returns:
            Extracted text as string
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager or call open().")
            
        if page_number is not None:
            return self.document[page_number].get_text()
        else:
            text = ""
            for page in self.document:
                text += page.get_text()
            return text
    
    def get_page_count(self) -> int:
        """
        Get the total number of pages in the PDF.
        
        Returns:
            Number of pages
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager or call open().")
        return len(self.document)
    
    def get_page_dimensions(self, page_number: int) -> Tuple[float, float]:
        """
        Get the dimensions of a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager or call open().")
        page = self.document[page_number]
        rect = page.rect
        return (rect.width, rect.height)


def extract_text_from_pdf(pdf_path: str, page_number: Optional[int] = None) -> str:
    """
    Convenience function to extract text from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Specific page to extract from (0-indexed), None for all pages
        
    Returns:
        Extracted text as string
    """
    with TextExtractor(pdf_path) as extractor:
        return extractor.extract_text(page_number)


def extract_text_blocks_from_pdf(pdf_path: str, page_number: Optional[int] = None) -> List[TextBlock]:
    """
    Convenience function to extract text blocks with metadata from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Specific page to extract from (0-indexed), None for all pages
        
    Returns:
        List of TextBlock objects
    """
    with TextExtractor(pdf_path) as extractor:
        return extractor.extract_text_blocks(page_number)
