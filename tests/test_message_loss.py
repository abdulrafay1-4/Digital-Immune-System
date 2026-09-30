"""A lossy link and an on-path dropper: frames vanish, the monitor never knows."""

from __future__ import annotations

import simpy

from m8_eval_harness.simulator import _LossyLink


class _Sink:
    def __init__(self) -> None:
        self.frames: list[float] = []

    def publish(self, topic: str, model: float) -> None:
        self.frames.append(model)


def _run(loss: float, window: tuple[float, float] | None, seed: int = 7) -> list[float]:
    env = simpy.Environment()
    sink = _Sink()
    link = _LossyLink(sink, "node-3", seed, loss, window, env)

    def proc():
        for t in range(200):
            link.publish("trust", float(t))
            yield env.timeout(1)

    env.process(proc())
    env.run()
    return sink.frames


def test_an_on_path_dropper_removes_exactly_its_window():
    frames = _run(0.0, (20.0, 40.0))
    assert frames == [float(t) for t in range(200) if not 20 <= t < 40]


def test_random_loss_is_seeded_and_near_its_rate():
    first, again = _run(0.1, None), _run(0.1, None)
    assert first == again
    assert 0.03 <= 1 - len(first) / 200 <= 0.2
    assert _run(0.0, None) == [float(t) for t in range(200)]
