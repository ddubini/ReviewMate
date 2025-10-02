# app/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# -----------------------------
# 1) Auth / Token
# -----------------------------
class GoogleLoginIn(BaseModel):
    id_token: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


# -----------------------------
# 2) User & Profile
# -----------------------------
class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    is_active: Optional[bool] = True

    # Pydantic v2: ORM 객체 직렬화를 허용
    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    mbti: Optional[str] = None
    closest_style_id: Optional[int] = None
    closest_persona_id: Optional[int] = None
    preferred_price_min: Optional[int] = None
    preferred_price_max: Optional[int] = None
    preferred_cuisines: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------
# 3) Style / Persona
# -----------------------------
class StyleCatalogOut(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str] = None
    example_snippet: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonaOut(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------
# 4) Review Request / Draft
# -----------------------------
class ReviewRequestIn(BaseModel):
    restaurant_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    persona_id: Optional[int] = None     # 사용자 커스텀 스타일
    style_id: Optional[int] = None       # 카탈로그 스타일
    requirements: Optional[str] = None   # 톤/키워드/금지어 등


class ReviewRequestOut(BaseModel):
    id: int
    user_id: int
    restaurant_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    persona_id: Optional[int] = None
    style_id: Optional[int] = None
    requirements: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewDraftOut(BaseModel):
    id: int
    user_id: int
    request_id: Optional[int] = None
    persona_id: Optional[int] = None
    style_id: Optional[int] = None
    title: Optional[str] = None
    body: str
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_cents: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------
# 5) 복합 응답
# -----------------------------
class AuthResponse(BaseModel):
    user: UserOut
    tokens: TokenOut
    profile: Optional[UserProfileOut] = None
    closest_style: Optional[StyleCatalogOut] = None
    personas: Optional[List[PersonaOut]] = None

# ---------- 리뷰 요청 ----------
class ReviewRequestIn(BaseModel):
    restaurant_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    requirements: Optional[str] = None
    style_id: Optional[int] = None  # 명시하면 이 스타일로 생성

class ReviewRequestOut(BaseModel):
    id: int
    user_id: int
    restaurant_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    requirements: Optional[str] = None
    style_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}  # SQLModel -> Pydantic 변환용


# ---------- 드래프트 ----------
class ReviewDraftOut(BaseModel):
    id: int
    user_id: int
    request_id: Optional[int] = None
    persona_id: Optional[int] = None
    style_id: Optional[int] = None
    title: Optional[str] = None
    body: str
    model: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ---------- 챗봇 이어쓰기 ----------
class ChatTurn(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatIn(BaseModel):
    history: List[ChatTurn]
    style_id: Optional[int] = None  # 명시 시 해당 스타일, 없으면 프로필의 closest_style 사용

class ChatOut(BaseModel):
    reply: str

# -----------------------------
# 6) Chat History (Thread / Message)
# -----------------------------
class ChatThreadCreate(BaseModel):
    request_id: Optional[int] = None
    style_id: Optional[int] = None
    title: Optional[str] = None


class ChatThreadOut(BaseModel):
    id: int
    user_id: int
    request_id: Optional[int] = None
    style_id: Optional[int] = None
    title: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ChatMessageIn(BaseModel):
    content: str


class ChatMessageOut(BaseModel):
    id: int
    thread_id: int
    user_id: int
    role: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}
