"""
The same scenario on the container deployment and in the simulator, compared decision by decision.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from deploy.wire import adversary_counters
from m8_eval_harness.scenarios.catalogue import by_id

SCENARIOS = ("s1", "s2", "s3", "s4", "s5", "s6", "a4", "a5", "a10", "a12", "a13")
OUT = Path("results/container_twin")
LEAD_TICKS = 20
BASE_NODES = 3
STOLEN_ATTESTERS = ("correlation", "fusion")


def _overlay(scenario: Any, env: dict[str, str]) -> dict[str, Any]:
    """Compose services for the devices beyond the base file's three."""
    extra = range(BASE_NODES, scenario.n_nodes)
    shared = {k: env[k] for k in env if k.startswith("DIS_")} | {
        "REDIS_URL": "rediss://redis:6379/0",
        "DIS_TICK_SECONDS": "1.0",
    }
    control_volumes = (
        [f"attester-{a}-secrets:/stolen/{a}:ro" for a in STOLEN_ATTESTERS]
        if type(scenario.adversary).__name__ == "MemoryPoisoner"
        else []
    )
    services: dict[str, Any] = {
        "provision": {"volumes": [f"node-{i}-secrets:/out/nodes/mon-node-{i}" for i in extra]},
        "control": {
            "environment": {"EXPECT_RESTRICTED": "", "EXPECT_HEALTHY": "", "EXPECT_REFUSALS": ""},
            "volumes": control_volumes,
        },
        "console": {"environment": {"CONSOLE_AUTO_ADJUDICATE": "oracle"}},
    }
    for i in extra:
        services[f"node-{i}"] = {
            "image": "trust-aware-dis:latest",
            "command": "node",
            "networks": ["dis"],
            "depends_on": {"control": {"condition": "service_healthy"}},
            "environment": shared | {"NODE_ID": f"node-{i}"},
            "volumes": [f"node-{i}-secrets:/secrets:ro"],
        }
    return {"services": services, "volumes": {f"node-{i}-secrets": {} for i in extra}}


