# Helper functions to write text onto PDFs
from fpdf import FPDF


def create_simple_pdf(lines):
    """Return PDF as bytes"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    for line in lines:
        pdf.cell(0, 10, line, ln=True)
    return pdf.output(dest='S')
