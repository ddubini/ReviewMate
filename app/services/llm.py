# app/services/llm.py
from typing import Optional, List, Dict, Any

from sqlmodel import Session, select
from jinja2 import Environment, BaseLoader

from app.models import ReviewPromptTemplate

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


# -------- 첫 리뷰 생성(데모) --------
def generate_first_review(
    session: Session,
    *,
    style_key: Optional[str],
    restaurant_name: Optional[str],
    cuisine_type: Optional[str],
    price_min: Optional[int],
    price_max: Optional[int],
    requirements: Optional[str],
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


# -------- 챗봇 이어쓰기(데모) --------
def chat_reply(
    session: Session,
    style_key: Optional[str],
    history: List[Dict[str, Any]],
) -> str:
    tpl = _get_template(session, prompt_key="chat_reply", style_key=style_key)
    tone_prefix = _tone_prefix_for(style_key)
    prompt = _render_jinja(
        tpl,
        {
            "tone_prefix": tone_prefix,
            "history": history,
        },
    )

    # 마지막 user 발화를 찾아 간단 요약(데모)
    last_user = ""
    for turn in reversed(history):
        if (turn.get("role") == "user") and (turn.get("content")):
            last_user = str(turn["content"])
            break

    if not last_user:
        last_user = "무엇을 도와드릴까요?"

    reply = f"{tone_prefix} 요청하신 내용 정리하면: {last_user[:80]} ..."
    # 필요시 prompt를 로깅하거나 draft에 남기도록 확장 가능
    return reply
