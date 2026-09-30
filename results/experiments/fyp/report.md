# Experiment report: `fyp`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "fyp",
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
  "git_commit": "f3b074c5c9be5d8352d1fd8cab00b5e1c77df48b",
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
  },
  "reanalysed": true
}
```

## Means with bootstrap 95% CI

| scenario | variant | arm | runs | device_tpr | device_fpr | device_f1 | latency_response_mean | response_coverage | mttr_mean | false_restriction_rate | disruptive_actions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s1 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.1667 [5.967, 6.333] | 0.9074 [0.904, 0.912] | — | 0.0 [0.000, 0.000] | 43.8333 [43.667, 44.033] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 45.0 [45.000, 45.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.175 [3.025, 3.333] | 0.9478 [0.941, 0.954] | — | 0.0 [0.000, 0.000] | 93.3 [92.667, 93.901] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.4 [71.800, 74.833] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.4917 [4.400, 4.583] | 0.8576 [0.852, 0.863] | — | 0.0 [0.000, 0.000] | 156.0333 [155.667, 156.400] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.4833 [2.950, 4.025] | 0.469 [0.440, 0.500] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 13.9 [12.967, 14.834] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.400, 5.583] | 0.8005 [0.795, 0.806] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 47.7333 [47.300, 48.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.2 [9.100, 9.300] | 0.0 [0.000, 0.000] | 51.7667 [51.400, 52.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.2417 [0.175, 0.308] | 0.0 [0.000, 0.000] | 0.5016 [0.451, 0.565] | 16.1905 [15.452, 16.976] | 0.0619 [0.044, 0.081] | 9.375 [9.125, 9.750] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0 [3.000, 3.000] | 0.9667 [0.967, 0.967] | — | 0.0 [0.000, 0.000] | 31.0 [31.000, 31.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 30.0 [30.000, 30.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 30.0 [30.000, 30.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0667 [7.000, 7.167] | 0.8311 [0.828, 0.833] | — | 0.0 [0.000, 0.000] | 26.0 [25.767, 26.233] |
| s4 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.9667 [2.900, 3.000] | 0.9561 [0.955, 0.959] | — | 0.0 [0.000, 0.000] | 29.0333 [29.000, 29.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 22.0 [22.000, 22.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 22.0 [22.000, 22.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0333 [7.000, 7.100] | 0.7712 [0.768, 0.773] | — | 0.0 [0.000, 0.000] | 18.2 [17.967, 18.467] |
| s5 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 45.0 [45.000, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 24.0 [24.000, 24.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 24.0 [24.000, 24.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.874 | 0.882 | -0.007 [-0.007, -0.007] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.907 | 0.885 | +0.022 [+0.022, +0.022] | 1.2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 6.167 | 7.167 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 43.833 | 0.0 | +43.833 [+43.633, +44.033] | 2.3e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_response | 30 | 4.289 | 3.812 | +0.478 [+0.377, +0.581] | 6.5e-08 | +0.98 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 4.9e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.525 | 3.812 | -0.287 [-0.356, -0.219] | 1.8e-07 | -0.96 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.882 | +0.118 [+0.116, +0.121] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 45.0 | 0.0 | +45.000 [+45.000, +45.000] | 2.6e-07 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.648 | 3.812 | -0.163 [-0.220, -0.103] | 0.00014 | -0.80 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.768 | 3.812 | -0.044 [-0.104, +0.036] | 0.012 | -0.60 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 4.021 | 3.812 | +0.210 [+0.103, +0.325] | 0.0095 | +0.62 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 4.033 | 3.812 | +0.222 [+0.165, +0.280] | 4e-07 | +0.96 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.843 | 0.814 | +0.030 [+0.027, +0.033] | 3e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.948 | 0.9 | +0.048 [+0.045, +0.051] | 1.4e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 3.175 | 4.225 | -1.050 [-1.092, -1.017] | 6.5e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 3.175 | 7.65 | -4.475 [-4.558, -4.392] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 93.3 | 73.667 | +19.633 [+18.433, +21.033] | 3.4e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 4.9e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.395 | 4.296 | -0.901 [-1.122, -0.705] | 1.1e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.814 | +0.186 [+0.181, +0.192] | 2.9e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.9 | +0.100 [+0.093, +0.107] | 2.6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 3.175 | -3.175 [-3.325, -3.025] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 4.225 | -4.225 [-4.375, -4.075] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 7.65 | -7.650 [-7.775, -7.525] | 4.1e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 8.1e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 90.0 | 73.667 | +16.333 [+15.067, +17.767] | 3e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.59 | 4.296 | -0.706 [-0.955, -0.493] | 1.1e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 4.5e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 3.905 | 4.296 | -0.391 [-0.631, -0.181] | 0.0029 | -0.66 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.46 | 0.749 | -0.289 [-0.290, -0.287] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.858 | 0.819 | +0.039 [+0.036, +0.041] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 4.492 | 5.167 | -0.675 [-0.717, -0.633] | 6.5e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 4.492 | 7.558 | -3.067 [-3.108, -3.033] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_response | 30 | 4.258 | 4.464 | -0.206 [-0.253, -0.158] | 1.5e-05 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 156.033 | 52.167 | +103.867 [+103.633, +104.133] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_response | 30 | 4.08 | 5.201 | -1.121 [-1.416, -0.899] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.33 | 0.749 | -0.419 [-0.436, -0.402] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.469 | 0.819 | -0.350 [-0.378, -0.321] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 3.483 | 4.492 | -1.008 [-1.500, -0.483] | 0.0027 | -0.70 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 3.483 | 5.167 | -1.683 [-2.175, -1.150] | 0.00011 | -0.86 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 3.483 | 7.558 | -4.075 [-4.567, -3.550] | 5.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 13.9 | 52.167 | -38.267 [-39.100, -37.400] | 4.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.58 | 5.201 | -1.621 [-1.873, -1.442] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.749 | +0.251 [+0.248, +0.254] | 2.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 2.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 4.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.8 | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 70.0 | 52.167 | +17.833 [+17.367, +18.300] | 3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 4.073 | 5.201 | -1.128 [-1.520, -0.755] | 0.00017 | -0.78 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_memory | 30 | 0.738 | 0.749 | -0.011 [-0.013, -0.009] | 8.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | no_memory | 30 | 0.8 | 0.819 | -0.019 [-0.021, -0.016] | 6.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_memory | 30 | 5.492 | 5.167 | +0.325 [+0.283, +0.367] | 2.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_memory | 30 | 8.6 | 7.558 | +1.042 [+1.008, +1.075] | 1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | no_memory | 30 | 3.108 | 2.392 | +0.717 [+0.658, +0.767] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | no_memory | 30 | 4.258 | 4.464 | -0.206 [-0.253, -0.158] | 1.5e-05 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_memory | 30 | 47.733 | 52.167 | -4.433 [-4.633, -4.233] | 4.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.912 | 5.201 | -1.289 [-1.572, -1.085] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_recovery | 30 | 0.751 | 0.749 | +0.002 [+0.001, +0.003] | 0.0095 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | no_recovery | 30 | 4.2 | 4.464 | -0.264 [-0.322, -0.211] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_recovery | 30 | 51.767 | 52.167 | -0.400 [-0.567, -0.233] | 0.011 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.242 | 1.0 | -0.758 [-0.825, -0.692] | 3.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | no_sharing | 21 | 0.502 | 1.0 | -0.498 [-0.549, -0.448] | 0.00016 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 19 | 0.096 | 0.749 | -0.652 [-0.673, -0.632] | 0.00039 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.062 | 0.819 | -0.757 [-0.777, -0.737] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 28 | 13.929 | 4.492 | +9.455 [+8.708, +10.217] | 1.1e-05 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 21 | 16.19 | 5.167 | +11.012 [+10.226, +11.857] | 0.00018 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | no_sharing | 21 | 4.19 | 4.464 | -0.238 [-0.369, -0.095] | 0.017 | -0.73 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.939 | 5.201 | -1.262 [-1.546, -1.059] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.819 | -0.819 [-0.824, -0.814] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 4.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 3.939 | 5.201 | -1.262 [-1.558, -1.052] | 1.1e-08 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.885 | 0.867 | +0.019 [+0.019, +0.019] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.967 | 0.933 | +0.033 [+0.033, +0.033] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 3.0 | 4.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 3.0 | 6.0 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 31.0 | 28.0 | +3.000 [+3.000, +3.000] | 2.6e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 1.0 | 0.867 | +0.133 [+0.133, +0.133] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 1.0 | 0.933 | +0.067 [+0.067, +0.067] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 0.0 | 6.0 | -6.000 [-6.000, -6.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 30.0 | 28.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.449 | 2.459 | -0.010 [-0.171, +0.214] | 0.014 | -0.51 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.867 | +0.133 [+0.133, +0.133] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.933 | +0.067 [+0.067, +0.067] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 6.0 | -6.000 [-6.000, -6.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 30.0 | 28.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 2.342 | 2.459 | -0.117 [-0.235, +0.023] | 0.027 | -0.51 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 2.381 | 2.459 | -0.078 [-0.126, -0.033] | 0.012 | -0.59 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.806 | 0.867 | -0.061 [-0.063, -0.060] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.831 | 0.933 | -0.102 [-0.106, -0.100] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 4.067 | 3.0 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 7.067 | 4.0 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 8.0 | 6.0 | +2.000 [+1.767, +2.233] | 3.1e-06 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.933 | 2.0 | -1.067 [-1.333, -0.800] | 1.8e-05 | -0.95 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 26.0 | 28.0 | -2.000 [-2.233, -1.767] | 4.7e-06 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 2.395 | 2.459 | -0.064 [-0.111, -0.022] | 0.036 | -0.52 |
| s4|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.933 | -0.933 [-0.933, -0.933] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 28.0 | -28.000 [-28.000, -28.000] | 2.6e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.395 | 2.459 | -0.064 [-0.105, -0.021] | 0.0044 | -0.62 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.746 | 0.819 | -0.073 [-0.073, -0.073] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.956 | 0.911 | +0.045 [+0.045, +0.045] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 2.967 | 3.967 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 2.967 | 5.967 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 29.033 | 20.033 | +9.000 [+9.000, +9.000] | 2.6e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_response | 30 | 2.561 | 2.432 | +0.129 [+0.084, +0.176] | 2.1e-05 | +0.86 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 1.0 | 0.819 | +0.181 [+0.179, +0.182] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 1.0 | 0.911 | +0.089 [+0.086, +0.091] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 0.0 | 2.967 | -2.967 [-3.000, -2.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 0.0 | 3.967 | -3.967 [-4.000, -3.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 0.0 | 5.967 | -5.967 [-6.000, -5.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 5.167 | -5.167 [-5.300, -5.033] | 1.3e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 22.0 | 20.033 | +1.967 [+1.900, +2.000] | 3.4e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.18 | 2.432 | -0.252 [-0.282, -0.221] | 1.1e-08 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.819 | +0.181 [+0.179, +0.182] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.911 | +0.089 [+0.086, +0.091] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 2.967 | -2.967 [-3.000, -2.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 3.967 | -3.967 [-4.000, -3.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 5.967 | -5.967 [-6.000, -5.900] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 5.167 | -5.167 [-5.300, -5.033] | 8.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 22.0 | 20.033 | +1.967 [+1.900, +2.000] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 2.426 | 2.432 | -0.005 [-0.166, +0.207] | 0.027 | -0.51 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 2.677 | 2.432 | +0.245 [+0.142, +0.359] | 0.00076 | +0.75 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.731 | 0.819 | -0.088 [-0.091, -0.086] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.771 | 0.911 | -0.139 [-0.144, -0.136] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 4.033 | 2.967 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 7.033 | 3.967 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 7.8 | 5.967 | +1.833 [+1.567, +2.100] | 3.5e-06 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.767 | 2.0 | -1.233 [-1.467, -0.967] | 9.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 18.2 | 20.033 | -1.833 [-2.100, -1.567] | 5.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.911 | -0.911 [-0.914, -0.909] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 20.033 | -20.033 [-20.100, -20.000] | 3.4e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.373 | 2.432 | -0.058 [-0.093, -0.024] | 0.0044 | -0.62 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_response | 30 | 2.895 | 2.627 | +0.268 [-0.048, +0.541] | 0.0003 | +0.76 |
| s6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 8.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 5.8e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 2.385 | 2.627 | -0.242 [-0.562, -0.003] | 0.0015 | -0.68 |
| s6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 8.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 24.0 | 44.8 | -20.800 [-21.000, -20.600] | 4.3e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 2.303 | 2.627 | -0.323 [-0.594, -0.157] | 8.4e-06 | -0.89 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 2.926 | 2.627 | +0.300 [-0.034, +0.529] | 9.1e-05 | +0.82 |
| s6|op=absent|adj=oracle|noise=gaussian|device_fpr | static_trust | 30 | 0.0 | 0.033 | -0.033 [-0.033, -0.033] | 2.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | static_trust | 30 | 0.0 | 0.033 | -0.033 [-0.033, -0.033] | 2.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|availability_cost | static_trust | 30 | 0.0 | 44.8 | -44.800 [-45.000, -44.600] | 8.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 44.8 | -44.800 [-45.000, -44.600] | 5.8e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.903 | 2.627 | +0.276 [-0.049, +0.581] | 0.0024 | +0.69 |

Only comparisons significant after Holm correction are listed; all 645 are in `comparisons.csv`.
