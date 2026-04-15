document.addEventListener("DOMContentLoaded", function () {
  loadGuestRegistrationMeta();

  const form = document.getElementById("guestRegistrationForm");
  const clearBtn = document.getElementById("guestClearBtn");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const payload = {
      firstName: document.getElementById("firstName").value.trim(),
      lastName: document.getElementById("lastName").value.trim(),
      email: document.getElementById("email").value.trim(),
      phoneNumber: document.getElementById("phoneNumber").value.trim(),
      dateOfBirth: document.getElementById("dateOfBirth").value,
      passportId: document.getElementById("passportId").value.trim(),
      highFloor: document.getElementById("highFloor").checked,
      quietRoom: document.getElementById("quietRoom").checked,
      featherFreePillows: document.getElementById("featherFreePillows").checked,
      accessibleRoom: document.getElementById("accessibleRoom").checked,
      kingBed: document.getElementById("kingBed").checked,
      preferenceNotes: document.getElementById("preferenceNotes").value.trim()
    };

    if (!payload.firstName || !payload.lastName || !payload.email) {
      alert("Please fill in First Name, Last Name, and Email Address.");
      return;
    }

    fetch("/api/guest-registration/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          document.getElementById("guestId").value = data.guestId;
          document.getElementById("memberSince").value = data.memberSince;
          showGuestMessage(`Guest account created successfully. Guest ID: ${data.guestId}`);
        } else {
          alert("Unable to create guest account.");
        }
      });
  });

  clearBtn.addEventListener("click", function () {
    form.reset();
    loadGuestRegistrationMeta();
    removeGuestMessage();
  });
});

function loadGuestRegistrationMeta() {
  fetch("/api/guest-registration/meta")
    .then(response => response.json())
    .then(data => {
      document.getElementById("guestId").value = data.guestId;
      document.getElementById("memberSince").value = data.memberSince;
    });
}

function showGuestMessage(message) {
  removeGuestMessage();
  const msg = document.createElement("div");
  msg.className = "guest-message";
  msg.id = "guestMessage";
  msg.textContent = message;
  document.getElementById("guestRegistrationForm").appendChild(msg);
}

function removeGuestMessage() {
  const existing = document.getElementById("guestMessage");
  if (existing) existing.remove();
}