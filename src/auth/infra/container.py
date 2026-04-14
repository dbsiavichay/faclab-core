from src.auth.app.commands.create_user import CreateUserCommandHandler
from src.auth.infra.mappers import UserMapper
from src.auth.infra.password_hasher import BcryptPasswordHasher
from src.auth.infra.repositories import SqlAlchemyUserRepository

INJECTABLES = [
    UserMapper,
    BcryptPasswordHasher,
    SqlAlchemyUserRepository,
    CreateUserCommandHandler,
]