def run_containers(scenario: Any) -> dict[str, Any]:
    run_id = f"{scenario.scenario_id}-full-{scenario.seed}"
    env = os.environ | {
        "DIS_SCENARIO": scenario.scenario_id,
        "DIS_NODES": ",".join(f"node-{i}" for i in range(scenario.n_nodes)),
        "DIS_TICKS": str(scenario.ticks),
        "DIS_SEED": str(scenario.seed),
        "DIS_RUN_ID": run_id,
        "DIS_LEAD_TICKS": str(LEAD_TICKS),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    overlay = OUT / "overlay.json"
    overlay.write_text(json.dumps(_overlay(scenario, env), indent=1))
    compose = ["docker", "compose", "-p", "dis-twin", "-f", "docker-compose.yml"]
    compose += ["-f", str(overlay)]

    def call(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([*compose, *args], env=env, capture_output=True, text=True)

    call("down", "-v", "--remove-orphans")
    try:
        up = call("up", "-d", "--scale", "impersonator=0")
        control = call("ps", "-aq", "control").stdout.strip()
        waited = subprocess.run(["docker", "wait", control], capture_output=True, text=True)
        lines = call("logs", "--no-log-prefix", "control").stdout.splitlines()
        hosted = [
            json.loads(line)["adversary"]
            for line in call("logs", "--no-log-prefix").stdout.splitlines()
            if line.startswith('{"role": "node"') and '"adversary"' in line
        ]
    finally:
        call("down", "-v", "--remove-orphans")
    records = [json.loads(line) for line in lines if line.startswith("{")]
    summary = next((r for r in records if "summary" in r), None)
    if summary is None:
        tail = up.stdout[-3000:] + up.stderr[-2000:] + "\n".join(lines[-20:])
        raise RuntimeError(f"{scenario.scenario_id}: no summary from the control plane\n{tail}")
    return {
        "exit_code": int(waited.stdout.strip() or -1),
        "levels": {int(r["tick"]): r["levels"] for r in records if "tick" in r and "levels" in r},
        "enforced": {int(r["tick"]): r["enforced"] for r in records if "enforced" in r},
        "recall": {int(r["tick"]): r["recall"] for r in records if "recall" in r},
        "summary": summary["summary"],
        "hosted": hosted[0] if hosted else None,
        "checks": summary["checks"],
    }


def run_simulator(scenario: Any) -> dict[str, Any]:
    from m8_eval_harness.baselines.base import FULL
    from m8_eval_harness.scenario_runner import run_scenario

    result = run_scenario(scenario, FULL, seed=scenario.seed)
    outcomes = result.pipeline.outcomes
    return {
        "levels": {
            int(o.sim_time): {p.node_id: int(p.proposed_level) for p in o.plans} for o in outcomes
        },
        "enforced": {
            int(o.sim_time): {
                p.node_id: int(r.level)
                for p, r in zip(o.plans, o.executions, strict=True)
                if r.executed and r.level is not None
            }
            for o in outcomes
        },
        "recall": {int(o.sim_time): o.correlation.recall_boost for o in outcomes},
        "adversary": (
            adversary_counters(result.adversary) if result.adversary is not None else None
        ),
    }


def outcome(scenario: Any, levels: dict[int, dict[str, int]]) -> dict[str, Any]:
    """Device-level results, computed the same way for both sides."""
    worst: dict[str, int] = {}
    first: dict[str, int] = {}
    for tick in sorted(levels):
        for node, level in levels[tick].items():
            worst[node] = max(worst.get(node, 0), level)
            if level >= 2:
                first.setdefault(node, tick)
    truth = scenario.ground_truth
    detected = [n for n in truth if worst.get(n, 0) >= 2]
    latencies = [first[n] - onset for n, onset in truth.items() if n in first]
    return {
        "detected": len(detected),
        "attacked": len(truth),
        "healthy_restricted": sum(1 for n in scenario.healthy if worst.get(n, 0) >= 3),
        "mean_latency_ticks": sum(latencies) / len(latencies) if latencies else None,
    }


def compare(sim: dict[int, dict[str, int]], box: dict[int, dict[str, int]]) -> dict[str, Any]:
    ticks = sorted(set(sim) & set(box))
    cells = [(t, n) for t in ticks for n in sorted(set(sim[t]) | set(box[t]))]
    differ = [
        (t, n, sim[t].get(n), box[t].get(n)) for t, n in cells if sim[t].get(n) != box[t].get(n)
    ]
    return {
        "ticks_compared": len(ticks),
        "ticks_only_in_simulator": sorted(set(sim) - set(box)),
        "ticks_only_in_containers": sorted(set(box) - set(sim)),
        "device_ticks": len(cells),
        "identical": len(cells) - len(differ),
        "first_differences": differ[:20],
    }


def twin(scenario_id: str) -> dict[str, Any]:
    scenario = by_id(scenario_id)
    box = run_containers(scenario)
    sim = run_simulator(scenario)
    row = {
        "scenario": scenario_id,
        "devices": scenario.n_nodes,
        "ticks": scenario.ticks,
        "containers_exit_code": box["exit_code"],
        "container_checks": box["checks"],
        "proposed": compare(sim["levels"], box["levels"]),
        "enforced": compare(sim["enforced"], box["enforced"]),
        "recall": compare(
            {t: {"fleet": v} for t, v in sim["recall"].items()},
            {t: {"fleet": v} for t, v in box["recall"].items()},
        ),
        "simulator": outcome(scenario, sim["levels"]),
        "containers": outcome(scenario, box["levels"]),
        "adversary_simulator": sim["adversary"],
        "adversary_containers": box["summary"].get("adversary") or box["hosted"],
        "container_summary": box["summary"],
    }
    (OUT / f"{scenario_id}.json").write_text(json.dumps(row, indent=1, default=str))
    return row


def main(argv: list[str]) -> int:
    rows = [twin(s) for s in (argv or SCENARIOS)]
    for r in rows:
        p = r["proposed"]
        print(
            f"{r['scenario']:>4} {r['devices']:>3} devices {r['ticks']:>3} ticks"
            f" | exit {r['containers_exit_code']}"
            f" | identical {p['identical']}/{p['device_ticks']} proposed,"
            f" {r['enforced']['identical']}/{r['enforced']['device_ticks']} enforced"
            f" | sim {r['simulator']} | containers {r['containers']}"
        )
    if not argv:
        (OUT / "summary.json").write_text(json.dumps(rows, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
