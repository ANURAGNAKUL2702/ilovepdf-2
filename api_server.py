"""
Flask API server for PDF Editor frontend integration.

This server bridges the frontend React app with the existing Python PDF editing system.
"""
import os
import json
import tempfile
import uuid
import fitz  # PyMuPDF
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pdf_editor import PDFEditor

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}

# Store active PDF editors
pdf_sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'PDF Editor API'})

@app.route('/api/pdf/upload', methods=['POST'])
def upload_pdf():
    """Upload a PDF file and initialize editor"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDFs allowed.'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        pdf_id = str(uuid.uuid4())
        filepath = os.path.join(UPLOAD_FOLDER, f"{pdf_id}_{filename}")
        file.save(filepath)

        # Initialize PDF editor
        editor = PDFEditor(filepath)
        editor.load()
        
        # Store the editor session
        pdf_sessions[pdf_id] = {
            'editor': editor,
            'filepath': filepath,
            'original_filename': filename
        }

        # Get basic metadata
        page_count = editor.get_page_count()
        dimensions = editor.get_page_dimensions(0) if page_count > 0 else (612, 792)

        return jsonify({
            'id': pdf_id,
            'metadata': {
                'pages': page_count,
                'width': dimensions[0],
                'height': dimensions[1],
                'filename': filename
            }
        })

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/text-blocks', methods=['GET'])
def get_text_blocks(pdf_id):
    """Get text blocks from a PDF page or all pages"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        editor = pdf_sessions[pdf_id]['editor']
        page_number = request.args.get('page', type=int)
        
        # Convert to frontend format (matching TextBlock interface)
        text_blocks = []
        
        if page_number is not None:
            # Get blocks for specific page
            blocks = editor.get_text_blocks(page_number)
            for i, block in enumerate(blocks):
                text_blocks.append({
                    'id': f"{pdf_id}-{page_number}-{i}",
                    'text': block.text,
                    'x0': block.x0,
                    'y0': block.y0,
                    'x1': block.x1,
                    'y1': block.y1,
                    'pageNumber': block.page_number,
                    'fontName': getattr(block, 'font_name', 'Helvetica'),
                    'fontSize': getattr(block, 'font_size', 12),
                    'fontFlags': getattr(block, 'font_flags', 0),
                    'color': getattr(block, 'color', '#000000'),
                    'lineNumber': getattr(block, 'line_number', 0),
                    'blockNumber': getattr(block, 'block_number', i)
                })
        else:
            # Get blocks from all pages
            page_count = editor.get_page_count()
            for page_num in range(page_count):
                blocks = editor.get_text_blocks(page_num)
                for i, block in enumerate(blocks):
                    text_blocks.append({
                        'id': f"{pdf_id}-{page_num}-{i}",
                        'text': block.text,
                        'x0': block.x0,
                        'y0': block.y0,
                        'x1': block.x1,
                        'y1': block.y1,
                        'pageNumber': block.page_number,
                        'fontName': getattr(block, 'font_name', 'Helvetica'),
                        'fontSize': getattr(block, 'font_size', 12),
                        'fontFlags': getattr(block, 'font_flags', 0),
                        'color': getattr(block, 'color', '#000000'),
                        'lineNumber': getattr(block, 'line_number', 0),
                        'blockNumber': getattr(block, 'block_number', i)
                    })

        return jsonify({'textBlocks': text_blocks})

    except Exception as e:
        return jsonify({'error': f'Failed to get text blocks: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/check-spelling', methods=['POST'])
def check_spelling(pdf_id):
    """Check spelling in PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        editor = pdf_sessions[pdf_id]['editor']
        page_number = request.json.get('page', None)
        
        mistakes = editor.check_spelling(page_number)
        
        spelling_errors = []
        for block, errors in mistakes:
            for word, start, end in errors:
                spelling_errors.append({
                    'word': word,
                    'start': start,
                    'end': end,
                    'block_text': block.text,
                    'x': block.x0,
                    'y': block.y0,
                    'page': block.page_number
                })

        return jsonify({'errors': spelling_errors})

    except Exception as e:
        return jsonify({'error': f'Spell check failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/replace-text', methods=['POST'])
def replace_text(pdf_id):
    """Replace text in PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        data = request.json
        block_id = data.get('blockId')
        new_text = data.get('newText')
        preserve_style = data.get('preserveStyle', True)

        if not block_id or new_text is None:
            return jsonify({'error': 'Block ID and new text required'}), 400

        # Parse block_id to get page and block index
        # Format: "{pdf_id}-{page_number}-{block_index}"
        parts = block_id.split('-')
        if len(parts) < 3:
            return jsonify({'error': 'Invalid block ID format'}), 400
        
        page_number = int(parts[-2])
        block_index = int(parts[-1])
        
        # Get the current block to find old text
        session = pdf_sessions[pdf_id]
        editor = session['editor']
        blocks = editor.get_text_blocks(page_number)
        
        if block_index >= len(blocks):
            return jsonify({'error': 'Block not found'}), 404
        
        old_block = blocks[block_index]
        old_text = old_block.text
        
        # Create a temporary output file
        temp_output = os.path.join(UPLOAD_FOLDER, f"temp_{pdf_id}.pdf")
        
        # Replace the text using the PDF editor
        editor.replace_text(
            output_path=temp_output,
            old_text=old_text,
            new_text=new_text,
            preserve_style=preserve_style
        )
        
        # Update the session with the new file
        if os.path.exists(temp_output):
            os.replace(temp_output, session['filepath'])
            # Reload the editor
            session['editor'] = PDFEditor(session['filepath'])
            session['editor'].load()
        
        return jsonify({'success': True, 'message': 'Text replaced successfully'})

    except Exception as e:
        return jsonify({'error': f'Text replacement failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/insert-text', methods=['POST'])
def insert_text(pdf_id):
    """Insert text into PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        data = request.json
        text = data.get('text')
        x = data.get('x')
        y = data.get('y')
        page_number = data.get('pageNumber', 0)
        options = data.get('options', {})
        font_size = options.get('fontSize', 12)
        font_name = options.get('fontName', 'Helvetica')

        if not text or x is None or y is None:
            return jsonify({'error': 'Text, x, and y coordinates required'}), 400

        # Create a temporary output file
        session = pdf_sessions[pdf_id]
        temp_output = os.path.join(UPLOAD_FOLDER, f"temp_{pdf_id}.pdf")
        
        # Use the PDFEditor to insert text
        editor = session['editor']
        editor.insert_text(
            output_path=temp_output,
            page_number=page_number,
            text=text,
            x=float(x),
            y=float(y),
            font_size=int(font_size)
        )
        
        # Update the session with the new file
        if os.path.exists(temp_output):
            os.replace(temp_output, session['filepath'])
            # Reload the editor
            session['editor'] = PDFEditor(session['filepath'])
            session['editor'].load()
        
        return jsonify({'success': True, 'message': 'Text inserted successfully'})

    except Exception as e:
        return jsonify({'error': f'Text insertion failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/find-text', methods=['POST'])
def find_text(pdf_id):
    """Find text in PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        data = request.json
        search_text = data.get('searchText')
        page_number = data.get('page')

        if not search_text:
            return jsonify({'error': 'Search text required'}), 400

        editor = pdf_sessions[pdf_id]['editor']
        results = editor.find_text(search_text, page_number)

        matches = []
        for i, block in enumerate(results):
            matches.append({
                'id': f"match-{i}",
                'text': block.text,
                'x': block.x0,
                'y': block.y0,
                'page': block.page_number,
                'highlight': search_text
            })

        return jsonify({'matches': matches})

    except Exception as e:
        return jsonify({'error': f'Text search failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/download', methods=['GET'])
def download_pdf(pdf_id):
    """Download the current PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        session = pdf_sessions[pdf_id]
        return send_file(
            session['filepath'],
            as_attachment=True,
            download_name=f"edited_{session['original_filename']}"
        )

    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/export', methods=['GET'])
def export_pdf(pdf_id):
    """Export the current PDF (alias for download for frontend compatibility)"""
    return download_pdf(pdf_id)

@app.route('/api/pdf/<pdf_id>/page/<int:page_number>/rotate', methods=['POST'])
def rotate_page(pdf_id, page_number):
    """Rotate a PDF page"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        data = request.json
        rotation = data.get('rotation', 90)
        
        # Normalize rotation to positive values (0, 90, 180, 270)
        rotation = rotation % 360
        if rotation not in [0, 90, 180, 270]:
            return jsonify({'error': 'Rotation must be 90, 180, or 270 degrees'}), 400

        session = pdf_sessions[pdf_id]
        
        # Open the PDF
        doc = fitz.open(session['filepath'])
        
        # Rotate the specified page (0-indexed)
        if 0 <= page_number < len(doc):
            page = doc[page_number]
            page.set_rotation(rotation)
            
            # Save the modified PDF
            temp_output = os.path.join(UPLOAD_FOLDER, f"temp_rotated_{pdf_id}.pdf")
            doc.save(temp_output)
            doc.close()
            
            # Update the session with the new file
            if os.path.exists(temp_output):
                os.replace(temp_output, session['filepath'])
                # Reload the editor
                session['editor'] = PDFEditor(session['filepath'])
                session['editor'].load()
            
            return jsonify({'success': True, 'message': f'Page {page_number} rotated by {rotation} degrees'})
        else:
            doc.close()
            return jsonify({'error': 'Page number out of range'}), 400

    except Exception as e:
        return jsonify({'error': f'Page rotation failed: {str(e)}'}), 500

@app.route('/api/pdf/<pdf_id>/fonts', methods=['GET'])
def get_fonts(pdf_id):
    """Get fonts used in PDF"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        editor = pdf_sessions[pdf_id]['editor']
        page_number = request.args.get('page', 0, type=int)
        
        fonts = editor.get_fonts(page_number)
        
        font_list = []
        for font in fonts:
            font_list.append({
                'name': font.name,
                'size': font.size,
                'is_bold': font.is_bold,
                'is_italic': font.is_italic,
                'color': font.color
            })

        return jsonify({'fonts': font_list})

    except Exception as e:
        return jsonify({'error': f'Font retrieval failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting PDF Editor API server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=8000)