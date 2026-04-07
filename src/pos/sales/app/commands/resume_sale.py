from dataclasses import dataclass

from wireup import injectable

from src.sales.app.repositories import SaleRepository
from src.shared.app.commands import Command, CommandHandler
from src.shared.domain.exceptions import NotFoundError


@dataclass
class ResumeSaleCommand(Command):
    sale_id: int


@injectable(lifetime="scoped")
class POSResumeSaleCommandHandler(CommandHandler[ResumeSaleCommand, dict]):
    def __init__(self, sale_repo: SaleRepository):
        self.sale_repo = sale_repo

    def _handle(self, command: ResumeSaleCommand) -> dict:
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundError(f"Sale with id {command.sale_id} not found")

        sale.resume()
        self.sale_repo.update(sale)

        return sale.dict()
