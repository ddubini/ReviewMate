# settings.py
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json


class Settings(BaseSettings):
    # ---- DB & CORS ----
    DATABASE_URL: str
    CORS_ORIGINS: List[str] = []

    # ---- Google OAuth ----
    GOOGLE_CLIENT_ID: str
    DEV_SKIP_GOOGLE_VERIFY: bool = False

    # ---- JWT ----
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

    # CORS_ORIGINS 값 파싱
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, list):
            return [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            # JSON 배열 형태일 때
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
