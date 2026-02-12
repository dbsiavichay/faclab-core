"""Database session factory for wireup dependency injection.

This module provides a generator-based session factory that leverages wireup 2.7.0's
native support for Iterator and generator injection patterns.
"""

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from wireup import injectable

_session_factory: sessionmaker | None = None


def configure_session_factory(connection_string: str) -> None:
    """Configures the global session factory with database connection string.

    Args:
        connection_string: SQLAlchemy database connection string

    Raises:
        ValueError: If connection_string is empty or None
    """
    global _session_factory
    if not connection_string:
        raise ValueError("Database connection string cannot be empty")

    engine = create_engine(connection_string)
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@injectable(lifetime="scoped")
def get_db_session() -> Iterator[Session]:
    """Provides a scoped database session with automatic cleanup.

    Wireup 2.7.0+ natively supports generator injection, ensuring the session
    is properly closed after the request scope ends.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        ValueError: If session factory not configured via configure_session_factory()
    """
    if not _session_factory:
        raise ValueError(
            "Database not configured. Call configure_session_factory() first."
        )

    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
