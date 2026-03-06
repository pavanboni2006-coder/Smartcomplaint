// ============================================================
// Smart Complaint Management System - script.js
// Client-side JavaScript for search, filter, validation, etc.
// ============================================================


// ============================================================
// 1. AUTO-DISMISS FLASH MESSAGES after 4 seconds
// ============================================================
document.addEventListener('DOMContentLoaded', function () {

    // Find all flash messages in the DOM
    const flashMessages = document.querySelectorAll('.flash');

    flashMessages.forEach(function (msg) {
        // Remove each flash after 4000ms (4 seconds)
        setTimeout(function () {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.4s';
            setTimeout(function () { msg.remove(); }, 400);
        }, 4000);
    });

});


// ============================================================
// 2. LIVE SEARCH FILTER on complaint tables (client-side)
//    Works on .complaint-row rows inside #complaintsTable
// ============================================================
const searchInput = document.getElementById('searchInput');

if (searchInput) {
    searchInput.addEventListener('input', function () {
        // Get the typed value in lowercase
        const query = this.value.toLowerCase().trim();

        // Select all table rows with class .complaint-row
        const rows = document.querySelectorAll('tbody tr');
        let visibleCount = 0;

        rows.forEach(function (row) {
            // Check if any cell text contains the query
            const rowText = row.textContent.toLowerCase();
            if (rowText.includes(query)) {
                row.style.display = '';  // Show row
                visibleCount++;
            } else {
                row.style.display = 'none';  // Hide row
            }
        });

        // Update the record count display
        const countEl = document.getElementById('record-count');
        if (countEl) {
            countEl.textContent = `Showing ${visibleCount} complaints`;
        }
    });
}


// ============================================================
// 3. REGISTER FORM - Confirm password check
//    Shows an error message below the confirm field if mismatch
// ============================================================
const registerForm = document.getElementById('registerForm');

if (registerForm) {
    const passwordField = document.getElementById('password');
    const confirmField = document.getElementById('confirm_password');
    const pwError = document.getElementById('pw-error');

    // Check on every keystroke in the confirm field
    confirmField.addEventListener('input', function () {
        if (passwordField.value !== confirmField.value) {
            pwError.style.display = 'block';
            confirmField.setCustomValidity('Passwords do not match');
        } else {
            pwError.style.display = 'none';
            confirmField.setCustomValidity('');  // Clear validation error
        }
    });

    // Final check on form submit
    registerForm.addEventListener('submit', function (e) {
        if (passwordField.value !== confirmField.value) {
            e.preventDefault();  // Stop form submission
            pwError.style.display = 'block';
        }
    });
}


// ============================================================
// 4. FILE UPLOAD PREVIEW
//    Shows the selected filename below the file input
// ============================================================
const photoInput = document.getElementById('photo');
const filePreview = document.getElementById('file-preview');

if (photoInput && filePreview) {
    photoInput.addEventListener('change', function () {
        const file = this.files[0];  // Get selected file

        if (file) {
            // Validate file size (5MB max = 5 * 1024 * 1024 bytes)
            const maxSize = 5 * 1024 * 1024;
            if (file.size > maxSize) {
                filePreview.style.display = 'block';
                filePreview.style.background = '#fee2e2';
                filePreview.style.color = '#991b1b';
                filePreview.textContent = '❌ File too large! Maximum size is 5MB.';
                photoInput.value = '';  // Clear the input
                return;
            }

            // Show file name if valid
            filePreview.style.display = 'block';
            filePreview.style.background = '';
            filePreview.style.color = '';
            filePreview.textContent = `📎 Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        } else {
            filePreview.style.display = 'none';
        }
    });
}


// ============================================================
// 5. CHARACTER COUNTER for the complaint description textarea
// ============================================================
const descArea = document.getElementById('description');
const descCounter = document.getElementById('desc-counter');

if (descArea && descCounter) {
    // Update count on every keypress
    descArea.addEventListener('input', function () {
        const len = this.value.length;
        const max = this.getAttribute('maxlength') || 2000;
        descCounter.textContent = `${len} / ${max} characters`;

        // Turn red when near the limit
        if (len > max - 100) {
            descCounter.style.color = '#dc2626';
        } else {
            descCounter.style.color = '';
        }
    });
}


// ============================================================
// 6. CONFIRM DELETE (backup JS confirm for delete buttons)
//    The admin_complaints.html also uses onsubmit="return confirm()"
//    This is an additional safety layer for any other delete forms.
// ============================================================
document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
        const message = form.getAttribute('data-confirm') || 'Are you sure?';
        if (!window.confirm(message)) {
            e.preventDefault();
        }
    });
});
