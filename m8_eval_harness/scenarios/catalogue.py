"""The evaluation scenarios, and the calibration set that must stay disjoint."""

from __future__ import annotations

from m1_monitoring.sensors.synthetic import NoiseModel
from m8_eval_harness.scenarios.adversaries import (
    CompromisedAgent,
    FutureDating,
    HealingWeaponiser,
    LyingCorrelation,
    MemoryPoisoner,
    SybilPadding,
)
from m8_eval_harness.scenarios.base import Anomaly, Scenario

S1_LOW_AND_SLOW = Scenario(
    scenario_id="s1",
    name="Low-and-slow",
    demonstrates=(
        "C1 continuous trust. A compromise shallow enough that no single reading "
        "is alarming, and only the accumulated EWMA separates it from noise."
    ),
    n_nodes=50,
    ticks=60,
    anomalies=(
        Anomaly(
            node_id="node-0",
            start_sim=10.0,
            end_sim=55.0,
            severity=0.70,
            dimensions=("behavioral", "network"),
        ),
    ),
    ground_truth={"node-0": 10.0},
    seed=101,
    notes=(
        "Two dimensions only, so the averaged observation moves about half as far "
        "as the severity suggests. Calibrated: detected at L2 in ~7 simulated "
        "seconds against ~3 for an unambiguous compromise. The latency gap is the "
        "result, not the detection."
    ),
)

S2_DISTRIBUTED_CAMPAIGN = Scenario(
    scenario_id="s2",
    name="Distributed campaign",
    demonstrates=(
        "C2 collaborative intelligence. Each device alone looks marginal; the "
        "fleet view is what makes it a campaign."
    ),
    n_nodes=50,
    ticks=40,
    anomalies=tuple(
        Anomaly(
            node_id=f"node-{i}",
            start_sim=12.0 + i,
            end_sim=36.0,
            severity=0.30,
            dimensions=("identity", "behavioral", "device", "network"),
        )
        for i in range(4)
    ),
    ground_truth={f"node-{i}": 12.0 + i for i in range(4)},
    seed=202,
    notes=(
        "Calibrated against the No-sharing arm: judging each device alone detects "
        "**none** of the 4, and that gap is the whole claim of C2. Staggered "
        "onsets, because a simultaneous campaign is easier than anything real "
        "and would flatter correlation. The scenario was calibrated when the "
        "full arm caught 2--3 of the 4 and was deliberately left there; later "
        "fixes raised it to 4 of 4 on every held-out seed, which is a result, "
        "not a target: a scenario tuned until the full arm scored 4 of 4 "
        "would have been tuned on the evaluation set."
    ),
)

S3_RECURRING_ATTACKER = Scenario(
    scenario_id="s3",
    name="Recurring attacker",
    demonstrates=(
        "C3 immune memory. The same attack shape twice; the second occurrence "
        "should be reached sooner, and only through correlation raising CTI."
    ),
    n_nodes=50,
    ticks=70,
    anomalies=(
        Anomaly("node-0", 8.0, 24.0, 0.80, ("device", "network")),
        Anomaly("node-1", 9.0, 24.0, 0.80, ("device", "network")),
        Anomaly("node-2", 44.0, 64.0, 0.80, ("device", "network")),
        Anomaly("node-3", 45.0, 64.0, 0.80, ("device", "network")),
    ),
    ground_truth={"node-0": 8.0, "node-1": 9.0, "node-2": 44.0, "node-3": 45.0},
    seed=303,
    notes=(
        "The recurrence lands on *different devices* on purpose. A pattern keyed "
        "on node ids would match trivially and prove nothing. Neither the "
        "Static-trust nor the No-sharing arm finds any of the four: correlation "
        "only amplifies a device whose own trust already shows something, so C2 "
        "has nothing to work with once C1 is removed."
    ),
)


