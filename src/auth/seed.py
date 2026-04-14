"""Bootstrap the initial admin user. Idempotent.

Usage:
    AUTH_SEED_USERNAME=admin \\
    AUTH_SEED_EMAIL=admin@faclab.local \\
    AUTH_SEED_PASSWORD=ChangeMe123! \\
    python -m src.auth.seed
"""

import sys

import structlog
from environs import Env

import src
from src.auth.app.commands.create_user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from src.auth.app.repositories import UserRepository
from src.auth.domain.entities import Role
from src.container import create_wireup_container
from src.shared.infra.events.scope import create_sync_scope

logger = structlog.get_logger(__name__)


def main() -> int:
    env = Env()
    env.read_env()
    username = env("AUTH_SEED_USERNAME")
    email = env("AUTH_SEED_EMAIL")
    password = env("AUTH_SEED_PASSWORD")

    src.wireup_container = create_wireup_container()

    with create_sync_scope() as scope:
        repo = scope.get(UserRepository)
        if repo.get_by_username(username) is not None:
            logger.info("auth_seed_skip_exists", username=username)
            return 0

        handler = scope.get(CreateUserCommandHandler)
        result = handler.handle(
            CreateUserCommand(
                username=username,
                email=email,
                password=password,
                role=Role.ADMIN.value,
                is_active=True,
            )
        )
        logger.info(
            "auth_seed_created",
            user_id=result["id"],
            username=username,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
