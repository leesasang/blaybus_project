(function () {
  const DURATION_MS = 2200;
  const LETTERS = 7;
  const REDIRECT_URL = "home.html";

  const barFill = document.getElementById("loadingBarFill");
  const letters = Array.from(document.querySelectorAll(".letter"));

  const start = performance.now();

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / DURATION_MS, 1);

    barFill.style.width = progress * 100 + "%";

    const letterProgressEnd = 0.85;
    const threshold = (i) => (letterProgressEnd / LETTERS) * (i + 1);
    letters.forEach((el, i) => el.classList.toggle("filled", progress >= threshold(i)));

    if (progress < 1) return requestAnimationFrame(tick);

    sessionStorage.setItem("fromLoading", "1");
    window.location.href = REDIRECT_URL;
  }

  requestAnimationFrame(tick);
})();

