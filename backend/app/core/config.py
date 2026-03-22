import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
# 실행 cwd와 무관하게 backend/.env 로드 (프로젝트 루트에서 uvicorn 실행해도 동작)
load_dotenv(_BACKEND_ROOT / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
COMFYUI_TIMEOUT_SECONDS = int(os.getenv("COMFYUI_TIMEOUT_SECONDS", "120"))
COMFYUI_MAX_WAIT_SECONDS = int(os.getenv("COMFYUI_MAX_WAIT_SECONDS", "900"))

COMFYUI_IMAGE_WORKFLOW_PATH = os.getenv(
    "COMFYUI_IMAGE_WORKFLOW_PATH",
    str(_BACKEND_ROOT / "workflows" / "hackathon_image_generation_model.json"),
)
COMFYUI_VIDEO_PIPELINE_WORKFLOW_PATH = os.getenv(
    "COMFYUI_VIDEO_PIPELINE_WORKFLOW_PATH",
    str(_BACKEND_ROOT / "workflows" / "hackathon_image,video_generation.json"),
)

PLOT_GENERATION_PYTHON = os.getenv("PLOT_GENERATION_PYTHON", "python3")
PLOT_GENERATION_CLI = os.getenv(
    "PLOT_GENERATION_CLI",
    "/Users/tykim/PycharmProjects/PythonProject/hackerton_2026_03_11_image_ai/"
    "hackerton_2026_03_11_image_ai/inference/generate_plot_cli.py",
)
# meta-llama 등 게이트 모델 다운로드용 (https://huggingface.co/settings/tokens)
# .env 에서 "HF_TOKEN = xxx" 처럼 공백이 있으면 값에 공백이 섞일 수 있어 strip
_hf_raw = (os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN") or "").strip()
HF_TOKEN = _hf_raw or None
# Llama 베이스 전체를 로컬에 받아 둔 경우 (config.json 있는 폴더). HF 허브 403 회피용
PLOT_BASE_MODEL_LOCAL = (os.getenv("PLOT_BASE_MODEL_LOCAL") or "").strip() or None

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "storage")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "")
R2_ENDPOINT = os.getenv("R2_ENDPOINT", "")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL", "")
