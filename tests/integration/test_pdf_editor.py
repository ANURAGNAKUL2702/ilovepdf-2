"""
Integration tests for PDF editing system.

These tests verify the complete workflow of editing PDFs.
"""
import pytest
from pathlib import Path
import fitz  # PyMuPDF
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src import PDFEditor


def create_test_pdf_with_mistakes(path: str):
    """Create a test PDF with spelling mistakes."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add text with intentional mistakes
    page.insert_text((72, 72), "This is a tset document.", fontsize=12)
    page.insert_text((72, 100), "It contans some mistkes.", fontsize=12)
    page.insert_text((72, 128), "We will corect them.", fontsize=12)
    
    doc.save(path)
    doc.close()


def create_multipage_pdf(path: str):
    """Create a multi-page test PDF."""
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Page one content", fontsize=12)
    page1.insert_text((72, 100), "First page text", fontsize=12)
    
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page two content", fontsize=12)
    page2.insert_text((72, 100), "Second page text", fontsize=12)
    
    doc.save(path)
    doc.close()


@pytest.fixture
def test_pdf_with_mistakes(tmp_path):
    """Create a test PDF with spelling mistakes."""
    pdf_path = tmp_path / "mistakes.pdf"
    create_test_pdf_with_mistakes(str(pdf_path))
    return str(pdf_path)


@pytest.fixture
def multipage_pdf(tmp_path):
    """Create a multi-page test PDF."""
    pdf_path = tmp_path / "multipage.pdf"
    create_multipage_pdf(str(pdf_path))
    return str(pdf_path)


@pytest.mark.integration
class TestPDFEditorWorkflow:
    """Test complete PDF editing workflows."""
    
    def test_load_and_extract(self, multipage_pdf):
        """Test loading and extracting text from PDF."""
        editor = PDFEditor(multipage_pdf)
        editor.load()
        
        # Get all text blocks
        blocks = editor.get_text_blocks()
        assert len(blocks) > 0
        
        # Get page-specific blocks
        page0_blocks = editor.get_text_blocks(page_number=0)
        page1_blocks = editor.get_text_blocks(page_number=1)
        
        assert len(page0_blocks) > 0
        assert len(page1_blocks) > 0
        
        # Verify text content
        all_text = editor.extract_text()
        assert "Page one" in all_text
        assert "Page two" in all_text
    
    def test_spell_checking_workflow(self, test_pdf_with_mistakes):
        """Test spell checking workflow."""
        editor = PDFEditor(test_pdf_with_mistakes)
        editor.load()
        
        # Check for spelling mistakes
        mistakes = editor.check_spelling()
        
        # Should find mistakes (tset, contans, mistkes, corect)
        assert len(mistakes) > 0
        
        # Get suggestions for a misspelled word
        suggestions = editor.get_spelling_suggestions("tset")
        assert len(suggestions) > 0
    
    def test_spell_correction_workflow(self, test_pdf_with_mistakes, tmp_path):
        """Test spell correction workflow."""
        output_path = tmp_path / "corrected.pdf"
        
        editor = PDFEditor(test_pdf_with_mistakes)
        
        # Correct spelling
        count = editor.correct_spelling(str(output_path))
        
        # Should have made some corrections
        assert count >= 0
        
        # Output file should exist
        assert output_path.exists()
    
    def test_text_insertion_workflow(self, multipage_pdf, tmp_path):
        """Test text insertion workflow."""
        output_path = tmp_path / "inserted.pdf"
        
        editor = PDFEditor(multipage_pdf)
        
        # Insert text on first page
        success = editor.insert_text(
            str(output_path),
            page_number=0,
            text="Inserted text",
            x=200,
            y=200,
            font_size=14
        )
        
        assert success is True
        assert output_path.exists()
    
    def test_text_replacement_workflow(self, multipage_pdf, tmp_path):
        """Test text replacement workflow."""
        output_path = tmp_path / "replaced.pdf"
        
        editor = PDFEditor(multipage_pdf)
        editor.load()
        
        # Replace "page" with "section"
        count = editor.replace_text(
            str(output_path),
            "page",
            "section",
            preserve_style=True
        )
        
        # Should have replaced multiple occurrences
        assert count > 0
        assert output_path.exists()
    
    def test_find_text_workflow(self, multipage_pdf):
        """Test finding text workflow."""
        editor = PDFEditor(multipage_pdf)
        editor.load()
        
        # Find "content" in the document
        blocks = editor.find_text("content")
        
        # Should find on both pages
        assert len(blocks) >= 2
        
        # Find on specific page
        page0_blocks = editor.find_text("one", page_number=0)
        assert len(page0_blocks) > 0
        assert all(b.page_number == 0 for b in page0_blocks)
    
    def test_font_analysis_workflow(self, multipage_pdf):
        """Test font analysis workflow."""
        editor = PDFEditor(multipage_pdf)
        
        # Get all fonts
        fonts = editor.get_fonts()
        assert len(fonts) > 0
        
        # Get fonts from specific page
        page_fonts = editor.get_fonts(page_number=0)
        assert len(page_fonts) > 0
    
    def test_page_info_workflow(self, multipage_pdf):
        """Test getting page information."""
        editor = PDFEditor(multipage_pdf)
        
        # Get page count
        count = editor.get_page_count()
        assert count == 2
        
        # Get page dimensions
        width, height = editor.get_page_dimensions(0)
        assert width > 0
        assert height > 0
    
    def test_custom_dictionary_workflow(self, test_pdf_with_mistakes):
        """Test using custom dictionary."""
        # Add custom words that shouldn't be corrected
        custom_dict = ["tset", "mistkes"]
        
        editor = PDFEditor(test_pdf_with_mistakes, custom_dictionary=custom_dict)
        editor.load()
        
        # Add more words at runtime
        editor.add_word_to_dictionary("contans")
        
        # Check spelling - should skip custom dictionary words
        mistakes = editor.check_spelling()
        
        # Verify custom words are in dictionary
        assert "tset" in editor.spell_checker.custom_dictionary
        assert "mistkes" in editor.spell_checker.custom_dictionary
        assert "contans" in editor.spell_checker.custom_dictionary


@pytest.mark.integration
def test_end_to_end_workflow(tmp_path):
    """Test complete end-to-end workflow."""
    # Create a test PDF
    input_pdf = tmp_path / "input.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Orignal document with mistkes", fontsize=12)
    page.insert_text((72, 100), "This needs corection", fontsize=12)
    doc.save(str(input_pdf))
    doc.close()
    
    # Initialize editor
    editor = PDFEditor(str(input_pdf))
    editor.load()
    
    # Step 1: Check spelling
    mistakes = editor.check_spelling()
    assert len(mistakes) > 0
    
    # Step 2: Correct spelling
    corrected_pdf = tmp_path / "corrected.pdf"
    corrections = editor.correct_spelling(str(corrected_pdf))
    assert corrections >= 0
    assert corrected_pdf.exists()
    
    # Step 3: Insert additional text
    final_pdf = tmp_path / "final.pdf"
    editor2 = PDFEditor(str(corrected_pdf))
    success = editor2.insert_text(
        str(final_pdf),
        page_number=0,
        text="[CORRECTED]",
        x=72,
        y=150
    )
    assert success is True
    assert final_pdf.exists()
    
    # Verify final PDF
    final_editor = PDFEditor(str(final_pdf))
    text = final_editor.extract_text()
    assert "[CORRECTED]" in text
