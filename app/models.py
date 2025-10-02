# app/models.py
# 절대 넣지 마 -> from __future__ import annotations
# 이유: 타입 힌트가 모두 문자열로 평가가 지연돼서

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


# 1) User
class User(SQLModel, table=True):
    __tablename__ = "users"

    # 식별
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    google_sub: str = Field(index=True, unique=True)
    name: Optional[str] = None
    picture: Optional[str] = None
    # 활동 상태
    is_active: bool = True
    # 갱신
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 로그인 요약
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    last_login_ua: Optional[str] = None
    login_count: int = 0

    # relations
    profile: Optional["UserProfile"] = Relationship(
        # 양방향 연결 user.profile == profile.user
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}, #User 삭제 시 연결된 프로필도 자동 삭제
    )
    personas: List["Persona"] = Relationship(back_populates="user")
    drafts: List["ReviewDraft"] = Relationship(back_populates="user")
    style_samples: List["UserStyleSample"] = Relationship(back_populates="user")
    style_scores: List["UserStyleScore"] = Relationship(back_populates="user")
    review_requests: List["ReviewRequest"] = Relationship(back_populates="user")
    snapshots: List["ReviewSnapshot"] = Relationship(back_populates="user")  


# 2) 사용자 프로필
class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    age: Optional[int] = None
    mbti: Optional[str] = Field(default=None, max_length=4)

    # 추천 포인터
    closest_style_id: Optional[int] = Field(default=None, foreign_key="style_catalog.id", index=True)
    closest_persona_id: Optional[int] = Field(default=None, foreign_key="personas.id", index=True)

    # 유저의 개인화(필요없으면 빼도 됨)
    preferred_price_min: Optional[int] = None
    preferred_price_max: Optional[int] = None
    preferred_cuisines: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relations 
    # user와 closet_style 양방향
    user: "User" = Relationship(back_populates="profile")
    closest_style: Optional["StyleCatalog"] = Relationship(back_populates="chosen_by_profiles")
    closest_persona: Optional["Persona"] = Relationship()



# 3) 사전 정의 문체 카탈로그(StyleCatalog)

class StyleCatalog(SQLModel, table=True):
    __tablename__ = "style_catalog"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    # 사용자에게 보이는 이름
    name: str
    # 스타일 설명(톤/문장 길이/이모지 사용 등) -> 프롬프트/가드레일에 주석처럼 활용
    description: Optional[str] = None
    # 예문 -> 모델 프롬프트에 few-shot seed로 넣어서 톤을 고정
    example_snippet: Optional[str] = None
    # 노출/추천 여부 토글
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    chosen_by_profiles: List["UserProfile"] = Relationship(back_populates="closest_style")
    user_scores: List["UserStyleScore"] = Relationship(back_populates="style")
    review_requests: List["ReviewRequest"] = Relationship(back_populates="style")
    drafts: List["ReviewDraft"] = Relationship(back_populates="style")
    snapshots: List["ReviewSnapshot"] = Relationship(back_populates="style") 


#
# 4) 사용자 글 샘플(UserStyleSample)

class UserStyleSample(SQLModel, table=True):
    __tablename__ = "user_style_samples"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: Optional[str] = None
    text: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="style_samples")



# 5) 사용자-문체 유사도(UserStyleScore)

class UserStyleScore(SQLModel, table=True):
    __tablename__ = "user_style_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    style_id: int = Field(foreign_key="style_catalog.id", index=True)
    score: float = 0.0
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="style_scores")
    style: "StyleCatalog" = Relationship(back_populates="user_scores")



# 6) 페르소나(Persona)

class Persona(SQLModel, table=True):
    __tablename__ = "personas"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="personas")
    drafts: List["ReviewDraft"] = Relationship(back_populates="persona")
    snapshots: List["ReviewSnapshot"] = Relationship(back_populates="persona")  # ★ 추가


#
# 7) 리뷰 요청(ReviewRequest)

class ReviewStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class ReviewRequest(SQLModel, table=True):
    __tablename__ = "review_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    #리뷰 생성 요청
    restaurant_name: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None

    # 선택 db
    persona_id: Optional[int] = Field(default=None, foreign_key="personas.id", index=True)
    style_id: Optional[int] = Field(default=None, foreign_key="style_catalog.id", index=True)

    requirements: Optional[str] = None

    status: ReviewStatus = Field(default=ReviewStatus.queued)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="review_requests")
    persona: Optional["Persona"] = Relationship()
    style: Optional["StyleCatalog"] = Relationship()
    drafts: List["ReviewDraft"] = Relationship(back_populates="request")
    snapshots: List["ReviewSnapshot"] = Relationship(back_populates="request")  # ★ 추가


    
# 8) 리뷰 초안(ReviewDraft)
# 실제 생성된 퀵픽을 통한 첫 초안

class ReviewDraft(SQLModel, table=True):
    __tablename__ = "review_drafts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    request_id: Optional[int] = Field(default=None, foreign_key="review_requests.id", index=True)
    persona_id: Optional[int] = Field(default=None, foreign_key="personas.id", index=True)
    style_id: Optional[int] = Field(default=None, foreign_key="style_catalog.id", index=True)

    title: Optional[str] = None
    body: str
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_cents: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="drafts")
    request: Optional["ReviewRequest"] = Relationship(back_populates="drafts")
    persona: Optional["Persona"] = Relationship(back_populates="drafts")
    style: Optional["StyleCatalog"] = Relationship(back_populates="drafts")



# 9) 프롬프트 템플릿(ReviewPromptTemplate) 저장

class ReviewPromptTemplate(SQLModel, table=True):
    __tablename__ = "review_prompt_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_key: str = Field(index=True)             # "first_review", "chat_reply", ...
    style_key: Optional[str] = Field(default=None)  # "friendly" 등. None=공통
    template: str                                   # Jinja2 템플릿 문자열
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# 10) 챗 스레드 & 메시지

class ReviewChatThread(SQLModel, table=True):
    __tablename__ = "review_chat_threads"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    # 어떤 리뷰 요청과 연결할지(선택)
    request_id: Optional[int] = Field(default=None, foreign_key="review_requests.id", index=True)

    # 대화에 사용할 스타일(선택)
    style_id: Optional[int] = Field(default=None, foreign_key="style_catalog.id", index=True)

    title: Optional[str] = None  # 대화방 이름(선택)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship()
    request: Optional["ReviewRequest"] = Relationship()
    style: Optional["StyleCatalog"] = Relationship()
    messages: List["ReviewChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ReviewChatMessage(SQLModel, table=True):
    __tablename__ = "review_chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="review_chat_threads.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(index=True)     # "user" | "assistant"
    content: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    thread: "ReviewChatThread" = Relationship(back_populates="messages")
    user: "User" = Relationship()


# 11) 리뷰 스냅샷(ReviewSnapshot) - llm.py 기대 스키마

class ReviewSnapshot(SQLModel, table=True):
    __tablename__ = "review_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 분류: "first_review", "chat_reply" 등
    kind: str = Field(index=True)

    # 누가 만들었는지
    user_id: int = Field(foreign_key="users.id", index=True)

    # 선택 연결(없어도 됨)
    request_id: Optional[int] = Field(default=None, foreign_key="review_requests.id", index=True)
    persona_id: Optional[int] = Field(default=None, foreign_key="personas.id", index=True)
    style_id: Optional[int] = Field(default=None, foreign_key="style_catalog.id", index=True)

    # LLM 호출 원본/메타(JSON 문자열)
    payload_json: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relations
    user: "User" = Relationship(back_populates="snapshots")
    request: Optional["ReviewRequest"] = Relationship(back_populates="snapshots")
    persona: Optional["Persona"] = Relationship(back_populates="snapshots")
    style: Optional["StyleCatalog"] = Relationship(back_populates="snapshots")

