"""
Command-line interface for PDF editing system.

This script provides a CLI for common PDF editing operations.
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import PDFEditor


def check_spelling(args):
    """Check spelling in a PDF."""
    editor = PDFEditor(args.input, args.dictionary)
    editor.load()
    
    results = editor.check_spelling(args.page)
    
    if not results:
        print("No spelling mistakes found.")
        return
    
    print(f"Found spelling mistakes in {len(results)} text blocks:\n")
    for block, mistakes in results:
        print(f"Page {block.page_number + 1}, Position ({block.x0:.1f}, {block.y0:.1f}):")
        print(f"  Text: {block.text[:50]}...")
        for word, start, end in mistakes:
            suggestions = editor.get_spelling_suggestions(word, 3)
            print(f"    - '{word}' (position {start}-{end})")
            if suggestions:
                print(f"      Suggestions: {', '.join(suggestions)}")
        print()


def correct_spelling(args):
    """Correct spelling in a PDF."""
    editor = PDFEditor(args.input, args.dictionary)
    
    print(f"Correcting spelling in '{args.input}'...")
    count = editor.correct_spelling(args.output, args.page)
    print(f"Made {count} corrections. Saved to '{args.output}'")


def insert_text(args):
    """Insert text into a PDF."""
    editor = PDFEditor(args.input)
    
    success = editor.insert_text(
        args.output,
        args.page,
        args.text,
        args.x,
        args.y,
        font_size=args.font_size,
        font_name=args.font_name
    )
    
    if success:
        print(f"Text inserted successfully. Saved to '{args.output}'")
    else:
        print("Failed to insert text.", file=sys.stderr)
        sys.exit(1)


def replace_text(args):
    """Replace text in a PDF."""
    editor = PDFEditor(args.input)
    
    count = editor.replace_text(
        args.output,
        args.old,
        args.new,
        page_number=args.page,
        preserve_style=not args.no_preserve_style
    )
    
    print(f"Replaced {count} occurrences. Saved to '{args.output}'")


def extract_text(args):
    """Extract text from a PDF."""
    editor = PDFEditor(args.input)
    
    text = editor.extract_text(args.page)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text extracted to '{args.output}'")
    else:
        print(text)


def find_text(args):
    """Find text in a PDF."""
    editor = PDFEditor(args.input)
    editor.load()
    
    blocks = editor.find_text(args.search, args.page)
    
    if not blocks:
        print(f"No matches found for '{args.search}'")
        return
    
    print(f"Found {len(blocks)} matches:\n")
    for block in blocks:
        print(f"Page {block.page_number + 1}, Position ({block.x0:.1f}, {block.y0:.1f}):")
        print(f"  {block.text}\n")


def info(args):
    """Display PDF information."""
    editor = PDFEditor(args.input)
    
    page_count = editor.get_page_count()
    print(f"PDF: {args.input}")
    print(f"Pages: {page_count}\n")
    
    if args.fonts:
        fonts = editor.get_fonts()
        print(f"Unique Fonts ({len(fonts)}):")
        for font in fonts:
            style = []
            if font.is_bold:
                style.append("Bold")
            if font.is_italic:
                style.append("Italic")
            style_str = ", ".join(style) if style else "Regular"
            print(f"  - {font.name} ({font.size:.1f}pt, {style_str})")
    
    if args.page is not None:
        width, height = editor.get_page_dimensions(args.page)
        print(f"\nPage {args.page + 1} dimensions: {width:.1f} x {height:.1f} points")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PDF Editing System - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check spelling command
    check_parser = subparsers.add_parser('check', help='Check spelling in PDF')
    check_parser.add_argument('input', help='Input PDF file')
    check_parser.add_argument('-p', '--page', type=int, help='Specific page number (1-indexed)')
    check_parser.add_argument('-d', '--dictionary', nargs='+', help='Custom dictionary words')
    check_parser.set_defaults(func=check_spelling)
    
    # Correct spelling command
    correct_parser = subparsers.add_parser('correct', help='Correct spelling in PDF')
    correct_parser.add_argument('input', help='Input PDF file')
    correct_parser.add_argument('output', help='Output PDF file')
    correct_parser.add_argument('-p', '--page', type=int, help='Specific page number (1-indexed)')
    correct_parser.add_argument('-d', '--dictionary', nargs='+', help='Custom dictionary words')
    correct_parser.set_defaults(func=correct_spelling)
    
    # Insert text command
    insert_parser = subparsers.add_parser('insert', help='Insert text into PDF')
    insert_parser.add_argument('input', help='Input PDF file')
    insert_parser.add_argument('output', help='Output PDF file')
    insert_parser.add_argument('text', help='Text to insert')
    insert_parser.add_argument('page', type=int, help='Page number (1-indexed)')
    insert_parser.add_argument('x', type=float, help='X coordinate')
    insert_parser.add_argument('y', type=float, help='Y coordinate')
    insert_parser.add_argument('--font-size', type=float, help='Font size')
    insert_parser.add_argument('--font-name', help='Font name (helv, times, cour)')
    insert_parser.set_defaults(func=insert_text)
    
    # Replace text command
    replace_parser = subparsers.add_parser('replace', help='Replace text in PDF')
    replace_parser.add_argument('input', help='Input PDF file')
    replace_parser.add_argument('output', help='Output PDF file')
    replace_parser.add_argument('old', help='Text to replace')
    replace_parser.add_argument('new', help='Replacement text')
    replace_parser.add_argument('-p', '--page', type=int, help='Specific page number (1-indexed)')
    replace_parser.add_argument('--no-preserve-style', action='store_true', 
                               help='Do not preserve original text style')
    replace_parser.set_defaults(func=replace_text)
    
    # Extract text command
    extract_parser = subparsers.add_parser('extract', help='Extract text from PDF')
    extract_parser.add_argument('input', help='Input PDF file')
    extract_parser.add_argument('-o', '--output', help='Output text file (prints to stdout if not specified)')
    extract_parser.add_argument('-p', '--page', type=int, help='Specific page number (1-indexed)')
    extract_parser.set_defaults(func=extract_text)
    
    # Find text command
    find_parser = subparsers.add_parser('find', help='Find text in PDF')
    find_parser.add_argument('input', help='Input PDF file')
    find_parser.add_argument('search', help='Text to search for')
    find_parser.add_argument('-p', '--page', type=int, help='Specific page number (1-indexed)')
    find_parser.set_defaults(func=find_text)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display PDF information')
    info_parser.add_argument('input', help='Input PDF file')
    info_parser.add_argument('-p', '--page', type=int, help='Specific page for detailed info (1-indexed)')
    info_parser.add_argument('--fonts', action='store_true', help='Show font information')
    info_parser.set_defaults(func=info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Convert 1-indexed page numbers to 0-indexed
    if hasattr(args, 'page') and args.page is not None:
        args.page = args.page - 1
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()