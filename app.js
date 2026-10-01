/**
 * Student Records Management System - Frontend JavaScript
 * Handles CRUD operations via REST API fetch requests.
 */

// State
let currentDeleteId = null;
let searchDebounceTimer = null;

// DOM Elements
const studentTableBody = document.getElementById("student-table-body");
const createForm = document.getElementById("create-student-form");
const editForm = document.getElementById("edit-student-form");
const editModal = document.getElementById("edit-modal");
const deleteModal = document.getElementById("delete-modal");
const searchInput = document.getElementById("search-input");
const deptFilter = document.getElementById("dept-filter");
const btnRefresh = document.getElementById("btn-refresh");

const totalStudentsVal = document.getElementById("total-students-val");
const avgCgpaVal = document.getElementById("avg-cgpa-val");
const totalDeptsVal = document.getElementById("total-depts-val");
const dbEngineBadge = document.getElementById("db-engine-badge");

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
    loadStats();
    attachEventListeners();
});

function attachEventListeners() {
    // Create Student Form Submit
    createForm.addEventListener("submit", handleCreateStudent);

    // Edit Student Form Submit
    editForm.addEventListener("submit", handleUpdateStudent);

    // Edit Modal Close Handlers
    document.getElementById("btn-close-edit").addEventListener("click", () => closeModal(editModal));
    document.getElementById("btn-cancel-edit").addEventListener("click", () => closeModal(editModal));

    // Delete Modal Handlers
    document.getElementById("btn-close-delete").addEventListener("click", () => closeModal(deleteModal));
    document.getElementById("btn-cancel-delete").addEventListener("click", () => closeModal(deleteModal));
    document.getElementById("btn-confirm-delete").addEventListener("click", handleConfirmDelete);

    // Refresh Button
    btnRefresh.addEventListener("click", () => {
        loadStudents();
        loadStats();
        showToast("Refreshed records from database", "info");
    });

    // Real-time Search Input (Debounced 300ms)
    searchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            loadStudents();
        }, 300);
    });

    // Department Filter Dropdown
    deptFilter.addEventListener("change", () => {
        loadStudents();
    });

    // Close modals on clicking overlay backdrop
    window.addEventListener("click", (e) => {
        if (e.target === editModal) closeModal(editModal);
        if (e.target === deleteModal) closeModal(deleteModal);
    });
}

