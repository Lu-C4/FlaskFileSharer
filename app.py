from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, session
import os
import random
import string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ಓಂ ನಮ ಶಿವಾಯ'

BASE_UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

def generate_unique_code():
    """Generate a random unique code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def transfer():
    """Render the file transfer page with a new session code each time."""
    session['session_code'] = generate_unique_code()  # Regenerate on each reload
    return render_template('transfer.html', session_code=session['session_code'])

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    if 'file' not in request.files:
        return render_template('transfer.html', error='No file part')

    files = request.files.getlist('file')
    if not files or all(file.filename == '' for file in files):
        return render_template('transfer.html', error='No selected file')

    # Get the session code from the session object
    session_code = session.get('session_code')
    if not session_code:
        return jsonify({'   error': 'Session code not found'}), 400

    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_code)
    os.makedirs(session_folder, exist_ok=True)

    for file in files:
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(session_folder, filename))

    return jsonify({'message': 'Files uploaded successfully', 'code': session_code})

@app.route('/receive/<code>', methods=['GET'])
def receive_files(code):
    """Redirect to files page based on the code."""
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], code)
    if not os.path.exists(session_folder):
        return jsonify({'error': 'Invalid code or no files found'}), 404

    return redirect(url_for('files_page', code=code))

@app.route('/files/<code>', methods=['GET'])
def files_page(code):
    """Display the files uploaded in the folder."""
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], code)
    if not os.path.exists(session_folder):
        return jsonify({'error': 'Invalid code or no files found'}), 404

    files = os.listdir(session_folder)
    return render_template('files.html', code=code, files=files)

@app.route('/download/<code>/<filename>')
def download_file(code, filename):
    """Download a specific file."""
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], code)
    return send_from_directory(session_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
