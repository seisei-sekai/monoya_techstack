from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DiaryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class DiaryCreate(DiaryBase):
    pass

class DiaryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class DiaryResponse(DiaryBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    aiInsight: Optional[str] = None

    class Config:
        from_attributes = True

class AIInsightResponse(BaseModel):
    insight: str

