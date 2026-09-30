# A Trust-Aware Digital Immune System

Code, data and recorded results for a digital immune system (DIS) that defends a fleet of
connected devices while treating its own defenders as possible attack surfaces.

**Authors:** Dr. Muhammad Asim, Abdul Rafay, Huzaifa Malik

The system continuously assesses each device's trust, correlates evidence across the fleet,
remembers confirmed incidents, responds in graduated steps, and controls how a device returns to
normal operation. The monitors, correlation agent, classifier and memory curator that carry out
these functions may themselves be compromised, so the design separates **reasoning** from
**authority**:

* a reported trust score is a claim: the core recomputes it from the evidence behind it;
* fleet-wide correlation can amplify suspicion about a device but never originate it, and the
  core acts only on its own recomputation of correlation;
* immune memory admits a record only with 3 of 5 independent attester signatures, and a person
  decides what the record meant;
* the response level is derived by the response engine, every action needs a signed capability
  token, and isolation needs a person's approval;
* recovery can slow a device's return to trust but never raise trust above the device's own
  evidence.

The evaluation attacks both the devices and the immune system itself, on 25 held-out scenarios, on
real data (TON_IoT network traffic and Windows host counters, and the LANL authentication log),
and on a container deployment that is checked decision by decision against the simulator.

## Contents

| Path | What it holds |
|---|---|
| `shared/` | Message schemas, the bus, the injected clock, key derivation, signing, the audit log, the Redis transport |
| `m1_monitoring/` | M1 monitoring agent: the four-dimensional context vector and EWMA trust; telemetry sources |
| `agents/` | M2 orchestrator, M3 correlation, the classifiers, planner, verifier, approval gate, memory attesters, the MCP memory server, and the closed loop (`pipeline.py`) |
| `m4_response_engine/` | M4 graduated response: levels L0 to L4, hysteresis, the capability gate |
| `m5_immune_memory/` | M5 immune memory: FAISS and SQLite store, the write and read paths |
| `m6_trust_fusion/` | M6 global trust fusion, reputation, and replicated fusion |
| `m7_self_healing/` | M7 self-healing: revoke, recalibrate, reintegrate, roll back |
| `m8_eval_harness/` | M8 evaluation: SimPy simulator, scenarios, baselines and comparators, experiments, metrics, statistics |
| `m9_capability_binder/` | M9 capability binder in Rust (PyO3), with a Python mirror |
| `m10_persona_drift/` | M10 agent identities and persona-drift detection |
| `m11_memory_hardening/` | M11 quorum gate and outlier quarantine |
| `console/` | The operator console's HTTP API: operators' signed isolation approvals and memory verdicts |
| `deploy/`, `docker-compose*.yml` | The container deployment |
| `configs/` | Frozen coefficients and every calibration file |
| `data/` | The LANL data, and where to put TON_IoT (see `data/README.md`) |
| `results/` | The recorded evaluation (see `results/README.md`) |
| `scripts/` | Checks and figures from the recorded results: headline numbers, re-run verification, figures |
| `tests/` | 921 tests, including one or more for every attack the design defends against |

The five capabilities the modules implement are referred to as C1 to C5 in the code: C1
continuous trust (M1), C2 collaborative threat intelligence (M3), C3 immune memory (M5), C4
graduated response (M4) and C5 self-healing (M7). M9 to M11 are the layer that defends the immune
system against its own components.

## Install

Python 3.11 or newer (tested on 3.12).

    python -m venv .venv
    source .venv/bin/activate
    pip install torch --index-url https://download.pytorch.org/whl/cpu    # optional: keeps the install small
    pip install -e ".[dev,agents,console,deploy]"
    pytest

Optional components:

* **Rust capability binder.** `pip install ./m9_capability_binder` (needs a Rust toolchain). Without
  it the Python mirror runs, with the same tokens and checks.
