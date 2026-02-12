from flask import Blueprint, render_template, request, send_file, redirect, url_for
from common.pdf_utils import SAASPDFHelper
from pathlib import Path
import os
import io
import base64
import fitz  # PyMuPDF
from fillpdf import fillpdfs
from flask_htmx import HTMX

# Define the Blueprint.
# strictly separates templates/static so App #1 doesn't break App #2
z83_bp = Blueprint('z83', __name__,
                   template_folder='templates',
                   static_folder='static')

htmx = HTMX(z83_bp)

@z83_bp.route('/', methods=['GET', 'POST'])
def home():
    import json
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
    
    try:
        # Open the file in read mode ('r')
        with open('data/countries.json', 'r', encoding='utf-8') as file:
            # Load the JSON data into a Python dictionary
            data = json.load(file)
            data = sorted(data, key=lambda x: x['name']['common'])  # Sort countries by common name
            return render_template('form.html', countries=data)

    except FileNotFoundError:
        print("Error: The file 'data/countries.json' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file. Check for invalid syntax.")

    return render_template('form.html')

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

# route for dynamically adding qualifications inputs
@z83_bp.route('/add_qualifications', methods=['GET'])
def qualifications():
    if htmx:
        quals = int(request.args.get('quals', '1'))
        if quals < 4:
            return render_template('partials/qualifications/qualifications.html', qualification_number=quals)
        else:
            return render_template('partials/alerts/too_many_qualifications.html')

# route for dynamically adding experience inputs
@z83_bp.route('/add_experience', methods=['GET'])
def experience():
    if htmx:
        experience = int(request.args.get('experience', '1'))
        if experience < 3:
            return render_template('partials/experience/experience.html', experience_number=experience)
        else:
            return render_template('partials/alerts/too_much_experience.html')

# route for dynamically adding reference inputs
@z83_bp.route('/add_references', methods=['GET'])
def references():
    if htmx:
        references = int(request.args.get('refs', '1'))
        if references < 3:
            return render_template('partials/references/reference.html', reference_number=references)
        else:
            return render_template('partials/alerts/too_many_references.html')

@z83_bp.route('/save', methods=['POST'])
def save_form():
    # 1. Get Data
    data = request.form.to_dict()
    profile_name = data.get('profile_name', 'Unnamed Draft')

    #print(f"Received form data: {data}")
        
    # 2. Get contact details
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
    
    # 3. Map Input to PDF Keys (UPDATE THESE WITH YOUR STEP 1 RESULTS!)
    pdf_data = {
        # "PDF_KEY_FROM_SCRIPT": user_variable
        "Surname and Full names": data.get('Surname', ''),      # Example: Change 'Surname' to what the script found
        "Surname and Full names_2": data.get('FirstNames', ''),
        "Initials": data.get('Initials', ''),     # Example: Change 'Initials' to what the script found
        "Identity Number": data.get('IdentityNumber', ''),
        'Contact details in terms of the above': contact_details,
    }
        
    # 4. Load Blank editable Z83
    # Ensure 'editable_Z83.pdf' is inside apps/z83_form/static/
    base_pdf = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')
        
    # 5. Generate
    pdf_helper = SAASPDFHelper(base_pdf, pdf_data)
    filled_pdf_bytes = pdf_helper.fill_smart_pdf()

    # --- 6. HANDLE SIGNATURE INJECTION (New Code) ---
    signature_data = data.get('signature_data')

    # Temporary file path for the filled & flattened PDF
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_filled:
        filled_pdf_path = tmp_filled.name

    try:
        # ----------------------------------------------------------------------
        # Use fillpdf to fill fields and FLATTEN the form (bakes text permanently)
        # ----------------------------------------------------------------------
        from fillpdf import fillpdfs

        pdf_data = {
            "Surname and Full names": data.get('Surname', ''),
            "Surname and Full names_2": data.get('FirstNames', ''),
            "Initials": data.get('Initials', ''),
            "Identity Number": data.get('IdentityNumber', ''),
            'Contact details in terms of the above': contact_details,
            "Date": data.get('signedDate', ''),
            # Add ALL other field names exactly as they appear in the PDF here
            # You may need to inspect the PDF fields once with:
            # print(fillpdfs.get_form_fields(base_pdf_path))
        }

        base_pdf_path = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')

        fillpdfs.write_fillable_pdf(
            base_pdf_path,
            filled_pdf_path,
            pdf_data,
            flatten=True   # ← This is crucial: bakes appearances → no disappearance
        )

        # ----------------------------------------------------------------------
        # Now open the flattened PDF with PyMuPDF → only to add signature image
        # ----------------------------------------------------------------------
        doc = fitz.open(filled_pdf_path)

        if signature_data and "base64," in signature_data:
            # A. Decode signature
            encoded = signature_data.split(",", 1)[1]
            img_bytes = base64.b64decode(encoded)

            # B. Place on page 2 (index 1)
            target_page = doc[1]

            # C. Signature rectangle – adjust these values!
            #   - y increases DOWNWARD
            #   - Start conservative, increase y0 to move down
            fallback_rect = fitz.Rect(
                x0=0,   # left edge
                y0=690,   # top edge – increase to move signature DOWN into box
                x1=420,   # right edge
                y1=730    # bottom edge – decrease if still too tall
            ).normalize()

            try:
                target_page.insert_image(
                    fallback_rect,
                    stream=img_bytes,
                    keep_proportion=True,
                    overlay=True
                )
            except Exception as e:
                print(f"Signature insert failed: {e}")
                # Fallback: try slightly different rect or log for debugging

        # D. Save final PDF
        output_buffer = io.BytesIO()
        output_buffer.write(
            doc.write(
                garbage=4,
                deflate=True,
                clean=True
            )
        )
        doc.close()

    except Exception as e:
        print(f"Error during filling or signature: {e}")
        # Emergency fallback: return blank or original if critical failure
        output_buffer = io.BytesIO()
        with open(base_pdf_path, "rb") as f:
            output_buffer.write(f.read())

    finally:
        # Clean up temp file
        if os.path.exists(filled_pdf_path):
            try:
                os.unlink(filled_pdf_path)
            except:
                pass

    # 7. Make sure temp folder exists.
    surname = data.get('Surname', 'output')
    p=Path(f"/tmp/{surname}_z83.pdf") 
    p.parent.mkdir(parents=True, exist_ok=True)

    # 8. Save temp path.
    output_filename = f"/tmp/{surname}_z83.pdf"

    # Rect(128.57899475097656, 696.239990234375, 304.5050048828125, 714.239990234375)

    # 9. Rewind the file to the beginning before sending
    output_buffer.seek(0)
        
    # 10. Send file to user
    return send_file(output_buffer, as_attachment=True, download_name=output_filename, mimetype='application/pdf')