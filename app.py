from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 업로드 폴더 생성 (없으면)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html 필요

@app.route('/convert', methods=['POST'])
def convert_pdf_to_png():
    if 'pdfFile' not in request.files:
        return "PDF 파일이 전송되지 않았습니다.", 400

    file = request.files['pdfFile']
    if file.filename == '':
        return "파일이 선택되지 않았습니다.", 400

    # PDF 저장 경로 생성
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # 출력 이미지 경로
            img_path = os.path.join(tmpdir, 'converted.png')

            # PDF → PNG 변환 (첫 페이지)
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            pix.save(img_path)
            doc.close()

            # 변환된 파일 전송
            return send_file(img_path, mimetype='image/png', as_attachment=True, download_name='converted.png')

    except Exception as e:
        print("❌ 변환 중 오류:", e)
        return f"서버 오류: {str(e)}", 500

    finally:
        # 업로드된 원본 PDF 삭제
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            print(f"⚠️ PDF 삭제 실패: {e}")

if __name__ == '__main__':
    app.run(debug=True)
