from flask import Blueprint, render_template, request, send_file, redirect, url_for
from common.pdf_utils import SAASPDFHelper
from common.extensions import db
from apps.z83_form.models import Z83Form
from pathlib import Path
import os

# Define the Blueprint.
# strictly separates templates/static so App #1 doesn't break App #2
z83_bp = Blueprint('z83', __name__,
                   template_folder='templates',
                   static_folder='static')

@z83_bp.route('/', methods=['GET', 'POST'])
def home():
    return render_template('form.html')

@z83_bp.route('/save', methods=['POST'])
def save_form():
    # 1. Get Data
    data = request.form.to_dict()
    profile_name = data.get('profile_name', 'Unnamed Draft')
    
    # 2. Save to Database
    new_entry = Z83Form(
        profile_name=profile_name,
        form_data=data
    )
    db.session.add(new_entry)
    db.session.commit()

    print(f"Received form data: {data}")
        
    # 3. Map Input to PDF Keys (UPDATE THESE WITH YOUR STEP 1 RESULTS!)
    pdf_data = {
        # "PDF_KEY_FROM_SCRIPT": user_variable
        "Surname and Full names": data.get('Surname', ''),      # Example: Change 'Surname' to what the script found
        "Surname and Full names_2": data.get('FirstNames', ''),
        "Initials": data.get('Initials', ''),     # Example: Change 'Initials' to what the script found
        "Identity Number": data.get('IdentityNumber', ''),
        "Contact details in terms of the above": data.get('Phone', ''),
    }
        
    # 4. Load Blank editable Z83
    # Ensure 'editable_z83.pdf' is inside apps/z83_form/static/
    base_pdf = os.path.join(z83_bp.static_folder, 'editable_z83.pdf')
        
    # 5. Generate
    pdf_helper = SAASPDFHelper(base_pdf, pdf_data)
    output_pdf = pdf_helper.fill_smart_pdf()

    # 6. Make sure temp folder exists.
    surname = data.get('Surname', 'output')
    p=Path(f"/tmp/{surname}_z83.pdf") 
    p.parent.mkdir(parents=True, exist_ok=True)

    # 7. Save temp path.
    output_filename = f"/tmp/{surname}_z83.pdf"
        
    # 8. Send file to user
    return send_file(output_pdf, as_attachment=True, download_name=output_filename, mimetype='application/pdf')