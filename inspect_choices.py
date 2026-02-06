from PyPDF2 import PdfReader
import sys

# Force UTF-8 for Windows terminals to avoid encoding errors
sys.stdout.reconfigure(encoding='utf-8')

def analyze_pdf(path):
    try:
        reader = PdfReader(path)
        fields = reader.get_fields()
        
        if not fields:
            print("No fields found! Is this a 'Smart' PDF?")
            return
        with open("choice_inspector.txt", "w") as f:
            f.write(f"--- ANALYZING: {path} ---\n")
            f.write(f"Found {len(fields)} fields.\n")

            for field_name, value in fields.items():
                # Get the field type (Text, Button, Choice)
                field_type = value.get('/FT')

                # 1. DROPDOWNS (Combo Boxes)
                if '/Opt' in value:
                    f.write(f"[DROPDOWN] Field: {field_name}\n")
                    options = value['/Opt']
                    # Sometimes options are ['Display', 'Value'] pairs, sometimes just strings
                    clean_opts = [opt if isinstance(opt, str) else opt[1] for opt in options]
                    f.write(f"   Options: {clean_opts}\n")
                    f.write("-" * 20 + "\n")
                
                # 2. CHECKBOXES & RADIO BUTTONS
                elif field_type == '/Btn':
                    f.write(f"[BUTTON/CHECKBOX] Field: {field_name}")
                    
                    # Safe way to find the "On" value
                    try:
                        # We check if /AP (Appearance) and /N (Normal) exist before accessing
                        ap = value.get('/AP', {})
                        if hasattr(ap, 'get_object'): ap = ap.get_object()
                        
                        n_dict = ap.get('/N', {})
                        if hasattr(n_dict, 'get_object'): n_dict = n_dict.get_object()
                        
                        # Get keys excluding '/Off'
                        keys = n_dict.keys()
                        on_states = [k for k in keys if k != '/Off']
                        
                        if on_states:
                            f.write(f"   To Check (True):  '{on_states[0]}'\n")
                            f.write(f"   To Uncheck (False): '/Off'\n")
                        else:
                            f.write("   (Standard Checkbox - try using '/Yes' or '/On')\n")
                    except Exception as e:
                        # If deeper inspection fails, just suggest defaults
                        f.write(f"   (Could not read internal state - Defaulting to '/Yes')\n")
                    
                    f.write("-" * 20)

    except FileNotFoundError:
        print(f"ERROR: Could not find file at: {path}")
        print("Check the filename and ensure it is in the same folder.")

# Run it
if __name__ == "__main__":
    # Update this path if necessary
    target_file = "apps/z83_form/static/editable_z83.pdf" 
    analyze_pdf(target_file)