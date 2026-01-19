// Avatar preview
const avatarInput = document.getElementById('avatarInput');
const avatarPreview = document.getElementById('avatarPreview');
if (avatarInput) {
    avatarInput.addEventListener('change', function (e) {
        const [file] = e.target.files;
        if (file && file.type.startsWith('image/')) {
            if (file.size < 2 * 1024 * 1024) avatarPreview.src = URL.createObjectURL(file);
            else alert('File quá lớn, dưới 2MB!');
        }
    });
}

// Password toggle
const passwordInput = document.getElementById('passwordInput');
const confirmGroup = document.getElementById('confirmPasswordGroup');

passwordInput.addEventListener('input', function () {
    if (passwordInput.value.length > 0) {
        confirmGroup.style.display = 'block'; // show confirm password
    } else {
        confirmGroup.style.display = 'none'; // hide confirm password nếu password trống
        document.getElementById('confirmPasswordInput').value = ''; // reset confirm password
    }
});

// Toggle password function
function togglePassword() {
    const icon = document.querySelector('#passwordInput + .password-toggle i');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

function toggleConfirmPassword() {
    const confirmInput = document.getElementById('confirmPasswordInput');
    const icon = document.querySelector('#confirmPasswordInput + .password-toggle i');
    if (confirmInput.type === 'password') {
        confirmInput.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        confirmInput.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}


// Auto show toasts
var toastElList = [].slice.call(document.querySelectorAll('.toast'));
toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl, {delay: 3000}).show();
});

const avatarUploadBtn = document.getElementById('avatarUploadBtn');

avatarUploadBtn.addEventListener('click', () => {
    avatarInput.click();
});

avatarInput.addEventListener('change', function (e) {
    const [file] = e.target.files;
    if (file && file.type.startsWith('image/')) {
        if (file.size < 2 * 1024 * 1024) {
            avatarPreview.src = URL.createObjectURL(file);
        } else {
            alert('File quá lớn, dưới 2MB!');
        }
    }
});