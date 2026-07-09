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
from app.services.transcription_service import transcribe_audio
from app.services.summarization_service import summarize_meeting

router = APIRouter(prefix="/meetings", tags=["Meetings"])


def _to_detail_response(meeting: Meeting) -> MeetingDetailResponse:
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
    Full Step 3 flow:
    1. Save audio file
    2. Create DB record
    3. Transcribe audio
    4. Summarize transcript
    5. Persist transcript + summary + action items
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

    try:
        # Step 1: Transcribe
        meeting.status = "transcribing"
        db.commit()

        transcription_result = transcribe_audio(saved_path)
        meeting.transcript = transcription_result["transcript"]
        meeting.language = transcription_result.get("language")
        meeting.duration_seconds = transcription_result.get("duration_seconds")
        meeting.status = "transcribed"
        db.commit()

        # Step 2: Summarize
        meeting.status = "summarizing"
        db.commit()

        summary_result = summarize_meeting(
            transcript=meeting.transcript,
            title=meeting.title
        )

        meeting.summary = summary_result["summary"]
        meeting.key_decisions = json.dumps(summary_result["key_decisions"], ensure_ascii=False)
        meeting.action_items = json.dumps(summary_result["action_items"], ensure_ascii=False)
        meeting.status = "completed"

        db.commit()
        db.refresh(meeting)

    except Exception as exc:
        meeting.status = "failed"
        meeting.error_message = str(exc)
        db.commit()
        db.refresh(meeting)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meeting processing failed: {str(exc)}"
        )

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