from dataclasses import dataclass
from unittest.mock import MagicMock

from src.shared.domain.entities import Entity
from src.shared.infra.repositories import SqlAlchemyRepository


@dataclass
class FakeEntity(Entity):
    name: str = ""
    id: int | None = None


class FakeModel:
    id = 1
    name = "test"


class FakeRepo(SqlAlchemyRepository[FakeEntity]):
    __model__ = MagicMock


def _make_repo(auto_commit: bool = True):
    session = MagicMock()
    mapper = MagicMock()
    mapper.to_dict.return_value = {"name": "test"}
    mapper.to_entity.return_value = FakeEntity(id=1, name="test")
    repo = FakeRepo(session, mapper, auto_commit=auto_commit)
    return repo, session, mapper


def test_save_commits_when_auto_commit_true():
    repo, session, _ = _make_repo(auto_commit=True)
    repo._save()
    session.commit.assert_called_once()
    session.flush.assert_not_called()


def test_save_flushes_when_auto_commit_false():
    repo, session, _ = _make_repo(auto_commit=False)
    repo._save()
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_create_uses_save_with_auto_commit_true():
    repo, session, _ = _make_repo(auto_commit=True)
    entity = FakeEntity(name="test")
    repo.create(entity)
    session.commit.assert_called_once()
    session.flush.assert_not_called()


def test_create_uses_save_with_auto_commit_false():
    repo, session, _ = _make_repo(auto_commit=False)
    entity = FakeEntity(name="test")
    repo.create(entity)
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_update_uses_save_with_auto_commit_true():
    repo, session, _ = _make_repo(auto_commit=True)
    model = MagicMock()
    session.query.return_value.get.return_value = model
    entity = FakeEntity(id=1, name="updated")
    repo.update(entity)
    session.commit.assert_called_once()
    session.flush.assert_not_called()


def test_update_uses_save_with_auto_commit_false():
    repo, session, _ = _make_repo(auto_commit=False)
    model = MagicMock()
    session.query.return_value.get.return_value = model
    entity = FakeEntity(id=1, name="updated")
    repo.update(entity)
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_delete_uses_save_with_auto_commit_true():
    repo, session, _ = _make_repo(auto_commit=True)
    model = MagicMock()
    session.query.return_value.get.return_value = model
    repo.delete(1)
    session.commit.assert_called_once()
    session.flush.assert_not_called()


def test_delete_uses_save_with_auto_commit_false():
    repo, session, _ = _make_repo(auto_commit=False)
    model = MagicMock()
    session.query.return_value.get.return_value = model
    repo.delete(1)
    session.flush.assert_called_once()
    session.commit.assert_not_called()


def test_default_auto_commit_is_true():
    session = MagicMock()
    mapper = MagicMock()
    repo = FakeRepo(session, mapper)
    assert repo._auto_commit is True
