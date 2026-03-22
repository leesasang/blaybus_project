(function () {
  // Always start with side nav collapsed
  document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.remove("sideNav-open");
    const btn = document.querySelector(".menuToggle");
    if (btn) {
      btn.addEventListener("click", () => {
        document.body.classList.toggle("sideNav-open");
      });
    }
  });
})();

