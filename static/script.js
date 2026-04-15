let hotelData = {
  rooms: [],
  housekeepers: [],
  loyaltyMembers: [],
  rewards: [],
  staffMembers: []
};

let selectedStatus = "";
let selectedReward = null;
let currentMember = null;

loadAllData();

function loadAllData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      hotelData = data;
      initializePage();
    })
    .catch(error => {
      console.error("Error loading data:", error);
    });
}

function initializePage() {
  if (document.getElementById("summaryCards")) {
    initHousekeepingPage();
  }

  if (document.getElementById("lookupMemberBtn")) {
    initLoyaltyPage();
  }

  if (document.getElementById("staffTableBody")) {
    initStaffPage();
  }
}

function postJson(url, payload) {
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  }).then(response => response.json());
}

/* HOUSEKEEPING */

function initHousekeepingPage() {
  renderSummary();
  renderRooms();
  populateRoomSelect();
  populateHousekeepers();

  document.querySelectorAll(".status-btn").forEach(button => {
    button.addEventListener("click", () => {
      selectedStatus = button.dataset.status;
      highlightStatusButton();
    });
  });

  document.getElementById("statusForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const roomNumber = document.getElementById("roomSelect").value;
    const housekeeper = document.getElementById("housekeeperSelect").value;
    const priority = document.getElementById("prioritySelect").value;
    const notes = document.getElementById("notes").value;

    if (!roomNumber) {
      alert("Please select a room.");
      return;
    }

    if (!selectedStatus) {
      alert("Please select a status.");
      return;
    }

    postJson("/api/rooms/update", {
      number: roomNumber,
      status: selectedStatus,
      housekeeper: housekeeper,
      priority: priority,
      notes: notes
    }).then(result => {
      if (result.success) {
        loadAllData();
        alert(`Room ${roomNumber} updated successfully.`);
      }
    });
  });

  document.getElementById("clearBtn").addEventListener("click", () => {
    document.getElementById("statusForm").reset();
    selectedStatus = "";
    highlightStatusButton();
  });
}

function renderSummary() {
  const summaryCards = document.getElementById("summaryCards");
  const counts = {
    Clean: hotelData.rooms.filter(room => room.status === "Clean").length,
    Dirty: hotelData.rooms.filter(room => room.status === "Dirty").length,
    "In Progress": hotelData.rooms.filter(room => room.status === "In Progress").length,
    Occupied: hotelData.rooms.filter(room => room.status === "Occupied").length
  };

  summaryCards.innerHTML = `
    <div class="card"><div class="count">${counts.Clean}</div><div class="label">Clean & Ready</div></div>
    <div class="card"><div class="count">${counts.Dirty}</div><div class="label">Require Cleaning</div></div>
    <div class="card"><div class="count">${counts["In Progress"]}</div><div class="label">In Progress</div></div>
    <div class="card"><div class="count">${counts.Occupied}</div><div class="label">Occupied</div></div>
  `;
}

function renderRooms() {
  const roomGrid = document.getElementById("roomGrid");
  roomGrid.innerHTML = "";

  hotelData.rooms.forEach(room => {
    const card = document.createElement("div");
    card.className = "room-card";
    card.innerHTML = `
      <div class="room-number">${room.number}</div>
      <div class="room-type">${room.type}</div>
      <span class="badge ${getStatusClass(room.status)}">${room.status.toUpperCase()}</span>
    `;

    card.addEventListener("click", () => {
      document.getElementById("roomSelect").value = room.number;
      document.getElementById("housekeeperSelect").value = room.housekeeper || "";
      document.getElementById("prioritySelect").value = room.priority || "Standard";
      document.getElementById("notes").value = room.notes || "";
      selectedStatus = room.status;
      highlightStatusButton();
    });

    roomGrid.appendChild(card);
  });
}

function populateRoomSelect() {
  const roomSelect = document.getElementById("roomSelect");
  roomSelect.innerHTML = `<option value="">— Select a room —</option>`;
  hotelData.rooms.forEach(room => {
    const option = document.createElement("option");
    option.value = room.number;
    option.textContent = room.number;
    roomSelect.appendChild(option);
  });
}

