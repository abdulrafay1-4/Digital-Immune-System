# Experiment report: `llm`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "llm",
  "seeds": [
    20000,
    20001,
    20002,
    20003,
    20004,
    20005,
    20006,
    20007,
    20008,
    20009
  ],
  "workers": 1,
  "git_commit": "5ccff0bc27ab096d420fe8c779e95c99d7bf68cd",
  "git_dirty": false,
  "code_dirty": false,
  "frozen_params": {
    "trust_lambda": 0.7,
    "trust_lambda_up": null,
    "cohort_margin": 0.15,
    "cohort_min_nodes": 3,
    "rep_lam_up": 0.85,
    "rep_lam_down": 0.6,
    "hysteresis_n": 3,
    "alpha": 0.4,
    "beta": 0.35,
    "gamma": 0.25,
    "cti_k": 2.0,
    "campaign_ti_threshold": 0.4,
    "cohort_baseline_cap": 0.11,
    "max_auto_restrict_fraction": 0.1,
    "min_auto_restrict": 5,
    "intermittent_window": 20,
    "intermittent_alpha": 0.0001,
    "intermittent_loss_floor": 0.01,
    "obs_weights": [
      0.25,
      0.25,
      0.25,
      0.25
    ]
  },
  "config_hash": "f7910756c9520d28",
  "capability_binder": "rust",
  "development_key": true,
  "gt_key_fingerprint": "3bc99d3a9cac8f24",
  "python": "3.12.2",
  "platform": "macOS-27.0-arm64-arm-64bit",
  "cpu_count": 11,
  "packages": {
    "numpy": "2.5.2",
    "scipy": "1.18.1",
    "scikit-learn": "1.9.1",
    "simpy": "4.1.2",
    "pydantic": "2.13.4",
    "faiss-cpu": "1.15.0",
    "matplotlib": "3.11.2"
  }
}
```

## Means with bootstrap 95% CI

| scenario | variant | arm | runs | device_tpr | device_fpr | device_f1 | latency_response_mean | response_coverage | mttr_mean | false_restriction_rate | disruptive_actions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r3 | op=absent|adj=oracle|noise=gaussian | full | 10 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0 [6.700, 7.300] | 0.8889 [0.882, 0.896] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0 [6.700, 7.300] | 0.8889 [0.882, 0.896] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.075 [3.825, 4.350] | 0.9078 [0.896, 0.919] | — | 0.0 [0.000, 0.000] | 75.0 [73.800, 76.200] |
| s2 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.075 [3.825, 4.350] | 0.9078 [0.896, 0.919] | — | 0.0 [0.000, 0.000] | 75.0 [73.800, 76.200] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.075 [4.950, 5.225] | 0.8243 [0.816, 0.831] | 9.25 [9.050, 9.450] | 0.0 [0.000, 0.000] | 52.7 [52.000, 53.500] |
| s3 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.075 [4.950, 5.225] | 0.8243 [0.816, 0.831] | 9.25 [9.050, 9.450] | 0.0 [0.000, 0.000] | 52.7 [52.000, 53.500] |
| s4 | op=absent|adj=oracle|noise=gaussian | full | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | full | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9091 [0.909, 0.909] | — | 0.0 [0.000, 0.000] | 20.0 [20.000, 20.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9091 [0.909, 0.909] | — | 0.0 [0.000, 0.000] | 20.0 [20.000, 20.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | full | 10 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.400, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | full_llm | 10 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.400, 45.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1303.141 | 3.356 | +1299.785 [+1293.697, +1309.201] | 0.014 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|label_accuracy_primary | full_llm | 10 | 0.888 | 1.0 | -0.112 [-0.152, -0.078] | 0.0098 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1840.914 | 3.464 | +1837.450 [+1806.680, +1867.737] | 0.014 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1736.034 | 3.772 | +1732.262 [+1693.813, +1768.340] | 0.014 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|label_accuracy_primary | full_llm | 10 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 0.0098 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1629.459 | 4.43 | +1625.029 [+1598.788, +1661.295] | 0.014 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1803.691 | 2.133 | +1801.558 [+1788.004, +1818.353] | 0.014 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1791.712 | 2.176 | +1789.535 [+1781.777, +1798.290] | 0.014 | +1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full_llm | 10 | 1419.135 | 2.202 | +1416.933 [+1391.227, +1432.206] | 0.014 | +1.00 |

Only comparisons significant after Holm correction are listed; all 98 are in `comparisons.csv`.
