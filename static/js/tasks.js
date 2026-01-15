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
function setStatus(hiddenInputId, el) {
    const input = document.getElementById(hiddenInputId);
    if (!input) return;

    const dropdown = el.closest('.dropdown').querySelector('button');
    input.value = el.innerText.toLowerCase();
    if (dropdown) dropdown.innerText = el.innerText;
}

function setEditStatus(id, value) {
    const input = document.getElementById('editStatusInput' + id);
    const dropdown = document.getElementById('editStatusDropdown' + id);
    if (input) input.value = value;
    if (dropdown) dropdown.innerText = value.charAt(0).toUpperCase() + value.slice(1);
}


/* Update color cho select */
const select = document.querySelector('.pretty-status');
if (select) {
    function updateColor() {
        select.classList.remove('completed', 'pending');
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
                    labels: ['Completed', 'Pending'],
                    datasets: [{
                        label: 'Tasks Status',
                        data: [
                            Number(document.body.dataset.completed || 0),
                            Number(document.body.dataset.pending || 0)
                        ],
                        backgroundColor: ['#28a745', '#ffc107']
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
        const da = Number(a.dataset.created);
        const db = Number(b.dataset.created);
        return sortOrder.value === "newest" ? db - da : da - db;
    });

    sorted.forEach(r => tbody.appendChild(r));
}

/* =========================
   7️Dropdown kiểu Add Task cho Filter + Sort
========================= */

// Status Filter Dropdown
function setFilterStatus(value, el) {
    document.getElementById('statusFilter').value = value;
    document.getElementById('filterStatusDropdown').innerText = el.innerText;

    // Remove selected class từ các item khác
    document.querySelectorAll('.filter-dropdown .dropdown-item').forEach(i => i.classList.remove('selected'));
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

function setAssignedUser(id, username, el) {
    // Thay text button dropdown
    const dropdownBtn = document.getElementById('assignedUserDropdown');
    dropdownBtn.textContent = username;

    // Lưu id vào input ẩn
    const hiddenInput = document.getElementById('assignedUserInput');
    hiddenInput.value = id;

    // Reset search input
    document.getElementById('userSearchInput').value = '';

    // Close dropdown menu (tùy chọn, cần bootstrap 5 JS)
    const dropdown = bootstrap.Dropdown.getInstance(dropdownBtn);
    if (dropdown) dropdown.hide();
}

const addTaskForm = document.getElementById('addTaskForm');

if (addTaskForm) {
    addTaskForm.addEventListener('submit', function(e) {
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
            const bsToast = new bootstrap.Toast(toastEl, { delay: 3000 });
            bsToast.show();

            // Tự remove sau khi hết
            toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());

            // focus vào ô trống đầu tiên
            if (!titleInput.value.trim()) titleInput.focus();
            else descInput.focus();
        }
    });
}
