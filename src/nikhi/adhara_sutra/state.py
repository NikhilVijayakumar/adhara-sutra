"""Observable process-scoped application state."""

from __future__ import annotations

import logging
from typing import Any, Callable

_LOG = logging.getLogger(__name__)
StateListener = Callable[[str, str, Any], None]


class ObservableState(dict[str, Any]):
    """Dictionary notifying synchronous subscribers after top-level changes.

    Listeners receive (operation, key, value); operation is ``set`` or
    ``delete`` and deletion carries the removed value. Nested mutations do not
    emit notifications. Applications must synchronize concurrent updates.
    """

    def __init__(self) -> None:
        super().__init__()
        self._listeners: list[tuple[str | None, StateListener]] = []

    def subscribe(self, listener: StateListener, *, key: str | None = None) -> Callable[[], None]:
        """Subscribe to one key or all keys; return an idempotent unsubscribe function."""
        if not callable(listener):
            raise TypeError("listener must be callable")
        if key is not None and not isinstance(key, str):
            raise TypeError("key must be a string or None")
        entry = (key, listener)
        self._listeners.append(entry)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if active:
                active = False
                self._listeners.remove(entry)
        return unsubscribe

    def _notify(self, operation: str, key: str, value: Any) -> None:
        for watched, listener in tuple(self._listeners):
            if watched is None or watched == key:
                try:
                    listener(operation, key, value)
                except Exception:
                    _LOG.exception("State listener failed")

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, value)
        self._notify("set", key, value)

    def __delitem__(self, key: str) -> None:
        value = self[key]
        super().__delitem__(key)
        self._notify("delete", key, value)

    def update(self, *args: Any, **kwargs: Any) -> None:
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    def pop(self, key: str, *default: Any) -> Any:
        if len(default) > 1:
            raise TypeError("pop expected at most 2 arguments")
        if key not in self:
            if default:
                return default[0]
            raise KeyError(key)
        value = self[key]
        del self[key]
        return value

    def popitem(self) -> tuple[str, Any]:
        key, value = super().popitem()
        self._notify("delete", key, value)
        return key, value

    def clear(self) -> None:
        removed = tuple(self.items())
        super().clear()
        for key, value in removed:
            self._notify("delete", key, value)

    def __ior__(self, other: Any) -> "ObservableState":
        self.update(other)
        return self