S4_COMPROMISED_AGENT = Scenario(
    scenario_id="s4",
    name="Compromised agent",
    demonstrates=(
        "Identity binding and bounded influence. One monitoring agent under "
        "attacker control, trying to speak for devices it does not monitor and "
        "to lie about the one it does."
    ),
    n_nodes=30,
    ticks=40,
    anomalies=(Anomaly("node-0", 6.0, 36.0, 0.55),),
    ground_truth={"node-0": 6.0},
    adversary=CompromisedAgent(
        own_node="node-0",
        victim_ids=("node-5", "node-6", "node-7"),
        start_sim=6.0,
    ),
    seed=404,
    notes=(
        "Two attacks in one run. Forging for other devices should be refused "
        "outright; lying about its own is not refusable and is bounded instead, "
        "which is the honest limit this scenario measures."
    ),
)

S5_MEMORY_POISONING = Scenario(
    scenario_id="s5",
    name="Memory poisoning",
    demonstrates=(
        "Quorum-gated writes. Four escalating strategies, ending with truthful "
        "evidence under a falsified label, which quorum alone cannot see."
    ),
    n_nodes=30,
    ticks=40,
    anomalies=(Anomaly("node-0", 8.0, 30.0, 0.55),),
    ground_truth={"node-0": 8.0},
    adversary=MemoryPoisoner(start_sim=6.0, every=4.0),
    seed=505,
    notes="Result is a ratio: writes attempted against writes admitted. Target zero.",
)

S6_WEAPONISED_HEALING = Scenario(
    scenario_id="s6",
    name="Weaponised healing",
    demonstrates=(
        "The human gate and convergent recovery. A healthy device driven toward "
        "isolation repeatedly, to turn the response into the outage."
    ),
    n_nodes=30,
    ticks=50,
    anomalies=(),
    ground_truth={},
    adversary=HealingWeaponiser(target="node-1", start_sim=4.0),
    seed=606,
    notes=(
        "Ground truth is empty. Every restriction this scenario produces is a "
        "false positive, and the count of them is the result."
    ),
)

SCENARIOS: tuple[Scenario, ...] = (
    S1_LOW_AND_SLOW,
    S2_DISTRIBUTED_CAMPAIGN,
    S3_RECURRING_ATTACKER,
    S4_COMPROMISED_AGENT,
    S5_MEMORY_POISONING,
    S6_WEAPONISED_HEALING,
)


