
from src.sales.domain.entities import Payment, Sale, SaleItem
from src.sales.infra.models import PaymentModel, SaleItemModel, SaleModel
from src.shared.infra.repositories import BaseRepository


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