function populateHousekeepers() {
  const housekeeperSelect = document.getElementById("housekeeperSelect");
  housekeeperSelect.innerHTML = `<option value="">— Select —</option>`;
  hotelData.housekeepers.forEach(name => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    housekeeperSelect.appendChild(option);
  });
}

function getStatusClass(status) {
  if (status === "Clean") return "clean";
  if (status === "Dirty") return "dirty";
  if (status === "In Progress") return "progress";
  if (status === "Occupied") return "occupied";
  return "";
}

function highlightStatusButton() {
  document.querySelectorAll(".status-btn").forEach(button => {
    button.classList.toggle("active", button.dataset.status === selectedStatus);
  });
}

/* LOYALTY */

function initLoyaltyPage() {
  renderRewards();

  document.getElementById("lookupMemberBtn").addEventListener("click", lookupMember);

  document.getElementById("redeemForm").addEventListener("submit", function (e) {
    e.preventDefault();

    if (!currentMember) {
      alert("Please look up a member first.");
      return;
    }

    if (!selectedReward) {
      alert("Please select a reward.");
      return;
    }

    const reservationId = document.getElementById("reservationId").value.trim();
    const notes = document.getElementById("redemptionNotes").value.trim();

    postJson("/api/loyalty/redeem", {
      memberId: currentMember.id,
      rewardId: selectedReward.id,
      reservationId: reservationId,
      notes: notes,
      date: getTodayLabel()
    }).then(result => {
      if (!result.success) {
        alert(result.message || "Unable to process redemption.");
        return;
      }

      alert(`Redemption processed: ${selectedReward.title}`);
      selectedReward = null;
      document.getElementById("redeemForm").reset();
      highlightSelectedReward();
      reloadMember(currentMember.id, currentMember.lastName);
    });
  });

  document.getElementById("addPointsBtn").addEventListener("click", () => {
    if (!currentMember) {
      alert("Please look up a member first.");
      return;
    }

    postJson("/api/loyalty/add-points", {
      memberId: currentMember.id,
      points: 500,
      date: getTodayLabel()
    }).then(result => {
      if (!result.success) {
        alert(result.message || "Unable to add points.");
        return;
      }

      alert("500 points added manually.");
      reloadMember(currentMember.id, currentMember.lastName);
    });
  });

  const defaultMember = hotelData.loyaltyMembers[0];
  if (defaultMember) {
    document.getElementById("memberIdInput").value = defaultMember.id;
    document.getElementById("lastNameInput").value = defaultMember.lastName;
    currentMember = defaultMember;
    renderMemberProfile(currentMember);
    renderActivityHistory(currentMember);
  }
}

function lookupMember() {
  const lookup = document.getElementById("memberIdInput").value.trim();
  const lastName = document.getElementById("lastNameInput").value.trim();

  fetch(`/api/loyalty/member?lookup=${encodeURIComponent(lookup)}&lastName=${encodeURIComponent(lastName)}`)
    .then(response => response.json())
    .then(data => {
      if (!data.member) {
        currentMember = null;
        document.getElementById("memberProfileContainer").innerHTML =
          `<div class="message-box empty-text">No member found. Please check the member ID/email and last name.</div>`;
        document.getElementById("activityHistoryContainer").innerHTML = "";
        return;
      }

      currentMember = data.member;
      renderMemberProfile(currentMember);
      renderActivityHistory(currentMember);
    });
}

function reloadMember(memberId, lastName) {
  fetch(`/api/loyalty/member?lookup=${encodeURIComponent(memberId)}&lastName=${encodeURIComponent(lastName)}`)
    .then(response => response.json())
    .then(data => {
      if (data.member) {
        currentMember = data.member;
        renderMemberProfile(currentMember);
        renderActivityHistory(currentMember);
      }
      return fetch("/api/data");
    })
    .then(response => response.json())
    .then(data => {
      hotelData = data;
      renderRewards();
    });
}

