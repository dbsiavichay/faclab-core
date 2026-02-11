from collections.abc import Callable
from enum import Enum, auto
from typing import Generic, TypeVar, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

T = TypeVar("T")


class LifetimeScope(Enum):
    """Define the lifecycle of registered dependencies."""

    SINGLETON = auto()
    TRANSIENT = auto()
    SCOPED = auto()


class DependencyRegistration(Generic[T]):
    """Registration of a dependency with its factory and lifecycle information."""

    def __init__(
        self, factory: Callable[["DependencyContainer"], T], scope: LifetimeScope
    ):
        self.factory = factory
        self.scope = scope
        self.instance: T | None = None


class DependencyContainer:
    def __init__(self):
        self._registrations: dict[type, DependencyRegistration] = {}
        self._session_factory = None
        self._scoped_instances: dict[type, dict[str, object]] = {}

    def configure_db(self, connection_string: str) -> None:
        """Configures the database connection."""
        engine = create_engine(connection_string)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

    def get_db_session(self) -> Session:
        """
        Get a database session (the user is responsible for closing it).
        """
        if not self._session_factory:
            raise ValueError("Database not configured. Call configure_db first.")
        return self._session_factory()

    def get_scoped_db_session(self, scope_id: str) -> Session:
        """
        Get a database session for a specific scope (like a request).
        The session will be cached for the duration of the scope.
        """
        if not self._session_factory:
            raise ValueError("Database not configured. Call configure_db first.")

        # Create a unique key for the session in this scope
        session_key = f"db_session_{scope_id}"

        # If there's no entry for this scope, create it
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        # If there's no session for this scope, create it
        if session_key not in self._scoped_instances[scope_id]:
            self._scoped_instances[scope_id][session_key] = self._session_factory()

        return self._scoped_instances[scope_id][session_key]

    def close_scope(self, scope_id: str) -> None:
        """
        Close all resources associated with a scope.
        """
        if scope_id in self._scoped_instances:
            print(f"Closing scope {scope_id}")
            # Close the DB session if it exists
            session_key = f"db_session_{scope_id}"
            if session_key in self._scoped_instances[scope_id]:
                session = self._scoped_instances[scope_id][session_key]
                session.close()

            # Remove all instances from this scope
            del self._scoped_instances[scope_id]

    def resolve_scoped(self, interface_type: type[T], scope_id: str) -> T:
        """
        Resolves an implementation for an interface within a specific scope.
        """
        if interface_type not in self._registrations:
            raise ValueError(
                f"No implementation registered for {interface_type.__name__}"
            )

        registration = self._registrations[interface_type]

        if registration.scope == LifetimeScope.SCOPED:
            # If there's no entry for this scope, create it
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}

            # If the instance doesn't exist in this scope, create it
            if interface_type not in self._scoped_instances[scope_id]:
                self._scoped_instances[scope_id][interface_type] = registration.factory(
                    self
                )

            return cast(T, self._scoped_instances[scope_id][interface_type])
        elif registration.scope == LifetimeScope.SINGLETON:
            if registration.instance is None:
                registration.instance = registration.factory(self)
            return cast(T, registration.instance)
        else:  # TRANSIENT
            return registration.factory(self)

    def register(
        self,
        interface_type: type[T],
        implementation: T | None = None,
        factory: Callable[["DependencyContainer"], T] | None = None,
        scope: LifetimeScope = LifetimeScope.SINGLETON,
    ) -> None:
        """
        Registers an implementation for an interface.

        Args:
            interface_type: The interface type to register
            implementation: The concrete implementation (optional)
            factory: A function that creates the implementation (optional)
            scope: The dependency lifecycle

        Note: Either implementation or factory must be provided, but not both.
        """
        if implementation is not None and factory is not None:
            raise ValueError("Cannot provide both implementation and factory")

        if implementation is not None:
            # Create a factory that simply returns the implementation
            def factory_fn(_):
                return implementation

        elif factory is not None:
            factory_fn = factory
        else:
            raise ValueError("Must provide either implementation or factory")

        self._registrations[interface_type] = DependencyRegistration(factory_fn, scope)

    def resolve(self, interface_type: type[T]) -> T:
        """Resolves an implementation for an interface."""
        if interface_type not in self._registrations:
            raise ValueError(
                f"No implementation registered for {interface_type.__name__}"
            )

        registration = self._registrations[interface_type]

        if registration.scope == LifetimeScope.SINGLETON:
            if registration.instance is None:
                registration.instance = registration.factory(self)
            return cast(T, registration.instance)
        else:  # TRANSIENT
            return registration.factory(self)
