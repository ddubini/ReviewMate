# app/routers/styles.py
from __future__ import annotations
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlmodel import Session, select

from app.db import get_session
from app.security import decode_token, ensure_token_type
from app.models import UserProfile, StyleCatalog, UserStyleScore

router = APIRouter(prefix="/styles", tags=["styles"])
security = HTTPBearer()


def current_user_id(creds: HTTPAuthorizationCredentials = Depends(security)) -> int:
    payload = decode_token(creds.credentials)
    ensure_token_type(payload, "access")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return int(sub)


@router.get("")
def list_styles(session: Session = Depends(get_session)):
    styles = session.exec(select(StyleCatalog).where(StyleCatalog.is_active == True)).all()
    return [
        {
            "id": s.id,
            "key": s.key,
            "name": s.name,
            "description": s.description,
            "example_snippet": s.example_snippet,
        }
        for s in styles
    ]


def _heuristic_scores(age: Optional[int], mbti: Optional[str], styles: List[StyleCatalog]) -> Dict[int, float]:
    """
    아주 단순한 규칙 기반 점수. 필요시 고도화 가능.
    """
    base = {s.id: 0.3 for s in styles}  # 기본점

    m = (mbti or "").upper()
    for s in styles:
        if s.key == "analytical" and any(x in m for x in ["INT", "IST", "INTP", "INTJ"]):
            base[s.id] += 0.4
        if s.key == "friendly" and any(x in m for x in ["ENF", "ESF", "ENFP", "ESFJ"]):
            base[s.id] += 0.3
        if s.key == "witty" and any(x in m for x in ["ENFP", "ENTP"]):
            base[s.id] += 0.2
        if s.key == "critical" and any(x in m for x in ["ENTJ", "ISTJ"]):
            base[s.id] += 0.2
        if s.key == "plain" and any(x in m for x in ["ISTP", "ISFJ"]):
            base[s.id] += 0.2

    if age is not None:
        if age < 25:
            for s in styles:
                if s.key in ["friendly", "witty"]:
                    base[s.id] += 0.1
        elif age >= 40:
            for s in styles:
                if s.key in ["plain", "analytical", "critical"]:
                    base[s.id] += 0.1

    mx = max(base.values()) if base else 1.0
    return {k: round(v / mx, 3) for k, v in base.items()}


@router.post("/score")
def score_styles(user_id: int = Depends(current_user_id), session: Session = Depends(get_session)):
    # 프로필 필수
    prof = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not prof:
        raise HTTPException(status_code=400, detail="Profile not found. Save /profile first.")

    styles = session.exec(select(StyleCatalog).where(StyleCatalog.is_active == True)).all()
    if not styles:
        raise HTTPException(status_code=400, detail="No styles in catalog. Seed style_catalog first.")

    score_map = _heuristic_scores(prof.age, prof.mbti, styles)

    # 기존 점수 삭제
    session.exec(text("DELETE FROM user_style_scores WHERE user_id = :u").bindparams(u=user_id))
    session.commit()

    # 새 점수 저장 및 최고 선택
    best_id, best_score = None, -1.0
    for sid, sc in score_map.items():
        session.add(UserStyleScore(user_id=user_id, style_id=sid, score=float(sc)))
        if sc > best_score:
            best_id, best_score = sid, sc

    prof.closest_style_id = best_id
    session.add(prof)
    session.commit()

    return {
        "closest_style_id": best_id,
        "scores": [{"style_id": sid, "score": sc} for sid, sc in score_map.items()],
    }
