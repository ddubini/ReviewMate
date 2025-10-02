# config.py
from typing import List, Union
# 환경변수를 읽어와서 클래스 속성으로 매칭
from pydantic_settings import BaseSettings, SettingsConfigDict
# 필드 값이 로드될 때 유효성 검사/전처리
from pydantic import field_validator
import json

#

class Settings(BaseSettings):
    # DB & CORS 
    DATABASE_URL: str
    CORS_ORIGINS: List[str] = []

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    DEV_SKIP_GOOGLE_VERIFY: bool = False

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # .env 파일을 읽도록 지정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra= "ignore",
    )

    # Pydantic이 타입으로 강제 변환하기 이전 단계에서 이 함수를 먼저 돌림
    # 들어온 원시값을 List[str](원하는 형태)로 직접 가공
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # 리스트로 들어온 경우고 공백, 널값 없애기
        if isinstance(v, list):
            return [s.strip() for s in v if isinstance(s, str) and s.strip()]
        # 문자열로 들어온 경우
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            # JSON 배열 형태일 경우
            if s.startswith("["):
                try:
                    arr = json.loads(s)
                    if isinstance(arr, list):
                        return [x.strip() for x in arr if isinstance(x, str) and x.strip()]
                except Exception:
                    pass
            # 쉼표로 구분된 문자열일 때
            return [x.strip() for x in s.split(",") if x.strip()]
        return []


settings = Settings()
