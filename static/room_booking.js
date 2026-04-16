// room_booking.js
// This file handles frontend logic for Room Booking.
// It does the following:
// 1. loads auto-generated reservation information
// 2. allows room type selection
// 3. checks room availability
// 4. sends booking data to the Python backend

document.addEventListener("DOMContentLoaded", function () {
  let selectedRoomType = "";
  let selectedRate = 0;

  loadBookingMeta();

  const roomCards = document.querySelectorAll(".room-type-card");
  const form = document.getElementById("roomBookingForm");
  const clearBtn = document.getElementById("clearBookingBtn");

  roomCards.forEach(card => {
    card.addEventListener("click", function () {
      roomCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");

      selectedRoomType = card.dataset.type;
      selectedRate = card.dataset.rate;

      updateAvailability(selectedRoomType);
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const payload = {
      guestId: document.getElementById("guestId").value.trim(),
      numberOfGuests: document.getElementById("numberOfGuests").value,
      checkInDate: document.getElementById("checkInDate").value,
      checkOutDate: document.getElementById("checkOutDate").value,
      roomType: selectedRoomType,
      ratePerNight: selectedRate,
      status: document.getElementById("status").value
    };

    if (!payload.guestId || !payload.checkInDate || !payload.checkOutDate || !payload.roomType) {
      alert("Please fill in all required booking fields.");
      return;
    }

    fetch("/api/room-booking/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          document.getElementById("reservationId").value = data.reservationId;
          document.getElementById("createdAt").value = data.createdAt;
          showBookingMessage(`Reservation created successfully. ID: ${data.reservationId}`);
        } else {
          alert("Unable to create reservation.");
        }
      })
      .catch(error => {
        console.error("Booking error:", error);
        alert("Something went wrong.");
      });
  });

  clearBtn.addEventListener("click", function () {
    form.reset();
    roomCards.forEach(card => card.classList.remove("selected"));
    selectedRoomType = "";
    selectedRate = 0;
    document.getElementById("roomsAvailable").value = "";
    loadBookingMeta();
    removeBookingMessage();
  });
});

function loadBookingMeta() {
  fetch("/api/room-booking/meta")
    .then(response => response.json())
    .then(data => {
      document.getElementById("reservationId").value = data.reservationId;
      document.getElementById("createdAt").value = data.createdAt;
    });
}

function updateAvailability(roomType) {
  fetch("/api/room-booking/availability", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ roomType: roomType })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.getElementById("roomsAvailable").value = `${data.availableRooms} room(s) available`;
      }
    });
}

function showBookingMessage(message) {
  removeBookingMessage();

  const msg = document.createElement("div");
  msg.className = "booking-message";
  msg.id = "bookingMessage";
  msg.textContent = message;

  document.getElementById("roomBookingForm").appendChild(msg);
}

function removeBookingMessage() {
  const existing = document.getElementById("bookingMessage");
  if (existing) {
    existing.remove();
  }
}