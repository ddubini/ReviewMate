from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# 데이터베이스 연결 엔진 생성
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

# 세션을 생성해서 의존성 주입 형태로 제공
def get_session():
    with Session(engine) as session:
        yield session
