from wireup import injectable

from src.customers.domain.entities import Customer, CustomerContact
from src.customers.infra.models import CustomerContactModel, CustomerModel
from src.shared.infra.mappers import Mapper


@injectable(lifetime="singleton")
class CustomerMapper(Mapper[Customer, CustomerModel]):
    __entity__ = Customer
    __exclude_fields__ = frozenset({"created_at"})


@injectable(lifetime="singleton")
class CustomerContactMapper(Mapper[CustomerContact, CustomerContactModel]):
    __entity__ = CustomerContact
