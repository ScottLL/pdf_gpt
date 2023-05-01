from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
from ai_function.pdf_gpt import process_pdf, get_answer
import os
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from ai_function.pic_gpt import generate_image, get_prediction
from flask import jsonify
from flask import send_from_directory
import base64
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['uploaded_file'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({"error": "Invalid file type"}), 400
    return render_template("index.html")

@app.route("/pdf", methods=["POST"])
def pdf():
    if 'uploaded_file' not in session:
        return jsonify({"error": "No file uploaded"}), 400
    uploaded_file = session['uploaded_file']
    openai_api_key = OPENAI_API_KEY
    docsearch = process_pdf(uploaded_file, openai_api_key)
    question = request.form['question']
    result = get_answer(docsearch, question, openai_api_key)
    return jsonify({"answer": result})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
@app.route("/generate", methods=["POST"])
def generate():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    if file:
        input_image = Image.open(file)
        ai_image = generate_image(input_image)
        ai_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ai_image.jpg')  # Change the file extension to .jpg
        ai_image.save(ai_image_path)
        with open(ai_image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")
        return jsonify({"img_data": img_data})
    return redirect(url_for('index'))




@app.route("/recognize", methods=["POST"])
def recognize():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    if file:
        uploaded_array = np.array(Image.open(file).convert("RGB"))
        prediction, probability = get_prediction(uploaded_array)
        return jsonify({"prediction": prediction, "probability": probability})
    else:
        return jsonify({"error": "No file selected"}), 400





if __name__ == "__main__":
    app.run(debug=True)