CALIBRATION: tuple[Scenario, ...] = (
    Scenario(
        scenario_id="cal-1",
        name="Calibration: quiet fleet",
        demonstrates="False-positive floor with nothing wrong anywhere.",
        n_nodes=40,
        ticks=30,
        ground_truth={},
        seed=9001,
    ),
    Scenario(
        scenario_id="cal-2",
        name="Calibration: single obvious compromise",
        demonstrates="Detection ceiling with an unambiguous signal.",
        n_nodes=40,
        ticks=30,
        anomalies=(Anomaly("node-7", 10.0, 26.0, 0.70),),
        ground_truth={"node-7": 10.0},
        seed=9002,
    ),
    Scenario(
        scenario_id="cal-3",
        name="Calibration: two devices, moderate",
        demonstrates="Where the level boundaries land for a middling signal.",
        n_nodes=40,
        ticks=30,
        anomalies=(
            Anomaly("node-3", 8.0, 24.0, 0.40, ("device",)),
            Anomaly("node-9", 8.0, 24.0, 0.40, ("device",)),
        ),
        ground_truth={"node-3": 8.0, "node-9": 8.0},
        seed=9003,
    ),
    Scenario(
        scenario_id="cal-4",
        name="Calibration: low-and-slow, identity and behaviour",
        demonstrates="Latency and escalation for a shallow sustained compromise.",
        n_nodes=50,
        ticks=60,
        anomalies=(Anomaly("node-5", 8.0, 50.0, 0.65, ("identity", "behavioral")),),
        ground_truth={"node-5": 8.0},
        seed=9004,
    ),
    Scenario(
        scenario_id="cal-5",
        name="Calibration: five-device campaign",
        demonstrates="What the fleet view adds for a moderate distributed attack.",
        n_nodes=60,
        ticks=50,
        anomalies=tuple(Anomaly(f"node-{20 + i}", 15.0 + i, 45.0, 0.35) for i in range(5)),
        ground_truth={f"node-{20 + i}": 15.0 + i for i in range(5)},
        seed=9005,
    ),
    Scenario(
        scenario_id="cal-6",
        name="Calibration: on-off attacker",
        demonstrates="Intermittent compromise, one tick in three.",
        n_nodes=40,
        ticks=90,
        anomalies=(Anomaly("node-8", 5.0, 85.0, 0.7, pulse_on=1, pulse_period=3),),
        ground_truth={"node-8": 5.0},
        seed=9006,
    ),
    Scenario(
        scenario_id="cal-7",
        name="Calibration: sub-threshold cohort",
        demonstrates="A large synchronised shift held beneath the absolute threshold.",
        n_nodes=100,
        ticks=50,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 40.0, 0.27) for i in range(30)),
        ground_truth={f"node-{i}": 10.0 for i in range(30)},
        seed=9007,
    ),
    Scenario(
        scenario_id="cal-8",
        name="Calibration: benign glitch",
        demonstrates="A two-tick sensor fault must not escalate past monitoring.",
        n_nodes=50,
        ticks=50,
        anomalies=(Anomaly("node-4", 12.0, 14.0, 0.75),),
        seed=9008,
    ),
    Scenario(
        scenario_id="cal-9",
        name="Calibration: benign maintenance",
        demonstrates="Six ticks of degraded posture, then a full recovery.",
        n_nodes=50,
        ticks=60,
        anomalies=(Anomaly("node-6", 10.0, 16.0, 0.45),),
        seed=9009,
    ),
    Scenario(
        scenario_id="cal-10",
        name="Calibration: benign fleet congestion",
        demonstrates="A correlated harmless event: the cost side of cohort implication.",
        n_nodes=60,
        ticks=60,
        anomalies=tuple(
            Anomaly(f"node-{30 + i}", 10.0, 14.0, 0.85, ("network", "device")) for i in range(15)
        ),
        seed=9010,
    ),
    Scenario(
        scenario_id="cal-11",
        name="Calibration: compromise then eviction",
        demonstrates="Recovery time once the attacker is gone.",
        n_nodes=40,
        ticks=50,
        anomalies=(Anomaly("node-2", 5.0, 20.0, 0.6),),
        ground_truth={"node-2": 5.0},
        seed=9011,
    ),
    Scenario(
        scenario_id="cal-12",
        name="Calibration: whitewashing monitor",
        demonstrates="A compromised device restarting its monitor every two ticks.",
        n_nodes=40,
        ticks=60,
        anomalies=(Anomaly("node-9", 5.0, 55.0, 0.6),),
        ground_truth={"node-9": 5.0},
        restarts={"node-9": (5.0, 2)},
        seed=9012,
    ),
    Scenario(
        scenario_id="cal-13",
        name="Calibration: quiet fleet, heavy-tailed noise",
        demonstrates="False-positive floor when healthy telemetry is not Gaussian.",
        n_nodes=40,
        ticks=40,
        noise=NoiseModel(kind="heavy_tail", sigma=0.03),
        seed=9013,
    ),
)


_CRASHED = tuple(f"node-{i}" for i in range(10, 15))

