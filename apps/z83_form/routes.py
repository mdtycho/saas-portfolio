from flask import Blueprint, render_template, request, send_file, redirect, url_for
from common.pdf_utils import SAASPDFHelper
from pathlib import Path
import os
import io
import base64
import fitz  # PyMuPDF
from fillpdf import fillpdfs
from flask_htmx import HTMX
from datetime import datetime

# Define the Blueprint.
# strictly separates templates/static so App #1 doesn't break App #2
z83_bp = Blueprint('z83', __name__,
                   template_folder='templates',
                   static_folder='static')

htmx = HTMX(z83_bp)

def get_dropdown_coordinates():

    """Retrieves coordinates of dropdowns in form."""


    base_pdf = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')

    field_locations = {}

    doc = fitz.open(base_pdf)

    page = doc[1]  # Assuming all dropdowns are on the 2nd page; adjust if needed for widget in page.widgets()

    for widget in page.widgets():
        if widget.field_name.startswith("Dropdown"):
            # Save the location.
            field_locations[widget.field_name] = widget.rect  # This is a fitz.Rect object with x0, y0, x1, y1

    doc.close()

    return field_locations

@z83_bp.route('/', methods=['GET', 'POST'])
def home():
    import json
    if htmx:
        contact = request.form.get('contactOption', 'Choice2')  # Default to 'email' if not provided
        match contact:
            case 'Choice1':
                return render_template('partials/contact_options/post.html')
            case 'Choice2':
                return render_template('partials/contact_options/email.html')
            case 'Choice3':
                return render_template('partials/contact_options/fax.html')
            case 'Choice4':
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
        if criminal == 'Choice6':
            return render_template('partials/criminal/past_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/pending_criminal', methods=['POST'])
def pending_criminal():
    if htmx:
        pending_criminal = request.form.get('PendingCase', '')

        # Ask about pending criminal case.
        if pending_criminal == 'Choice6':
            return render_template('partials/criminal/pending_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/disciplinary', methods=['POST'])
def disciplinary():
    if htmx:
        disciplinary = request.form.get('DisciplinaryHistory', '')

        # Ask about past disciplinary case.
        if disciplinary == 'Choice6':
            return render_template('partials/disciplinary/past_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/disciplinary_pending', methods=['POST'])
def disciplinary_pending():
    if htmx:
        disciplinary_pending = request.form.get('DisciplinaryPending', '')

        # Ask about pending disciplinary case.
        if disciplinary_pending == 'Choice6':
            return render_template('partials/disciplinary/pending_details.html')
        else:
            return '<div></div>'

@z83_bp.route('/resigned', methods=['POST'])
def resigned():
    if htmx:
        resigned = request.form.get('Resigned', '')

        # Ask about resigning due to pending disciplinary case.
        if resigned == 'Choice6':
            return render_template('partials/disciplinary/resigned.html')
        else:
            return '<div></div>'

@z83_bp.route('/discharged', methods=['POST'])
def discharged():
    if htmx:
        discharged = request.form.get('Discharged', '')

        # Ask about being discharged from previous employment.
        if discharged == 'Choice6':
            return render_template('partials/disciplinary/discharged.html')
        else:
            return '<div></div>'

@z83_bp.route('/conducting_business', methods=['POST'])
def conducting_business():
    if htmx:
        conducting_business = request.form.get('ConductingBusiness', '')

        # Ask about conducting business.
        if conducting_business == 'Choice6':
            return render_template('partials/conducting_business/conducting_business_details.html')
        else:
            return '<div></div>'

# route for dynamically adding qualifications inputs
@z83_bp.route('/add_qualifications', methods=['GET'])
def qualifications():
    quals = int(request.args.get('quals', '1'))
    if quals < 4:
        return render_template('partials/qualifications/qualifications.html', qualification_number=quals)
    else:
        return render_template('partials/alerts/too_many_qualifications.html')

