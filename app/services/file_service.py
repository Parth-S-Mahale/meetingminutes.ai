import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings

settings = get_settings()


def ensure_directories() -> None:
    """
    Create required local directories if they don't exist.
    """
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_audio_file(file: UploadFile) -> None:
    """
    Validate extension and basic filename presence.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename."
        )

    extension = get_file_extension(file.filename)
    if extension not in settings.ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported audio format '{extension}'. "
                f"Allowed formats: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )
        )


def save_upload_file(file: UploadFile) -> str:
    """
    Save the uploaded file to the configured upload directory with a unique name.
    Returns the saved file path.
    """
    ensure_directories()
    validate_audio_file(file)

    extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return saved_path