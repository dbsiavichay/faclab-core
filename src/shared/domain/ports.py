from abc import ABC, abstractmethod


class Logger(ABC):
    """Abstract base class for logging adapters."""

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        pass

    @abstractmethod
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        pass
