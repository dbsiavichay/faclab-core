from dataclasses import dataclass

from wireup import injectable

from src.auth.app.repositories import UserRepository
from src.shared.app.queries import Query, QueryHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class ListUsersQuery(Query):
    is_active: bool | None = None
    role: int | None = None
    limit: int | None = None
    offset: int | None = None


@injectable(lifetime="scoped")
class ListUsersQueryHandler(QueryHandler[ListUsersQuery, dict]):
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _handle(self, query: ListUsersQuery) -> dict:
        filters = {}
        if query.is_active is not None:
            filters["is_active"] = query.is_active
        if query.role is not None:
            filters["role"] = query.role
        return self.repo.paginate(limit=query.limit, offset=query.offset, **filters)


@dataclass
class GetUserByIdQuery(Query):
    user_id: int = 0


@injectable(lifetime="scoped")
class GetUserByIdQueryHandler(QueryHandler[GetUserByIdQuery, dict]):
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _handle(self, query: GetUserByIdQuery) -> dict:
        user = self.repo.get_by_id(query.user_id)
        if user is None:
            raise NotFoundError(f"User with id {query.user_id} not found")
        return user.dict()
