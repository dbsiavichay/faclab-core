from src.inventory.location.app.commands.create import CreateLocationCommandHandler
from src.inventory.location.app.commands.delete import DeleteLocationCommandHandler
from src.inventory.location.app.commands.update import UpdateLocationCommandHandler
from src.inventory.location.app.queries.get_location import (
    GetAllLocationsQueryHandler,
    GetLocationByIdQueryHandler,
)
from src.inventory.location.infra.mappers import LocationMapper
from src.inventory.location.infra.repositories import LocationRepository

INJECTABLES = [
    LocationMapper,
    LocationRepository,
    CreateLocationCommandHandler,
    UpdateLocationCommandHandler,
    DeleteLocationCommandHandler,
    GetAllLocationsQueryHandler,
    GetLocationByIdQueryHandler,
]
