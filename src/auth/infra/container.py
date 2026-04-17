from src.auth.app.commands.create_user import CreateUserCommandHandler
from src.auth.app.commands.login import LoginCommandHandler
from src.auth.app.commands.refresh_token import RefreshTokenCommandHandler
from src.auth.infra.mappers import UserMapper
from src.auth.infra.password_hasher import BcryptPasswordHasher
from src.auth.infra.repositories import SqlAlchemyUserRepository
from src.auth.infra.token_service import JwtTokenService

INJECTABLES = [
    UserMapper,
    BcryptPasswordHasher,
    JwtTokenService,
    SqlAlchemyUserRepository,
    CreateUserCommandHandler,
    LoginCommandHandler,
    RefreshTokenCommandHandler,
]
