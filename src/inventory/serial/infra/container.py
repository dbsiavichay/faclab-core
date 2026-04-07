from src.inventory.serial.app.commands.serial import (
    CreateSerialNumberCommandHandler,
    UpdateSerialStatusCommandHandler,
)
from src.inventory.serial.app.queries.serial import (
    GetSerialByIdQueryHandler,
    GetSerialByNumberQueryHandler,
    GetSerialsQueryHandler,
)
from src.inventory.serial.infra.mappers import SerialNumberMapper
from src.inventory.serial.infra.repositories import SqlAlchemySerialNumberRepository

SERIAL_INJECTABLES = [
    SerialNumberMapper,
    SqlAlchemySerialNumberRepository,
    CreateSerialNumberCommandHandler,
    UpdateSerialStatusCommandHandler,
    GetSerialsQueryHandler,
    GetSerialByNumberQueryHandler,
    GetSerialByIdQueryHandler,
]
