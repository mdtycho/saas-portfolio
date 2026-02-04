from PyPDF2 import PdfReader
import os

# Point this to your downloaded Z83
pdf_path = 'apps/z83_form/static/editable_z83.pdf'

try:
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    if fields:
        print("✅ SUCCESS: This is a Smart PDF!")
        print(f"Found {len(fields)} fields. Here are the first 5 keys:")
        for i, key in enumerate(fields.keys()):
            if i >= 5: break
            print(f" - {key}")
    else:
        print("❌ FAIL: This is a Dumb PDF (No embedded fields found).")
        print("We must use the X/Y coordinate method.")
        
except Exception as e:
    print(f"Error reading PDF: {e}")