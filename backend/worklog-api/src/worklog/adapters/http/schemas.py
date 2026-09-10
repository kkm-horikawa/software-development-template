from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StartActivityRequest(BaseModel):
    title: str


class ErrorResponse(BaseModel):
    detail: str


class ActivityResponse(BaseModel):
    id: UUID
    title: str
    started_at: datetime
