import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.meeting import Meeting
from app.schemas.meeting import (
    MeetingBaseResponse,
    MeetingDetailResponse,
    MeetingListResponse,
)
from app.services.file_service import save_upload_file

router = APIRouter(prefix="/meetings", tags=["Meetings"])


def _to_detail_response(meeting: Meeting) -> MeetingDetailResponse:
    """
    Convert DB model -> API response schema.
    key_decisions and action_items are stored as JSON strings in DB,
    so we parse them safely here.
    """
    key_decisions = []
    action_items = []

    if meeting.key_decisions:
        try:
            key_decisions = json.loads(meeting.key_decisions)
        except json.JSONDecodeError:
            key_decisions = []

    if meeting.action_items:
        try:
            action_items = json.loads(meeting.action_items)
        except json.JSONDecodeError:
            action_items = []

    return MeetingDetailResponse(
        id=meeting.id,
        title=meeting.title,
        original_filename=meeting.original_filename,
        status=meeting.status,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
        transcript=meeting.transcript,
        summary=meeting.summary,
        key_decisions=key_decisions,
        action_items=action_items,
        duration_seconds=meeting.duration_seconds,
        language=meeting.language,
        error_message=meeting.error_message,
    )


@router.post(
    "/upload",
    response_model=MeetingDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_meeting_audio(
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Step 2 version:
    - validate + save audio file
    - create DB record with status='uploaded'
    - return meeting record

    Step 3 will extend this endpoint to:
    - transcribe audio
    - summarize transcript
    - store transcript/summary/action items
    """
    saved_path = save_upload_file(file)

    meeting = Meeting(
        title=title,
        original_filename=file.filename,
        saved_file_path=saved_path,
        status="uploaded"
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return _to_detail_response(meeting)


@router.get("", response_model=MeetingListResponse)
def list_meetings(db: Session = Depends(get_db)):
    meetings: List[Meeting] = db.query(Meeting).order_by(Meeting.created_at.desc()).all()

    return MeetingListResponse(
        meetings=[
            MeetingBaseResponse.model_validate(meeting)
            for meeting in meetings
        ]
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with id={meeting_id} not found."
        )

    return _to_detail_response(meeting)