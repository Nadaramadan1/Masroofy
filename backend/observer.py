"""
observer.py
===========
Implements the **Observer** design pattern for the Masroofy application.

:class:`Observer` is an abstract base class; concrete observers (e.g.,
:class:`~notification_service.NotificationService`) implement
:meth:`Observer.update`.  :class:`Subject` manages the observer list and
broadcasts notifications.
"""

from abc import ABC, abstractmethod


class Observer(ABC):
    """Abstract base class for all event observers.

    Subclasses must implement :meth:`update` to react to notifications
    published by a :class:`Subject`.
    """

    @abstractmethod
    def update(self, data: dict) -> None:
        """Handle a notification from a :class:`Subject`.

        Args:
            data (dict): Payload describing the event.  The exact keys
                depend on the publishing subject.
        """


class Subject:
    """Manages a list of :class:`Observer` instances and notifies them.

    Any class that needs to broadcast events should inherit from or
    compose with :class:`Subject`.

    Attributes:
        _observers (list[Observer]): Internal list of registered observers.

    Example:
        >>> class MySubject(Subject):
        ...     def do_something(self):
        ...         self.notify_observers({"event": "something_happened"})
    """

    def __init__(self) -> None:
        """Initialise with an empty observer list."""
        self._observers: list = []

    def attach(self, observer: Observer) -> None:
        """Register an observer (idempotent — duplicates are ignored).

        Args:
            observer (Observer): The observer to add.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Remove a previously registered observer.

        Args:
            observer (Observer): The observer to remove.  No-op if not
                currently registered.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, data: dict = None) -> None:
        """Broadcast ``data`` to all registered observers.

        Args:
            data (dict, optional): Payload forwarded to each observer's
                :meth:`Observer.update` method.  Defaults to ``None``.
        """
        for observer in self._observers:
            observer.update(data)
