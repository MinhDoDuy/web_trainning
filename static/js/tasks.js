/* =========================
   1️Toasts
========================= */
document.querySelectorAll('.toast').forEach(toastEl => {
    new bootstrap.Toast(toastEl, {delay: 3000}).show();
});

/* =========================
2️Clear Input Function
========================= */
function clearInput(id) {
    const input = document.getElementById(id);
    if (!input) return;
    input.value = '';
    input.focus();
    applyFilters(); // hiển thị lại tất cả tasks
}

/* =========================
   3️Status Dropdowns (Add/Edit Task)
========================= */
function setStatus(inputId, el, isDefault = false) {
    const input = document.getElementById(inputId);

    let dot, textEl;
    if (inputId === 'statusInputAdmin') {
        dot = document.getElementById('statusDotAdmin');
        textEl = document.getElementById('statusTextAdmin');
    } else if (inputId === 'statusInputUser') {
        dot = document.getElementById('statusDotUser');
        textEl = document.getElementById('statusTextUser');
    }

    if (isDefault || !el) {
        input.value = '';
        textEl.textContent = 'Select Status';
        dot.classList.add('d-none');
    } else {
        input.value = el.dataset.value;
        textEl.textContent = el.textContent.trim();
        dot.classList.remove('d-none');

        switch (el.dataset.value) {
            case 'todo':
                dot.className = 'status-dot bg-secondary';
                break;
            case 'doing':
                dot.className = 'status-dot bg-warning';
                break;
            case 'done':
                dot.className = 'status-dot bg-success';
                break;
            default:
                dot.className = 'status-dot d-none';
        }
    }
}

// function setEditStatus(id, value) {
//     const input = document.getElementById('editStatusInput' + id);
//     const dropdown = document.getElementById('editStatusDropdown' + id);
//     if (input) input.value = value;
//     if (dropdown) dropdown.innerText = value.charAt(0).toUpperCase() + value.slice(1);
// }


/* Update color cho select */
const select = document.querySelector('.pretty-status');
if (select) {
    function updateColor() {
        select.classList.remove('todo', 'doing', 'done');
        select.classList.add(select.value);
    }

    updateColor();
    select.addEventListener('change', updateColor);
}

/* =========================
   4️Delete Modal Dynamic Link
========================= */
const deleteModal = document.getElementById('deleteModal');
if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const url = button.getAttribute('data-task-url');
        const taskTitle = button.getAttribute('data-task-title'); // thêm attr task title
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        const modalBody = document.getElementById('deleteModalBody');

        if (confirmBtn) confirmBtn.setAttribute('href', url);
        if (modalBody) modalBody.innerHTML = `Are you sure you want to delete task <strong>${taskTitle}</strong>?`;
    });
}


/* =========================
   5️Chart.js Task Overview
========================= */
const chartModal = document.getElementById('chartModal');
let modalChartInstance = null;

if (chartModal) {
    chartModal.addEventListener('shown.bs.modal', function () {
        if (!modalChartInstance) {
            const ctx = document.getElementById('taskChart').getContext('2d');
            modalChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['To Do', 'Doing', 'Done'],
                    datasets: [{
                        data: [
                            Number(document.body.dataset.todo || 0),
                            Number(document.body.dataset.doing || 0),
                            Number(document.body.dataset.done || 0)
                        ],
                        backgroundColor: ['#6c757d', '#FFCC00', '#28a745']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        legend: {position: 'bottom'},
                        tooltip: {mode: 'index'}
                    }
                }
            });
        }
    });
}

/* =========================
   6️Search / Filter / Sort
========================= */
const searchInput = document.getElementById("taskSearch");
const statusFilter = document.getElementById("statusFilter"); // hidden input
const sortOrder = document.getElementById("sortOrder");       // hidden input

function normalize(text) {
    return text.toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

function applyFilters() {
    const keyword = normalize(searchInput.value);
    const status = statusFilter.value;

    const rows = Array.from(document.querySelectorAll("table tbody tr"));

    rows.forEach(row => {
        const titleEl = row.querySelector(".task-title");
        if (!titleEl) return;

        const title = normalize(titleEl.innerText);
        const rowStatus = row.dataset.status;

        const matchText = title.includes(keyword);
        const matchStatus = (status === "all" || status === rowStatus);

        row.style.display = (matchText && matchStatus) ? "" : "none";
    });

    sortRows();
}

function sortRows() {
    const tbody = document.querySelector("table tbody");
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll("tr"))
        .filter(r => r.style.display !== "none");

    const sorted = rows.sort((a, b) => {
        const da = Number(a.dataset.created) || 0;
        const db = Number(b.dataset.created) || 0;

        if (sortOrder.value === "newest") {
            return db - da; // lớn nhất trước → mới nhất
        } else {
            return da - db; // nhỏ nhất trước → cũ nhất
        }
    });

    sorted.forEach((r, index) => {
        tbody.appendChild(r);
        const tdIndex = r.querySelector("td:first-child");
        if (tdIndex) {
            if (sortOrder.value === "newest") {
                // newest lên trên → cũ = 1, mới = n
                tdIndex.textContent = rows.length - index;
            } else {
                // oldest lên trên → cũ = 1, mới = n
                tdIndex.textContent = index + 1;
            }
        }
    });
}

