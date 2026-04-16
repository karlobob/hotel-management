// checkin_checkout.js
// This file handles frontend logic for Check-In / Check-Out.
// It does the following:
// 1. Look up reservations by reservation ID and guest ID
// 2. Display reservation details
// 3. Process check-in (assign room, update status)
// 4. Process check-out (update status, free room)
// 5. Reset the form

document.addEventListener("DOMContentLoaded", function () {
  // Store current reservation data
  let currentReservation = null;

  // Get DOM elements
  const lookupBtn = document.getElementById("lookupBtn");
  const checkinBtn = document.getElementById("checkinBtn");
  const checkoutBtn = document.getElementById("checkoutBtn");
  const resetBtn = document.getElementById("resetBtn");

  // Event: Look up reservation
  lookupBtn.addEventListener("click", function () {
    const reservationId = document.getElementById("lookupReservationId").value.trim();
    const guestId = document.getElementById("lookupGuestId").value.trim();

    // Validate inputs
    if (!reservationId || !guestId) {
      showMessage("Please enter both Reservation ID and Guest ID.", "error");
      return;
    }

    // Call API to look up reservation
    fetch("/api/checkin-checkout/lookup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reservationId: reservationId,
        guestId: guestId
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          currentReservation = data.reservation;
          displayReservation(data.reservation);
          updateRoomsAvailable(data.reservation.roomType);
          showMessage("Reservation found.", "success");
        } else {
          showMessage(data.message || "Reservation not found.", "error");
        }
      })
      .catch(error => {
        console.error("Lookup error:", error);
        showMessage("Something went wrong.", "error");
      });
  });

  // Event: Complete check-in
  checkinBtn.addEventListener("click", function () {
    if (!currentReservation) {
      showMessage("Please look up a reservation first.", "error");
      return;
    }

    // Check if already checked in
    if (currentReservation.status === "Checked-In") {
      showMessage("This reservation is already checked in.", "error");
      return;
    }

    // Call API to process check-in
    fetch("/api/checkin-checkout/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reservationId: currentReservation.reservationId,
        guestId: currentReservation.guestId,
        roomType: currentReservation.roomType
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update UI with assigned room
          document.getElementById("roomId").value = data.roomId;
          document.getElementById("reservationStatus").value = "Checked-In";
          currentReservation.roomId = data.roomId;
          currentReservation.status = "Checked-In";
          updateStatusOverview();
          updateRoomsAvailable(currentReservation.roomType);
          showMessage(data.message, "success");
        } else {
          showMessage(data.message || "Check-in failed.", "error");
        }
      })
      .catch(error => {
        console.error("Check-in error:", error);
        showMessage("Something went wrong.", "error");
      });
  });

  // Event: Process check-out
  checkoutBtn.addEventListener("click", function () {
    if (!currentReservation) {
      showMessage("Please look up a reservation first.", "error");
      return;
    }

    // Check if already checked out
    if (currentReservation.status === "Checked-Out") {
      showMessage("This reservation is already checked out.", "error");
      return;
    }

    // Check if not checked in yet
    if (currentReservation.status !== "Checked-In") {
      showMessage("Guest must be checked in before check-out.", "error");
      return;
    }

    // Call API to process check-out
    fetch("/api/checkin-checkout/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        reservationId: currentReservation.reservationId,
        guestId: currentReservation.guestId,
        roomId: currentReservation.roomId
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update UI
          document.getElementById("reservationStatus").value = "Checked-Out";
          currentReservation.status = "Checked-Out";
          updateStatusOverview();
          showMessage(data.message, "success");
        } else {
          showMessage(data.message || "Check-out failed.", "error");
        }
      })
      .catch(error => {
        console.error("Check-out error:", error);
        showMessage("Something went wrong.", "error");
      });
  });

  // Event: Reset form
  resetBtn.addEventListener("click", function () {
    currentReservation = null;
    clearForm();
    clearMessage();
  });

  /**
   * Display reservation details in the form fields
   */
  function displayReservation(reservation) {
    document.getElementById("reservationId").value = reservation.reservationId || "—";
    document.getElementById("createdAt").value = reservation.createdAt || "—";
    document.getElementById("guestId").value = reservation.guestId || "—";
    document.getElementById("roomId").value = reservation.roomId || "Assign on check-in";
    document.getElementById("checkInDate").value = reservation.checkInDate || "";
    document.getElementById("checkOutDate").value = reservation.checkOutDate || "";
    document.getElementById("reservationStatus").value = reservation.status || "";

    updateStatusOverview();
  }

  /**
   * Update rooms available count based on room type
   */
  function updateRoomsAvailable(roomType) {
    if (!roomType) {
      document.getElementById("roomsAvailable").value = "—";
      return;
    }

    fetch("/api/checkin-checkout/rooms-available", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roomType: roomType })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          document.getElementById("roomsAvailable").value = data.availableRooms;
        }
      });
  }

  /**
   * Update the status overview section
   */
  function updateStatusOverview() {
    const overview = document.getElementById("statusOverview");

    if (!currentReservation) {
      overview.innerHTML = `
        <span class="status-badge pending">PENDING</span>
        <span class="status-text">Guest: — · Room: — · Check-in: — · Check-out: —</span>
      `;
      return;
    }

    const status = currentReservation.status || "Pending";
    const statusClass = status.toLowerCase().replace(" ", "-");

    overview.innerHTML = `
      <span class="status-badge ${statusClass}">${status.toUpperCase()}</span>
      <span class="status-text">
        Guest: ${currentReservation.guestId || "—"} ·
        Room: ${currentReservation.roomId || "—"} ·
        Check-in: ${currentReservation.checkInDate || "—"} ·
        Check-out: ${currentReservation.checkOutDate || "—"}
      </span>
    `;
  }

  /**
   * Clear all form fields
   */
  function clearForm() {
    document.getElementById("lookupReservationId").value = "";
    document.getElementById("lookupGuestId").value = "";
    document.getElementById("reservationId").value = "";
    document.getElementById("createdAt").value = "";
    document.getElementById("guestId").value = "";
    document.getElementById("roomId").value = "";
    document.getElementById("checkInDate").value = "";
    document.getElementById("checkOutDate").value = "";
    document.getElementById("roomsAvailable").value = "";
    document.getElementById("reservationStatus").value = "";

    updateStatusOverview();
  }

  /**
   * Show a message to the user
   */
  function showMessage(text, type) {
    const area = document.getElementById("messageArea");
    area.innerHTML = `<div class="message ${type}">${text}</div>`;
  }

  /**
   * Clear the message area
   */
  function clearMessage() {
    document.getElementById("messageArea").innerHTML = "";
  }
});