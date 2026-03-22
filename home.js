(function () {
  const categories = [
    { id: "dog", name: "강아지", emoji: "🐶", hint: "멍뭉이 힐링" },
    { id: "cat", name: "고양이", emoji: "🐱", hint: "냥냥이 모음" },
    { id: "rabbit", name: "토끼", emoji: "🐰", hint: "말랑 폭신" },
    { id: "hamster", name: "햄스터", emoji: "🐹", hint: "쪼꼬미" },
    { id: "panda", name: "판다", emoji: "🐼", hint: "대왕 귀여움" },
    { id: "otter", name: "수달", emoji: "🦦", hint: "물개미소" },
    { id: "fox", name: "여우", emoji: "🦊", hint: "똑똑 큐트" },
    { id: "penguin", name: "펭귄", emoji: "🐧", hint: "빙하 산책" },
  ];

  const boards = [
    { id: "dog_daily", board: "강아지 게시판", title: "오늘의 멍뭉이: 심장 저격 모음", stats: "조회수 12.7만 · 1시간 전" },
    { id: "cat_asmr", board: "고양이 게시판", title: "골골송 ASMR: 고양이 힐링 1시간", stats: "조회수 127만 · 1일 전" },
    { id: "panda_cafe", board: "판다 게시판", title: "판다의 점심시간: 대나무 먹방", stats: "조회수 48.2만 · 3일 전" },
    { id: "otter_play", board: "수달 게시판", title: "수달 장난감 리뷰: 물장구 꿀잼", stats: "조회수 21.4만 · 1주 전" },
  ];

  const categoriesEl = document.getElementById("categories");
  const boardsEl = document.getElementById("boards");

  if (categoriesEl) {
    categoriesEl.innerHTML = categories
      .map(
        (c) => `
        <a class="categoryCard" href="./board.html?board=${encodeURIComponent(c.id)}&skipLoading=1">
          <div class="emoji">${c.emoji}</div>
          <strong>${escapeHtml(c.name)}</strong>
          <span>${escapeHtml(c.hint)}</span>
        </a>
      `
      )
      .join("");
  }

  if (boardsEl) {
    boardsEl.innerHTML = boards
      .map(
        (b) => `
        <a class="feedCard" href="./board.html?board=${encodeURIComponent(b.id)}&skipLoading=1">
          <div class="feedCardHeader">
            <div class="board">${escapeHtml(b.board)}</div>
            <div class="titleTxt">${escapeHtml(b.title)}</div>
          </div>
          <div class="thumbWide" aria-hidden="true"></div>
          <div class="feedCardMeta"><span>${escapeHtml(b.stats)}</span></div>
        </a>
      `
      )
      .join("");
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m]));
  }
})();

