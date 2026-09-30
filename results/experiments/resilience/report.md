# Experiment report: `resilience`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "resilience",
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
  "git_commit": "1d19cf5eb963e7b744e46ec5f677a133c90802e0",
  "git_dirty": true,
  "code_dirty": true,
  "frozen_params": {
    "trust_lambda": 0.7,
    "trust_lambda_up": null,
    "cohort_margin": 0.15,
    "cohort_min_nodes": 3,
    "rep_lam_up": 0.85,
    "rep_lam_down": 0.6,
    "hysteresis_n": 3,
    "drift_coeff": 0.3,
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
  "merged_arms": [
    "tolerance",
    "tolerance_no_recovery",
    "tolerance_periodic@5"
  ],
  "merged_into_rows": 2340
}
```

## Means with bootstrap 95% CI

| scenario | variant | arm | runs | device_tpr | device_fpr | device_f1 | latency_response_mean | response_coverage | mttr_mean | false_restriction_rate | disruptive_actions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r1 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.0893 [0.077, 0.103] | — | — | — | — | 0.0893 [0.077, 0.103] | 4.7 [4.000, 5.433] |
| r1 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.1 [0.100, 0.100] | 297.6 [296.666, 298.567] |
| r1 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.1 [0.100, 0.100] | 132.5333 [130.233, 134.835] |
| r1 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.1 [0.100, 0.100] | 100.0 [100.000, 100.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | — | 1.0 [1.000, 1.000] | — | — | — | — | 1.0 [1.000, 1.000] | 730.0 [730.000, 730.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.9222 [2.822, 3.000] | 0.9693 [0.967, 0.973] | — | 0.0 [0.000, 0.000] | 93.3333 [92.967, 93.734] |
| r2 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 5.0 [5.000, 5.000] | 0.9 [0.900, 0.900] | — | 0.0 [0.000, 0.000] | 128.9333 [128.833, 129.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.7 [3.600, 3.800] | 0.9433 [0.940, 0.947] | 2.2333 [2.067, 2.389] | 0.0 [0.000, 0.000] | 85.6 [85.033, 86.133] |
| r2 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.9 [2.767, 3.000] | 0.97 [0.967, 0.974] | 11.3667 [11.211, 11.511] | 0.0 [0.000, 0.000] | 92.4 [91.800, 93.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.9 [2.767, 3.000] | 0.97 [0.967, 0.974] | 11.3667 [11.211, 11.511] | 0.0 [0.000, 0.000] | 92.4 [91.800, 93.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | 1.0 [1.000, 1.000] | 0.0638 [0.052, 0.074] | 0.6848 [0.646, 0.729] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.1444 [0.000, 0.433] | 0.0638 [0.052, 0.074] | 93.2 [92.667, 93.733] |
| r2 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 1.9889 [1.967, 2.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 0.0 [0.000, 0.000] | 90.0333 [90.000, 90.100] |
| r2 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0 [3.000, 3.000] | 0.7 [0.700, 0.700] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 21.0 [21.000, 21.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.9 [2.767, 3.000] | 0.97 [0.967, 0.974] | 18.5278 [18.411, 18.644] | 0.0 [0.000, 0.000] | 112.9 [112.567, 113.200] |
| r2 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.1064 [0.106, 0.106] | 247.3667 [246.433, 248.300] |
| r2 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.1064 [0.106, 0.106] | 223.9667 [222.500, 225.400] |
| r2 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.1064 [0.106, 0.106] | 190.0 [190.000, 190.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | 1.0 [1.000, 1.000] | 1.0 [1.000, 1.000] | 0.1132 [0.113, 0.113] | 0.0 [0.000, 0.000] | 0.6 [0.600, 0.600] | 16.0 [16.000, 16.000] | 1.0 [1.000, 1.000] | 530.0 [530.000, 530.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | — | 0.0013 [0.000, 0.003] | — | — | — | — | 0.0013 [0.000, 0.003] | 0.0667 [0.000, 0.167] |
| r3 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.0853 [0.074, 0.097] | — | — | — | — | 0.0853 [0.074, 0.097] | 5.4667 [4.867, 6.100] |
| r3 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | — | 0.0007 [0.000, 0.002] | — | — | — | — | 0.0007 [0.000, 0.002] | 0.0667 [0.000, 0.200] |
| r3 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 47.0 [47.000, 47.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 10.9 [10.533, 11.267] |
| r3 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 1.7 [1.533, 1.867] |
| r3 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | — | 1.0 [1.000, 1.000] | — | — | — | — | 1.0 [1.000, 1.000] | 550.0 [550.000, 550.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.0107 [0.007, 0.014] | 2.1333 [1.467, 2.800] |
| r4 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.0 [8.000, 8.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.0 [8.000, 8.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.002 [0.000, 0.005] | 0.5 [0.000, 1.167] |
| r4 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 6.8 [6.433, 7.133] |
| r4 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 5.3667 [5.200, 5.533] |
| r4 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 5.3667 [5.200, 5.533] |
| r4 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.1093 [0.096, 0.124] | — | — | — | — | 0.1093 [0.096, 0.124] | 12.8 [12.067, 13.567] |
| r4 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.0 [8.000, 8.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 13.0667 [11.233, 14.867] |
| r4 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 66.4667 [66.300, 66.633] |
| r4 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 25.9667 [25.400, 26.500] |
| r4 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.0 [8.000, 8.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | — | 1.0 [1.000, 1.000] | — | — | — | — | 1.0 [1.000, 1.000] | 750.0 [750.000, 750.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1927 [0.185, 0.202] | 25.0 [25.000, 25.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 90.9667 [90.033, 91.933] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.3553 [0.345, 0.365] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | — | 0.3787 [0.371, 0.385] | — | — | — | — | 0.3787 [0.371, 0.385] | 43.4 [41.367, 45.301] |
| r5 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.308 [0.291, 0.325] | — | — | — | — | 0.308 [0.291, 0.325] | 21.4 [20.167, 22.533] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | — | 0.012 [0.007, 0.018] | — | — | — | — | 0.012 [0.007, 0.018] | 1.2 [0.600, 1.900] |
| r5 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 20.0 [20.000, 20.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.226 [0.208, 0.243] | 77.3333 [76.833, 77.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.3993 [0.398, 0.400] | 335.0 [335.000, 335.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.358 [0.347, 0.369] | 100.1667 [99.833, 100.533] |
| r5 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | — | 1.0 [1.000, 1.000] | — | — | — | — | 1.0 [1.000, 1.000] | 750.0 [750.000, 750.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1507 [0.143, 0.159] | 25.0 [25.000, 25.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 91.1333 [90.133, 92.267] |
| r6 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.36 [0.351, 0.369] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | ddca@0.85:4 | 30 | — | 0.348 [0.337, 0.359] | — | — | — | — | 0.348 [0.337, 0.359] | 38.9333 [37.100, 40.734] |
| r6 | op=absent|adj=oracle|noise=gaussian | dirichlet_reliability | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2973 [0.289, 0.306] | 52.1667 [51.667, 52.700] |
| r6 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2973 [0.289, 0.306] | 52.1667 [51.667, 52.700] |
| r6 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.3107 [0.292, 0.330] | — | — | — | — | 0.3107 [0.292, 0.330] | 21.8333 [20.400, 23.267] |
| r6 | op=absent|adj=oracle|noise=gaussian | isolation_forest_persistent@0.002 | 30 | — | 0.01 [0.006, 0.014] | — | — | — | — | 0.01 [0.006, 0.014] | 1.1 [0.600, 1.667] |
| r6 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 20.0 [20.000, 20.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | penalty_healing@10 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.288 [0.273, 0.303] | 150.5 [148.599, 152.033] |
| r6 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 385.0 [385.000, 385.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | stopping_response_release | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.398 [0.395, 0.400] | 195.1667 [194.133, 196.234] |
| r6 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | tolerance_no_recovery | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | tolerance_periodic@5 | 30 | — | 1.0 [1.000, 1.000] | — | — | — | — | 1.0 [1.000, 1.000] | 850.0 [850.000, 850.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.686 | 3.621 | +0.064 [-0.004, +0.116] | 0.0034 | +0.66 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.275 | 3.621 | -0.346 [-0.442, -0.251] | 9.4e-07 | -0.92 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.187 | 3.621 | -0.435 [-0.496, -0.385] | 1.1e-08 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | ddca@0.85:4 | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.332 | 3.621 | -0.289 [-0.355, -0.233] | 1.1e-08 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | dirichlet_reliability | 30 | 3.782 | 3.621 | +0.161 [+0.099, +0.212] | 0.00018 | +0.77 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.089 | 0.1 | -0.011 [-0.023, +0.004] | 0.029 | -0.49 |
| r1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.089 | 0.0 | +0.089 [+0.077, +0.104] | 9e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 4.7 | 0.0 | +4.700 [+4.000, +5.467] | 9.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 4.7 | 0.0 | +4.700 [+4.000, +5.467] | 9.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.17 | 3.621 | +6.549 [+6.381, +6.736] | 1.1e-08 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest_persistent@0.002 | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 10.188 | 3.621 | +6.566 [+6.477, +6.646] | 1.1e-08 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | page_cusum@0.05:1.6 | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.475 | 3.621 | -0.147 [-0.205, -0.095] | 5.7e-06 | -0.90 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | penalty_healing@10 | 30 | 3.369 | 3.621 | -0.253 [-0.314, -0.202] | 1.1e-08 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.1 | 0.0 | +0.100 [+0.100, +0.100] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 297.6 | 0.0 | +297.600 [+296.633, +298.533] | 6.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 297.6 | 0.0 | +297.600 [+296.633, +298.533] | 6.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response_release | 30 | 0.1 | 0.0 | +0.100 [+0.100, +0.100] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 132.533 | 0.0 | +132.533 [+130.200, +134.800] | 7.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 132.533 | 0.0 | +132.533 [+130.200, +134.800] | 7.2e-06 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response_release | 30 | 3.535 | 3.621 | -0.086 [-0.148, -0.038] | 0.0029 | -0.66 |
| r1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.1 | 0.0 | +0.100 [+0.100, +0.100] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 100.0 | 0.0 | +100.000 [+100.000, +100.000] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 100.0 | 0.0 | +100.000 [+100.000, +100.000] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.419 | 3.621 | -0.203 [-0.262, -0.157] | 1.1e-08 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_no_recovery | 30 | 0.0 | 0.1 | -0.100 [-0.100, -0.100] | 2.6e-07 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.247 | 3.621 | -0.374 [-0.436, -0.325] | 1.1e-08 | -1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.1 | +0.900 [+0.900, +0.900] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 730.0 | 0.0 | +730.000 [+730.000, +730.000] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 730.0 | 0.0 | +730.000 [+730.000, +730.000] | 2.6e-07 | +1.00 |
| r1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.504 | 3.621 | -0.117 [-0.183, -0.065] | 6.9e-07 | -0.91 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | beta_reputation | 30 | 0.608 | 0.63 | -0.022 [-0.023, -0.020] | 1.4e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | beta_reputation | 30 | 5.822 | 4.9 | +0.922 [+0.867, +0.967] | 4e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | beta_reputation | 30 | 2.9 | 2.0 | +0.900 [+0.833, +0.956] | 4.9e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | beta_reputation | 11 | 18.864 | 4.878 | +13.955 [+13.773, +14.121] | 0.00098 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | beta_reputation | 30 | 93.333 | 92.4 | +0.933 [+0.467, +1.433] | 0.008 | +0.88 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 4.031 | 3.7 | +0.331 [+0.272, +0.387] | 9.3e-08 | +0.98 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | binary_zt | 30 | 1.0 | 0.545 | +0.455 [+0.455, +0.455] | 4.3e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 1.0 | 0.63 | +0.370 [+0.368, +0.372] | 1.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 0.0 | 1.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 0.0 | 2.9 | -2.900 [-3.000, -2.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 0.0 | 4.9 | -4.900 [-5.000, -4.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 11.367 | -11.367 [-11.511, -11.222] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 90.0 | 92.4 | -2.400 [-3.000, -1.800] | 9e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.464 | 3.7 | -0.236 [-0.385, -0.065] | 0.0093 | -0.54 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | binary_zt@0.8 | 30 | 1.0 | 0.545 | +0.455 [+0.455, +0.455] | 4.3e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.63 | +0.370 [+0.368, +0.372] | 1.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 1.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 2.9 | -2.900 [-3.000, -2.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 4.9 | -4.900 [-5.000, -4.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.8 | 30 | 0.0 | 11.367 | -11.367 [-11.511, -11.222] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 90.0 | 92.4 | -2.400 [-3.000, -1.800] | 9e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.513 | 3.7 | -0.187 [-0.313, -0.033] | 0.00021 | -0.73 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | cusum@0.15:6.4 | 30 | 0.526 | 0.63 | -0.104 [-0.106, -0.102] | 1.2e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.9 | 0.97 | -0.070 [-0.074, -0.067] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | cusum@0.15:6.4 | 30 | 4.0 | 1.9 | +2.100 [+2.000, +2.233] | 1.4e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 5.0 | 2.9 | +2.100 [+2.000, +2.233] | 1.4e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | cusum@0.15:6.4 | 30 | 7.022 | 4.9 | +2.122 [+2.022, +2.244] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 128.933 | 92.4 | +36.533 [+36.000, +37.100] | 4.1e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.884 | 3.7 | +0.183 [+0.106, +0.249] | 0.00057 | +0.74 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | ddca@0.85:4 | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | ddca@0.85:4 | 30 | 1.0 | 0.545 | +0.455 [+0.455, +0.455] | 4.3e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | ddca@0.85:4 | 30 | 0.899 | 0.63 | +0.269 [+0.265, +0.272] | 1.7e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | ddca@0.85:4 | 30 | 0.943 | 0.97 | -0.027 [-0.031, -0.022] | 1.2e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | ddca@0.85:4 | 30 | 3.7 | 1.9 | +1.800 [+1.667, +1.944] | 1.1e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | ddca@0.85:4 | 30 | 3.7 | 2.9 | +0.800 [+0.667, +0.944] | 1.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | ddca@0.85:4 | 30 | 3.7 | 4.9 | -1.200 [-1.333, -1.056] | 1.1e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | ddca@0.85:4 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | ddca@0.85:4 | 30 | 2.233 | 11.367 | -9.133 [-9.356, -8.900] | 1.6e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | ddca@0.85:4 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | ddca@0.85:4 | 30 | 85.6 | 92.4 | -6.800 [-7.700, -5.933] | 9.6e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.539 | 3.7 | -0.161 [-0.207, -0.123] | 3.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | dirichlet_reliability | 30 | 4.001 | 3.7 | +0.301 [+0.264, +0.336] | 1.5e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.064 | 0.106 | -0.043 [-0.054, -0.032] | 1e-05 | -0.96 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.002 | 30 | 0.685 | 0.545 | +0.139 [+0.100, +0.183] | 5.2e-06 | +0.96 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.002 | 30 | 0.983 | 0.63 | +0.352 [+0.349, +0.356] | 1.7e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.002 | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.002 | 30 | 0.0 | 1.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.002 | 30 | 0.0 | 2.9 | -2.900 [-3.000, -2.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest@0.002 | 30 | 0.0 | 4.9 | -4.900 [-5.000, -4.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest@0.002 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest@0.002 | 30 | 0.144 | 11.367 | -11.222 [-11.456, -10.911] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.002 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.064 | 0.0 | +0.064 [+0.052, +0.074] | 9e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 3.1 | 0.0 | +3.100 [+2.533, +3.667] | 9.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.238 | 3.7 | +6.537 [+6.428, +6.647] | 1.1e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest_persistent@0.002 | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest_persistent@0.002 | 30 | 1.0 | 0.545 | +0.455 [+0.455, +0.455] | 4.3e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest_persistent@0.002 | 30 | 0.934 | 0.63 | +0.303 [+0.301, +0.305] | 1.3e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest_persistent@0.002 | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest_persistent@0.002 | 30 | 1.989 | 2.9 | -0.911 [-1.011, -0.789] | 2.8e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest_persistent@0.002 | 30 | 1.989 | 4.9 | -2.911 [-3.011, -2.789] | 2e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest_persistent@0.002 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest_persistent@0.002 | 30 | 2.0 | 11.367 | -9.367 [-9.511, -9.222] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest_persistent@0.002 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest_persistent@0.002 | 30 | 90.033 | 92.4 | -2.367 [-2.933, -1.800] | 1.5e-05 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 10.675 | 3.7 | +6.975 [+6.894, +7.053] | 1.1e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | page_cusum@0.05:1.6 | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | page_cusum@0.05:1.6 | 30 | 1.0 | 0.545 | +0.455 [+0.455, +0.455] | 4.3e-08 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | page_cusum@0.05:1.6 | 30 | 0.378 | 0.63 | -0.252 [-0.254, -0.250] | 1.2e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.7 | 0.97 | -0.270 [-0.274, -0.267] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | page_cusum@0.05:1.6 | 30 | 3.0 | 1.9 | +1.100 [+1.000, +1.233] | 1.4e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | page_cusum@0.05:1.6 | 30 | 3.0 | 4.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 11.367 | -11.367 [-11.511, -11.222] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 21.0 | 92.4 | -71.400 [-72.000, -70.800] | 4e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.475 | 3.7 | -0.225 [-0.279, -0.177] | 1.1e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | penalty_healing@10 | 30 | 0.584 | 0.63 | -0.046 [-0.048, -0.045] | 1.7e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | penalty_healing@10 | 30 | 18.528 | 11.367 | +7.161 [+6.989, +7.344] | 1.7e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | penalty_healing@10 | 30 | 13.578 | 4.878 | +8.700 [+8.567, +8.844] | 1.3e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | penalty_healing@10 | 30 | 112.9 | 92.4 | +20.500 [+19.867, +21.167] | 6.3e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | penalty_healing@10 | 30 | 3.541 | 3.7 | -0.159 [-0.219, -0.109] | 1.1e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 30 | 0.376 | 0.63 | -0.254 [-0.256, -0.252] | 1.7e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 30 | 2.0 | 2.9 | -0.900 [-1.000, -0.767] | 2.1e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | stopping_response | 30 | 3.411 | 4.9 | -1.489 [-1.622, -1.344] | 1.4e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | stopping_response | 30 | 1.411 | 2.0 | -0.589 [-0.689, -0.489] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.106 | 0.0 | +0.106 [+0.106, +0.106] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 107.6 | 0.0 | +107.600 [+106.633, +108.533] | 6.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 247.367 | 92.4 | +154.967 [+153.933, +156.000] | 6.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response_release | 30 | 0.435 | 0.63 | -0.195 [-0.199, -0.192] | 1.7e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response_release | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response_release | 30 | 2.0 | 2.9 | -0.900 [-1.000, -0.767] | 2.1e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | stopping_response_release | 30 | 3.411 | 4.9 | -1.489 [-1.622, -1.344] | 1.4e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | stopping_response_release | 30 | 1.411 | 2.0 | -0.589 [-0.689, -0.489] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response_release | 30 | 0.106 | 0.0 | +0.106 [+0.106, +0.106] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 84.2 | 0.0 | +84.200 [+82.667, +85.700] | 7.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 223.967 | 92.4 | +131.567 [+130.067, +133.100] | 7.2e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 30 | 0.643 | 0.63 | +0.013 [+0.010, +0.015] | 1.9e-06 | +0.98 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.97 | +0.030 [+0.026, +0.033] | 2.1e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 1.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 2.9 | -2.900 [-3.000, -2.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | tolerance | 30 | 0.0 | 4.9 | -4.900 [-5.000, -4.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | tolerance | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | tolerance | 30 | 0.0 | 11.367 | -11.367 [-11.511, -11.222] | 1.5e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | tolerance | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.106 | 0.0 | +0.106 [+0.106, +0.106] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 100.0 | 0.0 | +100.000 [+100.000, +100.000] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 190.0 | 92.4 | +97.600 [+97.000, +98.200] | 2.8e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.604 | 3.7 | -0.096 [-0.174, -0.016] | 0.019 | -0.49 |
| r2|op=absent|adj=oracle|noise=gaussian|device_tpr | tolerance_no_recovery | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_no_recovery | 30 | 0.0 | 0.106 | -0.106 [-0.106, -0.106] | 2.6e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance_no_recovery | 30 | 0.0 | 0.97 | -0.970 [-0.974, -0.967] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_no_recovery | 30 | 0.0 | 92.4 | -92.400 [-93.000, -91.800] | 4e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.262 | 3.7 | -0.438 [-0.493, -0.395] | 1.1e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.106 | +0.894 [+0.894, +0.894] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance_periodic@5 | 30 | 0.113 | 0.545 | -0.432 [-0.432, -0.432] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance_periodic@5 | 30 | 0.058 | 0.63 | -0.572 [-0.574, -0.570] | 1.2e-06 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance_periodic@5 | 30 | 0.6 | 0.97 | -0.370 [-0.374, -0.367] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance_periodic@5 | 30 | 0.0 | 1.9 | -1.900 [-2.000, -1.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance_periodic@5 | 30 | 0.0 | 2.9 | -2.900 [-3.000, -2.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | tolerance_periodic@5 | 30 | 0.0 | 4.9 | -4.900 [-5.000, -4.767] | 1.4e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|containment_mean | tolerance_periodic@5 | 30 | 0.0 | 2.0 | -2.000 [-2.000, -2.000] | 4.3e-08 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|mttr_mean | tolerance_periodic@5 | 30 | 16.0 | 11.367 | +4.633 [+4.489, +4.778] | 1.5e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | tolerance_periodic@5 | 30 | 0.0 | 4.878 | -4.878 [-4.944, -4.811] | 6.5e-07 | -1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 497.0 | 0.0 | +497.000 [+497.000, +497.000] | 2.6e-07 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 530.0 | 92.4 | +437.600 [+437.000, +438.200] | 2.7e-06 | +1.00 |
| r2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.521 | 3.7 | -0.179 [-0.236, -0.133] | 1.1e-08 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | beta_reputation | 30 | 17.533 | 8.3 | +9.233 [+8.867, +9.600] | 5e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.753 | 3.619 | +0.133 [+0.115, +0.150] | 3.4e-08 | +0.99 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.319 | 3.619 | -0.300 [-0.321, -0.281] | 1.1e-08 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.321 | 3.619 | -0.298 [-0.316, -0.279] | 1.1e-08 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 1.8 | 8.3 | -6.500 [-7.033, -5.967] | 4.1e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.665 | 3.619 | +0.046 [+0.033, +0.059] | 2.9e-06 | +0.92 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | ddca@0.85:4 | 30 | 0.067 | 8.3 | -8.233 [-8.400, -8.067] | 2.3e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.851 | 3.619 | +0.232 [+0.151, +0.308] | 2.1e-05 | +0.82 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | dirichlet_reliability | 30 | 3.937 | 3.619 | +0.318 [+0.273, +0.367] | 1.1e-08 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.085 | 0.0 | +0.085 [+0.075, +0.097] | 9e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.002 | 30 | 1.433 | 8.3 | -6.867 [-8.333, -4.100] | 2.7e-05 | -0.87 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.085 | 0.0 | +0.085 [+0.075, +0.097] | 9e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 5.467 | 0.0 | +5.467 [+4.867, +6.100] | 9.2e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 5.467 | 0.0 | +5.467 [+4.867, +6.100] | 9.2e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 11.355 | 3.619 | +7.736 [+7.471, +7.997] | 1.1e-08 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest_persistent@0.002 | 30 | 0.1 | 8.3 | -8.200 [-8.400, -7.967] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 11.502 | 3.619 | +7.882 [+7.676, +8.085] | 1.1e-08 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.555 | 3.619 | -0.064 [-0.104, -0.023] | 0.011 | -0.57 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | penalty_healing@10 | 30 | 3.466 | 3.619 | -0.154 [-0.237, -0.044] | 0.0011 | -0.69 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 47.0 | 0.0 | +47.000 [+47.000, +47.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 47.0 | 0.0 | +47.000 [+47.000, +47.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.949 | 3.619 | +0.330 [+0.205, +0.480] | 5.1e-07 | +0.95 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response_release | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | stopping_response_release | 30 | 12.9 | 8.3 | +4.600 [+4.233, +4.967] | 4.9e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response_release | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 10.9 | 0.0 | +10.900 [+10.533, +11.267] | 5.7e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 10.9 | 0.0 | +10.900 [+10.533, +11.267] | 5.7e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 1.7 | 0.0 | +1.700 [+1.533, +1.867] | 2.2e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 1.7 | 0.0 | +1.700 [+1.533, +1.867] | 2.8e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.429 | 3.619 | -0.190 [-0.201, -0.179] | 1.1e-08 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_no_recovery | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 1.7e-06 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.244 | 3.619 | -0.375 [-0.387, -0.364] | 1.1e-08 | -1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_periodic@5 | 30 | 44.0 | 8.3 | +35.700 [+35.533, +35.867] | 1.7e-06 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 550.0 | 0.0 | +550.000 [+550.000, +550.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 550.0 | 0.0 | +550.000 [+550.000, +550.000] | 2.6e-07 | +1.00 |
| r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.511 | 3.619 | -0.108 [-0.123, -0.095] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | beta_reputation | 30 | 21.733 | 10.167 | +11.567 [+11.233, +11.933] | 5e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | beta_reputation | 30 | 0.011 | 0.02 | -0.009 [-0.013, -0.006] | 0.0024 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | beta_reputation | 30 | 2.133 | 5.367 | -3.233 [-3.933, -2.533] | 8.3e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | beta_reputation | 30 | 2.133 | 5.367 | -3.233 [-3.933, -2.533] | 8.3e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.167 | -10.167 [-10.300, -10.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 3.5e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 3.5e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.244 | 4.022 | -0.778 [-1.053, -0.543] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 10.167 | -10.167 [-10.300, -10.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 3.5e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 3.5e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.258 | 4.022 | -0.764 [-1.035, -0.533] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 15.8 | 10.167 | +5.633 [+5.400, +5.900] | 4.1e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | cusum@0.15:6.4 | 30 | 0.002 | 0.02 | -0.018 [-0.020, -0.015] | 1.2e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | cusum@0.15:6.4 | 30 | 0.5 | 5.367 | -4.867 [-5.300, -4.333] | 4.6e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 0.5 | 5.367 | -4.867 [-5.300, -4.333] | 4.1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.58 | 4.022 | -0.442 [-0.709, -0.216] | 1.1e-07 | -0.98 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | ddca@0.85:4 | 30 | 2.6 | 10.167 | -7.567 [-7.833, -7.300] | 3.4e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | ddca@0.85:4 | 30 | 6.8 | 5.367 | +1.433 [+1.067, +1.833] | 1.9e-05 | +0.96 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | ddca@0.85:4 | 30 | 6.8 | 5.367 | +1.433 [+1.067, +1.833] | 1.4e-05 | +0.96 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.455 | 4.022 | -0.566 [-0.840, -0.332] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.109 | 0.02 | +0.089 [+0.076, +0.105] | 9e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.002 | 30 | 3.2 | 10.167 | -6.967 [-10.233, -1.733] | 0.00016 | -0.75 |
| r4|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.109 | 0.02 | +0.089 [+0.076, +0.105] | 9e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 12.8 | 5.367 | +7.433 [+6.700, +8.267] | 9.2e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 12.8 | 5.367 | +7.433 [+6.700, +8.267] | 9.2e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.075 | 4.022 | +6.053 [+5.704, +6.370] | 1.1e-08 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest_persistent@0.002 | 30 | 2.0 | 10.167 | -8.167 [-8.300, -8.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest_persistent@0.002 | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 4.1e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest_persistent@0.002 | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 4.1e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 10.415 | 4.022 | +6.393 [+6.111, +6.643] | 1.1e-08 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 10.167 | -10.167 [-10.300, -10.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | page_cusum@0.05:1.6 | 30 | 2.0 | 5.367 | -3.367 [-3.533, -3.200] | 4.1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 2.0 | 5.367 | -3.367 [-3.533, -3.200] | 4e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.632 | 4.022 | -0.390 [-0.673, -0.142] | 0.011 | -0.54 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | penalty_healing@10 | 30 | 17.633 | 10.167 | +7.467 [+5.700, +9.167] | 2.4e-05 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | penalty_healing@10 | 30 | 13.067 | 5.367 | +7.700 [+5.867, +9.533] | 2.4e-05 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | penalty_healing@10 | 30 | 13.067 | 5.367 | +7.700 [+5.867, +9.533] | 1.8e-05 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | penalty_healing@10 | 30 | 3.359 | 4.022 | -0.663 [-0.932, -0.435] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 66.467 | 5.367 | +61.100 [+60.867, +61.333] | 5.4e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 66.467 | 5.367 | +61.100 [+60.867, +61.333] | 5.4e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.545 | 4.022 | -0.477 [-0.751, -0.244] | 1e-06 | -0.94 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | stopping_response_release | 30 | 22.5 | 10.167 | +12.333 [+11.867, +12.800] | 4.9e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 25.967 | 5.367 | +20.600 [+20.033, +21.133] | 7.2e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 25.967 | 5.367 | +20.600 [+20.033, +21.133] | 7.2e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response_release | 30 | 3.523 | 4.022 | -0.499 [-0.770, -0.269] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 30 | 0.0 | 10.167 | -10.167 [-10.300, -10.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 2.2e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 8.0 | 5.367 | +2.633 [+2.467, +2.800] | 2.8e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.442 | 4.022 | -0.580 [-0.853, -0.348] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_no_recovery | 30 | 0.0 | 0.02 | -0.020 [-0.020, -0.020] | 2.6e-07 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_no_recovery | 30 | 0.0 | 10.167 | -10.167 [-10.300, -10.033] | 1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_no_recovery | 30 | 0.0 | 0.02 | -0.020 [-0.020, -0.020] | 2.6e-07 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_no_recovery | 30 | 0.0 | 5.367 | -5.367 [-5.533, -5.200] | 4.1e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_no_recovery | 30 | 0.0 | 5.367 | -5.367 [-5.533, -5.200] | 4e-06 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.246 | 4.022 | -0.776 [-1.043, -0.548] | 1.1e-08 | -1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.02 | +0.980 [+0.980, +0.980] | 2.6e-07 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_periodic@5 | 30 | 58.0 | 10.167 | +47.833 [+47.700, +47.967] | 1e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.02 | +0.980 [+0.980, +0.980] | 2.6e-07 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 750.0 | 5.367 | +744.633 [+744.467, +744.800] | 2.1e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 750.0 | 5.367 | +744.633 [+744.467, +744.800] | 2.7e-06 | +1.00 |
| r4|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.504 | 4.022 | -0.518 [-0.786, -0.289] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | beta_reputation | 30 | 18.365 | 10.413 | +7.952 [+7.890, +8.013] | 5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | beta_reputation | 30 | 0.193 | 0.169 | +0.024 [+0.012, +0.036] | 0.0062 | +0.74 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | beta_reputation | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 8.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | beta_reputation | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 8.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.924 | 3.796 | +0.128 [+0.103, +0.153] | 1e-07 | +0.97 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 7.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 6.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 6.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.383 | 3.796 | -0.413 [-0.453, -0.368] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 7.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.391 | 3.796 | -0.405 [-0.435, -0.373] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | cusum@0.15:6.4 | 30 | 0.355 | 0.4 | -0.045 [-0.055, -0.035] | 1.4e-05 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 7.577 | 10.413 | -2.837 [-2.980, -2.693] | 4.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | cusum@0.15:6.4 | 30 | 0.0 | 0.169 | -0.169 [-0.181, -0.156] | 7.4e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | cusum@0.15:6.4 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 7.8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | ddca@0.85:4 | 30 | 0.379 | 0.4 | -0.021 [-0.029, -0.015] | 6e-05 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | ddca@0.85:4 | 30 | 1.27 | 10.413 | -9.143 [-9.232, -9.058] | 3.4e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | ddca@0.85:4 | 30 | 0.379 | 0.169 | +0.210 [+0.196, +0.224] | 1e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | ddca@0.85:4 | 30 | 43.4 | 27.333 | +16.067 [+14.133, +17.967] | 1e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | ddca@0.85:4 | 30 | 43.4 | 27.333 | +16.067 [+14.133, +17.967] | 9.6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.404 | 3.796 | -0.392 [-0.418, -0.369] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | dirichlet_reliability | 30 | 4.249 | 3.796 | +0.453 [+0.282, +0.674] | 1.5e-08 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.308 | 0.4 | -0.092 [-0.109, -0.075] | 9e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.002 | 30 | 2.657 | 10.413 | -7.757 [-8.373, -7.115] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.308 | 0.169 | +0.139 [+0.118, +0.160] | 9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 21.4 | 27.333 | -5.933 [-7.167, -4.800] | 9.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 21.4 | 27.333 | -5.933 [-7.167, -4.800] | 9.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.04 | 3.796 | +6.244 [+6.196, +6.286] | 1.1e-08 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest_persistent@0.002 | 30 | 0.012 | 0.4 | -0.388 [-0.393, -0.382] | 3.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest_persistent@0.002 | 30 | 0.018 | 10.413 | -10.395 [-10.438, -10.355] | 3.3e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest_persistent@0.002 | 30 | 0.012 | 0.169 | -0.157 [-0.171, -0.141] | 9.7e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest_persistent@0.002 | 30 | 1.2 | 27.333 | -26.133 [-26.800, -25.467] | 8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest_persistent@0.002 | 30 | 1.2 | 27.333 | -26.133 [-26.800, -25.467] | 8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 10.375 | 3.796 | +6.578 [+6.526, +6.627] | 1.1e-08 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | page_cusum@0.05:1.6 | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 8.8e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | page_cusum@0.05:1.6 | 30 | 20.0 | 27.333 | -7.333 [-7.833, -6.833] | 7.8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 20.0 | 27.333 | -7.333 [-7.833, -6.833] | 6.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.655 | 3.796 | -0.142 [-0.218, -0.056] | 0.0029 | -0.66 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | penalty_healing@10 | 30 | 17.492 | 10.413 | +7.078 [+6.717, +7.445] | 6.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | penalty_healing@10 | 30 | 0.226 | 0.169 | +0.057 [+0.043, +0.071] | 3.1e-05 | +0.97 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | penalty_healing@10 | 30 | 77.333 | 27.333 | +50.000 [+50.000, +50.000] | 2.6e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | penalty_healing@10 | 30 | 77.333 | 27.333 | +50.000 [+50.000, +50.000] | 2.6e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.399 | 0.169 | +0.231 [+0.218, +0.243] | 4.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 335.0 | 27.333 | +307.667 [+307.167, +308.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 335.0 | 27.333 | +307.667 [+307.167, +308.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | stopping_response_release | 30 | 17.488 | 10.413 | +7.075 [+6.982, +7.170] | 4.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response_release | 30 | 0.358 | 0.169 | +0.189 [+0.174, +0.205] | 4.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 100.167 | 27.333 | +72.833 [+72.200, +73.433] | 7.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 100.167 | 27.333 | +72.833 [+72.200, +73.433] | 7.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response_release | 30 | 3.705 | 3.796 | -0.091 [-0.115, -0.068] | 5.2e-07 | -0.95 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 4.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 3.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 3.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.564 | 3.796 | -0.232 [-0.251, -0.214] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_no_recovery | 30 | 0.0 | 0.4 | -0.400 [-0.400, -0.400] | 2.6e-07 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_no_recovery | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_no_recovery | 30 | 0.0 | 0.169 | -0.169 [-0.181, -0.156] | 7.4e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_no_recovery | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 7.8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_no_recovery | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.259 | 3.796 | -0.537 [-0.559, -0.516] | 1.1e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.4 | +0.600 [+0.600, +0.600] | 2.6e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_periodic@5 | 30 | 61.0 | 10.413 | +50.587 [+50.548, +50.623] | 3.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.169 | +0.831 [+0.819, +0.844] | 2.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 750.0 | 27.333 | +722.667 [+722.167, +723.167] | 3.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 750.0 | 27.333 | +722.667 [+722.167, +723.167] | 3.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.517 | 3.796 | -0.279 [-0.299, -0.260] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | beta_reputation | 30 | 17.755 | 10.413 | +7.342 [+7.292, +7.392] | 5e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | beta_reputation | 30 | 0.151 | 0.297 | -0.147 [-0.157, -0.136] | 1e-05 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | beta_reputation | 30 | 25.0 | 52.167 | -27.167 [-27.700, -26.633] | 8.3e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | beta_reputation | 30 | 25.0 | 52.167 | -27.167 [-27.700, -26.633] | 8.3e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 7.4e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 91.133 | 52.167 | +38.967 [+37.867, +40.200] | 6.5e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 91.133 | 52.167 | +38.967 [+37.867, +40.200] | 6.5e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.309 | 5.339 | -2.030 [-2.204, -1.851] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 7.4e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 100.0 | 52.167 | +47.833 [+47.300, +48.367] | 6.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 100.0 | 52.167 | +47.833 [+47.300, +48.367] | 6.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.327 | 5.339 | -2.012 [-2.188, -1.832] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | cusum@0.15:6.4 | 30 | 0.36 | 0.4 | -0.040 [-0.049, -0.031] | 1.4e-05 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 7.618 | 10.413 | -2.795 [-2.918, -2.663] | 4.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | cusum@0.15:6.4 | 30 | 0.0 | 0.297 | -0.297 [-0.307, -0.289] | 7.4e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | cusum@0.15:6.4 | 30 | 0.0 | 52.167 | -52.167 [-52.700, -51.633] | 7.8e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 0.0 | 52.167 | -52.167 [-52.700, -51.633] | 6.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 4.727 | 5.339 | -0.613 [-0.779, -0.442] | 2.9e-06 | -0.92 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | ddca@0.85:4 | 30 | 0.348 | 0.4 | -0.052 [-0.063, -0.041] | 8.4e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | ddca@0.85:4 | 30 | 1.222 | 10.413 | -9.192 [-9.278, -9.103] | 3.4e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | ddca@0.85:4 | 30 | 0.348 | 0.297 | +0.051 [+0.035, +0.066] | 0.00015 | +0.88 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | ddca@0.85:4 | 30 | 38.933 | 52.167 | -13.233 [-15.200, -11.267] | 1e-05 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | ddca@0.85:4 | 30 | 38.933 | 52.167 | -13.233 [-15.200, -11.267] | 9.6e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | ddca@0.85:4 | 30 | 3.423 | 5.339 | -1.916 [-2.090, -1.740] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | dirichlet_reliability | 30 | 5.63 | 5.339 | +0.290 [+0.236, +0.351] | 1.1e-08 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.311 | 0.4 | -0.089 [-0.108, -0.071] | 9e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.002 | 30 | 1.905 | 10.413 | -8.508 [-9.097, -7.898] | 5.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 21.833 | 52.167 | -30.333 [-31.967, -28.767] | 9.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 21.833 | 52.167 | -30.333 [-31.967, -28.767] | 9.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.029 | 5.339 | +4.689 [+4.510, +4.869] | 1.1e-08 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest_persistent@0.002 | 30 | 0.01 | 0.4 | -0.390 [-0.394, -0.385] | 3.5e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest_persistent@0.002 | 30 | 0.018 | 10.413 | -10.395 [-10.445, -10.348] | 3.3e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest_persistent@0.002 | 30 | 0.01 | 0.297 | -0.287 [-0.298, -0.277] | 9.7e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest_persistent@0.002 | 30 | 1.1 | 52.167 | -51.067 [-51.800, -50.333] | 8e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest_persistent@0.002 | 30 | 1.1 | 52.167 | -51.067 [-51.800, -50.333] | 8e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest_persistent@0.002 | 30 | 10.367 | 5.339 | +5.027 [+4.838, +5.222] | 1.1e-08 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | page_cusum@0.05:1.6 | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 8.8e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | page_cusum@0.05:1.6 | 30 | 20.0 | 52.167 | -32.167 [-32.700, -31.633] | 7.8e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 20.0 | 52.167 | -32.167 [-32.700, -31.633] | 6.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.759 | 5.339 | -1.581 [-1.799, -1.341] | 1.9e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | penalty_healing@10 | 30 | 17.697 | 10.413 | +7.283 [+6.832, +7.712] | 6.9e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | penalty_healing@10 | 30 | 150.5 | 52.167 | +98.333 [+96.667, +99.667] | 9.9e-07 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | penalty_healing@10 | 30 | 150.5 | 52.167 | +98.333 [+96.667, +99.667] | 9.9e-07 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | penalty_healing@10 | 30 | 4.579 | 5.339 | -0.760 [-0.932, -0.583] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 4.4e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 385.0 | 52.167 | +332.833 [+332.300, +333.367] | 6.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 385.0 | 52.167 | +332.833 [+332.300, +333.367] | 6.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 4.114 | 5.339 | -1.226 [-1.467, -0.976] | 7.8e-08 | -0.98 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | stopping_response_release | 30 | 17.533 | 10.413 | +7.120 [+7.020, +7.218] | 4.9e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response_release | 30 | 0.398 | 0.297 | +0.101 [+0.091, +0.110] | 4.4e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response_release | 30 | 195.167 | 52.167 | +143.000 [+141.866, +144.100] | 7.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response_release | 30 | 195.167 | 52.167 | +143.000 [+141.866, +144.100] | 7.2e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response_release | 30 | 3.789 | 5.339 | -1.550 [-1.763, -1.316] | 1.9e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 4.4e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 100.0 | 52.167 | +47.833 [+47.300, +48.367] | 3.1e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 100.0 | 52.167 | +47.833 [+47.300, +48.367] | 3.1e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.559 | 5.339 | -1.781 [-1.952, -1.604] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_no_recovery | 30 | 0.0 | 0.4 | -0.400 [-0.400, -0.400] | 2.6e-07 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_no_recovery | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_no_recovery | 30 | 0.0 | 0.297 | -0.297 [-0.307, -0.289] | 7.4e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_no_recovery | 30 | 0.0 | 52.167 | -52.167 [-52.700, -51.633] | 7.8e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_no_recovery | 30 | 0.0 | 52.167 | -52.167 [-52.700, -51.633] | 6.2e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_no_recovery | 30 | 3.271 | 5.339 | -2.069 [-2.245, -1.887] | 1.1e-08 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance_periodic@5 | 30 | 1.0 | 0.4 | +0.600 [+0.600, +0.600] | 2.6e-07 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance_periodic@5 | 30 | 46.0 | 10.413 | +35.587 [+35.543, +35.627] | 3.1e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance_periodic@5 | 30 | 1.0 | 0.297 | +0.703 [+0.693, +0.711] | 2.9e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance_periodic@5 | 30 | 850.0 | 52.167 | +797.833 [+797.300, +798.367] | 3.1e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance_periodic@5 | 30 | 850.0 | 52.167 | +797.833 [+797.300, +798.367] | 3.1e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance_periodic@5 | 30 | 3.527 | 5.339 | -1.813 [-1.987, -1.636] | 1.1e-08 | -1.00 |

Only comparisons significant after Holm correction are listed; all 855 are in `comparisons.csv`.
