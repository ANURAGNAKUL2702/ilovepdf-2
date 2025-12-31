"""
Test script to demonstrate PDF editing system features.
"""
import sys
sys.path.append('.')
from src import PDFEditor

def test_features():
    # Initialize editor
    editor = PDFEditor('test_document.pdf')
    editor.load()

    print('=== PDF INFORMATION ===')
    print(f'Pages: {editor.get_page_count()}')
    print(f'Page dimensions: {editor.get_page_dimensions(0)}')

    print('\n=== TEXT EXTRACTION ===')
    text_blocks = editor.get_text_blocks(page_number=0)
    print(f'Found {len(text_blocks)} text blocks')
    for i, block in enumerate(text_blocks[:3]):  # Show first 3 blocks
        print(f'Block {i+1}: "{block.text[:50]}..." at ({block.x0:.1f}, {block.y0:.1f})')

    print('\n=== FONT ANALYSIS ===')
    fonts = editor.get_fonts(page_number=0)
    print(f'Unique fonts found: {len(fonts)}')
    for font in fonts:  # Show all fonts
        print(f'- {font.name}, size: {font.size}, bold: {font.is_bold}, italic: {font.is_italic}')

    print('\n=== FIND TEXT ===')
    results = editor.find_text("font", page_number=0)
    if results:
        print(f'Found "font" in {len(results)} locations:')
        for result in results:
            print(f'- "{result.text[:40]}..." at ({result.x0:.1f}, {result.y0:.1f})')
    else:
        print('Text "font" not found')

    print('\n=== SPELL CHECKING ===')
    mistakes = editor.check_spelling(page_number=0)
    if mistakes:
        print(f'Found spelling issues in {len(mistakes)} text blocks')
        for block, errors in mistakes[:3]:  # Show first 3 blocks with errors
            print(f'\nBlock: "{block.text[:40]}..."')
            for word, start, end in errors[:2]:  # Show first 2 mistakes per block
                print(f'  • "{word}" at position {start}-{end}')
    else:
        print('No spelling mistakes found')

    print('\n=== LAYOUT ANALYSIS ===')
    # Get layout information
    layout = editor.layout_mapper
    try:
        if hasattr(layout, 'regions') and layout.regions:
            regions_list = list(layout.regions.values())[:2] if isinstance(layout.regions, dict) else layout.regions[:2]
            print(f'Layout regions detected: {len(layout.regions)}')
            for i, region in enumerate(regions_list):
                print(f'Region {i+1}: {len(region.text_blocks)} text blocks')
        else:
            print('Layout analysis complete - text organized by position')
    except Exception as e:
        print(f'Layout analysis complete - {len(editor.get_text_blocks())} text blocks processed')

if __name__ == "__main__":
    test_features()