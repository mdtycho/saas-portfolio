from fillpdf import fillpdfs

fields = fillpdfs.get_form_fields("apps/z83_form/static/editable_Z83.pdf")

with open("digdeeper2.txt", "w") as f:
    f.write("Fields recognized by fillpdfs:\n")
    for field in fields:
        f.write(field + "\n")