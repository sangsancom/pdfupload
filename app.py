from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # templates 폴더 필요!

@app.route('/convert', methods=['POST'])
def convert_pdf_to_png():
    if 'pdfFile' not in request.files:
        return "No file part", 400

    file = request.files['pdfFile']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # PDF → 이미지 변환 (첫 페이지만 PNG로 저장)
        doc = fitz.open(filepath)
        page = doc.load_page(0)  # 첫 페이지
        pix = page.get_pixmap(dpi=150)  # 해상도 설정

        # 임시 PNG 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            pix.save(tmp.name)
            return send_file(tmp.name, mimetype='image/png', as_attachment=True, download_name='converted.png')
    finally:
        # 원본 PDF 정리
        os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
