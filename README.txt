실행 방법

[정적 페이지만]
1) loading.html 을 더블클릭해서 브라우저로 여세요.
2) 로딩 후 home.html 로 이동합니다.

[AI MVP 전체: DB + 백엔드 + 프론트]
1) PostgreSQL 16: brew install postgresql@16 && brew services start postgresql@16
   (최초 1회) 슈퍼유저 postgres / DB hackathon_db 를 만들고 backend/.env 의 DATABASE_URL 과 맞춥니다.
2) backend 폴더에서: alembic upgrade head
3) backend: python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
4) 프로젝트 루트: python3 -m http.server 3000
5) 브라우저에서 http://127.0.0.1:3000/create.html — API 는 http://127.0.0.1:8000
6) ComfyUI API(기본 8188)와 플롯 LoRA용 generate_plot_cli.py 경로(PLOT_GENERATION_CLI)가 필요합니다.
7) Docker 사용 시: docker compose up -d (루트의 docker-compose.yml)

구성
- home.html: 홈(게시판/카테고리)
- search.html: 탐색(검색)
- board.html: 게시판 상세
- create.html: AI 채팅으로 만들기
- challenges.html: 도전과제(진행/보상 수령)
- account.html: 라이트/다크/시스템 + 색 테마(오션·선셋), 프로필 아이콘
- theme-boot.js: 모든 페이지에서 저장된 테마/팔레트 즉시 적용
