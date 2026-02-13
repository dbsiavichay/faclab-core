from dataclasses import dataclass

from src.shared.app.commands import Command, CommandHandler


@dataclass
class CreateOrder(Command):
    product_id: int
    quantity: int


class CreateOrderHandler(CommandHandler[CreateOrder, int]):
    def _handle(self, command: CreateOrder) -> int:
        return command.product_id * command.quantity


def test_command_handler():
    handler = CreateOrderHandler()
    result = handler.handle(CreateOrder(product_id=5, quantity=3))
    assert result == 15
