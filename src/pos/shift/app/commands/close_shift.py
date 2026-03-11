from dataclasses import dataclass
from decimal import Decimal

from wireup import injectable

from src.pos.shift.domain.entities import Shift
from src.pos.shift.domain.events import ShiftClosed
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.events import EventPublisher
from src.shared.app.repositories import Repository
from src.shared.domain.exceptions import NotFoundError


@dataclass
class CloseShiftCommand(Command):
    """Comando para cerrar un turno"""

    shift_id: int
    closing_balance: Decimal
    notes: str | None = None


@injectable(lifetime="scoped")
class CloseShiftCommandHandler(CommandHandler[CloseShiftCommand, dict]):
    """Handler para cerrar un turno"""

    def __init__(self, repo: Repository[Shift], event_publisher: EventPublisher):
        self.repo = repo
        self.event_publisher = event_publisher

    def _handle(self, command: CloseShiftCommand) -> dict:
        shift = self.repo.get_by_id(command.shift_id)
        if shift is None:
            raise NotFoundError(f"Shift with id {command.shift_id} not found")

        # Por ahora expected_balance = opening_balance
        # En Session 8 se integrara con ventas en efectivo
        expected_balance = shift.opening_balance

        shift.close(
            closing_balance=command.closing_balance,
            expected_balance=expected_balance,
        )

        if command.notes is not None:
            shift.notes = command.notes

        self.repo.update(shift)

        self.event_publisher.publish(
            ShiftClosed(
                aggregate_id=shift.id,
                shift_id=shift.id,
                cashier_name=shift.cashier_name,
                closing_balance=shift.closing_balance,
                expected_balance=shift.expected_balance,
                discrepancy=shift.discrepancy,
            )
        )

        return shift.dict()
