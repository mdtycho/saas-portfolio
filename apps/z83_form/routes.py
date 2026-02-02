from flask import Blueprint, render_template, request, send_file
from fpdf import FPDF
from pathlib import Path

# Define the Blueprint.
# strictly separates templates/static so App #1 doesn't break App #2
z83_bp = Blueprint('z83', __name__, 
                   template_folder='templates',
                   static_folder='static')

@z83_bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 1. Get data from the HTML form
        surname = request.form.get('surname')
        id_number = request.form.get('id_number')
        
        # 2. Process the PDF (Stateless!)
        # We will move this logic to /common/pdf_utils.py later
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Z83 Application for: {surname}", ln=1, align='C')
        pdf.cell(200, 10, txt=f"ID: {id_number}", ln=1, align='C')
        
        # 3. Save to a temporary folder and return
        p=Path(f"/tmp/{surname}_z83.pdf") 
        p.parent.mkdir(parents=True, exist_ok=True)
        output_filename = f"/tmp/{surname}_z83.pdf"
        pdf.output(output_filename)
        
        return send_file(output_filename, as_attachment=True)

    return render_template('form.html')