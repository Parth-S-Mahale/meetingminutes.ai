from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ActionItem(BaseModel):
    task: str
    owner: str = "Unassigned"
    deadline: str = "Not specified"


class MeetingBaseResponse(BaseModel):
    id: int
    title: Optional[str] = None
    original_filename: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingDetailResponse(MeetingBaseResponse):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_decisions: List[str] = []
    action_items: List[ActionItem] = []
    duration_seconds: Optional[float] = None
    language: Optional[str] = None
    error_message: Optional[str] = None


class MeetingListResponse(BaseModel):
    meetings: List[MeetingBaseResponse]