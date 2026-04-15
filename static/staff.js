let staffData = { staffMembers: [] };

loadStaffData();

function loadStaffData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      staffData = data;
      populateFilters();
      renderStaffTable();
      bindStaffEvents();
    });
}

function bindStaffEvents() {
  document.getElementById("departmentFilter").onchange = renderStaffTable;
  document.getElementById("roleFilter").onchange = renderStaffTable;
  document.getElementById("addStaffBtn").onclick = addNewStaff;
}

function populateFilters() {
  const departmentFilter = document.getElementById("departmentFilter");
  const roleFilter = document.getElementById("roleFilter");

  departmentFilter.innerHTML = `<option value="All">All Departments</option>`;
  roleFilter.innerHTML = `<option value="All">All Roles</option>`;

  const departments = [...new Set(staffData.staffMembers.map(m => m.department))];
  const roles = [...new Set(staffData.staffMembers.map(m => m.role))];

  departments.forEach(item => {
    departmentFilter.innerHTML += `<option value="${item}">${item}</option>`;
  });

  roles.forEach(item => {
    roleFilter.innerHTML += `<option value="${item}">${item}</option>`;
  });
}

function renderStaffTable() {
  const tbody = document.getElementById("staffTableBody");
  const department = document.getElementById("departmentFilter").value;
  const role = document.getElementById("roleFilter").value;

  const filtered = staffData.staffMembers.filter(member => {
    const departmentMatch = department === "All" || member.department === department;
    const roleMatch = role === "All" || member.role === role;
    return departmentMatch && roleMatch;
  });

  tbody.innerHTML = "";

  filtered.forEach(member => {
    const employeeId = member.employee_id || member.employeeId;
    const lastLogin = member.last_login || member.lastLogin;
    const isActive = member.status === "Active";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="staff-member-cell">
          <div class="staff-avatar">${getInitials(member.name)}</div>
          <div>${member.name}</div>
        </div>
      </td>
      <td>${employeeId}</td>
      <td>${member.department}</td>
      <td><span class="role-pill ${getRoleClass(member.role)}">${member.role}</span></td>
      <td>
        <span class="status-indicator">
          <span class="status-dot ${isActive ? "active" : "inactive"}"></span>
          ${member.status}
        </span>
      </td>
      <td>${lastLogin}</td>
      <td>
        <span class="action-link action-edit" onclick="editStaff('${employeeId}', '${member.name}', '${member.role}')">EDIT</span>
        <span class="action-link ${isActive ? "action-danger" : "action-success"}" onclick="toggleStatus('${employeeId}')">
          ${isActive ? "DEACTIVATE" : "REACTIVATE"}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function addNewStaff() {
  const name = prompt("Enter staff full name:");
  if (!name) return;

  const department = prompt("Enter department:", "Front Desk");
  if (!department) return;

  const role = prompt("Enter role:", "Staff");
  if (!role) return;

  fetch("/api/staff/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, department, role })
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        alert("Staff added successfully.");
        loadStaffData();
      }
    });
}

function editStaff(employeeId, name, currentRole) {
  const newRole = prompt(`Edit role for ${name}:`, currentRole);
  if (!newRole) return;

  fetch("/api/staff/edit-role", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employeeId, role: newRole })
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        alert("Role updated successfully.");
        loadStaffData();
      }
    });
}

function toggleStatus(employeeId) {
  fetch("/api/staff/toggle-status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employeeId })
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        loadStaffData();
      }
    });
}

function getInitials(name) {
  return name.split(" ").map(part => part[0]).join("").substring(0, 2).toUpperCase();
}

function getRoleClass(role) {
  return `role-${role.toLowerCase().replace(/\s+/g, "-")}`;
}