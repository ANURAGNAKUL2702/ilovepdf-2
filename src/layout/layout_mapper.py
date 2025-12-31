"""
Layout mapping module for PDF editing system.

This module provides functionality to map and preserve text layout,
including coordinates, alignment, and spacing.
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..extraction.text_extractor import TextBlock


class Alignment(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFIED = "justified"


@dataclass
class LayoutRegion:
    """Represents a region in the PDF layout."""
    x0: float
    y0: float
    x1: float
    y1: float
    page_number: int
    text_blocks: List[TextBlock] = field(default_factory=list)
    
    @property
    def width(self) -> float:
        """Calculate region width."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Calculate region height."""
        return self.y1 - self.y0
    
    @property
    def center(self) -> Tuple[float, float]:
        """Calculate center point of the region."""
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)


class LayoutMapper:
    """Maps and preserves PDF layout information."""
    
    def __init__(self):
        """Initialize the layout mapper."""
        self.regions: Dict[int, List[LayoutRegion]] = {}
        
    def add_text_blocks(self, text_blocks: List[TextBlock]):
        """
        Add text blocks to the layout map.
        
        Args:
            text_blocks: List of TextBlock objects to add
        """
        for block in text_blocks:
            if block.page_number not in self.regions:
                self.regions[block.page_number] = []
                
            # Check if block fits in existing region
            added = False
            for region in self.regions[block.page_number]:
                if self._is_block_in_region(block, region):
                    region.text_blocks.append(block)
                    added = True
                    break
                    
            if not added:
                # Create new region for this block
                new_region = LayoutRegion(
                    x0=block.x0,
                    y0=block.y0,
                    x1=block.x1,
                    y1=block.y1,
                    page_number=block.page_number,
                    text_blocks=[block]
                )
                self.regions[block.page_number].append(new_region)
                
    def _is_block_in_region(self, block: TextBlock, region: LayoutRegion, 
                           tolerance: float = 5.0) -> bool:
        """
        Check if a text block fits in a region with tolerance.
        
        Args:
            block: TextBlock to check
            region: LayoutRegion to check against
            tolerance: Tolerance in points
            
        Returns:
            True if block fits in region, False otherwise
        """
        return (
            abs(block.x0 - region.x0) < tolerance and
            abs(block.x1 - region.x1) < tolerance and
            block.y0 >= region.y0 - tolerance and
            block.y1 <= region.y1 + tolerance
        )
    
    def get_regions_on_page(self, page_number: int) -> List[LayoutRegion]:
        """
        Get all layout regions on a specific page.
        
        Args:
            page_number: Page number (0-indexed)
            
        Returns:
            List of LayoutRegion objects
        """
        return self.regions.get(page_number, [])
    
    def detect_alignment(self, text_blocks: List[TextBlock], 
                        page_width: float) -> Alignment:
        """
        Detect the alignment of a group of text blocks.
        
        Args:
            text_blocks: List of TextBlock objects
            page_width: Width of the page
            
        Returns:
            Alignment enum value
        """
        if not text_blocks:
            return Alignment.LEFT
            
        # Calculate average position
        avg_x0 = sum(block.x0 for block in text_blocks) / len(text_blocks)
        avg_x1 = sum(block.x1 for block in text_blocks) / len(text_blocks)
        
        # Check for center alignment
        center_x = page_width / 2
        if abs((avg_x0 + avg_x1) / 2 - center_x) < 20:
            return Alignment.CENTER
            
        # Check for right alignment
        if avg_x1 > page_width * 0.8:
            return Alignment.RIGHT
            
        # Check for justified (blocks extend across most of the page)
        if avg_x1 - avg_x0 > page_width * 0.7:
            return Alignment.JUSTIFIED
            
        return Alignment.LEFT
    
    def calculate_line_spacing(self, text_blocks: List[TextBlock]) -> float:
        """
        Calculate average line spacing from text blocks.
        
        Args:
            text_blocks: List of TextBlock objects
            
        Returns:
            Average line spacing in points
        """
        if len(text_blocks) < 2:
            return 0.0
            
        # Sort blocks by vertical position
        sorted_blocks = sorted(text_blocks, key=lambda b: b.y0)
        
        # Calculate spacing between consecutive blocks
        spacings = []
        for i in range(len(sorted_blocks) - 1):
            spacing = sorted_blocks[i + 1].y0 - sorted_blocks[i].y1
            if spacing > 0:  # Only positive spacings
                spacings.append(spacing)
                
        return sum(spacings) / len(spacings) if spacings else 0.0
    
    def get_text_at_position(self, page_number: int, x: float, y: float,
                            tolerance: float = 5.0) -> Optional[TextBlock]:
        """
        Get text block at a specific position.
        
        Args:
            page_number: Page number (0-indexed)
            x: X coordinate
            y: Y coordinate
            tolerance: Tolerance in points
            
        Returns:
            TextBlock at position or None
        """
        regions = self.get_regions_on_page(page_number)
        
        for region in regions:
            for block in region.text_blocks:
                if (block.x0 - tolerance <= x <= block.x1 + tolerance and
                    block.y0 - tolerance <= y <= block.y1 + tolerance):
                    return block
                    
        return None
    
    def find_blocks_by_text(self, search_text: str, 
                           page_number: Optional[int] = None) -> List[TextBlock]:
        """
        Find text blocks containing specific text.
        
        Args:
            search_text: Text to search for
            page_number: Specific page to search (None for all pages)
            
        Returns:
            List of matching TextBlock objects
        """
        matching_blocks = []
        
        pages = [page_number] if page_number is not None else self.regions.keys()
        
        for page in pages:
            regions = self.get_regions_on_page(page)
            for region in regions:
                for block in region.text_blocks:
                    if search_text.lower() in block.text.lower():
                        matching_blocks.append(block)
                        
        return matching_blocks
    
    def get_column_structure(self, page_number: int, 
                            column_gap: float = 20.0) -> List[List[LayoutRegion]]:
        """
        Detect column structure on a page.
        
        Args:
            page_number: Page number (0-indexed)
            column_gap: Minimum gap between columns in points
            
        Returns:
            List of columns, each containing a list of regions
        """
        regions = self.get_regions_on_page(page_number)
        if not regions:
            return []
            
        # Sort regions by x position
        sorted_regions = sorted(regions, key=lambda r: r.x0)
        
        columns = []
        current_column = [sorted_regions[0]]
        
        for i in range(1, len(sorted_regions)):
            region = sorted_regions[i]
            prev_region = sorted_regions[i - 1]
            
            # Check if there's a significant gap (new column)
            if region.x0 - prev_region.x1 > column_gap:
                columns.append(current_column)
                current_column = [region]
            else:
                current_column.append(region)
                
        columns.append(current_column)
        return columns
