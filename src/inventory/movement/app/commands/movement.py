from dataclasses import dataclass
from datetime import datetime

from wireup import injectable

from src.inventory.movement.domain.constants import MovementType
from src.inventory.movement.domain.entities import Movement
from src.inventory.movement.domain.events import MovementCreated
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus


@dataclass
class CreateMovementCommand(Command):
    product_id: int = 0
    quantity: int = 0
    type: str = ""  # "in" or "out" string value
    reason: str | None = None
    date: datetime | None = None


@injectable(lifetime="scoped")
class CreateMovementCommandHandler(CommandHandler[CreateMovementCommand, dict]):
    """
    Maneja la creación de movimientos de inventario.
    Publica el evento MovementCreated que será consumido por el Stock event handler.
    """

    def __init__(self, repo: Repository[Movement]):
        self.repo = repo

    def _handle(self, command: CreateMovementCommand) -> dict:
        # Convert string type to enum
        movement_type = MovementType(command.type)

        # Create Movement entity (validates in __post_init__)
        movement = Movement(
            product_id=command.product_id,
            quantity=command.quantity,
            type=movement_type,
            reason=command.reason,
            date=command.date,
        )

        # Persist movement
        movement = self.repo.create(movement)

        # Publish domain event
        EventBus.publish(
            MovementCreated(
                aggregate_id=movement.id,
                product_id=movement.product_id,
                quantity=movement.quantity,
                type=movement.type.value,
                reason=movement.reason,
                date=movement.date,
            )
        )

        return movement.dict()
