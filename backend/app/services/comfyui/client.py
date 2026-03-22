from __future__ import annotations

import time

import httpx

from app.core.config import COMFYUI_BASE_URL, COMFYUI_TIMEOUT_SECONDS


class ComfyUIClient:
    def __init__(self) -> None:
        self.base_url = COMFYUI_BASE_URL.rstrip("/")
        self.timeout = COMFYUI_TIMEOUT_SECONDS

    def submit_workflow(self, workflow: dict) -> str:
        url = f"{self.base_url}/prompt"
        payload = {"prompt": workflow}

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        prompt_id = data.get("prompt_id")
        if not prompt_id:
            raise RuntimeError("ComfyUI response does not contain prompt_id")

        return prompt_id

    def get_history(self, prompt_id: str) -> dict:
        url = f"{self.base_url}/history/{prompt_id}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()

    def wait_until_done(
        self,
        prompt_id: str,
        *,
        poll_interval: float = 1.5,
        max_wait_seconds: int = 900,
    ) -> dict:
        started = time.time()

        while True:
            history = self.get_history(prompt_id)

            if prompt_id in history:
                return history[prompt_id]

            if time.time() - started > max_wait_seconds:
                raise TimeoutError("ComfyUI generation timed out")

            time.sleep(poll_interval)

    def download_artifact(
        self,
        *,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> bytes:
        url = f"{self.base_url}/view"
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.content

    def download_image(
        self,
        *,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> bytes:
        return self.download_artifact(
            filename=filename,
            subfolder=subfolder,
            folder_type=folder_type,
        )
