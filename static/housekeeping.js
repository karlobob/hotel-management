let hotelData = { rooms: [], housekeepers: [] };
let selectedStatus = "";

loadData();

function loadData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      hotelData = data;
      renderSummary();
      renderRooms();
      populateRoomSelect();
      populateHousekeepers();
      bindEvents();
    });
}

function bindEvents() {
  document.querySelectorAll(".status-btn").forEach(button => {
    button.onclick = () => {
      selectedStatus = button.dataset.status;
      highlightStatusButton();
    };
  });

  document.getElementById("statusForm").onsubmit = function (e) {
    e.preventDefault();

    const roomNumber = document.getElementById("roomSelect").value;
    if (!roomNumber || !selectedStatus) {
      alert("Please select a room and status.");
      return;
    }

    fetch("/api/rooms/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        number: roomNumber,
        status: selectedStatus,
        housekeeper: document.getElementById("housekeeperSelect").value,
        priority: document.getElementById("prioritySelect").value,
        notes: document.getElementById("notes").value
      })
    })
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          alert("Room updated successfully.");
          loadData();
        }
      });
  };

  document.getElementById("clearBtn").onclick = function () {
    document.getElementById("statusForm").reset();
    selectedStatus = "";
    highlightStatusButton();
  };
}

function renderSummary() {
  const summaryCards = document.getElementById("summaryCards");
  const counts = {
    Clean: hotelData.rooms.filter(r => r.status === "Clean").length,
    Dirty: hotelData.rooms.filter(r => r.status === "Dirty").length,
    "In Progress": hotelData.rooms.filter(r => r.status === "In Progress").length,
    Occupied: hotelData.rooms.filter(r => r.status === "Occupied").length
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
    card.onclick = () => {
      document.getElementById("roomSelect").value = room.number;
      document.getElementById("housekeeperSelect").value = room.housekeeper || "";
      document.getElementById("prioritySelect").value = room.priority || "Standard";
      document.getElementById("notes").value = room.notes || "";
      selectedStatus = room.status;
      highlightStatusButton();
    };
    roomGrid.appendChild(card);
  });
}

function populateRoomSelect() {
  const roomSelect = document.getElementById("roomSelect");
  roomSelect.innerHTML = `<option value="">— Select a room —</option>`;
  hotelData.rooms.forEach(room => {
    roomSelect.innerHTML += `<option value="${room.number}">${room.number}</option>`;
  });
}

function populateHousekeepers() {
  const select = document.getElementById("housekeeperSelect");
  select.innerHTML = `<option value="">— Select —</option>`;
  hotelData.housekeepers.forEach(name => {
    select.innerHTML += `<option value="${name}">${name}</option>`;
  });
}

function highlightStatusButton() {
  document.querySelectorAll(".status-btn").forEach(button => {
    button.classList.toggle("active", button.dataset.status === selectedStatus);
  });
}

function getStatusClass(status) {
  if (status === "Clean") return "clean";
  if (status === "Dirty") return "dirty";
  if (status === "In Progress") return "progress";
  if (status === "Occupied") return "occupied";
  return "";
}