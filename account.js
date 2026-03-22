(function () {
  const loginStatus = document.getElementById("loginStatus");
  const pointsBadge = document.getElementById("pointsBadge");
  const themeBadge = document.getElementById("themeBadge");
  const paletteBadge = document.getElementById("paletteBadge");

  const nicknameEl = document.getElementById("nickname");
  const emailEl = document.getElementById("email");
  const profileName = document.getElementById("profileName");
  const profileEmail = document.getElementById("profileEmail");
  const avatarEmoji = document.getElementById("avatarEmoji");
  const iconPicker = document.getElementById("iconPicker");

  const loginForm = document.getElementById("loginForm");
  const logoutBtn = document.getElementById("logoutBtn");

  const ICONS = [
    { id: "default", emoji: "☺", label: "기본", always: true },
    { id: "star", emoji: "⭐", label: "별빛" },
    { id: "compass", emoji: "🧭", label: "탐험" },
  ];

  const PALETTES = [
    { id: "default", label: "기본", always: true },
    { id: "ocean", label: "오션 블루" },
    { id: "sunset", label: "선셋 코랄" },
  ];

  function setUser(user) {
    window.BugSiteState.set("user", user);
  }

  function getUser() {
    return window.BugSiteState.get("user", null);
  }

  function setThemePref(pref) {
    window.BugSiteState.set("themePref", pref);
  }

  function getThemePref() {
    return window.BugSiteState.get("themePref", "light");
  }

  function setPalettePref(pref) {
    window.BugSiteState.set("palettePref", pref);
  }

  function getPalettePref() {
    return window.BugSiteState.get("palettePref", "default");
  }

  function getProfileIconId() {
    return window.BugSiteState.get("profileIconId", "default");
  }

  function setProfileIconId(id) {
    window.BugSiteState.set("profileIconId", id);
  }

  function isIconUnlocked(id) {
    if (id === "default") return true;
    const u = window.BugSiteState.get("unlockedIcons", []);
    return Array.isArray(u) && u.includes(id);
  }

  function isPaletteUnlocked(id) {
    if (id === "default") return true;
    const u = window.BugSiteState.get("unlockedPalettes", []);
    return Array.isArray(u) && u.includes(id);
  }

  function applyThemeBadges(pref) {
    const resolved =
      pref === "system"
        ? window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light"
        : pref;

    if (themeBadge) {
      themeBadge.textContent = pref === "system" ? "System" : resolved[0].toUpperCase() + resolved.slice(1);
    }

    const pal = getPalettePref();
    if (paletteBadge) {
      const p = PALETTES.find((x) => x.id === pal);
      paletteBadge.textContent = p ? p.label : "기본";
    }
  }

  function render() {
    const points = window.BugSiteState.get("points", 0);
    if (pointsBadge) pointsBadge.textContent = `${points} P`;

    const user = getUser();
    const loggedIn = !!(user && user.nickname);
    if (loginStatus) loginStatus.textContent = loggedIn ? "로그인됨" : "로그아웃";

    if (nicknameEl) nicknameEl.value = user?.nickname || "";
    if (emailEl) emailEl.value = user?.email || "";

    if (profileName) profileName.textContent = loggedIn ? user.nickname : "게스트";
    if (profileEmail) profileEmail.textContent = loggedIn ? user.email || "이메일 없음" : "로그인하면 이메일이 표시돼요";

    let iconId = getProfileIconId();
    if (!isIconUnlocked(iconId)) {
      iconId = "default";
      if (getProfileIconId() !== "default") setProfileIconId("default");
    }
    const iconDef = ICONS.find((x) => x.id === iconId) || ICONS[0];
    if (avatarEmoji) avatarEmoji.textContent = iconDef.emoji;

    const pref = getThemePref();
    applyThemeBadges(pref);
    window.BugSiteTheme?.apply();

    renderIconPicker();
    renderPalettePicker();
  }

  function renderIconPicker() {
    if (!iconPicker) return;
    const current = getProfileIconId();
    iconPicker.innerHTML = ICONS.map((ic) => {
      const open = ic.always || isIconUnlocked(ic.id);
      const active = ic.id === current;
      return `
        <button type="button" class="iconPick ${active ? "active" : ""} ${open ? "" : "locked"}" data-icon="${ic.id}" ${open ? "" : "disabled"} aria-label="${ic.label}" title="${open ? ic.label : "도전과제에서 잠금 해제"}">
          <span class="iconPickEmoji">${ic.emoji}</span>
          <span class="iconPickLbl">${ic.label}</span>
        </button>
      `;
    }).join("");

    iconPicker.querySelectorAll("[data-icon]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-icon");
        if (!id || !isIconUnlocked(id)) return;
        setProfileIconId(id);
        render();
      });
    });
  }

  function renderPalettePicker() {
    const row = document.getElementById("paletteRow");
    if (!row) return;
    const current = getPalettePref();
    row.innerHTML = PALETTES.map((p) => {
      const open = p.always || isPaletteUnlocked(p.id);
      const active = p.id === current;
      return `
        <button type="button" class="pillBtn ${active ? "primary" : ""} ${open ? "" : "locked"}" data-palette="${p.id}" ${open ? "" : "disabled"} title="${open ? p.label : "도전과제에서 잠금 해제"}">
          ${p.label}${open ? "" : " 🔒"}
        </button>
      `;
    }).join("");

    row.querySelectorAll("[data-palette]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-palette");
        if (!id || !isPaletteUnlocked(id)) return;
        setPalettePref(id);
        window.BugSiteTheme?.apply();
        render();
      });
    });
  }

  loginForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const nickname = (nicknameEl?.value || "").trim();
    const email = (emailEl?.value || "").trim();
    if (!nickname) {
      alert("닉네임을 입력해줘.");
      return;
    }
    setUser({ nickname, email });
    render();
  });

  logoutBtn?.addEventListener("click", () => {
    setUser(null);
    render();
  });

  document.querySelectorAll("[data-theme]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const pref = btn.getAttribute("data-theme");
      if (!pref) return;
      setThemePref(pref);
      window.BugSiteTheme?.apply();
      render();
    });
  });

  document.getElementById("systemThemeBtn")?.addEventListener("click", () => {
    setThemePref("system");
    window.BugSiteTheme?.apply();
    render();
  });

  if (window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      const pref = getThemePref();
      if (pref === "system") {
        window.BugSiteTheme?.apply();
        render();
      }
    };
    try {
      mq.addEventListener("change", handler);
    } catch {
      mq.addListener(handler);
    }
  }

  render();
})();
