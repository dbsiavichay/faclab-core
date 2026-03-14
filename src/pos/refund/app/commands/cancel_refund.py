from dataclasses import dataclass

from wireup import injectable

from src.pos.refund.domain.entities import Refund
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class CancelRefundCommand(Command):
    refund_id: int


@injectable(lifetime="scoped")
class CancelRefundCommandHandler(CommandHandler[CancelRefundCommand, dict]):
    def __init__(self, refund_repo: Repository[Refund]):
        self.refund_repo = refund_repo

    def _handle(self, command: CancelRefundCommand) -> dict:
        refund = self.refund_repo.get_by_id(command.refund_id)
        if not refund:
            raise NotFoundError(f"Refund with id {command.refund_id} not found")

        refund.cancel()
        self.refund_repo.update(refund)

        return refund.dict()
