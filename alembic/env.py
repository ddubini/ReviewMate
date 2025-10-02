# alembic/env.py
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# --- (중요) .env 로드: CLI에서도 환경변수가 필요할 수 있음 ---
from dotenv import load_dotenv
load_dotenv()  # .env 파일을 루트에서 읽어옴

# --- 앱 설정/모델 임포트: metadata 수집을 위해 반드시 필요 ---
from app.config import settings
# 모델 모듈을 import 해야 SQLModel.metadata에 테이블이 등록됩니다.
# models가 패키지라면 from app.models import * 또는 필요한 것만 import
import app.models  # noqa: F401

# 이 설정은 alembic.ini에서 가져온 설정 객체
config = context.config

# 로그 설정 로드
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# (핵심) DB URL을 런타임에 주입
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 대상 메타데이터: SQLModel의 메타데이터 사용
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """오프라인 모드: 연결 없이 DDL 생성"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드: 실제 연결로 DDL 실행"""
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
            compare_type=True,   # 타입 변경 감지
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
