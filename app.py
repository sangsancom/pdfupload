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
    return render_template('index.html')  # templates/index.html 필요!

@app.route('/convert', methods=['POST'])
def convert_pdf_to_png():
    if 'pdfFile' not in request.files:
        return "No file part", 400

    file = request.files['pdfFile']
    if file.filename == '':
        return "No selected file", 400

    # 파일 저장
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    tmp_path = None

    try:
        # PDF → PNG 변환
        doc = fitz.open(filepath)
        page = doc.load_page(0)  # 첫 페이지
        pix = page.get_pixmap(dpi=150)

        # 임시 PNG 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            pix.save(tmp_path)

        doc.close()  # 반드시 닫기

        return send_file(tmp_path, mimetype='image/png', as_attachment=True, download_name='converted.png')

    finally:
        # PDF 파일 삭제 (닫힌 후!)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"PDF 삭제 실패: {e}")

if __name__ == '__main__':
    app.run(debug=True)
