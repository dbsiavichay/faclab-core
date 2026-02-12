from sqlalchemy.orm import Session
from wireup import injectable

from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.mappers import PaymentMapper, SaleItemMapper, SaleMapper
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.app.repositories import Repository
from src.shared.infra.repositories import BaseRepository


@injectable(lifetime="scoped")
class SaleRepositoryImpl(BaseRepository[Sale]):
    """
    Implementation of the SaleRepository interface using SQLAlchemy.
    Provides methods to interact with sale data in the database.
    """

    __model__ = SaleModel

    def get_by_customer_id(self, customer_id: int) -> list[Sale]:
        """Get all sales for a specific customer"""
        models = (
            self.session.query(self.__model__).filter_by(customer_id=customer_id).all()
        )
        return [self.mapper.to_entity(model) for model in models]

    def get_by_status(self, status: str) -> list[Sale]:
        """Get all sales with a specific status"""
        models = self.session.query(self.__model__).filter_by(status=status).all()
        return [self.mapper.to_entity(model) for model in models]


@injectable(lifetime="scoped")
class SaleItemRepositoryImpl(BaseRepository[SaleItem]):
    """
    Implementation of the SaleItemRepository interface using SQLAlchemy.
    Provides methods to interact with sale item data in the database.
    """

    __model__ = SaleItemModel

    def get_by_sale_id(self, sale_id: int) -> list[SaleItem]:
        """Get all items for a specific sale"""
        models = self.session.query(self.__model__).filter_by(sale_id=sale_id).all()
        return [self.mapper.to_entity(model) for model in models]


@injectable(lifetime="scoped")
class PaymentRepositoryImpl(BaseRepository[Payment]):
    """
    Implementation of the PaymentRepository interface using SQLAlchemy.
    Provides methods to interact with payment data in the database.
    """

    __model__ = PaymentModel

    def get_by_sale_id(self, sale_id: int) -> list[Payment]:
        """Get all payments for a specific sale"""
        models = self.session.query(self.__model__).filter_by(sale_id=sale_id).all()
        return [self.mapper.to_entity(model) for model in models]


@injectable(lifetime="scoped", as_type=Repository[Sale])
def create_sale_repository(session: Session, mapper: SaleMapper) -> Repository[Sale]:
    """Factory function for creating SaleRepository with generic type binding."""
    return SaleRepositoryImpl(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[SaleItem])
def create_sale_item_repository(
    session: Session, mapper: SaleItemMapper
) -> Repository[SaleItem]:
    """Factory function for creating SaleItemRepository with generic type binding."""
    return SaleItemRepositoryImpl(session, mapper)


@injectable(lifetime="scoped", as_type=Repository[Payment])
def create_payment_repository(
    session: Session, mapper: PaymentMapper
) -> Repository[Payment]:
    """Factory function for creating PaymentRepository with generic type binding."""
    return PaymentRepositoryImpl(session, mapper)
