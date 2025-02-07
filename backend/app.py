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

def clear_old_files(folder, age_limit=10):  # 300 seconds = 5 minutes
    current_time = time.time()
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path) and (current_time - os.path.getmtime(file_path)) > age_limit:
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route("/preview", methods=["POST"])
def preview_files():
    if "invoice" not in request.files or "packing_slip" not in request.files or "shipping_label" not in request.files:
        return {"error": "All three PDFs (invoice, packing_slip, shipping_label) are required!"}, 400
    
    rotate_label = request.form.get("rotate_label", "portrait")
    rotate_angle = 90 if rotate_label == "landscape" else 0
    trim_percentage = int(request.form.get("trim_percentage", 100))
    
    clear_old_files(UPLOAD_FOLDER)
    clear_old_files(OUTPUT_FOLDER)
    
    unique_id = str(uuid.uuid4())[:8]
    
    invoice = request.files["invoice"]
    packing_slip = request.files["packing_slip"]
    shipping_label = request.files["shipping_label"]

    invoice_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_invoice.pdf")
    packing_slip_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_packing_slip.pdf")
    shipping_label_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_shipping_label.pdf")

    invoice.save(invoice_path)
    packing_slip.save(packing_slip_path)
    shipping_label.save(shipping_label_path)

    output_pdf = os.path.join(OUTPUT_FOLDER, f"{unique_id}_preview.pdf")
    merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_pdf, rotate_angle, trim_percentage)
    
    return send_file(output_pdf, as_attachment=False, mimetype='application/pdf')

@app.route("/upload", methods=["POST"])
def upload_files():
    if "invoice" not in request.files or "packing_slip" not in request.files or "shipping_label" not in request.files:
        return {"error": "All three PDFs (invoice, packing_slip, shipping_label) are required!"}, 400

    rotate_label = request.form.get("rotate_label", "portrait")  
    rotate_angle = 90 if rotate_label == "landscape" else 0  
    trim_percentage = int(request.form.get("trim_percentage", 100))  

    clear_old_files(UPLOAD_FOLDER)
    clear_old_files(OUTPUT_FOLDER)

    unique_id = str(uuid.uuid4())[:8]  

    invoice = request.files["invoice"]
    packing_slip = request.files["packing_slip"]
    shipping_label = request.files["shipping_label"]

    invoice_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_invoice.pdf")
    packing_slip_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_packing_slip.pdf")
    shipping_label_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_shipping_label.pdf")

    invoice.save(invoice_path)
    packing_slip.save(packing_slip_path)
    shipping_label.save(shipping_label_path)

    # ✅ Validate if uploaded files are proper PDFs
    for file_path in [invoice_path, packing_slip_path, shipping_label_path]:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return {"error": f"File {file_path} is missing or empty."}, 400

        try:
            with fitz.open(file_path) as test_pdf:
                if test_pdf.is_closed or len(test_pdf) == 0:
                    return {"error": f"File {file_path} is not a valid PDF."}, 400
        except Exception as e:
            return {"error": f"Failed to open {file_path} as PDF: {str(e)}"}, 400

    output_pdf = os.path.join(OUTPUT_FOLDER, f"{unique_id}_merged_shipmerge.pdf")
    merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_pdf, rotate_angle, trim_percentage)

    os.remove(invoice_path)
    os.remove(packing_slip_path)
    os.remove(shipping_label_path)

    return send_file(output_pdf, as_attachment=True, mimetype='application/pdf')

def merge_pdfs(invoice_path, packing_slip_path, shipping_label_path, output_path, rotate_angle, trim_percentage):
    invoice_pdf = fitz.open(invoice_path, filetype="pdf")
    packing_slip_pdf = fitz.open(packing_slip_path, filetype="pdf")
    shipping_label_pdf = fitz.open(shipping_label_path, filetype="pdf")
    merged_pdf = fitz.open()

    width, height = 595, 842  # A4 Size
    quadrant_width, quadrant_height = width / 2, height / 2  # Divide into 4 equal quadrants

    for i in range(max(len(invoice_pdf), len(packing_slip_pdf), len(shipping_label_pdf))):
        page = merged_pdf.new_page(width=width, height=height)
        mirror = i % 2 == 1  # Mirror every alternate page

        # Packing Slip - Top Left Quadrant
        if len(packing_slip_pdf) > i:
            pix = packing_slip_pdf[i].get_pixmap(dpi=300, alpha=False)
            page.insert_image(fitz.Rect(quadrant_width if mirror else 0, 0, width if mirror else quadrant_width, quadrant_height), pixmap=pix)

        # Shipping Label - Top Right Quadrant with Rotation and Trim
        if len(shipping_label_pdf) > i:
            page_rect = shipping_label_pdf[i].rect
            trimmed_width = int(page_rect.width * (trim_percentage / 100))
            trim_rect = fitz.Rect(0, 0, trimmed_width, page_rect.height)
            
            if rotate_angle:
                shipping_label_pdf[i].set_rotation(rotate_angle)

            label_pix = shipping_label_pdf[i].get_pixmap(matrix=fitz.Matrix(1, 1), clip=trim_rect, dpi=300, alpha=False)
            
            page.insert_image(fitz.Rect(0 if mirror else quadrant_width, 0, quadrant_width if mirror else width, quadrant_height), pixmap=label_pix)

        # Invoice - Stretch Across Bottom Two Quadrants
        if len(invoice_pdf) > i:
            invoice_pdf[i].set_rotation(90 if mirror else -90)
            high_res_pix = invoice_pdf[i].get_pixmap(dpi=300, alpha=False)  # Get high-quality image first
            page.insert_image(fitz.Rect(0, quadrant_height, width, height), pixmap=high_res_pix)

    # Compress PDF without losing quality
    merged_pdf.save(output_path, garbage=4, deflate=True, clean=True)
    merged_pdf.close()
    invoice_pdf.close()
    packing_slip_pdf.close()
    shipping_label_pdf.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
