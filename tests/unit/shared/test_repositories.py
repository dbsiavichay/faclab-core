from dataclasses import dataclass
from unittest.mock import MagicMock

from src.shared.domain.entities import Entity
from src.shared.infra.repositories import SqlAlchemyRepository


@dataclass
class FakeEntity(Entity):
    name: str = ""
    id: int | None = None


class FakeRepo(SqlAlchemyRepository[FakeEntity]):
    __model__ = MagicMock


def _make_repo():
    session = MagicMock()
    mapper = MagicMock()
    mapper.to_dict.return_value = {"name": "test"}
    mapper.to_entity.return_value = FakeEntity(id=1, name="test")
    repo = FakeRepo(session, mapper)
    return repo, session, mapper


def test_save_always_flushes():
    repo, session, _ = _make_repo()
    repo._save()
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_create_flushes():
    repo, session, _ = _make_repo()
    entity = FakeEntity(name="test")
    repo.create(entity)
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_update_flushes():
    repo, session, _ = _make_repo()
    model = MagicMock()
    session.query.return_value.get.return_value = model
    entity = FakeEntity(id=1, name="updated")
    repo.update(entity)
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_delete_flushes():
    repo, session, _ = _make_repo()
    model = MagicMock()
    session.query.return_value.get.return_value = model
    repo.delete(1)
    session.flush.assert_called_once()
    session.commit.assert_not_called()