RESILIENCE: tuple[Scenario, ...] = (
    Scenario(
        scenario_id="r1",
        name="Mass device crash",
        demonstrates=(
            "Five devices lose power on the same tick and reboot twenty seconds "
            "later. Recorded as one correlated outage; each is watched while dark; "
            "none is isolated; all return to full trust."
        ),
        n_nodes=50,
        ticks=80,
        outages={n: (10.0, 30.0) for n in _CRASHED},
        seed=7001,
    ),
    Scenario(
        scenario_id="r2",
        name="Crash during a campaign",
        demonstrates=(
            "The same outage while three devices are genuinely compromised. The "
            "outage must neither hide the campaign nor be mistaken for part of it."
        ),
        n_nodes=50,
        ticks=60,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 40.0, 0.5) for i in range(3)),
        ground_truth={f"node-{i}": 10.0 for i in range(3)},
        outages={n: (10.0, 30.0) for n in _CRASHED},
        seed=7002,
    ),
    Scenario(
        scenario_id="r3",
        name="Benign glitch",
        demonstrates="A two-tick sensor fault on a healthy device. Watched, then forgotten.",
        n_nodes=50,
        ticks=60,
        anomalies=(Anomaly("node-0", 10.0, 12.0, 0.8),),
        seed=7003,
    ),
    Scenario(
        scenario_id="r4",
        name="Benign maintenance window",
        demonstrates="Eight ticks of degraded posture during planned maintenance.",
        n_nodes=50,
        ticks=80,
        anomalies=(Anomaly("node-0", 10.0, 18.0, 0.5),),
        seed=7004,
    ),
    Scenario(
        scenario_id="r5",
        name="Benign fleet-wide congestion",
        demonstrates=(
            "Twenty devices lose network and device posture together for five "
            "ticks. Indistinguishable from a campaign while it lasts; the result "
            "is how many are restricted and whether all of them come back."
        ),
        n_nodes=50,
        ticks=80,
        anomalies=tuple(
            Anomaly(f"node-{i}", 10.0, 15.0, 0.9, ("network", "device")) for i in range(20)
        ),
        seed=7005,
    ),
    Scenario(
        scenario_id="r6",
        name="Benign fleet-wide congestion, twice",
        demonstrates=(
            "The same harmless event recurring on different devices. Remembered as "
            "an attack it amplifies the second wave (V7); adjudicated, it cannot."
        ),
        n_nodes=50,
        ticks=90,
        anomalies=tuple(
            Anomaly(f"node-{i}", 10.0, 15.0, 0.9, ("network", "device")) for i in range(10)
        )
        + tuple(
            Anomaly(f"node-{i}", 60.0, 65.0, 0.9, ("network", "device")) for i in range(10, 20)
        ),
        seed=7006,
    ),
)


