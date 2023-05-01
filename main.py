from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from ai_function.pdf_gpt import process_pdf, get_answer
from pathlib import Path

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

uploaded_file_path = None

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global uploaded_file_path
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return jsonify({"status": "success", "message": "File uploaded successfully"})
    return jsonify({"status": "error", "message": "Invalid file type"}), 400

@app.route("/get_answer", methods=["POST"])
def get_answer_route():
    global uploaded_file_path
    if not uploaded_file_path:
        return jsonify({"status": "error", "message": "No PDF file uploaded"}), 400

    openai_api_key = request.json['openai_api_key']
    docsearch = process_pdf(uploaded_file_path, openai_api_key)
    question = request.json['question']
    result = get_answer(docsearch, question, openai_api_key)
    return jsonify({"answer": result})

if __name__ == "__main__":
    app.run(debug=True)
