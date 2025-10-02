# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, reviews, profile, styles, reviews_chat


app = FastAPI(title="ReviewMate API")


# --- CORS origins 파싱: str(쉼표구분) 또는 list 모두 지원 ---
def parse_origins(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [o.strip() for o in value if isinstance(o, str) and o.strip()]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        if "," in s:
            return [o.strip() for o in s.split(",") if o.strip()]
        return [s]
    return []

origins = parse_origins(getattr(settings, "CORS_ORIGINS", None))

# 참고: credentials(True)와 '*' 동시 사용은 브라우저에서 허용되지 않습니다.
allow_credentials = True
if origins == ["*"]:
    # 자격증명 쿠키/Authorization 헤더를 쓰려면 구체적 origin 목록을 사용하세요.
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:3000"],
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 장착
app.include_router(auth.router)
app.include_router(reviews.router)
app.include_router(profile.router)
app.include_router(styles.router)
app.include_router(reviews_chat.router)

# 헬스 체크
@app.get("/health")
def health():
    return {"status": "ok"}
