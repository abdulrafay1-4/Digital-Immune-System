# Experiment report: `operators`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "operators",
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
| a10 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 225.0 [225.000, 225.000] |
| a10 | op=approve_after:5|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 825.0 [825.000, 825.000] |
| a10 | op=approve|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 900.0 [900.000, 900.000] |
| a10 | op=deny|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 225.0 [225.000, 225.000] |
| a6 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| a6 | op=approve_after:5|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 786.1333 [774.166, 797.933] |
| a6 | op=approve|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 849.8 [838.394, 861.433] |
| a6 | op=deny|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=approve_after:5|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=approve|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=deny|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|

Only comparisons significant after Holm correction are listed; all 0 are in `comparisons.csv`.
