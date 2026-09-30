"""Bus protocol: agents talk to channels, not to each other."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
Handler = Callable[[BaseModel], None]


@runtime_checkable
class Bus(Protocol):
    def publish(self, topic: str, model: BaseModel) -> None: ...

    def subscribe(self, topic: str, handler: Handler) -> None: ...


class InProcBus:
    """In-process pub/sub for SimPy evaluation runs."""

    def __init__(self, max_log: int = 10_000) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._log: deque[tuple[str, BaseModel]] = deque(maxlen=max_log)
        self.published = 0
        self.handler_errors = 0
        self.last_handler_error: str | None = None

    def publish(self, topic: str, model: BaseModel) -> None:
        self.published += 1
        self._log.append((topic, model))
        for handler in list(self._subs.get(topic, [])):
            self._deliver(topic, handler, model)
        for handler in list(self._subs.get("*", [])):
            self._deliver(topic, handler, model)

    def _deliver(self, topic: str, handler: Handler, model: BaseModel) -> None:
        try:
            handler(model)
        except Exception as exc:  # noqa: BLE001
            self.handler_errors += 1
            self.last_handler_error = f"{topic}: {type(exc).__name__}: {exc}"

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subs[topic].append(handler)

    @property
    def log(self) -> list[tuple[str, BaseModel]]:
        return list(self._log)

    def clear_log(self) -> None:
        self._log.clear()
