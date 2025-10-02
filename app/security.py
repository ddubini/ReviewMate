# app/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, TypedDict

from jose import jwt, JWTError
from app.config import settings


# --- 토큰 페이로드 타입(런타임 검증용) ---
class TokenPayload(TypedDict, total=False):
    sub: str            # 주체(고유 식별자) - 보통 user_id 또는 google_sub
    email: str          # 선택: 액세스 토큰에만 포함 권장
    type: Literal["access", "refresh"]
    exp: int            # 만료(Unix timestamp)


# --- 공통 만료 계산 ---
def _expire(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


# --- 액세스 토큰 발급 ---
def create_access_token(
    sub: str,
    *,
    email: Optional[str] = None,
    minutes: Optional[int] = None,
) -> str:
    exp_dt = _expire(minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: TokenPayload = {
        "sub": sub,
        "type": "access",
        "exp": int(exp_dt.timestamp()),
    }
    if email:
        to_encode["email"] = email
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


# --- 리프레시 토큰 발급 ---
def create_refresh_token(
    sub: str,
    *,
    days: Optional[int] = None,
) -> str:
    # 리프레시는 일 단위가 자연스러워 exp를 직접 계산
    exp_dt = datetime.now(timezone.utc) + timedelta(days=days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: TokenPayload = {
        "sub": sub,
        "type": "refresh",
        "exp": int(exp_dt.timestamp()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


# --- 디코드 + 기본 검증 ---
def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        # 최소 필드 검증
        if "sub" not in payload or "type" not in payload or "exp" not in payload:
            raise ValueError("Invalid token payload")
        return payload  # type: ignore[return-value]
    except JWTError as e:
        # 만료/서명오류/형식오류 등 jose 예외를 ValueError로 래핑
        raise ValueError(str(e)) from e


# --- 토큰 타입 확인 유틸 ---
def ensure_token_type(payload: TokenPayload, expected: Literal["access", "refresh"]) -> None:
    if payload.get("type") != expected:
        raise ValueError(f"Invalid token type: expected '{expected}', got '{payload.get('type')}'")


# --- 액세스/리프레시 한 번에 발급(로그인 응답용) ---
def issue_token_pair(
    sub: str,
    *,
    email: Optional[str] = None,
    access_minutes: Optional[int] = None,
    refresh_days: Optional[int] = None,
) -> dict:
    access = create_access_token(sub, email=email, minutes=access_minutes)
    refresh = create_refresh_token(sub, days=refresh_days)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
