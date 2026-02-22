from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from uuid import UUID

# Task 4.2 & 4.5
class MessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096, description="Pesan dari user")

# Task 4.3
class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str = Field(..., description="'user' atau 'model'")
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# Task 4.6
class ChatHistoryResponse(BaseModel):
    session_id: UUID
    messages: List[MessageResponse]