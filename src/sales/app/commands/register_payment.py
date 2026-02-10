from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.sales.domain.entities import Payment, PaymentMethod, Sale
from src.sales.domain.events import PaymentReceived
from src.shared.app.commands import Command, CommandHandler
from src.shared.app.repositories import Repository
from src.shared.infra.events.event_bus import EventBus
from src.shared.infra.exceptions import NotFoundException


@dataclass
class RegisterPaymentCommand(Command):
    """Comando para registrar un pago"""

    sale_id: int
    amount: float
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None


class RegisterPaymentCommandHandler(CommandHandler[RegisterPaymentCommand, dict]):
    """Handler para registrar un pago y actualizar el estado de pago de la venta"""

    def __init__(
        self,
        sale_repo: Repository[Sale],
        payment_repo: Repository[Payment],
    ):
        self.sale_repo = sale_repo
        self.payment_repo = payment_repo

    def handle(self, command: RegisterPaymentCommand) -> dict:
        """Registra el pago y actualiza el estado de la venta"""
        # Obtener la venta
        sale = self.sale_repo.get_by_id(command.sale_id)
        if not sale:
            raise NotFoundException(f"Sale with id {command.sale_id} not found")

        # Validar el método de pago
        try:
            payment_method = PaymentMethod(command.payment_method)
        except ValueError:
            raise ValueError(
                f"Invalid payment method: {command.payment_method}. "
                f"Valid methods: {[m.value for m in PaymentMethod]}"
            )

        # Crear el pago
        payment = Payment(
            sale_id=command.sale_id,
            amount=Decimal(str(command.amount)),
            payment_method=payment_method,
            reference=command.reference,
            notes=command.notes,
        )

        payment = self.payment_repo.create(payment)

        # Calcular total pagado
        all_payments = self.payment_repo.filter_by(sale_id=command.sale_id)
        total_paid = sum(p.amount for p in all_payments)

        # Actualizar estado de pago de la venta
        sale.update_payment_status(total_paid)
        self.sale_repo.update(sale)

        # Publicar evento
        EventBus.publish(
            PaymentReceived(
                aggregate_id=payment.id,
                payment_id=payment.id,
                sale_id=sale.id,
                amount=float(payment.amount),
                payment_method=payment.payment_method.value,
                reference=payment.reference or "",
            )
        )

        return payment.dict()
