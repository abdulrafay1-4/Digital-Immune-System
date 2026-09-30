"""Injected clock: modules never call datetime.now() or time.sleep() directly."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    def now(self) -> float:
        """Simulation seconds (or wall seconds for RealClock)."""
        ...

    def sleep(self, duration: float) -> None:
        """Advance / wait for `duration` seconds on this clock."""
        ...


class ManualClock:
    """Deterministic clock for unit tests (no SimPy dependency)."""

    def __init__(self, start: float = 0.0) -> None:
        self._t = float(start)

    def now(self) -> float:
        return self._t

    def sleep(self, duration: float) -> None:
        if duration < 0:
            raise ValueError("duration must be >= 0")
        self._t += float(duration)

    def set(self, t: float) -> None:
        self._t = float(t)


class SimPyClock:
    """Clock backed by a SimPy environment (virtual or realtime)."""

    def __init__(self, env: object) -> None:
        self._env = env

    def now(self) -> float:
        return float(self._env.now)  # type: ignore[attr-defined]

    def sleep(self, duration: float) -> None:
        if duration < 0:
            raise ValueError("duration must be >= 0")
        raise RuntimeError(
            "SimPyClock.sleep cannot block inline; yield env.timeout(duration) in a process"
        )


class RealClock:
    """Wall-clock driver for demos."""

    def now(self) -> float:
        import time as _time

        return _time.monotonic()

    def sleep(self, duration: float) -> None:
        import time as _time

        _time.sleep(duration)


class WallClock(RealClock):
    """Unix time, for comparing with dates issued elsewhere (an access token's expiry)."""

    def now(self) -> float:
        import time as _time

        return _time.time()
