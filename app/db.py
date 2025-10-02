from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# 데이터베이스 연결 엔진 생성
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

# DB 세션 객체 생성하여 실제 DB와 쿼리를 수행할 수 있는 통로 -> 요청 단위로 안전하게 DB 세션을 열고 닫도록 돕는 함수
def get_session():
    with Session(engine) as session:
        yield session # FastAPI 의존성 주입 패턴과 결합해서 깔끔하게 DB 접근 가능
