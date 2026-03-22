(function () {
  const params = new URLSearchParams(window.location.search);
  const board = params.get("board") || "all";

  const titleEl = document.getElementById("boardTitle");
  const subtitleEl = document.getElementById("boardSubtitle");
  const videosEl = document.getElementById("videos");

  const boardNameMap = {
    dog: "강아지 게시판",
    cat: "고양이 게시판",
    rabbit: "토끼 게시판",
    hamster: "햄스터 게시판",
    panda: "판다 게시판",
    otter: "수달 게시판",
    fox: "여우 게시판",
    penguin: "펭귄 게시판",
    dog_daily: "강아지 게시판",
    cat_asmr: "고양이 게시판",
    panda_cafe: "판다 게시판",
    otter_play: "수달 게시판",
    trending: "트렌딩",
    all: "전체 게시판",
  };

  const name = boardNameMap[board] || "게시판";
  if (titleEl) titleEl.textContent = name;
  if (subtitleEl) subtitleEl.textContent = "추천 영상";

  // challenge progress: count board visits
  if (window.BugSiteState) {
    window.BugSiteState.increment("boardVisits", 1);
  }

  const prefix = name.replace(" 게시판", "");
  const vids = [
    { t: `${prefix} · 귀여움 과다: 오늘의 하이라이트`, m: "조회수 12.7만 · 1시간 전" },
    { t: `${prefix} · 힐링 모음집: 스트레스 0%`, m: "조회수 8.1만 · 3시간 전" },
    { t: `${prefix} · 짧고 강력한 컷: 심장주의`, m: "조회수 21.4만 · 어제" },
    { t: `${prefix} · 무한 반복 각: ASMR 포함`, m: "조회수 5.5만 · 2일 전" },
    { t: `${prefix} · 최애 모먼트 TOP 10`, m: "조회수 33.2만 · 1주 전" },
    { t: `${prefix} · 입문자 추천: 이것부터 보자`, m: "조회수 4.9만 · 1주 전" },
  ];

  if (videosEl) {
    videosEl.innerHTML = vids
      .map(
        (v) => `
        <a class="videoCard" href="#" onclick="return false;">
          <div class="videoThumb" aria-hidden="true"></div>
          <div class="videoBody">
            <p class="videoTitle">${escapeHtml(v.t)}</p>
            <div class="videoSub">${escapeHtml(v.m)}</div>
          </div>
        </a>
      `
      )
      .join("");
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[m]));
  }
})();

