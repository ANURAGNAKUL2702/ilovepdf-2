"""
Unit tests for font detection module.
"""
import pytest
from pathlib import Path
import fitz  # PyMuPDF
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.font import FontDetector, FontInfo, detect_fonts_in_pdf


def create_test_pdf_with_fonts(path: str):
    """Create a test PDF with different fonts."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add text with different fonts
    page.insert_text((72, 72), "Regular text", fontsize=12)
    page.insert_text((72, 100), "Larger text", fontsize=16)
    
    doc.save(path)
    doc.close()


@pytest.fixture
def test_pdf_path(tmp_path):
    """Create a temporary test PDF."""
    pdf_path = tmp_path / "test_fonts.pdf"
    create_test_pdf_with_fonts(str(pdf_path))
    return str(pdf_path)


@pytest.mark.unit
class TestFontInfo:
    """Test FontInfo data class."""
    
    def test_font_info_from_span(self):
        """Test creating FontInfo from span dictionary."""
        span = {
            "font": "Helvetica",
            "size": 12.0,
            "flags": 0,
            "color": (0, 0, 0)
        }
        
        font_info = FontInfo.from_span(span)
        assert font_info.name == "Helvetica"
        assert font_info.size == 12.0
        assert font_info.color == (0, 0, 0)
    
    def test_font_flags_parsing(self):
        """Test parsing font flags."""
        # Bold flag (bit 4)
        span = {"font": "Test", "size": 12.0, "flags": 2**4, "color": (0, 0, 0)}
        font_info = FontInfo.from_span(span)
        assert font_info.is_bold is True
        
        # Italic flag (bit 1)
        span = {"font": "Test", "size": 12.0, "flags": 2**1, "color": (0, 0, 0)}
        font_info = FontInfo.from_span(span)
        assert font_info.is_italic is True


@pytest.mark.unit
class TestFontDetector:
    """Test FontDetector class."""
    
    def test_context_manager(self, test_pdf_path):
        """Test using FontDetector as context manager."""
        with FontDetector(test_pdf_path) as detector:
            assert detector.document is not None
    
    def test_get_fonts_on_page(self, test_pdf_path):
        """Test getting fonts from a specific page."""
        with FontDetector(test_pdf_path) as detector:
            fonts = detector.get_fonts_on_page(0)
            assert len(fonts) > 0
            
            # Check first font
            font = fonts[0]
            assert isinstance(font, FontInfo)
            assert font.size > 0
    
    def test_get_unique_fonts(self, test_pdf_path):
        """Test getting unique fonts."""
        with FontDetector(test_pdf_path) as detector:
            fonts = detector.get_unique_fonts()
            assert len(fonts) > 0
            
            # Should have at least 2 different font sizes
            sizes = set(f.size for f in fonts)
            assert len(sizes) >= 2
    
    def test_get_dominant_font(self, test_pdf_path):
        """Test getting dominant font."""
        with FontDetector(test_pdf_path) as detector:
            font = detector.get_dominant_font()
            assert font is not None
            assert isinstance(font, FontInfo)
            assert font.size > 0
    
    def test_get_font_at_position(self, test_pdf_path):
        """Test getting font at specific position."""
        with FontDetector(test_pdf_path) as detector:
            # Get font at text position (72, 72)
            font = detector.get_font_at_position(0, 72, 72)
            assert font is not None
            assert isinstance(font, FontInfo)


@pytest.mark.unit
def test_detect_fonts_convenience(test_pdf_path):
    """Test convenience function for font detection."""
    fonts = detect_fonts_in_pdf(test_pdf_path)
    assert len(fonts) > 0
    assert all(isinstance(f, FontInfo) for f in fonts)
