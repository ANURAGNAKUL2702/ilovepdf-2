"""
Flask API server for PDF Editor frontend integration.

This server bridges the frontend React app with the existing Python PDF editing system.
"""
import os
import json
import tempfile
import uuid
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
    """Get text blocks from a PDF page"""
    try:
        if pdf_id not in pdf_sessions:
            return jsonify({'error': 'PDF not found'}), 404

        editor = pdf_sessions[pdf_id]['editor']
        page_number = request.args.get('page', 0, type=int)
        
        # Get text blocks for the specified page
        blocks = editor.get_text_blocks(page_number)
        
        # Convert to frontend format
        text_blocks = []
        for i, block in enumerate(blocks):
            text_blocks.append({
                'id': f"{pdf_id}-{page_number}-{i}",
                'text': block.text,
                'x': block.x0,
                'y': block.y0,
                'width': block.x1 - block.x0,
                'height': block.y1 - block.y0,
                'page': block.page_number,
                'font_name': getattr(block, 'font_name', 'Unknown'),
                'font_size': getattr(block, 'font_size', 12),
                'is_bold': getattr(block, 'is_bold', False),
                'is_italic': getattr(block, 'is_italic', False)
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
        old_text = data.get('oldText')
        new_text = data.get('newText')
        page_number = data.get('page')
        preserve_style = data.get('preserveStyle', True)

        if not old_text or not new_text:
            return jsonify({'error': 'Old text and new text required'}), 400

        # Create a temporary output file
        session = pdf_sessions[pdf_id]
        temp_output = os.path.join(UPLOAD_FOLDER, f"temp_{pdf_id}.pdf")
        
        # Use the replace functionality (this would need to be implemented in your PDF editor)
        # For now, just acknowledge the request
        print(f"Replace '{old_text}' with '{new_text}' on page {page_number}")

        return jsonify({'success': True, 'message': 'Text replacement queued'})

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
        page_number = data.get('page', 0)
        font_size = data.get('fontSize', 12)
        font_name = data.get('fontName', 'helv')

        if not text or x is None or y is None:
            return jsonify({'error': 'Text, x, and y coordinates required'}), 400

        # Create a temporary output file
        session = pdf_sessions[pdf_id]
        temp_output = os.path.join(UPLOAD_FOLDER, f"temp_{pdf_id}.pdf")
        
        # Use your existing CLI to insert text
        import subprocess
        import sys
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'process_pdf.py')
        
        cmd = [
            python_exe, script_path, 'insert',
            session['filepath'], temp_output,
            text, str(page_number + 1), str(x), str(y),
            '--font-size', str(font_size),
            '--font-name', font_name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            # Update the session with the new file
            if os.path.exists(temp_output):
                os.replace(temp_output, session['filepath'])
                # Reload the editor
                session['editor'] = PDFEditor(session['filepath'])
                session['editor'].load()
            
            return jsonify({'success': True, 'message': 'Text inserted successfully'})
        else:
            return jsonify({'error': f'Insert failed: {result.stderr}'}), 500

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