// --- 1. WIZARD LOGIC ---
function showStep(step) {
    // Hide all
    document.querySelectorAll('.form-step').forEach(el => el.classList.add('hidden'));
    // Show target
    document.querySelector(`.form-step[data-step="${step}"]`).classList.remove('hidden');
    // Update Bar
    const progress = (step / 8) * 100;
    document.getElementById('progressBar').style.width = `${progress}%`;
}

function nextStep(step) {
    const currentStep = step - 1;
    const currentDiv = document.querySelector(`.form-step[data-step="${currentStep}"]`);

    // Validate inputs in current step before moving
    const inputs = currentDiv.querySelectorAll('input, select');
    let valid = true;
    inputs.forEach(input => {
        if (!input.checkValidity()) {
            input.reportValidity();
            valid = false;
        }
    });

    if (valid) showStep(step);
}

function prevStep(step) { showStep(step); }

// Utility to wait for an element to exist in the DOM (useful for dynamic content)
function waitForElement(selector) {
    return new Promise((resolve) => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}

function incrementExperience() {
    const btn = document.getElementById('addExperience');
    let count = parseInt(btn.getAttribute('data-experience')) || 0;

    if (count >= 3) {
        btn.setAttribute('disabled', 'disabled');
    } else {
        count++;
        btn.setAttribute('data-experience', count);
    }

    console.log('Experience count:', btn.getAttribute('data-experience'));
    console.log('Experience count from variable:', count);
};



// Wait for the HTML to be fully loaded
document.addEventListener("DOMContentLoaded", async function () {

    // --- 2. AUTO-SAVE LOGIC ---
    const form = document.getElementById('z83Form');
    const status = document.getElementById('saveStatus');

    // Load
    const saved = localStorage.getItem('z83_draft');
    if (saved) {

        const data = JSON.parse(saved);

        console.log(data);

        for(const key of Object.keys(data)) {
            const el = form.elements[key];
            if (el) {
                if (el.type === 'checkbox') {
                    el.checked = data[key] == el.value; // Check the box if the saved value matches the checkbox value
                } else {
                    el.value = data[key];
                }
            }

            // Handle the addition of more qualifications, experience, and references when loading saved data. This ensures that if a user had added multiple qualifications/experience/reference entries, they will be correctly displayed when the draft is loaded.
            const dynamicFieldPrefixes = ['employer_', 'InstitutionName_', 'ReferenceName_'];
            if (dynamicFieldPrefixes.some(prefix => key.startsWith(prefix))) {
                const index = parseInt(key.at(-1)); // Get the index from the end of the key (e.g., 0, 1, 2)
                if (key.startsWith('employer_')) {
                    console.log('key: ', key);
                    const button = document.getElementById('addExperience');
                    console.log('experienceCount: ', button.dataset.experience);
                    const params = new URLSearchParams();

                    params.append("experience", button.dataset.experience);

                    const response = await fetch(`${experienceUrl}?${params}`);
                    const markup = await response.text();
                    const experienceContainer = document.getElementById('experienceContainer');
                    experienceContainer.insertAdjacentHTML('beforeend', markup);
                    button.dataset.experience = parseInt(button.dataset.experience) + 1;
                    console.log('button.dataset.experience: ', button.dataset.experience);
                    // Get element id's and populate the elements
                    const employer_id = `employer_${index}`;
                    document.getElementsByName(employer_id)[0].value = data[employer_id];

                    const job_title_id = `JobTitle_${index}`;
                    document.getElementsByName(job_title_id)[0].value = data[job_title_id];

                    const leaving_reason = `LeavingReason_${index}`;
                    document.getElementsByName(leaving_reason)[0].value = data[leaving_reason];

                    const start_year = `StartYear_${index}`;
                    document.getElementsByName(start_year)[0].value = data[start_year];

                    const start_month = `StartMonth_${index}`;
                    document.getElementsByName(start_month)[0].value = data[start_month];

                    const end_year = `EndYear_${index}`;
                    document.getElementsByName(end_year)[0].value = data[end_year];

                    const end_month = `EndMonth_${index}`;
                    document.getElementsByName(end_month)[0].value = data[end_month];
                }else if (key.startsWith('InstitutionName_')) {
                    const button = document.getElementById('addQualifications');
                    const params = new URLSearchParams();
                    params.append("quals", button.dataset.quals);
                    const response = await fetch(`${qualificationUrl}?${params}`);
                    const markup = await response.text();
                    const qualificationsContainer = document.getElementById('qualificationsContainer');
                    qualificationsContainer.insertAdjacentHTML('beforeend', markup);
                    button.dataset.quals = parseInt(button.dataset.quals) + 1;
                    // Get element id's and populate the elements
                    const institution_name_id = `InstitutionName_${index}`;
                    document.getElementsByName(institution_name_id)[0].value = data[institution_name_id];

                    const qualification_name_id = `QualificationName_${index}`;
                    document.getElementsByName(qualification_name_id)[0].value = data[qualification_name_id];

                    const year_obtained_id = `YearObtained_${index}`;
                    document.getElementsByName(year_obtained_id)[0].value = data[year_obtained_id];
                    
                }else if (key.startsWith('ReferenceName_')) {
                    const button = document.getElementById('addReferences');
                    const params = new URLSearchParams();
                    params.append("refs", button.dataset.refs);
                    const response = await fetch(`${referenceUrl}?${params}`);
                    const markup = await response.text();
                    const referencesContainer = document.getElementById('referencesContainer');
                    referencesContainer.insertAdjacentHTML('beforeend', markup);
                    button.dataset.refs = parseInt(button.dataset.refs) + 1;
                    // Get element id's and populate the elements
                    const reference_name_id = `ReferenceName_${index}`;
                    document.getElementsByName(reference_name_id)[0].value = data[reference_name_id];

                    const relationship_id = `Relationship_${index}`;
                    document.getElementsByName(relationship_id)[0].value = data[relationship_id];

                    const reference_telephone_id = `ReferenceTelephone_${index}`;
                    document.getElementsByName(reference_telephone_id)[0].value = data[reference_telephone_id];

                    const office_open_id = `officeOpen_${index}`;
                    document.getElementsByName(office_open_id)[0].value = data[office_open_id];

                    const office_close_id = `officeClose_${index}`;
                    document.getElementsByName(office_close_id)[0].value = data[office_close_id];
                }
            }

            // Trigger change event on contactOptions to ensure correct display of contact details field
            if (key === 'contactOption') {
                // map contactOption value to the corresponding input field
                var inputMap = {
                    'Choice2': 'Email',
                    'Choice1': 'PostalAddress',
                    'Choice3': 'FaxNumber',
                    'Choice4': 'Phone'
                };
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="contactOption"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // populate the contact details field based on the saved contact option
                const contactFieldId = inputMap[el.value];

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="${contactFieldId}"]`).then(element => {
                    element.value = data[contactFieldId] || '';
                });
            }

            // Trigger change event on countries to ensure correct display of permit field
            if (key === 'countries') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.getElementById('countries');
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="permit"][value="${data['permit']}"]`).then(element => {
                    element.checked = true;
                });
            }

            // Trigger change event on CriminalHistory to ensure correct display of CriminalDetails field
            if (key === 'CriminalHistory') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="CriminalHistory"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="CriminalDetails"]`).then(element => {
                    element.value = data['CriminalDetails'] || '';
                });
            }

            // Trigger change event on PendingCase to ensure correct display of PendingDetails field
            if (key === 'PendingCase') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="PendingCase"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="PendingDetails"]`).then(element => {
                    element.value = data['PendingDetails'] || '';
                });
            }

            // Trigger change event on DisciplinaryHistory to ensure correct display of DisciplinaryDetails field
            if (key === 'DisciplinaryHistory') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="DisciplinaryHistory"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="DisciplinaryDetails"]`).then(element => {
                    element.value = data['DisciplinaryDetails'] || '';
                });
            }

            // Trigger change event on DisciplinaryPending to ensure correct display of DisciplinaryPendingDetails field
            if (key === 'DisciplinaryPending') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="DisciplinaryPending"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="DisciplinaryPendingDetails"]`).then(element => {
                    element.value = data['DisciplinaryPendingDetails'] || '';
                });
            }

            // Trigger change event on Resigned to ensure correct display of ResignedDetails field
            if (key === 'Resigned') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="Resigned"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="ResignedDetails"]`).then(element => {
                    element.value = data['ResignedDetails'] || '';
                });
            }

            // Trigger change event on Discharged to ensure correct display of DischargedDetails field
            if (key === 'Discharged') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="Discharged"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="DischargedDetails"]`).then(element => {
                    element.value = data['DischargedDetails'] || '';
                });
            }

            // Trigger change event on ConductingBusiness to ensure correct display of ConductingBusinessDetails field
            if (key === 'ConductingBusiness') {
                
                const event = new Event('change', { bubbles: true });
                const inputElement = document.querySelector(`input[name="ConductingBusiness"][value="${el.value}"]`);
                console.log(inputElement);
                inputElement.dispatchEvent(event);

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="ConductingBusinessDetails"]`).then(element => {
                    element.value = data['ConductingBusinessDetails'] || '';
                });
            }

            // Enable and populate language proficiency selects based on saved data. This ensures that if a user had selected languages and proficiencies, they will be correctly displayed when the draft is loaded.
            if (key.endsWith('-speak') || key.endsWith('-write')) {
                
                const inputElement = document.querySelector(`select[name="${key}"]`);
                console.log(inputElement);
                inputElement.disabled = false;
                inputElement.value = data[key] || '';
            }
        };
        // Update the display of the range inputs for years of experience when loading saved data.
        document.getElementById('privateSectorValue').textContent = data['PrivateSectorExperience'] || 0;
        document.getElementById('publicSectorValue').textContent = data['PublicSectorExperience'] || 0;

        status.textContent = "Draft restored from browser storage";
    }

    // Save
    form.addEventListener('input', () => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        localStorage.setItem('z83_draft', JSON.stringify(data));
        status.textContent = "Saving...";
        setTimeout(() => status.textContent = "Draft Saved", 1000);
    });

    // Manage state of range inputs for years of public and private sector experience
    const privateInput = document.getElementById('PrivateSectorExperience');
    const privateSpan = document.getElementById('privateSectorValue');

    const publicInput = document.getElementById('PublicSectorExperience');
    const publicSpan = document.getElementById('publicSectorValue');

    // 1. Private Sector Listener
    if (privateInput && privateSpan) {
        privateInput.addEventListener('input', function () {
            privateSpan.textContent = this.value;
        });
    }

    // 2. Public Sector Listener
    if (publicInput && publicSpan) {
        publicInput.addEventListener('input', function () {
            publicSpan.textContent = this.value;
        });
    }

    // Language profciency logic: ensures not more than 5 languages selected and only profiencies for selected languages are enabled.
    document.querySelectorAll('.language-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const checkedCount = document.querySelectorAll('.language-checkbox:checked').length;

            if (checkedCount > 5 && !this.checked) {
                this.checked = true;
                return;
            }

            if (checkedCount > 5) {
                alert('You can select up to 5 languages only');
                this.checked = false;
                return;
            }

            const row = this.closest('.language-row');
            const selects = row.querySelectorAll('.language-select');
            selects.forEach(select => {
                select.disabled = !this.checked;
                if (!this.checked) select.value = '';
            });
        });
    });

    // Qualifications logic: limits to 4 qualifications and updates the data-quals attribute on the button to keep track of how many have been added. 
    // Disables the button when the limit is reached.
    // Note: The actual addition of qualification fields is handled by HTMX via the hx-get attribute on the button, so we only need to manage the count and disabling here.
    const addQualsBtn = document.getElementById('addQualifications');
    if (addQualsBtn) {
        addQualsBtn.addEventListener('click', function () {
            let count = parseInt(this.getAttribute('data-quals'));
            if (count >= 4) {
                this.setAttribute('disabled', 'disabled');
            } else {
                count++;
                this.setAttribute('data-quals', count);
            }
        });
    }

    // Experience logic: limits to 3 experience instances and updates the data-experience attribute on the button to keep track of how many have been added. 
    // Disables the button when the limit is reached.
    // Note: The actual addition of qualification fields is handled by HTMX via the hx-get attribute on the button, so we only need to manage the count and disabling here.
    const addExpBtn = document.getElementById('addExperience');
    if (addExpBtn) {
        addExpBtn.addEventListener('click', incrementExperience);
    }

    // References logic: limits to 3 reference instances and updates the data-refs attribute on the button to keep track of how many have been added. 
    // Disables the button when the limit is reached.
    // Note: The actual addition of qualification fields is handled by HTMX via the hx-get attribute on the button, so we only need to manage the count and disabling here.
    const addRefBtn = document.getElementById('addReferences');
    if (addRefBtn) {
        addRefBtn.addEventListener('click', function () {
            let count = parseInt(this.getAttribute('data-refs'));
            if (count >= 3) {
                this.setAttribute('disabled', 'disabled');
            } else {
                count++;
                this.setAttribute('data-refs', count);
            }
        });
    }

    // --- 3. SIGNATURE PAD LOGIC ---
    // --- Elements ---
    const modal = document.getElementById('signatureModal');
    const openBtn = document.getElementById('openSignatureModal');
    const cancelBtn = document.getElementById('cancelSigBtn');
    const saveBtn = document.getElementById('saveSigBtn');
    const clearBtn = document.getElementById('clearSigBtn');
    const canvas = document.getElementById('signatureCanvas');
    const sigInput = document.getElementById('signatureInput');
    const preview = document.getElementById('signaturePreview');
    const placeholder = document.getElementById('sigPlaceholder');

    // --- State ---
    let signaturePad = null;

    // --- Core Resizing Logic ---
    // This function makes the canvas resolution match the screen pixels exactly
    function resizeCanvas() {
        if (!signaturePad) return;

        // 1. Get the actual visible size of the canvas
        // (This relies on the modal being OPEN and VISIBLE)
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        
        // 2. Set the internal resolution matches the display size
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        
        // 3. Scale the drawing context context
        canvas.getContext("2d").scale(ratio, ratio);

        // 4. IMPORTANT: Resizing clears the canvas, so we must clear the data too
        // or the ink will be in the wrong place.
        signaturePad.clear(); 
    }

    // --- Initialization ---
    // We delay initialization until the user actually clicks "Sign"
    // This prevents the "0 width" bug.
    openBtn.addEventListener('click', () => {
        // A. Show the modal
        modal.classList.remove('hidden');

        // B. Initialize the library ONLY if it hasn't been created yet
        if (!signaturePad) {
            signaturePad = new SignaturePad(canvas, {
                minWidth: 2.0,
                maxWidth: 5.0,
                penColor: "#000000",
                backgroundColor: "rgba(255, 255, 255, 0)" // Transparent
            });
        }

        // C. Force a Resize (The Magic Step)
        // We use a tiny timeout to let the browser "paint" the modal 
        // before we try to measure it.
        setTimeout(() => {
            resizeCanvas();
        }, 50); 
    });

    // --- Window Resize Handling ---
    // Handle rotating phones
    window.addEventListener("resize", () => {
        if(!modal.classList.contains('hidden')) {
            resizeCanvas();
        }
    });

    // --- Button Logic ---
    const closeModal = () => modal.classList.add('hidden');
    
    cancelBtn.addEventListener('click', closeModal);
    
    clearBtn.addEventListener('click', () => {
        if(signaturePad) signaturePad.clear();
    });

    saveBtn.addEventListener('click', () => {
        if (!signaturePad || signaturePad.isEmpty()) {
            alert("Please provide a signature.");
            return;
        }
        
        // Save as Base64
        const dataURL = signaturePad.toDataURL('image/png');
        sigInput.value = dataURL;

        // Update UI
        preview.src = dataURL;
        preview.classList.remove('hidden');
        placeholder.classList.add('hidden'); // Hide the "Click here" text
        
        closeModal();
    });
});