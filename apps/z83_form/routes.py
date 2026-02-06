from flask import Blueprint, render_template, request, send_file, redirect, url_for
from common.pdf_utils import SAASPDFHelper
from common.extensions import db
from apps.z83_form.models import Z83Form
from pathlib import Path
import os
from flask_htmx import HTMX
import requests

# Define the Blueprint.
# strictly separates templates/static so App #1 doesn't break App #2
z83_bp = Blueprint('z83', __name__,
                   template_folder='templates',
                   static_folder='static')

htmx = HTMX(z83_bp)

@z83_bp.route('/', methods=['GET', 'POST'])
def home():
    if htmx:
        contact = request.form.get('contactOption', 'email')
        match contact:
            case 'post':
                return render_template('partials/contact_options/post.html')
            case 'email':
                return render_template('partials/contact_options/email.html')
            case 'fax':
                return render_template('partials/contact_options/fax.html')
            case 'phone':
                    return render_template('partials/contact_options/phone.html')
    
    # The API endpoint URL for getting countries.
    url = 'https://restcountries.com/v3.1/all?fields=name'

    # Make the GET request
    response = requests.get(url)

    data = {}

    # Check if the request was successful (status code 200-299)
    if response.status_code == 200:
        # Parse the JSON response content into a Python dictionary/list
        data = response.json()
        data = sorted(data, key=lambda x: x['name']['common'])  # Sort countries by common name
    else:
        print(f"Request failed with status code: {response.status_code}")
        # You can use response.raise_for_status() to raise an exception for bad status codes
    return render_template('form.html', countries=data)

@z83_bp.route('/country', methods=['POST'])
def country():
    if htmx:
        country = request.form.get('countries', '')

        # If not South African, ask about work permit. If South African, skip question and go to contact details.
        if country != 'South Africa':
            return render_template('partials/country/validPermit.html')
        else:
            return '<div></div>'

@z83_bp.route('/criminal', methods=['POST'])
def criminal():
    if htmx:
        criminal = request.form.get('CriminalHistory', '')

        # Ask about past criminal case.
        if criminal == 'Yes':
            return render_template('partials/criminal/past_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/pending_criminal', methods=['POST'])
def pending_criminal():
    if htmx:
        pending_criminal = request.form.get('PendingCase', '')

        # Ask about pending criminal case.
        if pending_criminal == 'Yes':
            return render_template('partials/criminal/pending_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/disciplinary', methods=['POST'])
def disciplinary():
    if htmx:
        disciplinary = request.form.get('DisciplinaryHistory', '')

        # Ask about past disciplinary case.
        if disciplinary == 'Yes':
            return render_template('partials/disciplinary/past_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/disciplinary_pending', methods=['POST'])
def disciplinary_pending():
    if htmx:
        disciplinary_pending = request.form.get('DisciplinaryPending', '')

        # Ask about pending disciplinary case.
        if disciplinary_pending == 'Yes':
            return render_template('partials/disciplinary/pending_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/resigned', methods=['POST'])
def resigned():
    if htmx:
        resigned = request.form.get('Resigned', '')

        # Ask about resigning due to pending disciplinary case.
        if resigned == 'Yes':
            return render_template('partials/disciplinary/resigned.html')
        else:
            return '<div></div>'

@z83_bp.route('/conducting_business', methods=['POST'])
def conducting_business():
    if htmx:
        conducting_business = request.form.get('ConductingBusiness', '')

        # Ask about conducting business.
        if conducting_business == 'Yes':
            return render_template('partials/conducting_business/conducting_business_details.html')
        else:
            return '<div></div>'

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
    contact_details = ""
    match data.get('contactOption', 'email'):
        case 'post':
            contact_details = data.get('PostalAddress', '')
        case 'email':
            contact_details = data.get('Email', '')
        case 'fax':
            contact_details = data.get('FaxNumber', '')
        case 'phone':
            contact_details = data.get('Phone', '')
    pdf_data = {
        # "PDF_KEY_FROM_SCRIPT": user_variable
        "Surname and Full names": data.get('Surname', ''),      # Example: Change 'Surname' to what the script found
        "Surname and Full names_2": data.get('FirstNames', ''),
        "Initials": data.get('Initials', ''),     # Example: Change 'Initials' to what the script found
        "Identity Number": data.get('IdentityNumber', ''),
        "Contact details in terms of the above": contact_details,
    }
        
    # 4. Load Blank editable Z83
    # Ensure 'editable_Z83.pdf' is inside apps/z83_form/static/
    base_pdf = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')
        
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