// Simple localStorage-backed state for challenges/progress
(function () {
  const KEY = "bugSiteState.v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch {
      return {};
    }
  }

  function save(s) {
    localStorage.setItem(KEY, JSON.stringify(s));
  }

  function get(path, fallback = 0) {
    const s = load();
    return s[path] ?? fallback;
  }

  function set(path, value) {
    const s = load();
    s[path] = value;
    save(s);
    return value;
  }

  function increment(path, delta = 1) {
    const cur = Number(get(path, 0)) || 0;
    return set(path, cur + delta);
  }

  function grantRewards(rewards) {
    if (!rewards || !rewards.length) return;
    for (const r of rewards) {
      if (r.type === "icon") {
        const a = get("unlockedIcons", []);
        if (!a.includes(r.id)) {
          a.push(r.id);
          set("unlockedIcons", a);
        }
      } else if (r.type === "palette") {
        const a = get("unlockedPalettes", []);
        if (!a.includes(r.id)) {
          a.push(r.id);
          set("unlockedPalettes", a);
        }
      }
    }
  }

  function claim(id, rewards) {
    const claimedKey = `claimed.${id}`;
    if (get(claimedKey, false)) return false;
    set(claimedKey, true);
    grantRewards(rewards);
    increment("points", 10);
    return true;
  }

  window.BugSiteState = { load, get, set, increment, claim, grantRewards };
})();

