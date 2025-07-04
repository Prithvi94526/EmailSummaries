from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import sys

# Add the current directory to Python path to import EmailSummaries
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your EmailSummaries module
try:
    from EmailSummaries import EmailSummarizer  # Adjust import based on your actual class/function names
except ImportError:
    print("Warning: Could not import EmailSummaries module")
    EmailSummarizer = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'email-file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['email-file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the file with your EmailSummaries code
            if EmailSummarizer:
                # Adjust this based on your actual EmailSummaries implementation
                summarizer = EmailSummarizer()
                summaries = summarizer.process_file(filepath)  # Adjust method name as needed
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'summaries': summaries
                })
            else:
                return jsonify({
                    'success': True,
                    'summaries': ['EmailSummaries module not available. Please check your implementation.']
                })
                
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 