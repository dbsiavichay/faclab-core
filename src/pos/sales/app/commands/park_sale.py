from dataclasses import dataclass

from wireup import injectable

from src.sales.domain.entities import Sale
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class ParkSaleCommand(Command):
    sale_id: int
    reason: str | None = None


@injectable(lifetime="scoped")
class POSParkSaleCommandHandler(CommandHandler[ParkSaleCommand, dict]):
    def __init__(self, sale_repo: Repository[Sale]):
        self.sale_repo = sale_repo

    def _handle(self, command: ParkSaleCommand) -> dict:
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {command.sale_id} not found")

        sale.park(command.reason)
        self.sale_repo.update(sale)

        return sale.dict()
