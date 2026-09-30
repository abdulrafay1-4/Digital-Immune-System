# Recorded results

Every number in the evaluation comes from the files in this folder. Each was produced by the code
in this repository on held-out seeds, with the coefficients frozen in `m8_eval_harness/params.py`.

## `experiments/<suite>/`

| File | Contents |
|---|---|
| `rows.jsonl.gz` | One JSON row per run: scenario, arm, seed, and every metric in `m8_eval_harness/evaluation.py` |
| `summary.json`, `summary.csv` | Means and bootstrap intervals per scenario and arm |
| `comparisons.csv` | Paired comparisons against the full system: Wilcoxon p-values, Holm-corrected, with effect sizes |
| `report.md` | The same, as tables |
| `manifest.json` | Seeds, coefficients, config hash, capability binder, key posture and package versions of the run |
| `figures/` | Figures drawn from the rows |

The grid suites (`m8_eval_harness.experiment`) write all of these. The security experiments
write `rows.jsonl.gz` and `report.md`; the real-data experiments add their own `summary.json`.

Read the rows with, for example:

    python -c "import gzip, json; rows = [json.loads(l) for l in gzip.open('results/experiments/external/rows.jsonl.gz', 'rt')]; print(len(rows))"

Running a suite again writes a fresh `rows.jsonl` beside the recorded `.gz`; the code reads
`rows.jsonl` when it exists and the recorded file otherwise (`--reanalyse`, `--arms`, the
console, and `scripts/paper_figures.py`).

| Suite | What it measures | Command |
|---|---|---|
| `fyp` | Full system against Binary Zero Trust and Memoryless on s1 to s6 | `python -m m8_eval_harness.experiment --suite fyp` |
| `contributions` | One ablation per contribution, plus the C1 x C2 factorial | `--suite contributions` |
| `external` | Published comparators (fitted on calibration) on s1 to s6 and the adaptive attacks | `--suite external` |
| `adaptive` | The adaptive attacks against the ablations | `--suite adaptive` |
| `resilience` | Crashes and benign anomalies | `--suite resilience` |
| `robustness` | Random report loss, on-path frame drops, and the reporting-drift ablation | `--suite robustness` |
| `noise` | Five noise models, including noise measured on real TON_IoT traffic | `--suite noise` |
| `operators`, `adjudication` | Operator and memory-review models | `--suite operators` |
| `sweeps`, `sensitivity` | Severity and threshold curves; one coefficient moved at a time | `--suite sweeps` |
| `scale` | 50 to 5,000 devices (run with `--workers 1`) | `--suite scale --workers 1` |
| `registration` | Sybil registration under provisioned binding and trust-on-first-use | `--suite registration` |
| `llm` | Rules classifier against the local model (needs Ollama) | `--suite llm --workers 1` |
| `ablations`, `research`, `fairness` | Security-plane ablations, staged baselines, comparator settings | `--suite ablations` |
| `quorum` | 0 to 5 of 5 attesters compromised, 1,000 write attempts each | `python -m m8_eval_harness.security_experiments --experiment quorum` |
| `compromised`, `compromised_patient`, `compromised_patient_attested` | 0% to 30% of monitors compromised, loud and patient liars, with and without device attestation | `--experiment compromised` |
| `mcp` | The immune-memory MCP server under impersonation, replay, flooding, poisoning and tool-change attacks | `--experiment mcp` |
| `trusted` | Fusion, orchestrator and operator compromised one at a time | `--experiment trusted` |
| `device` | A compromised device, with and without independent observers | `--experiment device` |
| `overhead`, `overhead_replicated_fusion` | Per-tick cost of each mechanism | `--experiment overhead` |
| `ton_iot` | Real network traffic (TON_IoT) | `python -m m8_eval_harness.ton_iot evaluate` |
| `ton_iot_windows`, `ton_iot_windows_revised` | Real Windows 7 and 10 host counters, first and revised mapping | `python -m m8_eval_harness.ton_iot_windows evaluate [--mapping revised]` |
| `lanl_identity` | Real enterprise authentication with a red-team exercise (LANL) | `python -m m8_eval_harness.lanl_identity evaluate` |

## `container_twin/`

Eleven scenarios run on the container deployment and in the simulator with the same seed, compared
device by device and tick by tick (`python -m m8_eval_harness.container_twin`, needs Docker).
`summary.json` gives, per scenario, the device-ticks on which the two chose the same response level.
