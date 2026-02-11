 // --- 1. WIZARD LOGIC ---
function showStep(step) {
    // Hide all
    document.querySelectorAll('.form-step').forEach(el => el.classList.add('hidden'));
    // Show target
    document.querySelector(`.form-step[data-step="${step}"]`).classList.remove('hidden');
    // Update Bar
    const progress = (step / 6) * 100;
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



// Wait for the HTML to be fully loaded
document.addEventListener("DOMContentLoaded", function() {

    // --- 2. AUTO-SAVE LOGIC ---
    const form = document.getElementById('z83Form');
    const status = document.getElementById('saveStatus');

    // Load
    const saved = localStorage.getItem('z83_draft');
    if (saved) {

        const data = JSON.parse(saved);

        Object.keys(data).forEach(key => {
            const el = form.elements[key];
            if (el){
                if (el.type === 'checkbox') {
                    el.checked = data[key] == el.value; // Check the box if the saved value matches the checkbox value
                }else{
                    el.value = data[key];
                }
            }

            // Trigger click event on contactOptions to ensure correct display of contact details field
            if (key === 'contactOption') {
                // map contactOption value to the corresponding input field
                var inputMap = {
                    'email': 'Email',
                    'post': 'PostalAddress',
                    'fax': 'FaxNumber',
                    'phone': 'Phone'
                };
                const event = new Event('change', { bubbles: true });
                console.log(el.value);
                const inputElement = document.querySelector(`input[value="${el.value}"]`);
                inputElement.dispatchEvent(event);

                // populate the contact details field based on the saved contact option
                const contactFieldId = inputMap[el.value];

                // Ensure the contact details field exists on the DOM before trying to set its value
                waitForElement(`input[name="${contactFieldId}"]`).then(element => {
                    console.log("Element found:", element);
                    element.value = data[contactFieldId] || '';
                });
            }
        });
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
        privateInput.addEventListener('input', function() {
            privateSpan.textContent = this.value;
        });
    }

    // 2. Public Sector Listener
    if (publicInput && publicSpan) {
        publicInput.addEventListener('input', function() {
            publicSpan.textContent = this.value;
        });
    }

    // Language profciency logic: ensures not more than 5 languages selected and only profiencies for selected languages are enabled.
    document.querySelectorAll('.language-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
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
        addQualsBtn.addEventListener('click', function() {
            let count = parseInt(this.getAttribute('data-quals'));
            if (count >= 4) {
                this.setAttribute('disabled', 'disabled');
            } else {
                count++;
                this.setAttribute('data-quals', count);
            }
        });
    }
});