/* =========================
   7️Dropdown kiểu Add Task cho Filter + Sort
========================= */

// Status Filter Dropdown
function setFilterStatus(value, el) {
    const statusInput = document.getElementById('statusFilter');
    const textEl = document.getElementById('filterStatusText');
    const dotEl = document.getElementById('filterStatusDot');

    statusInput.value = value;
    textEl.innerText = el.innerText.trim();

    // reset dot
    dotEl.className = 'status-dot';

    if (value === 'all') {
        dotEl.classList.add('d-none');
    } else {
        dotEl.classList.remove('d-none');
        dotEl.classList.add(value);
    }

    // selected style
    document.querySelectorAll('.filter-dropdown .dropdown-item')
        .forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');

    applyFilters();
}


function setSortOrder(value, el) {
    document.getElementById('sortOrder').value = value;
    document.getElementById('sortOrderDropdown').innerText = el.innerText;

    // Remove selected class từ các item khác
    document.querySelectorAll('.sort-dropdown .dropdown-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');

    applyFilters();
}

/* =========================
   8️Event Listeners
========================= */
if (searchInput) searchInput.addEventListener("input", applyFilters);

/* Hidden inputs thay vì select cũ, dropdown đã auto apply */
applyFilters();

function filterUsers() {
    const input = document.getElementById('userSearchInput');
    const filter = input.value.toLowerCase();
    const items = document.querySelectorAll('.dropdown-item.user-item');

    items.forEach(item => {
        const username = item.getAttribute('data-username').toLowerCase();
        if (username.includes(filter)) {
            item.style.display = "flex"; // show
        } else {
            item.style.display = "none"; // hide
        }
    });
}

function setAssignedUser(userId, username, el, isDefault = false) {
    document.getElementById('assignedUserInput').value = userId;
    const userText = document.getElementById('userText');
    const userDot = document.getElementById('userDot');

    userText.textContent = username;
    if (isDefault || !userId) {
        userDot.classList.add('d-none');
    } else {
        userDot.classList.remove('d-none');
        userDot.className = 'status-dot bg-primary'; // màu dot Assigned User
    }
}

const addTaskForm = document.getElementById('addTaskForm');

if (addTaskForm) {
    addTaskForm.addEventListener('submit', function (e) {
        const titleInput = addTaskForm.querySelector('input[name="title"]');
        const descInput = addTaskForm.querySelector('input[name="description"]');

        if (!titleInput.value.trim() || !descInput.value.trim()) {
            e.preventDefault(); // chặn submit

            // Tạo toast dynamically
            const toastContainer = document.querySelector('.toast-container');
            const toastEl = document.createElement('div');
            toastEl.className = 'toast align-items-center text-bg-warning border-0 mb-2';
            toastEl.role = 'alert';
            toastEl.ariaLive = 'assertive';
            toastEl.ariaAtomic = 'true';

            toastEl.innerHTML = `
                <div class="d-flex">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    <div class="toast-body">Please fill in Title and Description!</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

            toastContainer.appendChild(toastEl);
            const bsToast = new bootstrap.Toast(toastEl, {delay: 3000});
            bsToast.show();

            // Tự remove sau khi hết
            toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());

            // focus vào ô trống đầu tiên
            if (!titleInput.value.trim()) titleInput.focus();
            else descInput.focus();
        }
    });
}

function capitalizeWords(str) {
    return str.replace(/(^|\s)(\p{L})/gu, (_, space, char) => space + char.toUpperCase());
}


addTaskForm.addEventListener('submit', function () {
    const statusInput = document.getElementById('statusInputAdmin');
    if (statusInput) {
        statusInput.value = statusInput.value.toLowerCase();
    }

    // --- Gọi capitalize cho title & description ---
    const titleInput = addTaskForm.querySelector('input[name="title"]');
    const descInput = addTaskForm.querySelector('input[name="description"]');

    if (titleInput) titleInput.value = capitalizeWords(titleInput.value);
    if (descInput) descInput.value = capitalizeWords(descInput.value);
});


// TEST loader khi chạy local
setTimeout(() => {
    document.body.classList.add("loaded");
}, 5000);

