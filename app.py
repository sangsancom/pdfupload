from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 업로드 폴더 없으면 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf_to_png():
    if 'pdfFile' not in request.files:
        return "No file part", 400

    file = request.files['pdfFile']
    if file.filename == '':
        return "No selected file", 400

    # 업로드된 파일 저장
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 임시 디렉토리 사용 (자동 정리)
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, 'output.png')

            # PDF 열기 및 첫 페이지 PNG로 저장
            doc = fitz.open(filepath)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            pix.save(img_path)
            doc.close()

            # 파일 전송 (파일 사용 완료되면 자동 삭제됨)
            return send_file(img_path, mimetype='image/png', as_attachment=True, download_name='converted.png')

    finally:
        # 업로드된 PDF 삭제
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"PDF 삭제 실패: {e}")
