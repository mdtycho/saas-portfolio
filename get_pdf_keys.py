from PyPDF2 import PdfReader

# Point this to your smart Z83
reader = PdfReader("apps/z83_form/static/editable_z83.pdf")
fields = reader.get_fields()

with open("pdf_fields.txt", "w") as f:
    f.write("-" * 30 + '\n')
    f.write("COPY THESE EXACT KEYS INTO YOUR CODE:" + '\n')
    f.write("-" * 30 + '\n')

    for key, value in fields.items():
        # We f.write the key and a hint about what it might be
        f.write(f"Key: '{key}'" + '\n')

    f.write("-" * 30)