# route for dynamically adding experience inputs
@z83_bp.route('/add_experience', methods=['GET'])
def experience():
    experience = int(request.args.get('experience', ''))
    print('Experience count from route:', experience)
    if experience < 3:
        return render_template('partials/experience/experience.html', experience_number=experience)
    else:
        return render_template('partials/alerts/too_much_experience.html')

# route for dynamically adding reference inputs
@z83_bp.route('/add_references', methods=['GET'])
def references():
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
    dropdown_coordinates = get_dropdown_coordinates()

        
    # 2. Get contact details
    contact_details = ""
    match data.get('contactOption', 'Choice3'):
        case 'Choice1':
            contact_details = data.get('PostalAddress', '').replace(',', '\n')  # Replace commas with newlines for better PDF formatting
            contact_details = contact_details.replace('\n\n', '\n')  # Remove any accidental double newlines
            contact_details = contact_details.strip()  # Remove leading/trailing whitespace
            contact_details = contact_details.replace('\n ', '\n')  # Remove spaces after newlines
        case 'Choice2':
            contact_details = data.get('Email', '')
        case 'Choice3':
            contact_details = data.get('FaxNumber', '')
        case 'Choice4':
            contact_details = data.get('Phone', '')
    
   
    # Parse date strings into a datetime objects
    # The format string in strptime() MUST match the input string's format
    signature_date = datetime.strptime(data.get('signedDate', ''), "%Y-%m-%d").strftime("%d/%m/%Y")

    dob_date = datetime.strptime(data.get('DateOfBirth', ''), "%Y-%m-%d").strftime("%d/%m/%Y")

    reg_date = datetime.strptime(data.get('RegistrationDate', ''), "%Y-%m-%d").strftime("%d/%m/%Y")
        
    # 3. Load Blank editable Z83
    # Ensure 'editable_Z83.pdf' is inside apps/z83_form/static/
    base_pdf = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')

    
    # Retrieve all languages in the form data that match South African languages (these are the field names in the PDF) 
    
    all_sa_languages = ['isizulu', 'sign-language', 'english', 'afrikaans', 'isixhosa', 'sesotho', 'setswana', 'tshivenda', 'xitsonga', 'siswati', 'sepedi', 'isindebele']

    form_language_fields = [key for key in data.keys() if key in all_sa_languages]

    # Retrieve all form fields that start with 'employer'
    employer_fields = [key for key in data.keys() if key.startswith('employer')]

    # --- 4. HANDLE SIGNATURE INJECTION (New Code) ---
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
            "Position for which you are applying as advertised": data.get('Position', ''),
            "Department where the position was advertised": data.get('Department', ''),
            "Reference number as stated in the advert": data.get('ReferenceNumber', ''),
            "If you are offered the position when can you start OR how much notice must you serve with your current employer": data.get('NoticeTime', ''),
            "Surname and Full names": data.get('Surname', ''),
            "Surname and Full names_2": data.get('FirstNames', ''),
            "Initials": data.get('Initials', ''),
            "DDMMYY": dob_date,
            "Identity Number": data.get('IdentityNumber', ''),
            "Passport2 number": data.get('PassportNumber', ''),
            "Group2": data.get('Race', ''),
            "Group3": data.get('Gender', ''),
            "Group4": data.get('Disability', ''),
            "Group5": 'Choice6' if data.get('countries', '') == 'South Africa' else 'Choice7',
            "Text5": '' if data.get('countries', '') == 'South Africa' else data.get('countries', ''),
            "Group6": '' if data.get('countries', '') == 'South Africa' else data.get('permit', ''),
            "Group7": data.get('CriminalHistory', ''),
            "Text6": data.get('CriminalDetails', ''),
            "Group8": data.get('PendingCase', ''),
            "Text7": data.get('PendingDetails', ''),
            "Group9": data.get('DisciplinaryHistory', ''),
            "Text8": data.get('DisciplinaryDetails', ''),
            "Group10": data.get('DisciplinaryPending', ''),
            "Text9": data.get('DisciplinaryPendingDetails', ''),
            "Group11": data.get('Resigned', ''),
            "Text10": data.get('ResignedDetails', ''),
            "Group12": data.get('Discharged', ''),
            "Group13": data.get('ConductingBusiness', ''),
            "Text11": data.get('ConductingBusinessDetails', ''),
            "Group14": data.get('Relinquish', ''),
            "Text12": data.get('PrivateSectorExperience', ''),
            "Text14": data.get('PublicSectorExperience', ''),
            "Text15": reg_date,
            "Text16": data.get('RegistrationNumber', ''),
            "Text1": data.get('Initials', ''),
            "Preferred language for correspondence": data.get('PreferredLanguage', ''),
            "Group16": data.get('contactOption', ''),
            'Contact details in terms of the above': contact_details,
            "Date": signature_date,
            'Name of SchoolTechnical CollegeRow1': data.get('InstitutionName', ''),
            'Name of qualification obtainedRow1': data.get('QualificationName', ''),
            'Year obtainedRow1': data.get('YearObtained', ''),
            'Name of SchoolTechnical CollegeRow2': data.get('InstitutionName_1', ''),
            'Name of qualification obtainedRow2': data.get('QualificationName_1', ''),
            'Year obtainedRow2': data.get('YearObtained_1', ''),
            'Name of SchoolTechnical CollegeRow3': data.get('InstitutionName_2', ''),
            'Name of qualification obtainedRow3': data.get('QualificationName_2', ''),
            'Year obtainedRow3': data.get('YearObtained_2', ''),
            'Name of SchoolTechnical CollegeRow4': data.get('InstitutionName_3', ''),
            'Name of qualification obtainedRow4': data.get('QualificationName_3', ''),
            'Year obtainedRow4': data.get('YearObtained_3', ''),
            'Current study institution and qualification': data.get('InProgressQualification', ''),
            "Group17": 'Choice1' if data.get('Discharged', '') == 'Choice6' else 'Choice2',
            'If yes Provide the name of the previous employing department and indicate the nature of the condition': data.get('DischargedDetails', ''),
            "NameRow1": data.get('ReferenceName', ''),
            "Relationship to youRow1": data.get('Relationship', ''),
            'Tel No office hoursRow1': data.get('ReferenceTelephone', '') + ' (' + data.get('officeOpen', '') + ' - ' + data.get('officeClose', '') + ')' if data.get('ReferenceTelephone', '') else '',
            "NameRow2": data.get('ReferenceName_1', ''),
            "Relationship to youRow2": data.get('Relationship_1', ''),
            'Tel No office hoursRow2': data.get('ReferenceTelephone_1', '') + ' (' + data.get('officeOpen_1', '') + ' - ' + data.get('officeClose_1', '') + ')' if data.get('ReferenceTelephone_1', '') else '',
            "NameRow3": data.get('ReferenceName_2', ''),
            "Relationship to youRow3": data.get('Relationship_2', ''),
            'Tel No office hoursRow3': data.get('ReferenceTelephone_2', '') + ' (' + data.get('officeOpen_2', '') + ' - ' + data.get('officeClose_2', '') + ')' if data.get('ReferenceTelephone_2', '') else '',
            # Add ALL other field names exactly as they appear in the PDF here
            # You may need to inspect the PDF fields once with:
            # print(fillpdfs.get_form_fields(base_pdf_path))
        }

        # Include language text fields in the dict to be written to the pdf form with fillpdf
        for i in range(len(form_language_fields)):
            lang_field =  form_language_fields[i]
            if i == 0:
                pdf_data['Languages specifyRow1'] = data.get(lang_field, '')
            else:
                pdf_data[f'Languages specifyRow1_{i+1}'] = data.get(lang_field, '')

        # Write the text fields associated with an employer to the dict
        for i in range(len(employer_fields)):
            underscore = '' if i == 0 else f'_{i}'
            emp_field = employer_fields[i]
            pdf_data[f"Employer including current employerRow{i+1}"] = data.get(emp_field, '')
            pdf_data[f"Post heldRow{i+1}"] = data.get(f"JobTitle{underscore}", '')
            pdf_data[f"YYRow{i+1}"] = data.get(f"StartYear{underscore}", '')
            pdf_data[f"YYRow{i+1}_2"] = data.get(f"EndYear{underscore}", '')
            pdf_data[f"Reason for leavingRow{i+1}"] = data.get(f"LeavingReason{underscore}", '')

        base_pdf_path = os.path.join(z83_bp.static_folder, 'editable_Z83.pdf')

        fillpdfs.write_fillable_pdf(
            base_pdf_path,
            filled_pdf_path,
            pdf_data,
            flatten=True   # ← This is crucial: bakes appearances → no disappearance
        )

        # -----------------------------------------------------------------------------------------
        # Now open the flattened PDF with PyMuPDF → only to add signature image and dropdown values
        # ------------------------------------------------------------------------------------------
        doc = fitz.open(filled_pdf_path)

        # -------------------------------------------------
        # CRITICAL FIX: Remove the 'Ghost' Widgets
        # -------------------------------------------------
        # Since fillpdfs missed these fields, they are still 'live' and blocking your text.
        # We iterate through all pages and kill any remaining interactive fields.
        for page in doc:
            for widget in page.widgets():
                if widget.field_name.startswith("Dropdown"):
                    page.delete_widget(widget)

        # Start by writing language speak and write fields

        for i in range(len(form_language_fields)):

            rect_speak = dropdown_coordinates[f"Dropdown3.0.{i}"]
            rect_write = dropdown_coordinates[f"Dropdown3.1.{i}"]

            page = doc[1]  # Assuming all dropdowns are on the 2nd page; adjust if needed

            page.insert_text(
            (rect_speak.x0 + 2, rect_speak.y1 - 4), # Slight padding for alignment
            data.get(form_language_fields[i] + '-speak', ''),
            fontsize=10,
            fontname="helv",
            color=(0, 0, 0)
            )

            page.insert_text(
            (rect_write.x0 + 2, rect_write.y1 - 4), # Slight padding for alignment
            data.get(form_language_fields[i] + '-write', ''),
            fontsize=10,
            fontname="helv",
            color=(0, 0, 0)
            )

        # Then write the employer dropdown fields

        for i in range(len(employer_fields)):
            rect_from = dropdown_coordinates[f"Dropdown1.{i}.0"]
            rect_to = dropdown_coordinates[f"Dropdown1.{i}.1"]

            underscore = '' if i == 0 else f'_{i}'

            page = doc[1]  # Assuming all dropdowns are on the 2nd page; adjust if needed

            page.insert_text(
            (rect_from.x0+ 2, rect_from.y1 - 4), # Slight padding for alignment
            data.get(f"StartMonth{underscore}", ''),
            fontsize=10,
            fontname="helv",
            color=(0, 0, 0)
            )

            page.insert_text(
            (rect_to.x0 + 2, rect_to.y1 - 4), # Slight padding for alignment
            data.get(f"EndMonth{underscore}", ''),
            fontsize=10,
            fontname="helv",
            color=(0, 0, 0)
            )

        # Finally, handle the signature image if it exists

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

    # 5. Make sure temp folder exists.
    surname = data.get('Surname', 'output')
    p=Path(f"/tmp/{surname}_z83.pdf") 
    p.parent.mkdir(parents=True, exist_ok=True)

    # 6. Save temp path.
    output_filename = f"/tmp/{surname}_z83.pdf"

    # Rect(128.57899475097656, 696.239990234375, 304.5050048828125, 714.239990234375)

    # 7. Rewind the file to the beginning before sending
    output_buffer.seek(0)
        
    # 8. Send file to user
    return send_file(output_buffer, as_attachment=True, download_name=output_filename, mimetype='application/pdf')