function renderMemberProfile(member) {
  const container = document.getElementById("memberProfileContainer");
  const progressPercent = Math.min((member.availablePoints / member.nextTierPoints) * 100, 100);
  const remainingPoints = Math.max(member.nextTierPoints - member.availablePoints, 0);

  container.innerHTML = `
    <div class="member-card">
      <div class="member-tier">✦ ${member.tier}</div>
      <div class="member-name">${member.fullName}</div>
      <div class="member-meta">Member ID: ${member.id} · Enrolled: ${member.enrolled}</div>
      <div class="member-stats">
        <div>
          <div class="member-stat-label">Available Points</div>
          <div class="member-stat-value">${formatNumber(member.availablePoints)}</div>
        </div>
        <div>
          <div class="member-stat-label">Lifetime Stays</div>
          <div class="member-stat-value small-white">${member.lifetimeStays}</div>
        </div>
        <div>
          <div class="member-stat-label">Nights This Year</div>
          <div class="member-stat-value small-white">${member.nightsThisYear}</div>
        </div>
      </div>
    </div>
    <div class="progress-wrap">
      <div class="progress-header">
        <span>Progress to ${member.nextTier}</span>
        <span>${formatNumber(member.availablePoints)} / ${formatNumber(member.nextTierPoints)} pts</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${progressPercent}%"></div>
      </div>
      <div class="progress-labels">
        <span>${member.tier.replace(" Member", "")}</span>
        <span>${formatNumber(remainingPoints)} pts to ${member.nextTier}</span>
        <span>${member.nextTier}</span>
      </div>
    </div>
  `;
}

function renderActivityHistory(member) {
  const container = document.getElementById("activityHistoryContainer");

  if (!member.activityHistory || member.activityHistory.length === 0) {
    container.innerHTML = `<div class="message-box empty-text">No activity history available.</div>`;
    return;
  }

  const rows = member.activityHistory.map(item => `
    <tr>
      <td>${item.date}</td>
      <td>${item.description}</td>
      <td>${item.refId}</td>
      <td class="${item.points >= 0 ? "points-positive" : "points-negative"}">
        ${item.points >= 0 ? "+" : ""}${formatNumber(item.points)}
      </td>
      <td>${formatNumber(item.balance)}</td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table class="activity-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Description</th>
          <th>Ref ID</th>
          <th>Points</th>
          <th>Balance</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderRewards() {
  const rewardGrid = document.getElementById("rewardGrid");
  if (!rewardGrid) return;

  rewardGrid.innerHTML = "";

  hotelData.rewards.forEach(reward => {
    const card = document.createElement("div");
    card.className = "reward-card";
    card.dataset.rewardId = reward.id;
    card.innerHTML = `
      <div class="reward-title">${reward.title}</div>
      <div class="reward-points">${formatNumber(reward.points)} pts</div>
      <div class="reward-desc">${reward.description}</div>
    `;

    card.addEventListener("click", () => {
      selectedReward = reward;
      highlightSelectedReward();
    });

    rewardGrid.appendChild(card);
  });
}

function highlightSelectedReward() {
  document.querySelectorAll(".reward-card").forEach(card => {
    card.classList.toggle("selected", selectedReward && card.dataset.rewardId === selectedReward.id);
  });
}

/* STAFF */

function initStaffPage() {
  populateStaffFilters();
  renderStaffTable();

  document.getElementById("departmentFilter").addEventListener("change", renderStaffTable);
  document.getElementById("roleFilter").addEventListener("change", renderStaffTable);
  document.getElementById("addStaffBtn").addEventListener("click", addNewStaff);
}

function populateStaffFilters() {
  const departmentFilter = document.getElementById("departmentFilter");
  const roleFilter = document.getElementById("roleFilter");

  departmentFilter.innerHTML = `<option value="All">All Departments</option>`;
  roleFilter.innerHTML = `<option value="All">All Roles</option>`;

  const departments = [...new Set(hotelData.staffMembers.map(member => member.department))];
  const roles = [...new Set(hotelData.staffMembers.map(member => member.role))];

  departments.forEach(department => {
    const option = document.createElement("option");
    option.value = department;
    option.textContent = department;
    departmentFilter.appendChild(option);
  });

  roles.forEach(role => {
    const option = document.createElement("option");
    option.value = role;
    option.textContent = role;
    roleFilter.appendChild(option);
  });
}

function renderStaffTable() {
  const tbody = document.getElementById("staffTableBody");
  const selectedDepartment = document.getElementById("departmentFilter").value;
  const selectedRole = document.getElementById("roleFilter").value;

  const filteredStaff = hotelData.staffMembers.filter(member => {
    const departmentMatch = selectedDepartment === "All" || member.department === selectedDepartment;
    const roleMatch = selectedRole === "All" || member.role === selectedRole;
    return departmentMatch && roleMatch;
  });

  tbody.innerHTML = "";

  filteredStaff.forEach(member => {
    const tr = document.createElement("tr");
    const initials = getInitials(member.name);
    const roleClass = getRoleClass(member.role);
    const isActive = member.status === "Active";

    tr.innerHTML = `
      <td>
        <div class="staff-member-cell">
          <div class="staff-avatar">${initials}</div>
          <div class="staff-name">${member.name}</div>
        </div>
      </td>
      <td>${member.employee_id || member.employeeId}</td>
      <td>${member.department}</td>
      <td><span class="role-pill ${roleClass}">${member.role}</span></td>
      <td>
        <span class="status-indicator">
          <span class="status-dot ${isActive ? "active" : "inactive"}"></span>
          ${member.status}
        </span>
      </td>
      <td>${member.last_login || member.lastLogin}</td>
      <td>
        <span class="action-link action-edit" data-action="edit" data-id="${member.employee_id || member.employeeId}">EDIT</span>
        <span class="action-link ${isActive ? "action-danger" : "action-success"}" data-action="toggle" data-id="${member.employee_id || member.employeeId}">
          ${isActive ? "DEACTIVATE" : "REACTIVATE"}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });

  attachStaffActionEvents();
}

