# app/routers/examples.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List

from app.db import get_session
from app.models import ReviewExample

router = APIRouter(prefix="/examples", tags=["examples"])

class ExampleIn(BaseModel):
    style_key: Optional[str] = None
    persona_id: Optional[int] = None
    title: Optional[str] = None
    text: str
    quality_score: Optional[float] = 1.0

class ExampleOut(BaseModel):
    id: int
    style_key: Optional[str]
    persona_id: Optional[int]
    title: Optional[str]
    text: str
    quality_score: Optional[float]
    class Config:  # pydantic v2면 model_config={"from_attributes": True}
        from_attributes = True

@router.post("/", response_model=ExampleOut, status_code=status.HTTP_201_CREATED)
def create_example(body: ExampleIn, session: Session = Depends(get_session)):
    if not body.style_key and not body.persona_id:
        raise HTTPException(400, "style_key 또는 persona_id 중 하나는 필요")
    ex = ReviewExample(**body.model_dump())
    session.add(ex)
    session.commit()
    session.refresh(ex)
    return ex

@router.get("/", response_model=List[ExampleOut])
def list_examples(style_key: Optional[str] = None, persona_id: Optional[int] = None, session: Session = Depends(get_session)):
    q = select(ReviewExample)
    if style_key:
        q = q.where(ReviewExample.style_key == style_key)
    if persona_id:
        q = q.where(ReviewExample.persona_id == persona_id)
    return session.exec(q.order_by(ReviewExample.quality_score.desc(), ReviewExample.id.desc())).all()
