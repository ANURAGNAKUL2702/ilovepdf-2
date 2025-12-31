"""
Unit tests for rendering module.
"""
import pytest
from pathlib import Path
import fitz  # PyMuPDF
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rendering import PDFRenderer, RenderOptions, render_text_to_pdf
from src.extraction import TextBlock
from src.font import FontInfo


def create_test_pdf(path: str):
    """Create a simple test PDF file."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Original text", fontsize=12)
    doc.save(path)
    doc.close()


@pytest.fixture
def test_pdf_path(tmp_path):
    """Create a temporary test PDF."""
    pdf_path = tmp_path / "test.pdf"
    create_test_pdf(str(pdf_path))
    return str(pdf_path)


@pytest.mark.unit
class TestRenderOptions:
    """Test RenderOptions class."""
    
    def test_render_options_default(self):
        """Test default render options."""
        options = RenderOptions()
        assert options.font_name == "helv"
        assert options.font_size == 12.0
        assert options.color == (0, 0, 0)
        assert options.align == 0
    
    def test_render_options_custom(self):
        """Test custom render options."""
        options = RenderOptions(
            font_name="times",
            font_size=14.0,
            color=(1, 0, 0),
            align=1
        )
        assert options.font_name == "times"
        assert options.font_size == 14.0
        assert options.color == (1, 0, 0)
        assert options.align == 1
    
    def test_from_font_info(self):
        """Test creating RenderOptions from FontInfo."""
        font_info = FontInfo(
            name="Helvetica",
            size=14.0,
            flags=0,
            is_bold=False,
            is_italic=False,
            is_monospace=False,
            is_serif=False,
            color=(0, 0, 0)
        )
        
        options = RenderOptions.from_font_info(font_info)
        assert options.font_size == 14.0
        assert options.color == (0, 0, 0)
    
    def test_from_text_block(self):
        """Test creating RenderOptions from TextBlock."""
        block = TextBlock(
            text="Test",
            x0=10.0,
            y0=20.0,
            x1=50.0,
            y1=40.0,
            font_name="Helvetica",
            font_size=16.0,
            font_flags=0,
            color=(0.5, 0.5, 0.5),
            page_number=0,
            block_number=0,
            line_number=0
        )
        
        options = RenderOptions.from_text_block(block)
        assert options.font_size == 16.0
        assert options.color == (0.5, 0.5, 0.5)


@pytest.mark.unit
class TestPDFRenderer:
    """Test PDFRenderer class."""
    
    def test_context_manager(self, test_pdf_path):
        """Test using PDFRenderer as context manager."""
        with PDFRenderer(test_pdf_path) as renderer:
            assert renderer.document is not None
    
    def test_insert_text(self, test_pdf_path, tmp_path):
        """Test inserting text into PDF."""
        output_path = tmp_path / "output.pdf"
        
        with PDFRenderer(test_pdf_path, str(output_path)) as renderer:
            success = renderer.insert_text(0, "New text", 100, 100)
            assert success is True
            renderer.save()
        
        # Verify the file was created
        assert output_path.exists()
    
    def test_insert_textbox(self, test_pdf_path, tmp_path):
        """Test inserting text in a box."""
        output_path = tmp_path / "output.pdf"
        
        with PDFRenderer(test_pdf_path, str(output_path)) as renderer:
            success = renderer.insert_textbox(
                0, 
                "Boxed text", 
                (100, 100, 200, 150)
            )
            assert success is True
            renderer.save()
        
        assert output_path.exists()
    
    def test_replace_text_block(self, test_pdf_path, tmp_path):
        """Test replacing a text block."""
        output_path = tmp_path / "output.pdf"
        
        block = TextBlock(
            text="Original text",
            x0=72.0,
            y0=60.0,
            x1=150.0,
            y1=84.0,
            font_name="Helvetica",
            font_size=12.0,
            font_flags=0,
            color=(0, 0, 0),
            page_number=0,
            block_number=0,
            line_number=0
        )
        
        with PDFRenderer(test_pdf_path, str(output_path)) as renderer:
            success = renderer.replace_text_block(block, "Replaced text")
            assert success is True
            renderer.save()
        
        assert output_path.exists()
    
    def test_remove_text_block(self, test_pdf_path, tmp_path):
        """Test removing a text block."""
        output_path = tmp_path / "output.pdf"
        
        block = TextBlock(
            text="Original text",
            x0=72.0,
            y0=60.0,
            x1=150.0,
            y1=84.0,
            font_name="Helvetica",
            font_size=12.0,
            font_flags=0,
            color=(0, 0, 0),
            page_number=0,
            block_number=0,
            line_number=0
        )
        
        with PDFRenderer(test_pdf_path, str(output_path)) as renderer:
            success = renderer.remove_text_block(block)
            assert success is True
            renderer.save()
        
        assert output_path.exists()
    
    def test_get_page_count(self, test_pdf_path):
        """Test getting page count."""
        with PDFRenderer(test_pdf_path) as renderer:
            count = renderer.get_page_count()
            assert count == 1
    
    def test_save_to_different_path(self, test_pdf_path, tmp_path):
        """Test saving to a different path."""
        output_path = tmp_path / "different_output.pdf"
        
        with PDFRenderer(test_pdf_path) as renderer:
            renderer.insert_text(0, "Test", 100, 100)
            renderer.save(str(output_path))
        
        assert output_path.exists()


@pytest.mark.unit
def test_render_text_convenience(test_pdf_path, tmp_path):
    """Test convenience function for rendering."""
    output_path = tmp_path / "output.pdf"
    
    success = render_text_to_pdf(
        test_pdf_path,
        str(output_path),
        0,
        "New text",
        100,
        100
    )
    
    assert success is True
    assert output_path.exists()
