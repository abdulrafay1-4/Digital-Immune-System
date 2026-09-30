# Experiment report: `research`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "research",
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
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.4 [71.800, 74.833] |
| s2 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.4 [71.800, 74.833] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.4833 [2.950, 4.025] | 0.469 [0.440, 0.500] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 13.9 [12.967, 14.834] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.400, 5.583] | 0.8005 [0.795, 0.806] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 47.7333 [47.300, 48.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | 0.2417 [0.175, 0.308] | 0.0 [0.000, 0.000] | 0.5016 [0.451, 0.565] | 16.1905 [15.452, 16.976] | 0.0619 [0.044, 0.081] | 9.375 [9.125, 9.750] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.400, 5.583] | 0.8005 [0.795, 0.806] | 9.2 [9.100, 9.300] | 0.0 [0.000, 0.000] | 47.6 [47.200, 48.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 30.0 [30.000, 30.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0667 [7.000, 7.167] | 0.8311 [0.828, 0.833] | — | 0.0 [0.000, 0.000] | 26.0 [25.767, 26.233] |
| s4 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 22.0 [22.000, 22.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0333 [7.000, 7.100] | 0.7712 [0.768, 0.773] | — | 0.0 [0.000, 0.000] | 18.2 [17.967, 18.467] |
| s5 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s6 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 24.0 [24.000, 24.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | trust_only | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | trust_ti | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 4.9e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.343 | 4.312 | -0.969 [-1.162, -0.803] | 1.1e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.866 | 4.312 | -0.445 [-0.652, -0.263] | 4.6e-05 | -0.85 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | trust_only | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_only | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_only | 30 | 3.556 | 4.312 | -0.756 [-0.994, -0.538] | 3e-06 | -0.91 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_ti | 30 | 3.634 | 4.312 | -0.677 [-0.903, -0.476] | 3.2e-07 | -0.96 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 4.9e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.792 | 4.305 | -0.512 [-0.849, -0.136] | 2.4e-05 | -0.82 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | trust_only | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_only | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | trust_only | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_only | 30 | 3.822 | 4.305 | -0.483 [-0.810, -0.138] | 0.0017 | -0.67 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_ti | 30 | 3.835 | 4.305 | -0.470 [-0.730, -0.249] | 1.1e-05 | -0.87 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.33 | 0.749 | -0.419 [-0.436, -0.402] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.469 | 0.819 | -0.350 [-0.378, -0.321] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 3.483 | 4.492 | -1.008 [-1.500, -0.483] | 0.0027 | -0.70 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 3.483 | 5.167 | -1.683 [-2.175, -1.150] | 0.00011 | -0.86 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 3.483 | 7.558 | -4.075 [-4.567, -3.550] | 5.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 13.9 | 52.167 | -38.267 [-39.100, -37.400] | 4.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.539 | 5.151 | -1.612 [-1.730, -1.498] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_memory | 30 | 0.738 | 0.749 | -0.011 [-0.013, -0.009] | 8.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | no_memory | 30 | 0.8 | 0.819 | -0.019 [-0.021, -0.016] | 6.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_memory | 30 | 5.492 | 5.167 | +0.325 [+0.283, +0.367] | 2.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_memory | 30 | 8.6 | 7.558 | +1.042 [+1.008, +1.075] | 1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | no_memory | 30 | 3.108 | 2.392 | +0.717 [+0.658, +0.767] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | no_memory | 30 | 4.258 | 4.464 | -0.206 [-0.253, -0.158] | 1.5e-05 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_memory | 30 | 47.733 | 52.167 | -4.433 [-4.633, -4.233] | 4.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.871 | 5.151 | -1.280 [-1.419, -1.146] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | trust_only | 30 | 0.242 | 1.0 | -0.758 [-0.825, -0.692] | 3.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | trust_only | 21 | 0.502 | 1.0 | -0.498 [-0.549, -0.448] | 0.00016 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | trust_only | 19 | 0.096 | 0.749 | -0.652 [-0.673, -0.632] | 0.00039 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_only | 30 | 0.062 | 0.819 | -0.757 [-0.777, -0.737] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | trust_only | 28 | 13.929 | 4.492 | +9.455 [+8.708, +10.217] | 1.1e-05 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | trust_only | 21 | 16.19 | 5.167 | +11.012 [+10.226, +11.857] | 0.00018 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | trust_only | 21 | 4.19 | 4.464 | -0.238 [-0.369, -0.095] | 0.017 | -0.73 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | trust_only | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_only | 30 | 3.782 | 5.151 | -1.369 [-1.498, -1.233] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | trust_ti | 30 | 0.739 | 0.749 | -0.010 [-0.012, -0.008] | 8.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_ti | 30 | 0.8 | 0.819 | -0.019 [-0.021, -0.016] | 6.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | trust_ti | 30 | 5.492 | 5.167 | +0.325 [+0.283, +0.367] | 2.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | trust_ti | 30 | 8.6 | 7.558 | +1.042 [+1.008, +1.075] | 1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | trust_ti | 30 | 3.108 | 2.392 | +0.717 [+0.658, +0.767] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | trust_ti | 30 | 4.2 | 4.464 | -0.264 [-0.322, -0.211] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | trust_ti | 30 | 47.6 | 52.167 | -4.567 [-4.800, -4.367] | 5.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_ti | 30 | 3.799 | 5.151 | -1.352 [-1.529, -1.149] | 4.7e-08 | -0.99 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 1.0 | 0.867 | +0.133 [+0.133, +0.133] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 1.0 | 0.933 | +0.067 [+0.067, +0.067] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 0.0 | 6.0 | -6.000 [-6.000, -6.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 30.0 | 28.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.266 | 2.648 | -0.382 [-0.621, -0.153] | 6.5e-06 | -0.88 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | trust_only | 30 | 0.806 | 0.867 | -0.061 [-0.063, -0.060] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_only | 30 | 0.831 | 0.933 | -0.102 [-0.106, -0.100] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | trust_only | 30 | 4.067 | 3.0 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | trust_only | 30 | 7.067 | 4.0 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | trust_only | 30 | 8.0 | 6.0 | +2.000 [+1.767, +2.233] | 3.1e-06 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | trust_only | 30 | 0.933 | 2.0 | -1.067 [-1.333, -0.800] | 1.8e-05 | -0.95 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | trust_only | 30 | 26.0 | 28.0 | -2.000 [-2.233, -1.767] | 4.7e-06 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_only | 30 | 2.304 | 2.648 | -0.344 [-0.563, -0.179] | 2.8e-06 | -0.91 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 1.0 | 0.819 | +0.181 [+0.179, +0.182] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 1.0 | 0.911 | +0.089 [+0.086, +0.091] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 0.0 | 2.967 | -2.967 [-3.000, -2.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 0.0 | 3.967 | -3.967 [-4.000, -3.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 0.0 | 5.967 | -5.967 [-6.000, -5.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 5.167 | -5.167 [-5.300, -5.033] | 1.3e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 22.0 | 20.033 | +1.967 [+1.900, +2.000] | 3.4e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.16 | 2.38 | -0.220 [-0.262, -0.178] | 7.8e-08 | -0.97 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | trust_only | 30 | 0.731 | 0.819 | -0.088 [-0.091, -0.086] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | trust_only | 30 | 0.771 | 0.911 | -0.139 [-0.144, -0.136] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | trust_only | 30 | 4.033 | 2.967 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | trust_only | 30 | 7.033 | 3.967 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | trust_only | 30 | 7.8 | 5.967 | +1.833 [+1.567, +2.100] | 3.5e-06 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | trust_only | 30 | 0.767 | 2.0 | -1.233 [-1.467, -0.967] | 9.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | trust_only | 30 | 18.2 | 20.033 | -1.833 [-2.100, -1.567] | 5.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_only | 30 | 2.22 | 2.38 | -0.160 [-0.188, -0.132] | 1.1e-08 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | trust_ti | 30 | 2.22 | 2.38 | -0.160 [-0.187, -0.133] | 1.1e-08 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 8.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 5.8e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.216 | 2.454 | -0.238 [-0.279, -0.199] | 1.1e-08 | -1.00 |

Only comparisons significant after Holm correction are listed; all 366 are in `comparisons.csv`.
