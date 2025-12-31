"""
Main PDF Editor module integrating all components.

This module provides a high-level interface for PDF editing operations
including text extraction, spell checking, and text modification.
"""
from typing import List, Optional, Tuple
from pathlib import Path

from .extraction import TextExtractor, TextBlock, extract_text_blocks_from_pdf
from .font import FontDetector, FontInfo
from .layout import LayoutMapper, Alignment
from .utils import SpellChecker, TextModifier
from .rendering import PDFRenderer, RenderOptions


class PDFEditor:
    """
    Main PDF editor class integrating all editing functionality.
    
    This class provides a high-level interface for:
    - Text extraction with layout preservation
    - Font detection and analysis
    - Spell checking and correction
    - Text insertion and modification
    - Re-rendering with style preservation
    """
    
    def __init__(self, pdf_path: str, custom_dictionary: Optional[List[str]] = None):
        """
        Initialize PDF editor.
        
        Args:
            pdf_path: Path to the PDF file
            custom_dictionary: Optional custom dictionary for spell checking
        """
        self.pdf_path = pdf_path
        self.custom_dictionary = custom_dictionary or []
        self.spell_checker = SpellChecker(self.custom_dictionary)
        self.layout_mapper = LayoutMapper()
        self._text_blocks: Optional[List[TextBlock]] = None
        
    def load(self):
        """Load and analyze the PDF document."""
        # Extract text blocks
        with TextExtractor(self.pdf_path) as extractor:
            self._text_blocks = extractor.extract_text_blocks()
            
        # Build layout map
        if self._text_blocks:
            self.layout_mapper.add_text_blocks(self._text_blocks)
    
    def get_text_blocks(self, page_number: Optional[int] = None) -> List[TextBlock]:
        """
        Get extracted text blocks.
        
        Args:
            page_number: Specific page number (0-indexed), None for all pages
            
        Returns:
            List of TextBlock objects
        """
        if self._text_blocks is None:
            self.load()
            
        if page_number is None:
            return self._text_blocks or []
        else:
            return [b for b in (self._text_blocks or []) if b.page_number == page_number]
    
    def check_spelling(self, page_number: Optional[int] = None) -> List[Tuple[TextBlock, List[Tuple[str, int, int]]]]:
        """
        Check spelling in the PDF.
        
        Args:
            page_number: Specific page to check (0-indexed), None for all pages
            
        Returns:
            List of tuples (TextBlock, mistakes) where mistakes is a list of
            (misspelled_word, start_pos, end_pos)
        """
        blocks = self.get_text_blocks(page_number)
        results = []
        
        for block in blocks:
            mistakes = self.spell_checker.check_text(block.text)
            if mistakes:
                results.append((block, mistakes))
                
        return results
    
    def correct_spelling(self, output_path: str, page_number: Optional[int] = None) -> int:
        """
        Correct spelling mistakes in the PDF.
        
        Args:
            output_path: Path to save corrected PDF
            page_number: Specific page to correct (0-indexed), None for all pages
            
        Returns:
            Number of corrections made
        """
        blocks = self.get_text_blocks(page_number)
        corrections_count = 0
        
        with PDFRenderer(self.pdf_path, output_path) as renderer:
            for block in blocks:
                corrected_text = self.spell_checker.correct_text(block.text)
                
                if corrected_text != block.text:
                    # Replace text block with corrected version
                    options = RenderOptions.from_text_block(block)
                    renderer.replace_text_block(block, corrected_text, options)
                    corrections_count += 1
                    
            renderer.save()
            
        return corrections_count
    
    def insert_text(self, output_path: str, page_number: int, text: str,
                   x: float, y: float, font_size: Optional[float] = None,
                   font_name: Optional[str] = None) -> bool:
        """
        Insert new text at a specific position.
        
        Args:
            output_path: Path to save modified PDF
            page_number: Page number (0-indexed)
            text: Text to insert
            x: X coordinate
            y: Y coordinate
            font_size: Optional font size (uses dominant font if None)
            font_name: Optional font name (uses dominant font if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Get dominant font for default styling
        with FontDetector(self.pdf_path) as detector:
            dominant_font = detector.get_dominant_font(page_number)
            
        if dominant_font and (font_size is None or font_name is None):
            options = RenderOptions.from_font_info(dominant_font)
            if font_size is not None:
                options.font_size = font_size
        else:
            options = RenderOptions(
                font_size=font_size or 12.0,
                font_name=font_name or "helv"
            )
        
        with PDFRenderer(self.pdf_path, output_path) as renderer:
            success = renderer.insert_text(page_number, text, x, y, options)
            if success:
                renderer.save()
            return success
    
    def replace_text(self, output_path: str, old_text: str, new_text: str,
                    page_number: Optional[int] = None, preserve_style: bool = True) -> int:
        """
        Replace occurrences of text in the PDF.
        
        Args:
            output_path: Path to save modified PDF
            old_text: Text to replace
            new_text: Replacement text
            page_number: Specific page (0-indexed), None for all pages
            preserve_style: Whether to preserve original text style
            
        Returns:
            Number of replacements made
        """
        blocks = self.layout_mapper.find_blocks_by_text(old_text, page_number)
        replacements_count = 0
        
        with PDFRenderer(self.pdf_path, output_path) as renderer:
            for block in blocks:
                # Replace text in block
                modified_text = block.text.replace(old_text, new_text)
                
                if modified_text != block.text:
                    options = RenderOptions.from_text_block(block) if preserve_style else None
                    renderer.replace_text_block(block, modified_text, options)
                    replacements_count += 1
                    
            renderer.save()
            
        return replacements_count
    
    def find_text(self, search_text: str, page_number: Optional[int] = None) -> List[TextBlock]:
        """
        Find text blocks containing specific text.
        
        Args:
            search_text: Text to search for
            page_number: Specific page to search (0-indexed), None for all pages
            
        Returns:
            List of matching TextBlock objects
        """
        if self._text_blocks is None:
            self.load()
            
        return self.layout_mapper.find_blocks_by_text(search_text, page_number)
    
    def get_fonts(self, page_number: Optional[int] = None) -> List[FontInfo]:
        """
        Get unique fonts in the PDF.
        
        Args:
            page_number: Specific page (0-indexed), None for all pages
            
        Returns:
            List of unique FontInfo objects
        """
        with FontDetector(self.pdf_path) as detector:
            return detector.get_unique_fonts(page_number)
    
    def get_page_count(self) -> int:
        """
        Get the number of pages in the PDF.
        
        Returns:
            Number of pages
        """
        with TextExtractor(self.pdf_path) as extractor:
            return extractor.get_page_count()
    
    def get_page_dimensions(self, page_number: int) -> Tuple[float, float]:
        """
        Get dimensions of a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points
        """
        with TextExtractor(self.pdf_path) as extractor:
            return extractor.get_page_dimensions(page_number)
    
    def extract_text(self, page_number: Optional[int] = None) -> str:
        """
        Extract plain text from the PDF.
        
        Args:
            page_number: Specific page (0-indexed), None for all pages
            
        Returns:
            Extracted text
        """
        with TextExtractor(self.pdf_path) as extractor:
            return extractor.extract_text(page_number)
    
    def add_word_to_dictionary(self, word: str):
        """
        Add a word to the custom spell checking dictionary.
        
        Args:
            word: Word to add
        """
        self.spell_checker.add_to_dictionary(word)
        
    def get_spelling_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Word to get suggestions for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested corrections
        """
        return self.spell_checker.get_suggestions(word, max_suggestions)