function attachStaffActionEvents() {
  document.querySelectorAll('[data-action="edit"]').forEach(button => {
    button.addEventListener("click", function () {
      editStaffMember(this.dataset.id);
    });
  });

  document.querySelectorAll('[data-action="toggle"]').forEach(button => {
    button.addEventListener("click", function () {
      toggleStaffStatus(this.dataset.id);
    });
  });
}

function editStaffMember(employeeId) {
  const member = hotelData.staffMembers.find(staff => (staff.employee_id || staff.employeeId) === employeeId);
  if (!member) return;

  const currentRole = member.role;
  const newRole = prompt(`Edit role for ${member.name}:`, currentRole);

  if (newRole && newRole.trim() !== "") {
    postJson("/api/staff/edit-role", {
      employeeId: employeeId,
      role: newRole.trim()
    }).then(result => {
      if (result.success) {
        loadAllData();
        alert(`Updated role for ${member.name}`);
      }
    });
  }
}

function toggleStaffStatus(employeeId) {
  postJson("/api/staff/toggle-status", {
    employeeId: employeeId
  }).then(result => {
    if (result.success) {
      loadAllData();
    }
  });
}

function addNewStaff() {
  const name = prompt("Enter staff full name:");
  if (!name || !name.trim()) return;

  const department = prompt("Enter department:", "Front Desk");
  if (!department || !department.trim()) return;

  const role = prompt("Enter role:", "Staff");
  if (!role || !role.trim()) return;

  postJson("/api/staff/add", {
    name: name.trim(),
    department: department.trim(),
    role: role.trim()
  }).then(result => {
    if (result.success) {
      loadAllData();
      alert(`New staff member added: ${name}`);
    }
  });
}

function getInitials(name) {
  return name
    .split(" ")
    .map(part => part[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();
}

function getRoleClass(role) {
  return `role-${role.toLowerCase().replace(/\s+/g, "-")}`;
}

function formatNumber(value) {
  return Number(value).toLocaleString();
}

function getTodayLabel() {
  const now = new Date();
  const month = now.toLocaleString("en-US", { month: "short" });
  const day = String(now.getDate()).padStart(2, "0");
  const year = now.getFullYear();
  return `${month} ${day} ${year}`;
}