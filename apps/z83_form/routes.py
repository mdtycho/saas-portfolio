# The logic: Input -> Process -> PDF
from flask import render_template, request, send_file
from . import z83_bp
from fpdf import FPDF
import io


@z83_bp.route('/', methods=['GET'])
def form():
    return render_template('form.html')


@z83_bp.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', 'No name provided')

    # Simple PDF generation using fpdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, f'Z83 Form for: {name}', ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='z83_form.pdf', mimetype='application/pdf')
