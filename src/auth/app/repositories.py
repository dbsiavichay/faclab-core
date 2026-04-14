from src.auth.domain.entities import User
from src.shared.app.repositories import Repository


class UserRepository(Repository[User]):
    def get_by_username(self, username: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...
