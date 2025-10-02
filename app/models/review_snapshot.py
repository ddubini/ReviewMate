# app/models/review_snapshot.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ReviewSnapshot(SQLModel, table=True):
    __tablename__ = "review_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    review_id: int = Field(index=True)    # ForeignKey("reviews.id") 로 연결하고 싶다면 FK 추가 가능
    version: int = Field(default=1)
    content: str                           # 스냅샷 텍스트(또는 JSON 문자열)
    style_params: Optional[str] = None     # JSON 문자열로 (dict를 dumps해서 저장)
    created_at: datetime = Field(default_factory=datetime.utcnow)
