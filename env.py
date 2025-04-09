from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# 현재 프로젝트 루트를 sys.path에 추가 (import 에러 방지)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# .env 불러오기
load_dotenv()

# Alembic Config 객체 가져오기
config = context.config
fileConfig(config.config_file_name)

# db_init 패키지에서 Base, 모델들 import
from db_init.models import Base
import db_init.models  # autogenerate 시 꼭 필요함

# 메타데이터 설정
target_metadata = Base.metadata

def run_migrations_offline():
	"""오프라인 모드 (URL 기반 연결)"""
	url = os.getenv("DATABASE_URL")
	context.configure(
		url=url,
		target_metadata=target_metadata,
		literal_binds=True,
		compare_type=True,
	)

	with context.begin_transaction():
		context.run_migrations()


def run_migrations_online():
	"""온라인 모드 (엔진 기반 연결)"""
	connectable = engine_from_config(
		{
			'sqlalchemy.url': os.getenv("DATABASE_URL")  # ← 여기서 직접 넣으면 % 문제 없음
		},
		prefix="sqlalchemy.",
		poolclass=pool.NullPool,
	)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=target_metadata,
			compare_type=True,
		)

		with context.begin_transaction():
			context.run_migrations()

if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()
