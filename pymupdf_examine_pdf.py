import fitz # PyMuPDF

doc = fitz.open("apps/z83_form/static/editable_Z83.pdf")

for page in doc:
    widgets = page.widgets()
    for widget in widgets:
        with open("pdf_form_fields.txt", "a") as f:
            f.write(f"Field Name: {widget.field_name}\n")
            f.write(f"Field Value: {widget.field_value}\n")
            f.write(f"Widget Type: {widget.field_type_string}\n")
            f.write("-" * 20 + "\n")