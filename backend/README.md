# AI Creator Backend

AI 기반 콘텐츠 생성 플랫폼 백엔드 서버입니다.
이 서버는 **Job 기반 비동기 처리 구조**를 중심으로 설계되어 있습니다.

---

# 1. 핵심 구조 (중요)

```text
Client / Model Server
    ↓
[1] Job 생성 (POST)
    ↓
[2] 작업 수행 (외부 AI / 모델)
    ↓
[3] 상태 업데이트 (PATCH)  ← ⭐ 핵심
    ↓
[4] 결과 조회 (GET outputs)
```

👉 이 프로젝트의 핵심은
**"모든 생성 결과는 PATCH로 서버에 전달한다"** 입니다.

---

# 2. 인증

## 로그인

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test1234!"
```

응답:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

# 3. Job 생성

## 3.1 텍스트 → 이미지

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/text-to-image \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_ID",
    "prompt": "cyberpunk girl",
    "negative_prompt": "",
    "width": 512,
    "height": 512,
    "steps": 20,
    "cfg": 8,
    "sampler_name": "euler",
    "scheduler": "simple",
    "denoise": 1.0,
    "batch_size": 1,
    "save_prefix": "ComfyUI"
  }'
```

---

## 3.2 플롯 생성

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/plot-generation \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_ID",
    "prompt": "닌자 소년 성장 스토리"
  }'
```

---

# 4. Job 상태 업데이트 (🔥 핵심)

## 4.1 running 상태

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "running"
  }'
```

---

## 4.2 completed (이미지 생성 결과)

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "output_payload": {
      "progress": {
        "stage": "completed",
        "percent": 100
      },
      "outputs": [
        {
          "media_type": "image",
          "filename": "output.png",
          "original_filename": "output.png",
          "content_type": "image/png",
          "storage_provider": "local",
          "storage_path": "storage/generated/output.png",
          "public_url": "/storage/generated/output.png",
          "width": 512,
          "height": 512,
          "visibility": "private",
          "title": "generated image",
          "description": "AI output"
        }
      ]
    }
  }'
```

---

## 4.3 completed (플롯 생성)

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "output_payload": {
      "progress": {
        "stage": "completed",
        "percent": 100
      },
      "plot_text": "주인공이 성장하는 이야기"
    }
  }'
```

---

# 5. 결과 조회

## Job 상세

```bash
curl http://127.0.0.1:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer TOKEN"
```

---

## 생성 결과 조회

```bash
curl http://127.0.0.1:8000/api/v1/jobs/{job_id}/outputs \
  -H "Authorization: Bearer TOKEN"
```

응답:

```json
{
  "job_id": "...",
  "status": "completed",
  "outputs": [
    {
      "media_id": "...",
      "media_type": "image",
      "url": "/storage/generated/output.png"
    }
  ]
}
```

---

# 6. 규칙 (중요)

## 생성 Job

* completed 시 반드시 `outputs` 필요
* 없으면 400 에러 발생

## 플롯 Job

* completed 시 `plot_text` 필요

---

# 7. 저장 구조

```text
PostgreSQL → 메타데이터 저장
Object Storage → 실제 파일 저장
```

---

# 8. 기술 스택

* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT Auth
* Object Storage (R2 / Local)

---

# 9. 핵심 요약

```text
1. Job 생성
2. 모델이 작업 수행
3. 결과를 PATCH로 서버에 전달
4. 서버가 상태 + 결과 + Media 자동 처리
```

---


