from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.db import get_session
from app.security import decode_token, ensure_token_type
from app.models import ReviewChatThread, ReviewChatMessage, StyleCatalog, UserProfile
from app.schemas import ChatThreadCreate, ChatThreadOut, ChatMessageIn, ChatMessageOut
from app.services.llm import chat_reply

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()

def current_user_id(creds: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_token(creds.credentials)
    ensure_token_type(payload, "access")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return int(sub)

@router.post("/threads", response_model=ChatThreadOut, status_code=status.HTTP_201_CREATED)
def create_thread(
    body: ChatThreadCreate,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    thread = ReviewChatThread(
        user_id=user_id,
        request_id=body.request_id,
        style_id=body.style_id,
        title=body.title or "새 대화",
    )
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread

@router.get("/threads", response_model=List[ChatThreadOut])
def list_threads(
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    return session.exec(
        select(ReviewChatThread)
        .where(ReviewChatThread.user_id == user_id)
        .order_by(ReviewChatThread.created_at.desc())
    ).all()

@router.get("/threads/{thread_id}/messages", response_model=List[ChatMessageOut])
def list_messages(
    thread_id: int,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    thread = session.get(ReviewChatThread, thread_id)
    if not thread or thread.user_id != user_id:
        raise HTTPException(status_code=404, detail="Thread not found")
    return session.exec(
        select(ReviewChatMessage)
        .where(ReviewChatMessage.thread_id == thread_id)
        .order_by(ReviewChatMessage.created_at.asc())
    ).all()

@router.post("/threads/{thread_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
def add_message_and_reply(
    thread_id: int,
    body: ChatMessageIn,
    request: Request,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    thread = session.get(ReviewChatThread, thread_id)
    if not thread or thread.user_id != user_id:
        raise HTTPException(status_code=404, detail="Thread not found")

    # 1) 사용자 메시지 저장
    user_msg = ReviewChatMessage(
        thread_id=thread.id,
        user_id=user_id,
        role="user",
        content=body.content,
    )
    session.add(user_msg)
    session.commit()
    session.refresh(user_msg)

    # 2) 스타일 키 결정 (thread.style_id > profile.closest_style_id)
    style_key: Optional[str] = None
    style_id = thread.style_id
    if not style_id:
        prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
        if prof and prof.closest_style_id:
            style_id = prof.closest_style_id
    if style_id:
        st = session.get(StyleCatalog, style_id)
        if st:
            style_key = st.key

    # 3) 히스토리 로딩
    msgs = session.exec(
        select(ReviewChatMessage)
        .where(ReviewChatMessage.thread_id == thread.id)
        .order_by(ReviewChatMessage.created_at.asc())
    ).all()
    history = [{"role": m.role, "content": m.content} for m in msgs]

    # 4) 더미 LLM 답변
    reply_text = chat_reply(session, style_key, history)

    # 5) 어시스턴트 메시지 저장
    asst_msg = ReviewChatMessage(
        thread_id=thread.id,
        user_id=user_id,  # 같은 소유자 하에 저장
        role="assistant",
        content=reply_text,
    )
    session.add(asst_msg)
    session.commit()
    session.refresh(asst_msg)

    return asst_msg
