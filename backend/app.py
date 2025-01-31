from flask import Flask, request, send_file
from flask_cors import CORS  # Import CORS
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import os
import time
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clear_old_files(folder, age_limit=300):  # 300 seconds = 5 minutes
    current_time = time.time()
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > age_limit:
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route("/upload", methods=["POST"])
def upload_files():
    if "invoice" not in request.files or "packing_slip" not in request.files or "shipping_label" not in request.files:
        return {"error": "All three PDFs (invoice, packing slip, shipping label) are required!"}, 400
    
    clear_old_files(UPLOAD_FOLDER)
    clear_old_files(OUTPUT_FOLDER)
    
    # Generate unique filenames
    unique_id = str(uuid.uuid4())[:8]  # Short unique ID
    
    invoice = request.files["invoice"]
    packing_slip = request.files["packing_slip"]
    shipping_label = request.files["shipping_label"]

    invoice_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_invoice.pdf")
    packing_slip_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_packing_slip.pdf")
    shipping_label_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_shipping_label.pdf")

    invoice.save(invoice_path)
    packing_slip.save(packing_slip_path)
    shipping_label.save(shipping_label_path)

    output_pdf = os.path.join(OUTPUT_FOLDER, f"{unique_id}_merged_shipmerge.pdf")
    merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_pdf)

    # Delete uploaded files after merging
    os.remove(invoice_path)
    os.remove(packing_slip_path)
    os.remove(shipping_label_path)

    return send_file(output_pdf, as_attachment=True)

def merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_path):
    invoice_pdf = fitz.open(invoice_path)
    packing_slip_pdf = fitz.open(packing_slip_path)
    shipping_label_pdf = fitz.open(shipping_label_path)
    merged_pdf = fitz.open()

    width, height = 595, 842  # A4 Size
    quadrant_width, quadrant_height = width / 2, height / 2  # Divide into 4 equal quadrants

    for page_num in range(max(len(invoice_pdf), len(packing_slip_pdf), len(shipping_label_pdf))):
        page = merged_pdf.new_page(width=width, height=height)

        # Packing Slip - Top Left Quadrant
        if page_num < len(packing_slip_pdf):
            pix = packing_slip_pdf[page_num].get_pixmap(dpi=300, alpha=False)
            page.insert_image(fitz.Rect(0, 0, quadrant_width, quadrant_height), pixmap=pix)

        # Shipping Label - Top Right Quadrant
        if page_num < len(shipping_label_pdf):
            pix = shipping_label_pdf[page_num].get_pixmap(dpi=300, alpha=False)
            page.insert_image(fitz.Rect(quadrant_width, 0, width, quadrant_height), pixmap=pix)

        # Invoice - Rotate 90 degrees counterclockwise and Stretch Across Bottom Two Quadrants
        if page_num < len(invoice_pdf):
            matrix = fitz.Matrix(0, 1, -1, 0, width, 0)  # Rotate 90 degrees
            #rotated_pix = invoice_pdf[page_num].get_pixmap(matrix=matrix, dpi=300, alpha=False)
            rotated_pix = invoice_pdf[page_num].get_pixmap(matrix=matrix, alpha=False)
            # Insert into bottom two quadrants
            page.insert_image(fitz.Rect(0, quadrant_height, width, height), pixmap=rotated_pix)

    # Compress PDF without losing quality
    merged_pdf.save(output_path, garbage=4, deflate=True, clean=True)
    merged_pdf.close()
    invoice_pdf.close()
    packing_slip_pdf.close()
    shipping_label_pdf.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
