# Experiment report: `scale`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "scale",
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
    20009,
    20010,
    20011,
    20012,
    20013,
    20014,
    20015,
    20016,
    20017,
    20018,
    20019,
    20020,
    20021,
    20022,
    20023,
    20024,
    20025,
    20026,
    20027,
    20028,
    20029
  ],
  "workers": 3,
  "git_commit": "491a6a1f213df42bd125acc9705168082f47ee33",
  "git_dirty": true,
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
  },
  "reanalysed": true
}
```

## Means with bootstrap 95% CI

| scenario | variant | arm | runs | device_tpr | device_fpr | device_f1 | latency_response_mean | response_coverage | mttr_mean | false_restriction_rate | disruptive_actions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sweep:scale:100 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |
| sweep:scale:1000 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |
| sweep:scale:2500 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |
| sweep:scale:50 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.6833 [2.900, 4.433] | 0.486 [0.444, 0.531] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 6.4667 [5.833, 7.167] |
| sweep:scale:50 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |
| sweep:scale:500 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |
| sweep:scale:5000 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.6833 [2.900, 4.433] | 0.486 [0.444, 0.531] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 6.4667 [5.833, 7.167] |
| sweep:scale:5000 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.5667 [5.433, 5.684] | 0.7699 [0.762, 0.778] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 19.7 [19.400, 20.033] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.341 | 0.697 | -0.356 [-0.384, -0.328] | 3.4e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.486 | 0.77 | -0.284 [-0.325, -0.242] | 3.6e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 3.683 | 4.567 | -0.883 [-1.567, -0.167] | 0.032 | -0.51 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 3.683 | 5.567 | -1.883 [-2.567, -1.167] | 0.00018 | -0.83 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 3.683 | 8.7 | -5.017 [-5.700, -4.300] | 3.8e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 3.133 | -3.133 [-3.217, -3.067] | 9.5e-07 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 2e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.267 | -4.267 [-4.383, -4.167] | 1.8e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 6.467 | 19.7 | -13.233 [-13.833, -12.600] | 3e-06 | -1.00 |
| sweep:scale:50|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.429 | 3.824 | -0.395 [-0.443, -0.347] | 3.7e-09 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.341 | 0.697 | -0.356 [-0.384, -0.328] | 3.4e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.486 | 0.77 | -0.284 [-0.325, -0.242] | 3.6e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 3.683 | 4.567 | -0.883 [-1.567, -0.167] | 0.032 | -0.51 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 3.683 | 5.567 | -1.883 [-2.567, -1.167] | 0.00018 | -0.83 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 3.683 | 8.7 | -5.017 [-5.700, -4.300] | 3.8e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 3.133 | -3.133 [-3.217, -3.067] | 9.5e-07 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 2e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.267 | -4.267 [-4.383, -4.167] | 1.8e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 6.467 | 19.7 | -13.233 [-13.833, -12.600] | 3e-06 | -1.00 |
| sweep:scale:5000|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 357.035 | 388.409 | -31.374 [-31.865, -30.830] | 3.7e-09 | -1.00 |

Only comparisons significant after Holm correction are listed; all 36 are in `comparisons.csv`.
