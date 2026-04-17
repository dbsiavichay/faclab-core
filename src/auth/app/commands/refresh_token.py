from dataclasses import dataclass

from wireup import injectable

from src.auth.app.repositories import UserRepository
from src.auth.app.services.token_service import TokenPair, TokenService
from src.auth.domain.exceptions import InvalidTokenError
from src.shared.app.commands import Command, CommandHandler


@dataclass
class RefreshTokenCommand(Command):
    refresh_token: str = ""


@injectable(lifetime="scoped")
class RefreshTokenCommandHandler(CommandHandler[RefreshTokenCommand, TokenPair]):
    def __init__(self, repo: UserRepository, token_service: TokenService):
        self.repo = repo
        self.token_service = token_service

    def _handle(self, command: RefreshTokenCommand) -> TokenPair:
        claims = self.token_service.decode_refresh(command.refresh_token)
        user = self.repo.get_by_id(claims.sub)
        if user is None or not user.is_active:
            raise InvalidTokenError("user no longer valid")
        return self.token_service.issue_pair(user)
