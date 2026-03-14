from src.pos.refund.app.commands.cancel_refund import CancelRefundCommandHandler
from src.pos.refund.app.commands.create_refund import CreateRefundCommandHandler
from src.pos.refund.app.commands.process_refund import ProcessRefundCommandHandler
from src.pos.refund.app.queries.get_refunds import (
    GetRefundByIdQueryHandler,
    GetRefundsQueryHandler,
)
from src.pos.refund.infra.mappers import (
    RefundItemMapper,
    RefundMapper,
    RefundPaymentMapper,
)
from src.pos.refund.infra.repositories import (
    RefundItemRepository,
    RefundPaymentRepository,
    RefundRepository,
)

POS_REFUND_INJECTABLES = [
    RefundMapper,
    RefundItemMapper,
    RefundPaymentMapper,
    RefundRepository,
    RefundItemRepository,
    RefundPaymentRepository,
    CreateRefundCommandHandler,
    ProcessRefundCommandHandler,
    CancelRefundCommandHandler,
    GetRefundByIdQueryHandler,
    GetRefundsQueryHandler,
]
