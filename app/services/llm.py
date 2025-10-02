# app/services/llm.py
from typing import Optional, List, Dict, Any, Tuple
import json

from sqlmodel import Session, select
from jinja2 import Environment, BaseLoader

from app.models import (
    ReviewPromptTemplate,
    ReviewChatThread,
    ReviewChatMessage,
    ReviewSnapshot,      # 스냅샷 테이블 (payload_json 저장)
)

# ────────────────────────────────────────────────────────────
# Jinja2 환경: 블록 트리밍으로 출력 깔끔하게
# ────────────────────────────────────────────────────────────
_env = Environment(
    loader=BaseLoader(),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

# 스타일별 톤 프리픽스(데모)
_STYLE_TONE_PREFIX: Dict[str, str] = {
    "friendly":   "친근하고 따뜻한 말투로,",
    "plain":      "담백하고 간결한 말투로,",
    "witty":      "재치 있고 가벼운 톤으로,",
    "analytical": "차분하고 분석적인 톤으로,",
    "critical":   "솔직하고 날카로운 톤으로,",
}

def _tone_prefix_for(style_key: Optional[str]) -> str:
    return _STYLE_TONE_PREFIX.get(style_key or "", "자연스럽고 매끄러운 말투로,")

def _get_template(session: Session, prompt_key: str, style_key: Optional[str]) -> str:
    """
    템플릿 우선순위:
      1) (prompt_key, style_key) 완전일치
      2) (prompt_key, style_key=None) 공통 템플릿
      3) 내장 디폴트
    """
    if style_key:
        row = session.exec(
            select(ReviewPromptTemplate).where(
                (ReviewPromptTemplate.prompt_key == prompt_key)
                & (ReviewPromptTemplate.style_key == style_key)
            )
        ).first()
        if row:
            return row.template

    row2 = session.exec(
        select(ReviewPromptTemplate).where(
            (ReviewPromptTemplate.prompt_key == prompt_key)
            & (ReviewPromptTemplate.style_key.is_(None))
        )
    ).first()
    if row2:
        return row2.template

    # 최후의 안전망(하드코딩 템플릿)
    if prompt_key == "first_review":
        return (
            "다음 정보를 바탕으로 {{ tone_prefix }} 한국어 리뷰를 작성해줘.\n"
            "- 가게: {{ restaurant_name or '이름없음' }}\n"
            "- 음식 종류: {{ cuisine_type or '미상' }}\n"
            "- 가격대: {{ price_min or '-' }} ~ {{ price_max or '-' }}\n"
            "- 요구사항(톤/금지어 등): {{ requirements or '없음' }}\n"
            "요구사항을 지키되, 매끄럽고 자연스럽게 써줘."
        )
    if prompt_key == "chat_reply":
        return (
            "{{ tone_prefix }} 아래 대화 맥락을 고려해 한글로 답장해줘.\n"
            "{% for t in history %}"
            "{{ '[사용자]' if t.role=='user' else '[어시스턴트]' }}: {{ t.content }}\n"
            "{% endfor %}"
            "과장/모욕/금지어를 피하고, 간결하고 유익하게."
        )
    return "{{ tone_prefix }} 간단한 응답을 작성해줘."

def _render_jinja(template_str: str, context: Dict[str, Any]) -> str:
    return _env.from_string(template_str).render(**context)

# ────────────────────────────────────────────────────────────
# 공통: 스냅샷 저장 헬퍼
# ────────────────────────────────────────────────────────────
def _save_snapshot(
    session: Session,
    *,
    kind: str,  # "first_review" | "chat_reply" | ...
    payload: Dict[str, Any],
    user_id: int,
    request_id: Optional[int] = None,
    persona_id: Optional[int] = None,
    style_id: Optional[int] = None,
) -> int:
    snap = ReviewSnapshot(
        kind=kind,
        user_id=user_id,
        request_id=request_id,
        persona_id=persona_id,
        style_id=style_id,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    session.add(snap)
    session.commit()
    session.refresh(snap)
    return snap.id

# ────────────────────────────────────────────────────────────
# 1) 첫 리뷰 생성(데모) — 스냅샷까지 기록
# ────────────────────────────────────────────────────────────
def generate_first_review(
    session: Session,
    *,
    style_key: Optional[str],
    restaurant_name: Optional[str],
    cuisine_type: Optional[str],
    price_min: Optional[int],
    price_max: Optional[int],
    requirements: Optional[str],
    user_id: Optional[int] = None,            # 스냅샷용 (없어도 동작은 함)
    request_id: Optional[int] = None,         # 스냅샷용
    persona_id: Optional[int] = None,         # 스냅샷용
    style_id: Optional[int] = None,           # 스냅샷용
) -> str:
    tpl = _get_template(session, prompt_key="first_review", style_key=style_key)
    tone_prefix = _tone_prefix_for(style_key)
    prompt = _render_jinja(
        tpl,
        {
            "tone_prefix": tone_prefix,
            "restaurant_name": restaurant_name,
            "cuisine_type": cuisine_type,
            "price_min": price_min,
            "price_max": price_max,
            "requirements": requirements,
        },
    )

    # === 여기가 "LLM payload" ===
    payload = {
        "model": "demo-llm",
        "system": f"{tone_prefix} 음식 리뷰를 한국어로 작성합니다.",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    # 스냅샷 기록 (user_id가 넘어오면)
    if user_id:
        _save_snapshot(
            session,
            kind="first_review",
            payload=payload,
            user_id=user_id,
            request_id=request_id,
            persona_id=persona_id,
            style_id=style_id,
        )

    # 실제론 LLM 호출. 데모에선 생성된 프롬프트 기반의 결과처럼 더미 텍스트 반환.
    return (
        f"[DEMO: {style_key or 'default'}]\n"
        f"{prompt}\n\n"
        "— 위 정보를 반영한 리뷰 초안 —\n"
        f"{restaurant_name or '가게'}는 전반적으로 만족스러운 경험을 준 곳이었습니다. "
        f"{cuisine_type or '음식'} 메뉴가 가격 대비 충분히 납득가는 구성으로 제공되었고, "
        f"전체적인 맛의 밸런스가 좋았습니다. "
        f"특히 서비스 응대가 인상적이었고, 재방문 의사가 생겼습니다. "
        f"({requirements or '요구사항 반영'})"
    )

# ────────────────────────────────────────────────────────────
# 2) 챗봇 이어쓰기(데모)
#    - thread가 없으면 생성
#    - user turn 저장 → payload 스냅샷 → demo 응답 → assistant turn 저장
#    - 반환: (reply_text, thread_id)
# ────────────────────────────────────────────────────────────
def chat_reply(
    session: Session,
    *,
    user_id: int,
    history: List[Dict[str, Any]],       # [{role, content}]  ← API로부터 받은 히스토리
    style_key: Optional[str],
    thread_id: Optional[int] = None,     # 없으면 새로 만듦
    request_id: Optional[int] = None,    # 선택
    style_id: Optional[int] = None,      # 선택
) -> Tuple[str, int]:
    # 1) 스레드 확보
    thread = None
    if thread_id:
        thread = session.get(ReviewChatThread, thread_id)
    if not thread:
        thread = ReviewChatThread(
            user_id=user_id,
            request_id=request_id,
            style_id=style_id,
            title=None,
        )
        session.add(thread)
        session.commit()
        session.refresh(thread)

    # 2) 유저 발화 DB 저장 (history 끝에 있는 user 발화만 신입력으로 간주)
    if history and history[-1].get("role") == "user":
        session.add(ReviewChatMessage(
            thread_id=thread.id,
            user_id=user_id,
            role="user",
            content=str(history[-1].get("content") or ""),
        ))
        session.commit()

    # 3) 템플릿 → 프롬프트 → payload 생성
    tpl = _get_template(session, prompt_key="chat_reply", style_key=style_key)
    tone_prefix = _tone_prefix_for(style_key)
    prompt = _render_jinja(
        tpl,
        {
            "tone_prefix": tone_prefix,
            "history": history,
        },
    )

    payload = {
        "model": "demo-llm",
        "system": f"{tone_prefix} 리뷰 톤을 유지해 한국어로 대답합니다.",
        "messages": [
            # 히스토리를 그대로 메시지로 싣기
            *[
                {"role": t.get("role", "user"), "content": str(t.get("content", ""))}
                for t in history
            ]
        ],
        "temperature": 0.6,
        "max_tokens": 300,
    }

    # 4) 스냅샷 저장
    _save_snapshot(
        session,
        kind="chat_reply",
        payload=payload,
        user_id=user_id,
        request_id=request_id,
        style_id=style_id,
    )

    # 5) 데모 응답 생성 (진짜 LLM 붙이면 여기서 호출)
    last_user = ""
    for turn in reversed(history):
        if (turn.get("role") == "user") and (turn.get("content")):
            last_user = str(turn["content"])
            break
    if not last_user:
        last_user = "무엇을 도와드릴까요?"
    reply = f"{tone_prefix} 요청하신 내용 정리하면: {last_user[:80]} ..."

    # 6) 어시스턴트 발화 DB 저장
    session.add(ReviewChatMessage(
        thread_id=thread.id,
        user_id=user_id,
        role="assistant",
        content=reply,
    ))
    session.commit()

    return reply, thread.id

