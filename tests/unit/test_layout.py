"""
Unit tests for layout mapping module.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.layout import LayoutMapper, LayoutRegion, Alignment
from src.extraction import TextBlock


@pytest.mark.unit
class TestLayoutRegion:
    """Test LayoutRegion data class."""
    
    def test_layout_region_creation(self):
        """Test creating a LayoutRegion."""
        region = LayoutRegion(
            x0=10.0,
            y0=20.0,
            x1=100.0,
            y1=80.0,
            page_number=0
        )
        
        assert region.width == 90.0
        assert region.height == 60.0
        assert region.center == (55.0, 50.0)


@pytest.mark.unit
class TestLayoutMapper:
    """Test LayoutMapper class."""
    
    def test_add_text_blocks(self):
        """Test adding text blocks to mapper."""
        mapper = LayoutMapper()
        
        block = TextBlock(
            text="Test",
            x0=10.0,
            y0=20.0,
            x1=50.0,
            y1=40.0,
            font_name="Helvetica",
            font_size=12.0,
            font_flags=0,
            color=(0, 0, 0),
            page_number=0,
            block_number=0,
            line_number=0
        )
        
        mapper.add_text_blocks([block])
        regions = mapper.get_regions_on_page(0)
        assert len(regions) > 0
    
    def test_get_regions_on_page(self):
        """Test getting regions from a page."""
        mapper = LayoutMapper()
        
        # Add blocks on different pages
        block1 = TextBlock(
            text="Page 0", x0=10.0, y0=20.0, x1=50.0, y1=40.0,
            font_name="Helvetica", font_size=12.0, font_flags=0,
            color=(0, 0, 0), page_number=0, block_number=0, line_number=0
        )
        block2 = TextBlock(
            text="Page 1", x0=10.0, y0=20.0, x1=50.0, y1=40.0,
            font_name="Helvetica", font_size=12.0, font_flags=0,
            color=(0, 0, 0), page_number=1, block_number=0, line_number=0
        )
        
        mapper.add_text_blocks([block1, block2])
        
        regions_page0 = mapper.get_regions_on_page(0)
        regions_page1 = mapper.get_regions_on_page(1)
        
        assert len(regions_page0) > 0
        assert len(regions_page1) > 0
    
    def test_detect_alignment(self):
        """Test detecting text alignment."""
        mapper = LayoutMapper()
        page_width = 612.0  # Letter size width
        
        # Left-aligned blocks
        left_blocks = [
            TextBlock(
                text="Left", x0=72.0, y0=100.0, x1=150.0, y1=120.0,
                font_name="Helvetica", font_size=12.0, font_flags=0,
                color=(0, 0, 0), page_number=0, block_number=0, line_number=0
            )
        ]
        assert mapper.detect_alignment(left_blocks, page_width) == Alignment.LEFT
        
        # Center-aligned blocks
        center_blocks = [
            TextBlock(
                text="Center", x0=250.0, y0=100.0, x1=350.0, y1=120.0,
                font_name="Helvetica", font_size=12.0, font_flags=0,
                color=(0, 0, 0), page_number=0, block_number=0, line_number=0
            )
        ]
        assert mapper.detect_alignment(center_blocks, page_width) == Alignment.CENTER
        
        # Right-aligned blocks
        right_blocks = [
            TextBlock(
                text="Right", x0=450.0, y0=100.0, x1=540.0, y1=120.0,
                font_name="Helvetica", font_size=12.0, font_flags=0,
                color=(0, 0, 0), page_number=0, block_number=0, line_number=0
            )
        ]
        assert mapper.detect_alignment(right_blocks, page_width) == Alignment.RIGHT
    
    def test_calculate_line_spacing(self):
        """Test calculating line spacing."""
        mapper = LayoutMapper()
        
        blocks = [
            TextBlock(
                text="Line 1", x0=72.0, y0=100.0, x1=150.0, y1=115.0,
                font_name="Helvetica", font_size=12.0, font_flags=0,
                color=(0, 0, 0), page_number=0, block_number=0, line_number=0
            ),
            TextBlock(
                text="Line 2", x0=72.0, y0=120.0, x1=150.0, y1=135.0,
                font_name="Helvetica", font_size=12.0, font_flags=0,
                color=(0, 0, 0), page_number=0, block_number=0, line_number=1
            )
        ]
        
        spacing = mapper.calculate_line_spacing(blocks)
        assert spacing >= 0
    
    def test_find_blocks_by_text(self):
        """Test finding blocks by text content."""
        mapper = LayoutMapper()
        
        block1 = TextBlock(
            text="Hello world", x0=10.0, y0=20.0, x1=50.0, y1=40.0,
            font_name="Helvetica", font_size=12.0, font_flags=0,
            color=(0, 0, 0), page_number=0, block_number=0, line_number=0
        )
        block2 = TextBlock(
            text="Goodbye world", x0=10.0, y0=50.0, x1=50.0, y1=70.0,
            font_name="Helvetica", font_size=12.0, font_flags=0,
            color=(0, 0, 0), page_number=0, block_number=1, line_number=0
        )
        
        mapper.add_text_blocks([block1, block2])
        
        # Search for "world"
        results = mapper.find_blocks_by_text("world")
        assert len(results) == 2
        
        # Search for "Hello"
        results = mapper.find_blocks_by_text("Hello")
        assert len(results) == 1
        assert results[0].text == "Hello world"
    
    def test_get_text_at_position(self):
        """Test getting text at specific position."""
        mapper = LayoutMapper()
        
        block = TextBlock(
            text="Test", x0=10.0, y0=20.0, x1=50.0, y1=40.0,
            font_name="Helvetica", font_size=12.0, font_flags=0,
            color=(0, 0, 0), page_number=0, block_number=0, line_number=0
        )
        
        mapper.add_text_blocks([block])
        
        # Should find the block
        found = mapper.get_text_at_position(0, 30.0, 30.0)
        assert found is not None
        assert found.text == "Test"
        
        # Should not find anything
        found = mapper.get_text_at_position(0, 200.0, 200.0)
        assert found is None


@pytest.mark.unit
class TestAlignment:
    """Test Alignment enum."""
    
    def test_alignment_values(self):
        """Test alignment enum values."""
        assert Alignment.LEFT.value == "left"
        assert Alignment.CENTER.value == "center"
        assert Alignment.RIGHT.value == "right"
        assert Alignment.JUSTIFIED.value == "justified"
