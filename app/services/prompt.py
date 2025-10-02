from __future__ import annotations
from jinja2 import Environment, BaseLoader, StrictUndefined, Template
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from app.models import ReviewPromptTemplate

_jenv = Environment(
    loader=BaseLoader(),
    undefined=StrictUndefined,  # 누락 변수 터뜨려서 빨리 알아채게
    trim_blocks=True,
    lstrip_blocks=True,
)

def _render_tpl(tpl_str: str, ctx: Dict[str, Any]) -> str:
    tpl: Template = _jenv.from_string(tpl_str)
    return tpl.render(**ctx)

def load_template(session: Session, prompt_key: str, style_key: Optional[str]) -> str:
    # 1) 스타일 전용 > 2) 공통 템플릿 순으로 조회
    q = select(ReviewPromptTemplate).where(ReviewPromptTemplate.prompt_key == prompt_key)
    candidates = session.exec(q).all()
    spec = next((x for x in candidates if x.style_key == style_key), None)
    if spec:
        return spec.template
    common = next((x for x in candidates if x.style_key is None), None)
    if not common:
        raise ValueError(f"Template not found for key={prompt_key}")
    return common.template

def render_first_review(session: Session, style_key: Optional[str], ctx: Dict[str, Any]) -> str:
    tpl = load_template(session, "first_review", style_key)
    return _render_tpl(tpl, ctx)

def render_chat_reply(session: Session, style_key: Optional[str], ctx: Dict[str, Any]) -> str:
    tpl = load_template(session, "chat_reply", style_key)
    return _render_tpl(tpl, ctx)
