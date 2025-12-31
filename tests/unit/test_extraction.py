"""
Unit tests for text extraction module.
"""
import pytest
from pathlib import Path
import fitz  # PyMuPDF
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.extraction import TextExtractor, TextBlock, extract_text_from_pdf


# Create a simple test PDF
def create_test_pdf(path: str, text: str = "Test PDF content"):
    """Create a simple test PDF file."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    doc.save(path)
    doc.close()


@pytest.fixture
def test_pdf_path(tmp_path):
    """Create a temporary test PDF."""
    pdf_path = tmp_path / "test.pdf"
    create_test_pdf(str(pdf_path), "Hello World Test")
    return str(pdf_path)


@pytest.mark.unit
class TestTextBlock:
    """Test TextBlock data class."""
    
    def test_text_block_creation(self):
        """Test creating a TextBlock."""
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
        
        assert block.text == "Test"
        assert block.width == 40.0
        assert block.height == 20.0
        assert block.position == (10.0, 20.0)


@pytest.mark.unit
class TestTextExtractor:
    """Test TextExtractor class."""
    
    def test_context_manager(self, test_pdf_path):
        """Test using TextExtractor as context manager."""
        with TextExtractor(test_pdf_path) as extractor:
            assert extractor.document is not None
    
    def test_extract_text(self, test_pdf_path):
        """Test extracting text from PDF."""
        with TextExtractor(test_pdf_path) as extractor:
            text = extractor.extract_text()
            assert "Hello World Test" in text
    
    def test_extract_text_blocks(self, test_pdf_path):
        """Test extracting text blocks with metadata."""
        with TextExtractor(test_pdf_path) as extractor:
            blocks = extractor.extract_text_blocks()
            assert len(blocks) > 0
            
            # Check first block
            block = blocks[0]
            assert isinstance(block, TextBlock)
            assert len(block.text) > 0
            assert block.font_size > 0
    
    def test_get_page_count(self, test_pdf_path):
        """Test getting page count."""
        with TextExtractor(test_pdf_path) as extractor:
            count = extractor.get_page_count()
            assert count == 1
    
    def test_get_page_dimensions(self, test_pdf_path):
        """Test getting page dimensions."""
        with TextExtractor(test_pdf_path) as extractor:
            width, height = extractor.get_page_dimensions(0)
            assert width > 0
            assert height > 0
    
    def test_extract_specific_page(self, tmp_path):
        """Test extracting from specific page."""
        # Create multi-page PDF
        pdf_path = tmp_path / "multipage.pdf"
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text((72, 72), "Page 1", fontsize=12)
        page2 = doc.new_page()
        page2.insert_text((72, 72), "Page 2", fontsize=12)
        doc.save(str(pdf_path))
        doc.close()
        
        with TextExtractor(str(pdf_path)) as extractor:
            text = extractor.extract_text(page_number=1)
            assert "Page 2" in text
            assert "Page 1" not in text


@pytest.mark.unit
def test_extract_text_from_pdf_convenience(test_pdf_path):
    """Test convenience function for text extraction."""
    text = extract_text_from_pdf(test_pdf_path)
    assert "Hello World Test" in text
