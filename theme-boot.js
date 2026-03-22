(function () {
  const KEY = "bugSiteState.v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch {
      return {};
    }
  }

  function resolveTheme(pref) {
    if (pref === "system") {
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return pref === "dark" ? "dark" : "light";
  }

  function apply() {
    const s = load();
    const themePref = s.themePref || "light";
    document.documentElement.dataset.theme = resolveTheme(themePref);

    let pal = s.palettePref || "default";
    const unlocked = Array.isArray(s.unlockedPalettes) ? s.unlockedPalettes : [];
    if (pal !== "default" && !unlocked.includes(pal)) {
      pal = "default";
    }
    document.documentElement.dataset.palette = pal;
  }

  apply();

  if (window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      const s = load();
      if (s.themePref === "system") apply();
    };
    try {
      mq.addEventListener("change", onChange);
    } catch {
      mq.addListener(onChange);
    }
  }

  window.BugSiteTheme = { apply };
})();
