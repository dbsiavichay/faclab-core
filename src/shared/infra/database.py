from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from wireup import injectable


class Base(DeclarativeBase):
    pass


def create_session_factory(connection_string: str):
    if not connection_string:
        raise ValueError("Database connection string cannot be empty")

    engine = create_engine(connection_string)
    _factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @injectable(lifetime="scoped")
    def get_db_session() -> Iterator[Session]:
        session = _factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return get_db_session
