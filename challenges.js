(function () {
  const listEl = document.getElementById("challengeList");
  const pointsBtn = document.getElementById("pointsBtn");

  const challenges = [
    {
      id: "create_1",
      title: "첫 영상 만들기",
      desc: "만들기 페이지에서 1회 완료해보세요.",
      goal: 1,
      progressKey: "createCount",
      rewards: [{ type: "icon", id: "star" }],
    },
    {
      id: "create_3",
      title: "연속 제작자",
      desc: "영상 만들기 3회를 달성하세요.",
      goal: 3,
      progressKey: "createCount",
      rewards: [{ type: "palette", id: "ocean" }],
    },
    {
      id: "visit_3boards",
      title: "탐험가",
      desc: "게시판을 3번 방문하세요.",
      goal: 3,
      progressKey: "boardVisits",
      rewards: [
        { type: "icon", id: "compass" },
        { type: "palette", id: "sunset" },
      ],
    },
  ];

  const ICON_META = {
    star: { emoji: "⭐", name: "별빛" },
    compass: { emoji: "🧭", name: "탐험가 나침반" },
  };

  const PALETTE_META = {
    ocean: { name: "오션 블루" },
    sunset: { name: "선셋 코랄" },
  };

  function rewardSummary(rewards) {
    return rewards
      .map((r) => {
        if (r.type === "icon") {
          const m = ICON_META[r.id];
          return m ? `프로필 아이콘 ${m.emoji} ${m.name}` : "프로필 아이콘";
        }
        if (r.type === "palette") {
          const m = PALETTE_META[r.id];
          return m ? `색 테마 · ${m.name}` : "색 테마";
        }
        return "";
      })
      .filter(Boolean)
      .join(" · ");
  }

  function migrateLegacyRewards() {
    if (window.BugSiteState.get("rewardsMigratedV2")) return;
    challenges.forEach((c) => {
      if (window.BugSiteState.get(`claimed.${c.id}`, false)) {
        window.BugSiteState.grantRewards(c.rewards);
      }
    });
    window.BugSiteState.set("rewardsMigratedV2", true);
  }

  function render() {
    migrateLegacyRewards();

    const points = window.BugSiteState.get("points", 0);
    if (pointsBtn) pointsBtn.textContent = `${points} P`;

    if (!listEl) return;
    listEl.innerHTML = challenges
      .map((c) => {
        const progress = Math.min(window.BugSiteState.get(c.progressKey, 0), c.goal);
        const pct = Math.round((progress / c.goal) * 100);
        const claimed = !!window.BugSiteState.get(`claimed.${c.id}`, false);
        const canClaim = progress >= c.goal && !claimed;
        const rewardLine = rewardSummary(c.rewards);

        return `
          <div class="challengeCard">
            <div style="flex:1; min-width:0;">
              <h3>${escapeHtml(c.title)}</h3>
              <p>${escapeHtml(c.desc)} (${progress}/${c.goal})</p>
              <p class="rewardLine">${escapeHtml(rewardLine)}</p>
              <div class="progressWrap">
                <div class="progressTrack"><div class="progressFill" style="width:${pct}%"></div></div>
              </div>
            </div>
            <button class="pillBtn ${canClaim ? "primary" : ""}" data-claim="${escapeHtml(c.id)}" ${canClaim ? "" : "disabled"}>
              ${claimed ? "수령완료" : canClaim ? "보상 수령" : "진행중"}
            </button>
          </div>
        `;
      })
      .join("");

    listEl.querySelectorAll("[data-claim]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-claim");
        if (!id) return;
        const ch = challenges.find((x) => x.id === id);
        const ok = window.BugSiteState.claim(id, ch ? ch.rewards : []);
        if (ok) {
          const msg = rewardSummary(ch.rewards);
          alert(`보상을 받았어요!\n${msg}\n(+10P)`);
          window.BugSiteTheme?.apply();
        }
        render();
      });
    });
  }

  render();

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m]));
  }
})();
