"""
Rendering module for PDF editing system.

This module provides functionality to render and embed modified text
back into PDF documents while preserving original style and layout.
"""
import fitz  # PyMuPDF
from typing import Optional, Tuple, List
from dataclasses import dataclass

from ..extraction.text_extractor import TextBlock
from ..font.font_detector import FontInfo


@dataclass
class RenderOptions:
    """Options for rendering text in PDF."""
    font_name: str = "helv"  # Helvetica
    font_size: float = 12.0
    color: Tuple[float, float, float] = (0, 0, 0)
    align: int = 0  # 0=left, 1=center, 2=right
    overlay: bool = True  # True to overlay, False to insert
    
    @classmethod
    def from_font_info(cls, font_info: FontInfo, align: int = 0) -> 'RenderOptions':
        """
        Create RenderOptions from FontInfo.
        
        Args:
            font_info: FontInfo object
            align: Alignment (0=left, 1=center, 2=right)
            
        Returns:
            RenderOptions object
        """
        # Map PDF font names to PyMuPDF font names
        font_map = {
            "Times": "times",
            "TimesNewRoman": "times",
            "Helvetica": "helv",
            "Courier": "cour",
            "Symbol": "symb",
            "ZapfDingbats": "zadb"
        }
        
        # Try to find matching font
        font_name = "helv"  # Default
        for key, value in font_map.items():
            if key.lower() in font_info.name.lower():
                font_name = value
                break
                
        return cls(
            font_name=font_name,
            font_size=font_info.size,
            color=font_info.color,
            align=align
        )
    
    @classmethod
    def from_text_block(cls, text_block: TextBlock, align: int = 0) -> 'RenderOptions':
        """
        Create RenderOptions from TextBlock.
        
        Args:
            text_block: TextBlock object
            align: Alignment (0=left, 1=center, 2=right)
            
        Returns:
            RenderOptions object
        """
        font_map = {
            "Times": "times",
            "TimesNewRoman": "times",
            "Helvetica": "helv",
            "Courier": "cour",
            "Symbol": "symb",
            "ZapfDingbats": "zadb"
        }
        
        font_name = "helv"
        for key, value in font_map.items():
            if key.lower() in text_block.font_name.lower():
                font_name = value
                break
                
        return cls(
            font_name=font_name,
            font_size=text_block.font_size,
            color=text_block.color,
            align=align
        )


class PDFRenderer:
    """Render and modify text in PDF documents."""
    
    def __init__(self, pdf_path: str, output_path: Optional[str] = None):
        """
        Initialize PDF renderer.
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output PDF file (None for in-place modification)
        """
        self.pdf_path = pdf_path
        self.output_path = output_path or pdf_path
        self.document: Optional[fitz.Document] = None
        
    def __enter__(self):
        """Context manager entry."""
        self.document = fitz.open(self.pdf_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.document:
            self.document.close()
            
    def insert_text(self, page_number: int, text: str, x: float, y: float,
                   options: Optional[RenderOptions] = None) -> bool:
        """
        Insert text at a specific position.
        
        Args:
            page_number: Page number (0-indexed)
            text: Text to insert
            x: X coordinate
            y: Y coordinate
            options: RenderOptions for styling
            
        Returns:
            True if successful, False otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        if page_number >= len(self.document):
            return False
            
        page = self.document[page_number]
        opts = options or RenderOptions()
        
        # Insert text
        rc = page.insert_text(
            point=(x, y),
            text=text,
            fontname=opts.font_name,
            fontsize=opts.font_size,
            color=opts.color,
            overlay=opts.overlay
        )
        
        return rc >= 0
    
    def insert_textbox(self, page_number: int, text: str, 
                      rect: Tuple[float, float, float, float],
                      options: Optional[RenderOptions] = None) -> bool:
        """
        Insert text in a rectangular area.
        
        Args:
            page_number: Page number (0-indexed)
            text: Text to insert
            rect: Rectangle (x0, y0, x1, y1)
            options: RenderOptions for styling
            
        Returns:
            True if successful, False otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        if page_number >= len(self.document):
            return False
            
        page = self.document[page_number]
        opts = options or RenderOptions()
        
        # Insert text in box
        rc = page.insert_textbox(
            rect=fitz.Rect(rect),
            buffer=text,
            fontname=opts.font_name,
            fontsize=opts.font_size,
            color=opts.color,
            align=opts.align,
            overlay=opts.overlay
        )
        
        return rc >= 0
    
    def replace_text_block(self, text_block: TextBlock, new_text: str,
                          options: Optional[RenderOptions] = None) -> bool:
        """
        Replace a text block with new text, preserving style and position.
        
        Args:
            text_block: Original TextBlock to replace
            new_text: New text content
            options: Optional RenderOptions (uses block's style if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        page = self.document[text_block.page_number]
        
        # Remove old text by drawing white rectangle over it
        page.draw_rect(
            rect=fitz.Rect(text_block.x0, text_block.y0, text_block.x1, text_block.y1),
            color=(1, 1, 1),
            fill=(1, 1, 1),
            overlay=False
        )
        
        # Determine render options
        if options is None:
            options = RenderOptions.from_text_block(text_block)
        
        # Insert new text at same position
        return self.insert_text(
            page_number=text_block.page_number,
            text=new_text,
            x=text_block.x0,
            y=text_block.y0 + text_block.font_size,  # Adjust for baseline
            options=options
        )
    
    def remove_text_block(self, text_block: TextBlock) -> bool:
        """
        Remove a text block by covering it with white.
        
        Args:
            text_block: TextBlock to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        page = self.document[text_block.page_number]
        
        # Draw white rectangle over text
        page.draw_rect(
            rect=fitz.Rect(text_block.x0, text_block.y0, text_block.x1, text_block.y1),
            color=(1, 1, 1),
            fill=(1, 1, 1),
            overlay=False
        )
        
        return True
    
    def highlight_text_block(self, text_block: TextBlock, 
                            color: Tuple[float, float, float] = (1, 1, 0)) -> bool:
        """
        Highlight a text block.
        
        Args:
            text_block: TextBlock to highlight
            color: RGB color tuple (values 0-1)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        page = self.document[text_block.page_number]
        
        # Add highlight annotation
        highlight = page.add_highlight_annot(
            quads=fitz.Rect(text_block.x0, text_block.y0, text_block.x1, text_block.y1)
        )
        highlight.set_colors(stroke=color)
        highlight.update()
        
        return True
    
    def save(self, output_path: Optional[str] = None):
        """
        Save the modified PDF.
        
        Args:
            output_path: Path to save to (uses self.output_path if None)
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
            
        save_path = output_path or self.output_path
        self.document.save(save_path, garbage=4, deflate=True, clean=True)
    
    def get_page_count(self) -> int:
        """
        Get number of pages in document.
        
        Returns:
            Number of pages
        """
        if not self.document:
            raise RuntimeError("Document not opened. Use context manager.")
        return len(self.document)


def render_text_to_pdf(pdf_path: str, output_path: str, page_number: int,
                       text: str, x: float, y: float,
                       options: Optional[RenderOptions] = None) -> bool:
    """
    Convenience function to render text to a PDF.
    
    Args:
        pdf_path: Input PDF path
        output_path: Output PDF path
        page_number: Page number (0-indexed)
        text: Text to render
        x: X coordinate
        y: Y coordinate
        options: RenderOptions for styling
        
    Returns:
        True if successful, False otherwise
    """
    with PDFRenderer(pdf_path, output_path) as renderer:
        success = renderer.insert_text(page_number, text, x, y, options)
        if success:
            renderer.save()
        return success