* **Local language model.** The classifier defaults to deterministic rules. The model-backed arm
  (`full_llm`) and the `llm` suite use [Ollama](https://ollama.com) with `llama3.2:3b`; those tests
  skip when no model is available.
* **Docker**, for the container deployment.

## Run one scenario

    from m8_eval_harness.baselines import by_id as arm
    from m8_eval_harness.evaluation import evaluate
    from m8_eval_harness.scenario_runner import run_scenario
    from m8_eval_harness.scenarios.catalogue import by_id as scenario

    result = run_scenario(scenario("s2"), arm("full"), seed=20000)
    print(evaluate(result)["device_tpr"])        # share of attacked devices answered

Any scenario below can be run against any arm in `m8_eval_harness/baselines`.

## Reproduce the evaluation

Every suite runs on held-out seeds (20000 onward) with the coefficients frozen in
`m8_eval_harness/params.py`, and writes to `results/experiments/<suite>/`. For example:

    python -m m8_eval_harness.experiment --suite external --seeds 30 --workers 3
    python -m m8_eval_harness.security_experiments --experiment quorum
    python -m m8_eval_harness.ton_iot_windows evaluate --workers 3
    python -m m8_eval_harness.lanl_identity evaluate --workers 3
    python -m m8_eval_harness.container_twin                  # needs Docker
    python scripts/paper_figures.py

`results/README.md` lists every suite, what it measures and its command.

**Checking the recorded results.** Every run is seeded and deterministic, so a recorded result can
be checked without re-running a whole suite:

    python scripts/headline_numbers.py         # every headline number, computed from the recorded rows
    python scripts/verify_results.py           # re-run a random sample of recorded runs; each must match
    python scripts/verify_results.py --suites quorum mcp trusted device compromised

`verify_results.py` re-runs recorded runs with this code and compares every metric with the
recorded row (timings and memory, which depend on the machine, excepted). `--sample N` sets how
many runs per suite; the security experiments are re-run in full. `--suites container_twin`
re-runs the simulator side of the container comparison. Re-analysing a copy of a suite's rows
reproduces its `summary.csv` and `comparisons.csv` exactly:

    cp -r results/experiments/fyp /tmp/fyp
    python -m m8_eval_harness.experiment --suite fyp --reanalyse --out /tmp/fyp

The larger suites take hours and several gigabytes of memory per worker; three workers suit a
machine with 16 to 32 GB. Run `scale` with `--workers 1`, since its timings measure the load.

**Calibration.** The frozen coefficients were chosen on a calibration set that shares no seeds or
attack shapes with the evaluation, and every comparator's free parameters were fitted the same
way. To redo it:

    python -m m8_eval_harness.calibrate           # the DIS's own coefficients
    python -m m8_eval_harness.baseline_fit        # every comparator's settings
    python -m m8_eval_harness.stopping_fit        # the optimal-stopping comparator
    python -m m8_eval_harness.tolerance_fit       # TOLERANCE's node model

## Scenarios

| Id | Scenario | Id | Scenario |
|---|---|---|---|
| s1 | Low-and-slow compromise | a5 | Bad-mouthing: a lying correlation agent |
| s2 | Distributed campaign | a6 | Sub-threshold campaign |
| s3 | Recurring attacker (tests immune memory) | a7 | Sleeper |
| s4 | Compromised monitoring agent | a8 | Sybil padding during a campaign |
| s5 | Memory poisoning | a9 | Watermark poisoning during a campaign |
| s6 | Weaponised healing | a10 | Approval flood |
| a1, a2 | On-off attacker | a11 | Sybil baseline poisoning |
| a3 | Whitewashing | a12 | Selective reporting (a monitor that withholds bad reports) |
| a4 | Ballot-stuffing: a forged observation | a13 | Suppression: a lying correlation agent |

Resilience scenarios r1 to r6 are not attacks: a mass crash, a crash during a campaign, a benign
glitch, a maintenance window and fleet-wide congestion (once and twice). Every restriction they
produce is a cost. The calibration scenarios (`cal-1` to `cal-13`) are separate by construction.

## Compared methods

Besides one ablation per contribution, the evaluation compares against published methods,
reimplemented and fitted on the calibration set: binary zero trust, the Beta Reputation System,
Page's CUSUM (alone, and in place of the DIS's trust score), optimal multiple stopping (Hammar and
Stadler, 2022), the Isolation Forest, Dirichlet reporter reputation, a fixed-penalty recovery
scheme, the deterministic Dendritic Cell Algorithm, and TOLERANCE (Hammar and Stadler, 2024). Each
is documented at its definition in `m8_eval_harness/baselines/`.

## Container deployment

    docker compose up --build --exit-code-from control

Three monitoring agents, the control plane, immune memory served over MCP, five memory attesters,
three trust-fusion instances, an operator console and a Redis broker run in separate containers,
over mutually authenticated TLS, with every report signed under its agent's own key. The control
plane exits non-zero unless the attacked device was restricted, the others were left alone, and
everything an impersonator sent was refused. The overlay files add device attestation, a lying
fusion instance, a patient liar and an operator deciding on the console; each file's header says
how to run it. `python -m m8_eval_harness.container_twin` runs the evaluation scenarios on this
deployment at full fleet size and compares every decision with the simulator's.

## Operator console

In the container deployment the operator console is its own container: a person's answer to an
isolation question, or verdict on a remembered incident, is signed there with a key only the
console holds, and the control plane and memory service act only on that signature. The same HTTP
API can also run on its own, over a live simulated fleet:

    python -m console --demo-accounts             # http://127.0.0.1:8700

The first start writes generated passwords to `results/console/initial-credentials.txt`.

## Design rules the code keeps

* Trust scores, correlation, fused trust and response levels are computed by deterministic
  arithmetic. A language model may only label and narrate.
* No module reads the wall clock: time comes from an injected clock, so every simulated run is
  reproducible byte for byte from its seed.
* Every inter-module message is a Pydantic model carrying its run identity (`shared/schemas.py`).
* Isolation always requires a person's approval; without it an isolation is carried out as a
  restriction.
* Coefficients are never tuned on the evaluation scenarios.

## Data

`data/` holds the LANL files the real-data experiments use; TON_IoT may not be redistributed, so
`scripts/fetch_ton_iot.py` checks and installs a copy you download. Sources, terms and citations
are in `data/README.md`. Please cite the datasets if you use them.

## License

The code is released under the MIT License (see `LICENSE`). The datasets in `data/` remain under
their own terms, given in `data/README.md`.
