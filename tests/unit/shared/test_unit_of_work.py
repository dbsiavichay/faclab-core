from unittest.mock import MagicMock

from src.shared.infra.unit_of_work import SQLAlchemyUnitOfWork


def test_commit_on_success():
    session = MagicMock()
    session_factory = MagicMock(return_value=session)

    with SQLAlchemyUnitOfWork(session_factory) as uow:
        uow.commit()

    session.commit.assert_called_once()
    session.close.assert_called_once()
    session.rollback.assert_not_called()


def test_rollback_on_exception():
    session = MagicMock()
    session_factory = MagicMock(return_value=session)

    try:
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            raise ValueError("something went wrong")
    except ValueError:
        pass

    session.rollback.assert_called_once()
    session.close.assert_called_once()


def test_close_always_called():
    session = MagicMock()
    session_factory = MagicMock(return_value=session)

    with SQLAlchemyUnitOfWork(session_factory) as uow:
        pass

    session.close.assert_called_once()
