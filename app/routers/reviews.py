# app/routers/reviews.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.db import get_session
from app.security import decode_token, ensure_token_type

from pydantic import BaseModel

# 모델
from app.models import (
    ReviewDraft,
    ReviewRequest,
    UserProfile,
    StyleCatalog,
)

# 스키마 (이미 app/schemas.py에 있다고 가정)
from app.schemas import (
    ReviewDraftOut,
    ReviewRequestIn,
    ReviewRequestOut,
    ChatIn,
    ChatOut,
)

# 템플릿 기반 LLM 래퍼
from app.services.llm import generate_first_review, chat_reply

router = APIRouter(prefix="/reviews", tags=["reviews"])
security = HTTPBearer()


# 인증 헬퍼: 액세스 토큰에서 user_id 추출 
def current_user_id(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    payload = decode_token(creds.credentials)
    ensure_token_type(payload, "access")  # 액세스 토큰만 허용
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return int(sub)



# 1) 리뷰 요청 → 자동 초안 생성

@router.post("/requests", response_model=ReviewRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    body: ReviewRequestIn,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    # 1) 요청 저장
    req = ReviewRequest(user_id=user_id, **body.model_dump())
    session.add(req)
    session.commit()
    session.refresh(req)

    # 2) 스타일 결정: 명시된 style_id > 프로필의 closest_style_id
    style_id = body.style_id
    if not style_id:
        prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if prof and prof.closest_style_id:
            style_id = prof.closest_style_id

    # style_key 조회
    style_key: Optional[str] = None
    if style_id:
        st = session.get(StyleCatalog, style_id)
        if st:
            style_key = st.key

    # 3) 템플릿 기반 첫 리뷰 생성
    text = generate_first_review(
        session,
        style_key=style_key,
        restaurant_name=body.restaurant_name,
        cuisine_type=body.cuisine_type,
        price_min=body.price_min,
        price_max=body.price_max,
        requirements=body.requirements,
    )

    # 4) 초안 저장 + 요청 상태 갱신
    draft = ReviewDraft(
        user_id=user_id,
        request_id=req.id,
        style_id=style_id,
        title=(body.restaurant_name or "리뷰"),
        body=text,
        model="demo-llm",  # 실제 모델명으로 교체 가능
    )
    session.add(draft)
    req.status = "done"
    session.add(req)
    session.commit()
    session.refresh(req)
    return req


@router.get("/requests", response_model=List[ReviewRequestOut])
def list_requests(
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(ReviewRequest)
        .where(ReviewRequest.user_id == user_id)
        .order_by(ReviewRequest.created_at.desc())
    ).all()



# 2) 드래프트 목록/생성 (기존 기능 유지)

@router.get("/drafts", response_model=List[ReviewDraftOut])
def list_drafts(
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(ReviewDraft)
        .where(ReviewDraft.user_id == user_id)
        .order_by(ReviewDraft.created_at.desc())
    ).all()


class ReviewDraftCreate(BaseModel):  # BaseModel 상속
    request_id: Optional[int] = None
    persona_id: Optional[int] = None
    style_id: Optional[int] = None
    title: Optional[str] = None
    body: str
    model: Optional[str] = None


@router.post("/drafts", response_model=ReviewDraftOut, status_code=status.HTTP_201_CREATED)
def create_draft(
    draft_in: ReviewDraftCreate, 
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    draft = ReviewDraft(
        user_id=user_id,
        request_id=draft_in.request_id,
        persona_id=draft_in.persona_id,
        style_id=draft_in.style_id,
        title=draft_in.title,
        body=draft_in.body,
        model=draft_in.model,
    )
    session.add(draft)
    session.commit()
    session.refresh(draft)
    return draft



# 3) 챗봇형 이어쓰기

@router.post("/chat", response_model=ChatOut)
def chat(
    body: ChatIn,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    # 스타일 결정: 요청에 명시된 style_id > 프로필의 closest_style_id
    style_id = body.style_id
    if not style_id:
        prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if prof and prof.closest_style_id:
            style_id = prof.closest_style_id

    style_key: Optional[str] = None
    if style_id:
        st = session.get(StyleCatalog, style_id)
        if st:
            style_key = st.key

    reply_text = chat_reply(session, style_key, [t.model_dump() for t in body.history])
    return ChatOut(reply=reply_text)
