# migrations/env.py
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# --- .env 로드 방식: pydantic-settings 사용 (현재 스타일 유지) ---
from pydantic_settings import BaseSettings, SettingsConfigDict


class _S(BaseSettings):
    DATABASE_URL: str
    # .env 읽기, 기타 키는 무시
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


_cfg = _S()

# Alembic 설정 객체(alembic.ini)
config = context.config

# 로그 설정
if config.config_file_name:
    fileConfig(config.config_file_name)

# (핵심) DB URL 주입
config.set_main_option("sqlalchemy.url", _cfg.DATABASE_URL)

# (핵심) 모델 임포트: 이 import가 실행되어야 메타데이터에 테이블이 등록됩니다.
# - 단일 파일이라면: app/models.py
# - 패키지 구조라면: app/models/__init__.py가 내부에서 모든 모델을 import 하고 있어야 함
import app.models  # noqa: F401

# (핵심) Alembic이 비교에 사용할 메타데이터
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 타입 변경 감지
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    assert configuration is not None

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,            # 타입 변경 감지
            compare_server_default=True,  # server_default 변경 감지
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
