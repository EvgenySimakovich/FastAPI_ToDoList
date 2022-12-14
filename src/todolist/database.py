from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import settings


engine = create_engine(
    settings.database_url,
    connect_args={'check_same_thread': False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> SessionLocal:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
