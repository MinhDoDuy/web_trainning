/* ===============================
   Avatar upload + preview (<= 4.2MB)
================================ */
const avatarInput = document.getElementById('avatarInput');
const avatarPreview = document.getElementById('avatarPreview');
const avatarUploadBtn = document.getElementById('avatarUploadBtn');

const MAX_AVATAR_SIZE = 4.2 * 1024 * 1024;

if (avatarUploadBtn && avatarInput) {
    avatarUploadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        avatarInput.click();
    });
}

if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            avatarInput.value = '';
            return;
        }

        if (file.size > MAX_AVATAR_SIZE) {
            avatarInput.value = '';
            return;
        }

        // cleanup old preview
        if (avatarPreview.dataset.url) {
            URL.revokeObjectURL(avatarPreview.dataset.url);
        }

        const previewURL = URL.createObjectURL(file);
        avatarPreview.src = previewURL;
        avatarPreview.dataset.url = previewURL;
    });
}

/* ===============================
   Password + Confirm logic
================================ */
const passwordInput = document.getElementById('passwordInput');
const confirmGroup = document.getElementById('confirmPasswordGroup');
const confirmPasswordInput = document.getElementById('confirmPasswordInput');

if (passwordInput && confirmGroup) {
    passwordInput.addEventListener('input', () => {
        if (passwordInput.value.trim()) {
            confirmGroup.style.display = 'block';
        } else {
            confirmGroup.style.display = 'none';
            confirmPasswordInput.value = '';
            confirmPasswordInput.classList.remove('is-invalid');
        }
    });
}

// remove error when user types again
if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', () => {
        confirmPasswordInput.classList.remove('is-invalid');
    });
}

/* ===============================
   Initial form state (dirty check)
================================ */
const usernameInput = document.getElementById('username');

const initialState = {
    username: usernameInput ? usernameInput.value : '',
};

/* ===============================
   Check form changed
================================ */
function hasFormChanged() {
    const usernameChanged =
        usernameInput && usernameInput.value !== initialState.username;

    const avatarChanged =
        avatarInput && avatarInput.files && avatarInput.files.length > 0;

    const passwordChanged =
        passwordInput && passwordInput.value.trim() !== '';

    return usernameChanged || avatarChanged || passwordChanged;
}

/* ===============================
   Form submit + confirm modal
================================ */
const editProfileForm = document.getElementById('editProfileForm');
const openSaveBtn = document.getElementById('openConfirmSave');
const confirmSaveBtn = document.getElementById('confirmSaveBtn');
const saveModal = document.getElementById('confirmSaveModal');
const noChangeToast = document.getElementById('noChangeToast');
const confirmErrorIcon = document.getElementById('confirmPasswordErrorIcon');

if (
    editProfileForm &&
    openSaveBtn &&
    confirmSaveBtn &&
    saveModal &&
    passwordInput &&
    confirmPasswordInput
) {

    // Click Save → validate → open modal
    openSaveBtn.addEventListener('click', () => {

        // ❌ No change
        if (!hasFormChanged()) {
            if (noChangeToast) {
                new bootstrap.Toast(noChangeToast, {delay: 3000}).show();
            }
            return;
        }

        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', () => {
                confirmPasswordInput.classList.remove('is-invalid');
                confirmErrorIcon?.classList.add('d-none');
            });
        }

        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (password && !confirmPassword) {
            confirmPasswordInput.focus();
            return;
        }

        if (password && confirmPassword && password !== confirmPassword) {
            // Show flash toast
            const toastEl = document.getElementById('passwordMismatchToast');
            if (toastEl) {
                new bootstrap.Toast(toastEl, {delay: 3000}).show();
            }

            confirmPasswordInput.focus();
            return;
        }


        new bootstrap.Modal(saveModal).show();
    });

    // Confirm Save
    confirmSaveBtn.addEventListener('click', () => {
        editProfileForm.submit();
    });
}

/* ===============================
   Toggle password visibility
================================ */
function togglePassword() {
    if (!passwordInput) return;

    const icon = document.querySelector('#passwordInput + .password-toggle i');
    if (!icon) return;

    const hidden = passwordInput.type === 'password';
    passwordInput.type = hidden ? 'text' : 'password';

    icon.classList.toggle('bi-eye', !hidden);
    icon.classList.toggle('bi-eye-slash', hidden);
}

function toggleConfirmPassword() {
    if (!confirmPasswordInput) return;

    const icon = document.querySelector('#confirmPasswordInput + .password-toggle i');
    if (!icon) return;

    const hidden = confirmPasswordInput.type === 'password';
    confirmPasswordInput.type = hidden ? 'text' : 'password';

    icon.classList.toggle('bi-eye', !hidden);
    icon.classList.toggle('bi-eye-slash', hidden);
}

/* ===============================
   Auto show Bootstrap flash toasts
================================ */
// document.querySelectorAll('.toast').forEach(toastEl => {
//     new bootstrap.Toast(toastEl, {delay: 3000}).show();
// });
