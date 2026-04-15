let loyaltyData = { loyaltyMembers: [], rewards: [] };
let currentMember = null;
let selectedReward = null;

loadLoyaltyData();

function loadLoyaltyData() {
  fetch("/api/data")
    .then(response => response.json())
    .then(data => {
      loyaltyData = data;
      renderRewards();

      const defaultMember = loyaltyData.loyaltyMembers[0];
      if (defaultMember) {
        document.getElementById("memberIdInput").value = defaultMember.id;
        document.getElementById("lastNameInput").value = defaultMember.lastName;
        currentMember = defaultMember;
        renderMemberProfile(currentMember);
        renderActivityHistory(currentMember);
      }

      bindLoyaltyEvents();
    });
}

function bindLoyaltyEvents() {
  document.getElementById("lookupMemberBtn").onclick = lookupMember;

  document.getElementById("redeemForm").onsubmit = function (e) {
    e.preventDefault();

    if (!currentMember || !selectedReward) {
      alert("Please look up a member and select a reward.");
      return;
    }

    fetch("/api/loyalty/redeem", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        memberId: currentMember.id,
        rewardId: selectedReward.id,
        reservationId: document.getElementById("reservationId").value.trim(),
        notes: document.getElementById("redemptionNotes").value.trim(),
        date: getTodayLabel()
      })
    })
      .then(response => response.json())
      .then(result => {
        if (!result.success) {
          alert(result.message || "Unable to process redemption.");
          return;
        }
        alert("Redemption processed.");
        selectedReward = null;
        highlightSelectedReward();
        reloadMember(currentMember.id, currentMember.lastName);
        document.getElementById("redeemForm").reset();
      });
  };

  document.getElementById("addPointsBtn").onclick = function () {
    if (!currentMember) {
      alert("Please look up a member first.");
      return;
    }

    fetch("/api/loyalty/add-points", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        memberId: currentMember.id,
        points: 500,
        date: getTodayLabel()
      })
    })
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          alert("500 points added.");
          reloadMember(currentMember.id, currentMember.lastName);
        }
      });
  };
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
          `<div class="message-box">No member found.</div>`;
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
    });
}

function renderMemberProfile(member) {
  const progressPercent = Math.min((member.availablePoints / member.nextTierPoints) * 100, 100);
  const remainingPoints = Math.max(member.nextTierPoints - member.availablePoints, 0);

  document.getElementById("memberProfileContainer").innerHTML = `
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
        <div class="progress-fill" style="width:${progressPercent}%"></div>
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
  if (!member.activityHistory || member.activityHistory.length === 0) {
    document.getElementById("activityHistoryContainer").innerHTML = `<div class="message-box">No activity history available.</div>`;
    return;
  }

  const rows = member.activityHistory.map(item => `
    <tr>
      <td>${item.date}</td>
      <td>${item.description}</td>
      <td>${item.refId}</td>
      <td>${item.points >= 0 ? "+" : ""}${formatNumber(item.points)}</td>
      <td>${formatNumber(item.balance)}</td>
    </tr>
  `).join("");

  document.getElementById("activityHistoryContainer").innerHTML = `
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
  rewardGrid.innerHTML = "";

  loyaltyData.rewards.forEach(reward => {
    const card = document.createElement("div");
    card.className = "reward-card";
    card.dataset.rewardId = reward.id;
    card.innerHTML = `
      <div class="reward-title">${reward.title}</div>
      <div class="reward-points">${formatNumber(reward.points)} pts</div>
      <div class="reward-desc">${reward.description}</div>
    `;
    card.onclick = function () {
      selectedReward = reward;
      highlightSelectedReward();
    };
    rewardGrid.appendChild(card);
  });
}

function highlightSelectedReward() {
  document.querySelectorAll(".reward-card").forEach(card => {
    card.classList.toggle("selected", selectedReward && card.dataset.rewardId === selectedReward.id);
  });
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