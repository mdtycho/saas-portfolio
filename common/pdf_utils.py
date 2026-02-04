import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class SAASPDFHelper:

    original_pdf_path: str
    data_dict: dict

    def __init__(self, original_pdf_path: str, data_dict: dict):
        self.original_pdf_path = original_pdf_path
        self.data_dict = data_dict

    def fill_coordinates_pdf(self) -> io.BytesIO:
        """
        Overlays text onto an existing PDF using x, y coordinates.
        text_data: dict with format { (page_index, x, y): "Text to write" }
        """
        # 1. Create a "Watermark" PDF with the text
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        for (page_idx, x, y), text in self.data_dict.items():
            # In a real app, we would check page_idx to switch pages on the canvas
            # For now, we assume single-page or apply to all for simplicity
            can.drawString(x, y, str(text))
            
        can.save()
        packet.seek(0)
        
        # 2. Merge Watermark with Original
        watermark_pdf = PdfReader(packet)
        original_pdf = PdfReader(self.original_pdf_path)
        output = PdfWriter()

        # Loop through pages (Z83 has multiple pages)
        for i in range(len(original_pdf.pages)):
            page = original_pdf.pages[i]
            
            # If we have a watermark layer for this page, merge it
            # (Simplified: currently merging the same text layer on Page 1)
            if i == 0: 
                page.merge_page(watermark_pdf.pages[0])
                
            output.add_page(page)

        # 3. Save to memory buffer
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        
        return output_stream

    def fill_smart_pdf(self) -> io.BytesIO:
        """
        Fills a 'Smart' PDF (AcroForm) using a dictionary.
        data_dict format: { "Internal_PDF_Key": "Value to write" }
        """
        reader = PdfReader(self.original_pdf_path)
        writer = PdfWriter()

        # Copy all pages from the original
        for page in reader.pages:
            writer.add_page(page)

        # Inject the data into the fields
        # We assume the fields are on Page 1 (index 0)
        # If the Z83 has fields on other pages, you might need to loop this.
        writer.update_page_form_field_values(
            writer.pages[0], 
            self.data_dict
        )

        # Save to memory
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        return output_stream