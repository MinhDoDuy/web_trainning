// Dynamic delete link
var deleteModal = document.getElementById('deleteModal');
deleteModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;
    var url = button.getAttribute('data-user-url');
    document.getElementById('confirmDeleteBtn').setAttribute('href', url);
});

// Toast
document.querySelectorAll('.toast').forEach(toastEl => {
    new bootstrap.Toast(toastEl, {delay: 3000}).show();
});

// Clear input
function clearInput(id) {
    document.getElementById(id).value = '';
    document.getElementById(id).focus();
    if (id === 'userSearch') applyUserFilter();
}

// Set Role
function setRole(value) {
    document.getElementById('roleInput').value = value;
    document.getElementById('roleDropdown').innerText = value.charAt(0).toUpperCase() + value.slice(1);
}

// ===============================
// Live search for users (admin always visible)
// ===============================
const userSearchInput = document.getElementById("userSearch");

function applyUserFilter() {
    const keyword = userSearchInput.value.toLowerCase().trim();
    const allRows = Array.from(document.querySelectorAll("#userTableBody tr.user-row"));

    allRows.forEach(row => {
        const role = row.dataset.role;
        const username = row.children[1].innerText.toLowerCase();

        if (role === "admin") {
            row.style.display = ""; // Admin luôn hiển thị
        } else {
            row.style.display = username.includes(keyword) ? "" : "none";
        }
    });
}

if (userSearchInput) userSearchInput.addEventListener("input", applyUserFilter);

// ------------------------------
// Dynamic delete modal
// ------------------------------
var deleteModal = document.getElementById('deleteModal');

deleteModal.addEventListener('show.bs.modal', function(event) {
    var button = event.relatedTarget; // nút delete click
    var userName = button.getAttribute('data-user-name');
    var url = button.getAttribute('data-user-url');
    var tasks = JSON.parse(button.getAttribute('data-user-tasks'));

    // Hiển thị tên user
    document.getElementById('deleteUserMessage').innerHTML =
        `Are you sure you want to delete <strong>${userName}</strong>?`;

    // Set href nút Delete
    document.getElementById('confirmDeleteBtn').setAttribute('href', url);

    // Render danh sách task nếu có
    var ul = document.getElementById('userTaskList');
    ul.innerHTML = ""; // clear
    if(tasks.length > 0){
        tasks.forEach(function(task){
            var li = document.createElement('li');
            li.classList.add('list-group-item');
            li.innerHTML = `<i class="bi bi-check-circle-fill text-success me-1"></i> ${task.title} (${task.status})`;
            ul.appendChild(li);
        });
        ul.classList.remove('d-none');
    } else {
        ul.classList.add('d-none');
    }
});

