from src.inventory.warehouse.app.commands.create import CreateWarehouseCommandHandler
from src.inventory.warehouse.app.commands.delete import DeleteWarehouseCommandHandler
from src.inventory.warehouse.app.commands.update import UpdateWarehouseCommandHandler
from src.inventory.warehouse.app.queries.get_warehouse import (
    GetAllWarehousesQueryHandler,
    GetWarehouseByIdQueryHandler,
)
from src.inventory.warehouse.infra.mappers import WarehouseMapper
from src.inventory.warehouse.infra.repositories import WarehouseRepository

INJECTABLES = [
    WarehouseMapper,
    WarehouseRepository,
    CreateWarehouseCommandHandler,
    UpdateWarehouseCommandHandler,
    DeleteWarehouseCommandHandler,
    GetAllWarehousesQueryHandler,
    GetWarehouseByIdQueryHandler,
]
