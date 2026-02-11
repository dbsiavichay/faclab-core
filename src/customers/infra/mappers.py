from typing import Any

from src.customers.domain.entities import Customer, CustomerContact, TaxType
from src.customers.infra.models import CustomerContactModel, CustomerModel
from src.shared.infra.mappers import Mapper


class CustomerMapper(Mapper[Customer, CustomerModel]):
    def to_entity(self, model: CustomerModel | None) -> Customer | None:
        """Converts an infrastructure model to a domain entity"""
        if not model:
            return None

        return Customer(
            id=model.id,
            name=model.name,
            tax_id=model.tax_id,
            tax_type=TaxType(model.tax_type),
            email=model.email,
            phone=model.phone,
            address=model.address,
            city=model.city,
            state=model.state,
            country=model.country,
            credit_limit=model.credit_limit,
            payment_terms=model.payment_terms,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def to_dict(self, entity: Customer) -> dict[str, Any]:
        """Converts a domain entity to a dictionary for creating a model"""
        result = {
            "name": entity.name,
            "tax_id": entity.tax_id,
            "tax_type": entity.tax_type.value,
            "email": entity.email,
            "phone": entity.phone,
            "address": entity.address,
            "city": entity.city,
            "state": entity.state,
            "country": entity.country,
            "credit_limit": entity.credit_limit,
            "payment_terms": entity.payment_terms,
            "is_active": entity.is_active,
        }

        # Only include id if it's not None
        if entity.id is not None:
            result["id"] = entity.id

        return result


class CustomerContactMapper(Mapper[CustomerContact, CustomerContactModel]):
    def to_entity(
        self, model: CustomerContactModel | None
    ) -> CustomerContact | None:
        """Converts an infrastructure model to a domain entity"""
        if not model:
            return None

        return CustomerContact(
            id=model.id,
            customer_id=model.customer_id,
            name=model.name,
            role=model.role,
            email=model.email,
            phone=model.phone,
        )

    def to_dict(self, entity: CustomerContact) -> dict[str, Any]:
        """Converts a domain entity to a dictionary for creating a model"""
        result = {
            "customer_id": entity.customer_id,
            "name": entity.name,
            "role": entity.role,
            "email": entity.email,
            "phone": entity.phone,
        }

        # Only include id if it's not None
        if entity.id is not None:
            result["id"] = entity.id

        return result