ADAPTIVE: tuple[Scenario, ...] = (
    Scenario(
        scenario_id="a1",
        name="On-off attacker (1 tick in 3)",
        demonstrates="Intermittent compromise that decays out of a symmetric EWMA.",
        n_nodes=50,
        ticks=100,
        anomalies=(Anomaly("node-0", 5.0, 95.0, 0.6, pulse_on=1, pulse_period=3),),
        ground_truth={"node-0": 5.0},
        seed=8001,
    ),
    Scenario(
        scenario_id="a2",
        name="On-off attacker (2 ticks in 5)",
        demonstrates="A longer duty cycle at lower severity.",
        n_nodes=50,
        ticks=100,
        anomalies=(Anomaly("node-1", 5.0, 95.0, 0.5, pulse_on=2, pulse_period=5),),
        ground_truth={"node-1": 5.0},
        seed=8002,
    ),
    Scenario(
        scenario_id="a3",
        name="Whitewashing",
        demonstrates="The compromised monitor resets its own trust every two ticks.",
        n_nodes=30,
        ticks=65,
        anomalies=(Anomaly("node-0", 5.0, 60.0, 0.6),),
        ground_truth={"node-0": 5.0},
        restarts={"node-0": (5.0, 2)},
        seed=8003,
    ),
    Scenario(
        scenario_id="a4",
        name="Ballot-stuffing (forged observation)",
        demonstrates="The monitor claims a perfect observation beside a degraded context.",
        n_nodes=30,
        ticks=60,
        anomalies=(Anomaly("node-0", 5.0, 55.0, 0.6),),
        ground_truth={"node-0": 5.0},
        forged_observation={"node-0": 5.0},
        seed=8004,
    ),
    Scenario(
        scenario_id="a5",
        name="Bad-mouthing (lying correlation agent)",
        demonstrates="Correlation implicates the whole fleet while one device is attacked.",
        n_nodes=50,
        ticks=40,
        anomalies=(Anomaly("node-0", 10.0, 38.0, 0.9),),
        ground_truth={"node-0": 10.0},
        adversary=LyingCorrelation(start_sim=10.0),
        seed=8005,
    ),
    Scenario(
        scenario_id="a6",
        name="Sub-threshold campaign",
        demonstrates="Forty of a hundred devices held beneath the implication threshold.",
        n_nodes=100,
        ticks=50,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 45.0, 0.25) for i in range(40)),
        ground_truth={f"node-{i}": 10.0 for i in range(40)},
        seed=8006,
    ),
    Scenario(
        scenario_id="a7",
        name="Sleeper",
        demonstrates="Compromise, feign recovery for fifteen ticks, resume.",
        n_nodes=40,
        ticks=70,
        anomalies=(Anomaly("node-0", 10.0, 65.0, 0.6, pulse_on=20, pulse_period=35),),
        ground_truth={"node-0": 10.0},
        seed=8007,
    ),
    Scenario(
        scenario_id="a8",
        name="Sybil padding during a campaign",
        demonstrates="Two hundred fake healthy devices join while four are attacked.",
        n_nodes=50,
        ticks=45,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 40.0, 0.5) for i in range(4)),
        ground_truth={f"node-{i}": 10.0 for i in range(4)},
        adversary=SybilPadding(count=200),
        seed=8008,
    ),
    Scenario(
        scenario_id="a9",
        name="Watermark poisoning during a campaign",
        demonstrates="A bound agent future-dates its own report every tick.",
        n_nodes=30,
        ticks=40,
        anomalies=tuple(Anomaly(f"node-{i + 1}", 10.0, 35.0, 0.7) for i in range(3)),
        ground_truth={f"node-{i + 1}": 10.0 for i in range(3)},
        adversary=FutureDating(node_id="node-0"),
        seed=8009,
    ),
    Scenario(
        scenario_id="a10",
        name="Approval flood",
        demonstrates="Twenty devices driven to isolation at once: operator load.",
        n_nodes=50,
        ticks=60,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 50.0, 0.9) for i in range(20)),
        ground_truth={f"node-{i}": 10.0 for i in range(20)},
        seed=8010,
    ),
    Scenario(
        scenario_id="a11",
        name="Sybil baseline poisoning",
        demonstrates="150 mildly degraded fake devices lift the fleet baseline under a real "
        "sub-threshold campaign. Refused outright under provisioned binding; under "
        "trust-on-first-use the baseline cap is what keeps the campaign visible.",
        n_nodes=100,
        ticks=50,
        anomalies=tuple(Anomaly(f"node-{i}", 10.0, 45.0, 0.25) for i in range(40)),
        ground_truth={f"node-{i}": 10.0 for i in range(40)},
        adversary=SybilPadding(count=150, start_sim=1.0, level=0.55),
        seed=8011,
    ),
    Scenario(
        scenario_id="a12",
        name="Selective reporting",
        demonstrates="Compromised two ticks in three; the monitor withholds exactly those "
        "reports and never misses three in a row.",
        n_nodes=30,
        ticks=80,
        anomalies=(Anomaly("node-0", 5.0, 75.0, 0.9, pulse_on=2, pulse_period=3),),
        ground_truth={"node-0": 5.0},
        selective_reporting={"node-0": 5.0},
        seed=8012,
    ),
    Scenario(
        scenario_id="a13",
        name="Suppression (lying correlation agent)",
        demonstrates="A distributed campaign the correlation agent reports as nothing.",
        n_nodes=50,
        ticks=40,
        anomalies=tuple(Anomaly(f"node-{i}", 12.0 + i, 36.0, 0.30) for i in range(4)),
        ground_truth={f"node-{i}": 12.0 + i for i in range(4)},
        adversary=LyingCorrelation(start_sim=10.0, mode="suppress"),
        seed=8013,
    ),
)


def by_id(scenario_id: str) -> Scenario:
    for scenario in (*SCENARIOS, *CALIBRATION, *RESILIENCE, *ADAPTIVE):
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"unknown scenario: {scenario_id}")
