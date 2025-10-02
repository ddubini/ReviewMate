# app/routers/auth.py
# 구글 로그인 → 유저 upsert → JWT(액세스+리프레시) 발급과 리프레시로 재발급(실사용임)
from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

# 개발 모드에서도 import는 유지(실제 모드에 필요)
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.db import get_session
from app.models import User
from app.schemas import GoogleLoginIn, AuthResponse, TokenOut, UserOut, RefreshIn
from app.security import decode_token, ensure_token_type, issue_token_pair

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/google", response_model=AuthResponse)
def google_login(payload: GoogleLoginIn, session: Session = Depends(get_session)):
    
    # 1) Google id_token 검증 (개발 모드면 스킵)
    
    if settings.DEV_SKIP_GOOGLE_VERIFY:
        # 가짜 idinfo (원하면 email 등 바꿔도 됨)
        idinfo = {
            "sub": "dev-123",
            "email": "dev@example.com",
            "name": "Dev User",
            "picture": None,
        }
    else:
        try:
            idinfo = google_id_token.verify_oauth2_token(
                payload.id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception as e:
            print("[/auth/google] verify_oauth2_token failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google token verify failed: {str(e)}",
            )

    
    # 2) 필수 클레임
    
    sub = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name")
    picture = idinfo.get("picture")
    if not sub or not email:
        print("[/auth/google] missing claims:", json.dumps(idinfo, ensure_ascii=False))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing required claims",
        )

    
    # 3) 사용자 upsert
    
    try:
        user = session.exec(select(User).where(User.google_sub == sub)).first()
        if not user:
            # 동일 이메일 있으면 연결, 없으면 생성
            user = session.exec(select(User).where(User.email == email)).first()
            if user:
                user.google_sub = sub
                user.name = user.name or name
                user.picture = user.picture or picture
            else:
                user = User(email=email, google_sub=sub, name=name, picture=picture)
                session.add(user)

        session.commit()
        session.refresh(user)
    except IntegrityError as ie:
        session.rollback()
        print("[/auth/google] IntegrityError:", repr(ie))
        raise HTTPException(status_code=400, detail="DB integrity error (duplicate email/sub?)")
    except Exception as e:
        session.rollback()
        print("[/auth/google] DB unexpected error:", repr(e))
        raise HTTPException(status_code=500, detail="DB error")

    
    # 4) 토큰 페어 발급
    
    tokens = issue_token_pair(sub=str(user.id), email=user.email)

    return AuthResponse(
        user=UserOut(id=user.id, email=user.email, name=user.name, picture=user.picture),
        tokens=tokens,
        profile=None,
        closest_style=None,
        personas=None,
    )

@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn):
    data = decode_token(payload.refresh_token)
    ensure_token_type(data, "refresh")
    sub = data.get("sub")
    if not sub:
        raise HTTPException(status_code=400, detail="Invalid token payload")
    new_tokens = issue_token_pair(sub=sub)
    return TokenOut(
        access_token=new_tokens["access_token"],
        refresh_token=new_tokens["refresh_token"],
        token_type=new_tokens["token_type"],
    )
