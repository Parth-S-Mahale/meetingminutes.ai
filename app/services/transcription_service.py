from functools import lru_cache
from typing import Any, Dict

import torch
from transformers import pipeline

from app.config import get_settings

settings = get_settings()


def _resolve_torch_dtype():
    if settings.ASR_DEVICE.lower() == "cuda":
        return torch.float16
    return torch.float32


def _resolve_pipeline_device():
    """
    HF pipeline device:
    - 0 => first CUDA GPU
    - -1 => CPU
    """
    if settings.ASR_DEVICE.lower() == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError(
                "ASR_DEVICE is set to 'cuda' but torch.cuda.is_available() is False. "
                "Install CUDA-enabled PyTorch or switch ASR_DEVICE=cpu."
            )
        return 0
    return -1


@lru_cache(maxsize=1)
def get_asr_pipeline():
    torch_dtype = _resolve_torch_dtype()
    device = _resolve_pipeline_device()

    asr_pipe = pipeline(
        task="automatic-speech-recognition",
        model=settings.ASR_MODEL_ID,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True,
    )
    return asr_pipe


def transcribe_audio(file_path: str) -> Dict[str, Any]:
    asr_pipe = get_asr_pipeline()
    result = asr_pipe(file_path)

    transcript = result.get("text", "").strip()

    return {
        "transcript": transcript,
        "language": None,
        "duration_seconds": None,
    }