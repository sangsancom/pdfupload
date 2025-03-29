from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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

    # 이미지 임시 파일 생성 (삭제 예약하지 않음)
    tmp_png = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img_path = tmp_png.name
    tmp_png.close()  # Windows에서는 사용 중 에러 방지를 위해 반드시 닫아야 함

    try:
        # PDF → PNG 변환
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        pix.save(img_path)
        doc.close()

        # 변환된 이미지 전송
        return send_file(img_path, mimetype='image/png', as_attachment=True, download_name='converted.png')

    except Exception as e:
        print("❌ 변환 중 오류:", e)
        return f"서버 오류: {str(e)}", 500

    finally:
        # PDF 삭제
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            print(f"⚠️ PDF 삭제 실패: {e}")
        
        # PNG 삭제는 요청 후 일정 지연시간 뒤 별도로 하는 것이 안전하지만
        # 여기선 테스트용이므로 안 지움. 실제 서비스에선 비동기로 지워야 안전

if __name__ == '__main__':
    app.run(debug=True)
