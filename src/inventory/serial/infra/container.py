from src.inventory.serial.app.commands.serial import (
    CreateSerialNumberCommandHandler,
    UpdateSerialStatusCommandHandler,
)
from src.inventory.serial.app.queries.serial import (
    GetSerialByIdQueryHandler,
    GetSerialByNumberQueryHandler,
    GetSerialsByProductQueryHandler,
)
from src.inventory.serial.infra.mappers import SerialNumberMapper
from src.inventory.serial.infra.repositories import SerialNumberRepository

SERIAL_INJECTABLES = [
    SerialNumberMapper,
    SerialNumberRepository,
    CreateSerialNumberCommandHandler,
    UpdateSerialStatusCommandHandler,
    GetSerialsByProductQueryHandler,
    GetSerialByNumberQueryHandler,
    GetSerialByIdQueryHandler,
]
