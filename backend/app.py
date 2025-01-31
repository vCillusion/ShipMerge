from flask import Flask, request, send_file
from flask_cors import CORS  # Import CORS
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_files():
    if "invoice" not in request.files or "packing_slip" not in request.files or "shipping_label" not in request.files:
        return {"error": "All three PDFs (invoice, packing slip, shipping label) are required!"}, 400
    
    invoice = request.files["invoice"]
    packing_slip = request.files["packing_slip"]
    shipping_label = request.files["shipping_label"]

    invoice_path = os.path.join(UPLOAD_FOLDER, secure_filename(invoice.filename))
    packing_slip_path = os.path.join(UPLOAD_FOLDER, secure_filename(packing_slip.filename))
    shipping_label_path = os.path.join(UPLOAD_FOLDER, secure_filename(shipping_label.filename))

    invoice.save(invoice_path)
    packing_slip.save(packing_slip_path)
    shipping_label.save(shipping_label_path)

    output_pdf = os.path.join(OUTPUT_FOLDER, "merged_shipmerge.pdf")
    merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_pdf)

    return send_file(output_pdf, as_attachment=True)

def merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_path):
    invoice_pdf = fitz.open(invoice_path)
    packing_slip_pdf = fitz.open(packing_slip_path)
    shipping_label_pdf = fitz.open(shipping_label_path)
    merged_pdf = fitz.open()

    for page_num in range(min(len(invoice_pdf), len(packing_slip_pdf), len(shipping_label_pdf))):
        page = merged_pdf.new_page(width=595, height=842)
        
        # Fix: Use filename argument instead of Pixmap
        page.insert_image(fitz.Rect(0, 0, 595, 421), invoice_pdf[page_num].get_pixmap())
        page.insert_image(fitz.Rect(0, 421, 595, 842), packing_slip_pdf[page_num].get_pixmap())

        # If Shipping Label contains 2 pages (Label & Invoice)
        if len(shipping_label_pdf) > 1:
            shipping_label_page1 = shipping_label_pdf[0]  # First page (Shipping Label)
            shipping_label_page2 = shipping_label_pdf[1]  # Second page (Invoice)

            new_page = merged_pdf.new_page(width=595, height=842)
            new_page.insert_image(fitz.Rect(0, 0, 595, 421), filename=shipping_label_page1)
            new_page.insert_image(fitz.Rect(0, 421, 595, 842), filename=shipping_label_page2)
        else:
            new_page = merged_pdf.new_page(width=595, height=842)
            new_page.insert_image(fitz.Rect(0, 421, 595, 842), filename=shipping_label_path)


    merged_pdf.save(output_path)
    merged_pdf.close()
    invoice_pdf.close()
    packing_slip_pdf.close()
    shipping_label_pdf.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