// ========================================================
// [READ] Load Students from Database
// ========================================================
async function loadStudents() {
    const search = searchInput.value.trim();
    const department = deptFilter.value;

    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (department) params.append("department", department);

    try {
        const res = await fetch(`/api/students?${params.toString()}`);
        const result = await res.json();

        if (result.status === "success") {
            renderTable(result.data);
            if (result.engine) {
                updateEngineBadge(result.engine);
            }
        } else {
            showToast(result.message || "Failed to fetch student records", "error");
        }
    } catch (err) {
        console.error("Fetch error:", err);
        studentTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger" style="padding: 2rem; color: #ef4444;">
                    ⚠️ Error communicating with server. Ensure Flask app is running.
                </td>
            </tr>
        `;
    }
}

// Render records into Table
function renderTable(students) {
    if (!students || students.length === 0) {
        studentTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center" style="padding: 2.5rem; color: #64748b;">
                    No student records found in database. Try adding one from the left form!
                </td>
            </tr>
        `;
        return;
    }

    studentTableBody.innerHTML = students.map(student => {
        // CGPA Pill Class
        let cgpaClass = "cgpa-mid";
        if (student.cgpa >= 8.5) cgpaClass = "cgpa-high";
        else if (student.cgpa < 6.5) cgpaClass = "cgpa-low";

        return `
            <tr>
                <td><span class="roll-badge">${escapeHtml(student.roll_no)}</span></td>
                <td>
                    <div class="student-name">${escapeHtml(student.name)}</div>
                    <div class="student-email">${escapeHtml(student.email)}</div>
                </td>
                <td><span class="dept-tag">${escapeHtml(student.department)}</span></td>
                <td>Sem ${student.semester}</td>
                <td><span class="cgpa-pill ${cgpaClass}">${parseFloat(student.cgpa).toFixed(2)}</span></td>
                <td>
                    <div class="action-btns">
                        <button class="btn btn-secondary btn-sm" onclick="openEditModal(${student.id})">
                            ✏️ Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="openDeleteModal(${student.id}, '${escapeQuote(student.name)}', '${escapeQuote(student.roll_no)}')">
                            🗑️ Delete
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

// ========================================================
// [CREATE] Add New Student
// ========================================================
async function handleCreateStudent(e) {
    e.preventDefault();

    const submitBtn = document.getElementById("btn-submit-create");
    submitBtn.disabled = true;
    submitBtn.innerText = "Saving to Database...";

    const studentData = {
        roll_no: document.getElementById("roll_no").value.trim(),
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        department: document.getElementById("department").value,
        semester: parseInt(document.getElementById("semester").value, 10),
        cgpa: parseFloat(document.getElementById("cgpa").value)
    };

    try {
        const res = await fetch("/api/students", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(studentData)
        });

        let result = {};
        try {
            result = await res.json();
        } catch (parseErr) {
            result = { message: "Server returned a non-JSON response." };
        }

        if (res.ok && result.status === "success") {
            showToast(result.message, "success");
            createForm.reset();
            loadStudents();
            loadStats();
        } else {
            showToast(result.message || "Failed to create student.", "error");
        }
    } catch (err) {
        console.error("Create error:", err);
        showToast("Network error: Could not reach server.", "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Save to Database";
    }
}

// ========================================================
// [UPDATE] Edit Student
// ========================================================
async function openEditModal(studentId) {
    try {
        const res = await fetch(`/api/students/${studentId}`);
        const result = await res.json();

        if (res.ok && result.status === "success") {
            const s = result.data;
            document.getElementById("edit-id").value = s.id;
            document.getElementById("edit-roll_no").value = s.roll_no;
            document.getElementById("edit-name").value = s.name;
            document.getElementById("edit-email").value = s.email;
            document.getElementById("edit-department").value = s.department;
            document.getElementById("edit-semester").value = s.semester;
            document.getElementById("edit-cgpa").value = s.cgpa;

            openModal(editModal);
        } else {
            showToast(result.message || "Unable to fetch student details.", "error");
        }
    } catch (err) {
        console.error("Edit fetch error:", err);
        showToast("Error loading student for edit.", "error");
    }
}

async function handleUpdateStudent(e) {
    e.preventDefault();

    const studentId = document.getElementById("edit-id").value;
    const updatedData = {
        roll_no: document.getElementById("edit-roll_no").value.trim(),
        name: document.getElementById("edit-name").value.trim(),
        email: document.getElementById("edit-email").value.trim(),
        department: document.getElementById("edit-department").value,
        semester: parseInt(document.getElementById("edit-semester").value, 10),
        cgpa: parseFloat(document.getElementById("edit-cgpa").value)
    };

    try {
        const res = await fetch(`/api/students/${studentId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedData)
        });

        let result = {};
        try {
            result = await res.json();
        } catch (parseErr) {
            result = { message: "Server returned a non-JSON response." };
        }

        if (res.ok && result.status === "success") {
            showToast(result.message, "success");
            closeModal(editModal);
            loadStudents();
            loadStats();
        } else {
            showToast(result.message || "Failed to update record.", "error");
        }
    } catch (err) {
        console.error("Update error:", err);
        showToast("Network error: Could not reach server.", "error");
    }
}

// ========================================================
// [DELETE] Delete Student
// ========================================================
function openDeleteModal(studentId, name, rollNo) {
    currentDeleteId = studentId;
    document.getElementById("delete-student-name").innerText = name;
    document.getElementById("delete-student-roll").innerText = rollNo;
    openModal(deleteModal);
}

async function handleConfirmDelete() {
    if (!currentDeleteId) return;

    const confirmBtn = document.getElementById("btn-confirm-delete");
    confirmBtn.disabled = true;
    confirmBtn.innerText = "Deleting...";

    try {
        const res = await fetch(`/api/students/${currentDeleteId}`, {
            method: "DELETE"
        });

        const result = await res.json();

        if (res.ok && result.status === "success") {
            showToast(result.message, "success");
            closeModal(deleteModal);
            loadStudents();
            loadStats();
        } else {
            showToast(result.message || "Failed to delete student.", "error");
        }
    } catch (err) {
        console.error("Delete error:", err);
        showToast("Network error. Could not delete record.", "error");
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerText = "Yes, Delete";
        currentDeleteId = null;
    }
}

// ========================================================
// [STATS] Dashboard Metrics
// ========================================================
async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        const result = await res.json();

        if (result.status === "success") {
            totalStudentsVal.innerText = result.total_students;
            avgCgpaVal.innerText = result.avg_cgpa.toFixed(2);
            totalDeptsVal.innerText = (result.department_counts || []).length;
            updateEngineBadge(result.engine);
        }
    } catch (err) {
        console.error("Stats fetch error:", err);
    }
}

function updateEngineBadge(engine) {
    if (engine === "MYSQL") {
        dbEngineBadge.innerText = "⚡ Connected: MySQL Database";
        dbEngineBadge.className = "badge badge-mysql";
    } else {
        dbEngineBadge.innerText = "📁 Connected: SQLite (Auto Fallback)";
        dbEngineBadge.className = "badge badge-sqlite";
    }
}

// ========================================================
// UI Utilities
// ========================================================
function openModal(modal) {
    modal.classList.add("active");
}

function closeModal(modal) {
    modal.classList.remove("active");
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type === "success" ? "toast-success" : type === "error" ? "toast-error" : ""}`;
    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeQuote(str) {
    if (!str) return "";
    return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
