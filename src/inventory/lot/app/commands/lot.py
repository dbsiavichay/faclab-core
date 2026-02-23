from dataclasses import dataclass
from datetime import date

from wireup import injectable

from src.inventory.lot.domain.entities import Lot
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import DomainError, NotFoundError


@dataclass
class CreateLotCommand(Command):
    product_id: int = 0
    lot_number: str = ""
    initial_quantity: int = 0
    manufacture_date: date | None = None
    expiration_date: date | None = None
    notes: str | None = None


@dataclass
class UpdateLotCommand(Command):
    id: int = 0
    current_quantity: int | None = None
    manufacture_date: date | None = None
    expiration_date: date | None = None
    notes: str | None = None


@injectable(lifetime="scoped")
class CreateLotCommandHandler(CommandHandler[CreateLotCommand, dict]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, command: CreateLotCommand) -> dict:
        existing = self.repo.first(
            product_id=command.product_id, lot_number=command.lot_number
        )
        if existing is not None:
            raise DomainError(
                f"Lot '{command.lot_number}' already exists for product {command.product_id}."
            )

        lot = Lot(
            product_id=command.product_id,
            lot_number=command.lot_number,
            initial_quantity=command.initial_quantity,
            current_quantity=command.initial_quantity,
            manufacture_date=command.manufacture_date,
            expiration_date=command.expiration_date,
            notes=command.notes,
        )
        lot = self.repo.create(lot)
        return lot.dict()


@injectable(lifetime="scoped")
class UpdateLotCommandHandler(CommandHandler[UpdateLotCommand, dict]):
    def __init__(self, repo: Repository[Lot]):
        self.repo = repo

    def _handle(self, command: UpdateLotCommand) -> dict:
        lot = self.repo.get_by_id(command.id)
        if lot is None:
            raise NotFoundError(f"Lot with id {command.id} not found")

        updates = {}
        if command.current_quantity is not None:
            updates["current_quantity"] = command.current_quantity
        if command.manufacture_date is not None:
            updates["manufacture_date"] = command.manufacture_date
        if command.expiration_date is not None:
            updates["expiration_date"] = command.expiration_date
        if command.notes is not None:
            updates["notes"] = command.notes

        from dataclasses import replace as dc_replace

        lot = dc_replace(lot, **updates)
        lot = self.repo.update(lot)
        return lot.dict()
