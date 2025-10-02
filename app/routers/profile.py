# app/routers/profile.py
from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import UserProfile
from app.security import decode_token, ensure_token_type
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["profile"])
security = HTTPBearer()

def current_user_id(creds: HTTPAuthorizationCredentials = Depends(security)) -> int:
    data = decode_token(creds.credentials)
    ensure_token_type(data, "access")
    sub = data.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return int(sub)

# 입력 스키마 (업서트용)
class UserProfileIn(BaseModel):
    age: Optional[int] = None
    mbti: Optional[str] = None
    preferred_price_min: Optional[int] = None
    preferred_price_max: Optional[int] = None
    preferred_cuisines: Optional[str] = None

# 출력 스키마는 app/schemas.py의 UserProfileOut을 그대로 사용해도 되지만
# 의존을 줄이려면 여기서도 간단히 정의 가능.
from app.schemas import UserProfileOut

@router.post("/profile", response_model=UserProfileOut)
def upsert_profile(
    body: UserProfileIn,
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not prof:
        prof = UserProfile(user_id=user_id)

    # 필드 업데이트 (넘겨준 값만 반영)
    if body.age is not None:
        prof.age = body.age
    if body.mbti is not None:
        prof.mbti = body.mbti
    if body.preferred_price_min is not None:
        prof.preferred_price_min = body.preferred_price_min
    if body.preferred_price_max is not None:
        prof.preferred_price_max = body.preferred_price_max
    if body.preferred_cuisines is not None:
        prof.preferred_cuisines = body.preferred_cuisines

    session.add(prof)
    session.commit()
    session.refresh(prof)
    return prof

@router.get("/profile", response_model=UserProfileOut)
def get_profile(
    user_id: int = Depends(current_user_id),
    session: Session = Depends(get_session),
):
    prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return prof
