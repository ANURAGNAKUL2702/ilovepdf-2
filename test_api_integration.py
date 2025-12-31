#!/usr/bin/env python3
"""
Integration test for the PDF Editor API
Tests the complete workflow: upload, extract, edit, add text, rotate, and export
"""
import os
import sys
import time
import tempfile
import requests
from io import BytesIO

API_URL = "http://localhost:8000/api"
TEST_PDF = "test_document.pdf"

def test_upload_pdf():
    """Test uploading a PDF file"""
    print("Testing PDF upload...")
    with open(TEST_PDF, 'rb') as f:
        files = {'file': (TEST_PDF, f, 'application/pdf')}
        response = requests.post(f"{API_URL}/pdf/upload", files=files)
    
    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()
    assert 'id' in data, "No PDF ID returned"
    assert 'metadata' in data, "No metadata returned"
    print(f"✓ Upload successful. PDF ID: {data['id']}")
    return data['id']

def test_extract_text_blocks(pdf_id):
    """Test extracting text blocks"""
    print("Testing text block extraction...")
    response = requests.get(f"{API_URL}/pdf/{pdf_id}/text-blocks")
    
    assert response.status_code == 200, f"Extraction failed: {response.text}"
    data = response.json()
    assert 'textBlocks' in data, "No text blocks returned"
    blocks = data['textBlocks']
    assert len(blocks) > 0, "No text blocks found"
    print(f"✓ Extracted {len(blocks)} text blocks")
    return blocks

def test_replace_text(pdf_id, block_id, new_text):
    """Test replacing text"""
    print(f"Testing text replacement for block {block_id}...")
    response = requests.post(
        f"{API_URL}/pdf/{pdf_id}/replace-text",
        json={
            'blockId': block_id,
            'newText': new_text,
            'preserveStyle': True
        }
    )
    
    assert response.status_code == 200, f"Replace failed: {response.text}"
    data = response.json()
    assert data.get('success'), "Replace operation failed"
    print(f"✓ Text replaced successfully")

def test_insert_text(pdf_id, page_number, text, x, y):
    """Test inserting new text"""
    print(f"Testing text insertion at ({x}, {y})...")
    response = requests.post(
        f"{API_URL}/pdf/{pdf_id}/insert-text",
        json={
            'pageNumber': page_number,
            'text': text,
            'x': x,
            'y': y,
            'options': {
                'fontSize': 14,
                'fontName': 'Helvetica'
            }
        }
    )
    
    assert response.status_code == 200, f"Insert failed: {response.text}"
    data = response.json()
    assert data.get('success'), "Insert operation failed"
    print(f"✓ Text inserted successfully")

def test_rotate_page(pdf_id, page_number, rotation):
    """Test rotating a page"""
    print(f"Testing page rotation by {rotation} degrees...")
    response = requests.post(
        f"{API_URL}/pdf/{pdf_id}/page/{page_number}/rotate",
        json={'rotation': rotation}
    )
    
    assert response.status_code == 200, f"Rotation failed: {response.text}"
    data = response.json()
    assert data.get('success'), "Rotation operation failed"
    print(f"✓ Page rotated successfully")

def test_export_pdf(pdf_id):
    """Test exporting the modified PDF"""
    print("Testing PDF export...")
    response = requests.get(f"{API_URL}/pdf/{pdf_id}/export")
    
    assert response.status_code == 200, f"Export failed: {response.status_code}"
    assert len(response.content) > 0, "Empty PDF returned"
    print(f"✓ PDF exported successfully ({len(response.content)} bytes)")
    return response.content

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("PDF Editor API Integration Tests")
    print("=" * 60)
    
    try:
        # Test upload
        pdf_id = test_upload_pdf()
        
        # Test text block extraction
        blocks = test_extract_text_blocks(pdf_id)
        
        if blocks:
            # Test text replacement (edit text)
            first_block = blocks[0]
            test_replace_text(pdf_id, first_block['id'], "EDITED TEXT")
        
        # Test text insertion (add text)
        test_insert_text(pdf_id, 0, "NEW INSERTED TEXT", 100, 500)
        
        # Test page rotation
        test_rotate_page(pdf_id, 0, 90)
        
        # Test export
        pdf_content = test_export_pdf(pdf_id)
        
        # Save the exported PDF
        output_dir = tempfile.gettempdir()
        output_path = os.path.join(output_dir, "test_output.pdf")
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        print(f"\n✓ Exported PDF saved to: {output_path}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API server. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if not os.path.exists(TEST_PDF):
        print(f"Error: Test PDF '{TEST_PDF}' not found")
        sys.exit(1)
    
    success = run_integration_tests()
    sys.exit(0 if success else 1)
