from passlib.context import CryptContext
from wireup import injectable

from src.auth.app.services.password_hasher import PasswordHasher


@injectable(lifetime="singleton", as_type=PasswordHasher)
class BcryptPasswordHasher(PasswordHasher):
    def __init__(self):
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain: str) -> str:
        return self._ctx.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._ctx.verify(plain, hashed)
