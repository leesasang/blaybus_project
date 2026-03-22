(function () {
  const input = document.getElementById("searchInput");
  const resultsEl = document.getElementById("searchResults");
  const titleEl = document.getElementById("resultTitle");
  const hintEl = document.getElementById("searchHint");

  const items = [
    { type: "카테고리", label: "강아지 게시판", desc: "멍뭉이 힐링 영상 모음", to: "./board.html?board=dog&skipLoading=1", keys: ["강아지","멍뭉이","dog"] },
    { type: "카테고리", label: "고양이 게시판", desc: "골골송, 낮잠, ASMR", to: "./board.html?board=cat&skipLoading=1", keys: ["고양이","냥이","cat","asmr"] },
    { type: "게시판", label: "오늘의 멍뭉이: 심장 저격 모음", desc: "강아지 게시판 · 조회수 12.7만", to: "./board.html?board=dog_daily&skipLoading=1", keys: ["강아지","하이라이트"] },
    { type: "게시판", label: "골골송 ASMR: 고양이 힐링 1시간", desc: "고양이 게시판 · ASMR", to: "./board.html?board=cat_asmr&skipLoading=1", keys: ["고양이","asmr","힐링"] },
  ];

  function render(list){
    if (!resultsEl) return;
    resultsEl.innerHTML = list.map(i => `
      <a class="feedCard" href="${i.to}">
        <div class="feedCardHeader">
          <div class="board">${escapeHtml(i.type)}</div>
          <div class="titleTxt">${escapeHtml(i.label)}</div>
        </div>
        <div class="thumbWide" aria-hidden="true"></div>
        <div class="feedCardMeta"><span>${escapeHtml(i.desc)}</span></div>
      </a>
    `).join("");
  }

  function apply(q){
    const query = q.trim().toLowerCase();
    if (titleEl) titleEl.textContent = query ? "검색 결과" : "추천 게시판";
    if (!query) return render(items);
    const filtered = items.filter(i => (i.label+" "+i.desc+" "+i.keys.join(" ")).toLowerCase().includes(query));
    render(filtered);
  }

  if (input) input.addEventListener("input", () => apply(input.value));
  if (hintEl) {
    hintEl.querySelectorAll("[data-q]").forEach(btn => {
      btn.addEventListener("click", () => {
        const q = btn.getAttribute("data-q") || "";
        input.value = q;
        apply(q);
        input.focus();
      });
    });
  }

  apply("");

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m]));
  }
})();

