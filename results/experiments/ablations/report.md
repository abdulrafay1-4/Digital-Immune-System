# Experiment report: `ablations`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "ablations",
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
| s1 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.1667 [5.967, 6.333] | 0.9074 [0.904, 0.912] | — | 0.0 [0.000, 0.000] | 43.8333 [43.667, 44.033] |
| s1 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.175 [3.025, 3.333] | 0.9478 [0.941, 0.954] | — | 0.0 [0.000, 0.000] | 93.3 [92.667, 93.901] |
| s2 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.4 [71.800, 74.833] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.4917 [4.400, 4.583] | 0.8576 [0.852, 0.863] | — | 0.0 [0.000, 0.000] | 156.0333 [155.667, 156.400] |
| s3 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.400, 5.583] | 0.8005 [0.795, 0.806] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 47.7333 [47.300, 48.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.2 [9.100, 9.300] | 0.0 [0.000, 0.000] | 51.7667 [51.400, 52.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.2417 [0.175, 0.308] | 0.0 [0.000, 0.000] | 0.5016 [0.451, 0.565] | 16.1905 [15.452, 16.976] | 0.0619 [0.044, 0.081] | 9.375 [9.125, 9.750] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0 [3.000, 3.000] | 0.9667 [0.967, 0.967] | — | 0.0 [0.000, 0.000] | 31.0 [31.000, 31.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0667 [7.000, 7.167] | 0.8311 [0.828, 0.833] | — | 0.0 [0.000, 0.000] | 26.0 [25.767, 26.233] |
| s4 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 28.0 [28.000, 28.000] |
| s4 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s5 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.9667 [2.900, 3.000] | 0.9561 [0.955, 0.959] | — | 0.0 [0.000, 0.000] | 29.0333 [29.000, 29.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0333 [7.000, 7.100] | 0.7712 [0.768, 0.773] | — | 0.0 [0.000, 0.000] | 18.2 [17.967, 18.467] |
| s5 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9667 [3.900, 4.000] | 0.9106 [0.909, 0.914] | — | 0.0 [0.000, 0.000] | 20.0333 [20.000, 20.100] |
| s5 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | binary_response | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 45.0 [45.000, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | equal_weighting | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_quorum | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_recovery | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | no_weighting_no_quorum | 30 | — | 0.0333 [0.033, 0.033] | — | — | — | — | 0.0333 [0.033, 0.033] | 44.8 [44.600, 45.000] |
| s6 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.874 | 0.882 | -0.007 [-0.007, -0.007] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.907 | 0.885 | +0.022 [+0.022, +0.022] | 1.2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 6.167 | 7.167 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 43.833 | 0.0 | +43.833 [+43.633, +44.033] | 2.3e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.843 | 0.814 | +0.030 [+0.027, +0.033] | 3e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.948 | 0.9 | +0.048 [+0.045, +0.051] | 1.4e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 3.175 | 4.225 | -1.050 [-1.092, -1.017] | 6.5e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 3.175 | 7.65 | -4.475 [-4.558, -4.392] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 93.3 | 73.667 | +19.633 [+18.433, +21.033] | 3.4e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_quorum | 30 | 4.499 | 4.126 | +0.373 [+0.130, +0.665] | 0.0033 | +0.68 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.779 | 4.126 | -0.347 [-0.571, -0.147] | 0.00022 | -0.79 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_weighting_no_quorum | 30 | 4.3 | 4.126 | +0.174 [+0.086, +0.268] | 0.0048 | +0.66 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 4.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.46 | 0.749 | -0.289 [-0.290, -0.287] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.858 | 0.819 | +0.039 [+0.036, +0.041] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 4.492 | 5.167 | -0.675 [-0.717, -0.633] | 6.5e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 4.492 | 7.558 | -3.067 [-3.108, -3.033] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_response | 30 | 4.258 | 4.464 | -0.206 [-0.253, -0.158] | 1.5e-05 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 156.033 | 52.167 | +103.867 [+103.633, +104.133] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_memory | 30 | 0.738 | 0.749 | -0.011 [-0.013, -0.009] | 8.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | no_memory | 30 | 0.8 | 0.819 | -0.019 [-0.021, -0.016] | 6.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_memory | 30 | 5.492 | 5.167 | +0.325 [+0.283, +0.367] | 2.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_memory | 30 | 8.6 | 7.558 | +1.042 [+1.008, +1.075] | 1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | no_memory | 30 | 3.108 | 2.392 | +0.717 [+0.658, +0.767] | 3.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | no_memory | 30 | 4.258 | 4.464 | -0.206 [-0.253, -0.158] | 1.5e-05 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_memory | 30 | 47.733 | 52.167 | -4.433 [-4.633, -4.233] | 4.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.884 | 5.242 | -1.358 [-1.534, -1.206] | 1.1e-08 | -1.00 |
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
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.824 | 5.242 | -1.418 [-1.633, -1.232] | 1.1e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.819 | -0.819 [-0.824, -0.814] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 4.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 4.005 | 5.242 | -1.238 [-1.476, -1.013] | 2.2e-08 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.885 | 0.867 | +0.019 [+0.019, +0.019] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.967 | 0.933 | +0.033 [+0.033, +0.033] | 2.2e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 3.0 | 4.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 3.0 | 6.0 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 31.0 | 28.0 | +3.000 [+3.000, +3.000] | 2.6e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | equal_weighting | 30 | 2.616 | 2.415 | +0.201 [+0.059, +0.398] | 0.018 | +0.60 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 2.529 | 2.415 | +0.114 [+0.053, +0.174] | 0.0063 | +0.64 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.806 | 0.867 | -0.061 [-0.063, -0.060] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.831 | 0.933 | -0.102 [-0.106, -0.100] | 5.1e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 4.067 | 3.0 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 7.067 | 4.0 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 8.0 | 6.0 | +2.000 [+1.767, +2.233] | 3.1e-06 | +1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.933 | 2.0 | -1.067 [-1.333, -0.800] | 1.8e-05 | -0.95 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 26.0 | 28.0 | -2.000 [-2.233, -1.767] | 4.7e-06 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_weighting_no_quorum | 30 | 2.617 | 2.415 | +0.202 [+0.102, +0.312] | 0.0048 | +0.66 |
| s4|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.933 | -0.933 [-0.933, -0.933] | 2.2e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 28.0 | -28.000 [-28.000, -28.000] | 2.6e-07 | -1.00 |
| s4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.523 | 2.415 | +0.108 [+0.042, +0.174] | 0.023 | +0.57 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_response | 30 | 0.746 | 0.819 | -0.073 [-0.073, -0.073] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_response | 30 | 0.956 | 0.911 | +0.045 [+0.045, +0.045] | 2.7e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_response | 30 | 2.967 | 3.967 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_response | 30 | 2.967 | 5.967 | -3.000 [-3.000, -3.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_response | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_response | 30 | 29.033 | 20.033 | +9.000 [+9.000, +9.000] | 2.6e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_response | 30 | 2.876 | 2.471 | +0.404 [+0.187, +0.658] | 8.4e-05 | +0.83 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_quorum | 30 | 3.616 | 2.471 | +1.145 [+1.030, +1.279] | 1.1e-08 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.731 | 0.819 | -0.088 [-0.091, -0.086] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.771 | 0.911 | -0.139 [-0.144, -0.136] | 5.1e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 4.033 | 2.967 | +1.067 [+1.000, +1.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 7.033 | 3.967 | +3.067 [+3.000, +3.167] | 5.1e-07 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 7.8 | 5.967 | +1.833 [+1.567, +2.100] | 3.5e-06 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.767 | 2.0 | -1.233 [-1.467, -0.967] | 9.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 18.2 | 20.033 | -1.833 [-2.100, -1.567] | 5.8e-06 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_weighting_no_quorum | 30 | 3.39 | 2.471 | +0.919 [+0.792, +1.070] | 1.1e-08 | +1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.2e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.911 | -0.911 [-0.914, -0.909] | 2.7e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 20.033 | -20.033 [-20.100, -20.000] | 3.4e-07 | -1.00 |
| s5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.377 | 2.471 | -0.094 [-0.136, -0.051] | 0.0014 | -0.72 |
| s6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 2.447 | 2.841 | -0.394 [-0.782, -0.115] | 0.003 | -0.69 |
| s6|op=absent|adj=oracle|noise=gaussian|device_fpr | static_trust | 30 | 0.0 | 0.033 | -0.033 [-0.033, -0.033] | 2.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | static_trust | 30 | 0.0 | 0.033 | -0.033 [-0.033, -0.033] | 2.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|availability_cost | static_trust | 30 | 0.0 | 44.8 | -44.800 [-45.000, -44.600] | 8.6e-07 | -1.00 |
| s6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 44.8 | -44.800 [-45.000, -44.600] | 5.8e-07 | -1.00 |

Only comparisons significant after Holm correction are listed; all 722 are in `comparisons.csv`.
