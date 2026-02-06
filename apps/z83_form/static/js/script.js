 // --- 1. WIZARD LOGIC ---
function showStep(step) {
    // Hide all
    document.querySelectorAll('.form-step').forEach(el => el.classList.add('hidden'));
    // Show target
    document.querySelector(`.form-step[data-step="${step}"]`).classList.remove('hidden');
    // Update Bar
    const progress = (step / 4) * 100;
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
            if (el) el.value = data[key];
        });
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
});