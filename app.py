from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdfFile' not in request.files:
        return "No file uploaded", 400

    file = request.files['pdfFile']
    if file.filename == '':
        return "Empty filename", 400

    try:
        # 임시 PDF 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            file.save(tmp_pdf)
            tmp_pdf_path = tmp_pdf.name

        # 임시 PNG 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_png:
            tmp_png_path = tmp_png.name

        # PDF → PNG 변환
        doc = fitz.open(tmp_pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        pix.save(tmp_png_path)
        doc.close()

        return send_file(tmp_png_path, mimetype='image/png', as_attachment=True, download_name='converted.png')

    except Exception as e:
        print("❌ 변환 중 오류:", e)
        return "변환 실패", 500

    finally:
        try:
            if os.path.exists(tmp_pdf_path):
                os.remove(tmp_pdf_path)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True)
