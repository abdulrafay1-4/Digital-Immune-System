# Experiment report: `sweeps`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "sweeps",
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
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 90.9667 [90.033, 91.933] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.3 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.4 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.6 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.7 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 100.0 [100.000, 100.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.3 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.4 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0333 [0.000, 0.100] | 0.9985 [0.996, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 41.3667 [40.800, 41.900] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.7 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 45.0 [45.000, 45.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 45.0 [45.000, 45.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.3 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.4 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.775 [3.125, 4.517] | 0.4615 [0.430, 0.491] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 17.5 [15.967, 18.967] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.7 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.4833 [2.950, 4.025] | 0.469 [0.440, 0.500] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 13.9 [12.967, 14.834] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.3 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.4 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.7 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| sweep:campaign:0.20 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.5917 [6.392, 6.800] | 0.7959 [0.787, 0.805] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.20 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.25 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.9167 [4.800, 5.050] | 0.8704 [0.864, 0.876] | — | 0.0 [0.000, 0.000] | 45.8333 [42.867, 48.567] |
| sweep:campaign:0.25 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.30 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| sweep:campaign:0.30 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.35 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.85 [3.767, 3.958] | 0.9178 [0.913, 0.921] | — | 0.0 [0.000, 0.000] | 77.7 [77.167, 78.267] |
| sweep:campaign:0.35 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.40 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.5083 [4.400, 4.625] | 0.8885 [0.883, 0.893] | — | 0.0 [0.000, 0.000] | 80.9 [80.467, 81.300] |
| sweep:campaign:0.40 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.5417 [0.433, 0.650] | 0.0 [0.000, 0.000] | 0.7203 [0.642, 0.802] | 17.9568 [17.296, 18.679] | 0.1611 [0.124, 0.201] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:campaign:0.50 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.75 [3.750, 3.750] | 0.9222 [0.922, 0.922] | — | 0.0 [0.000, 0.000] | 86.0 [86.000, 86.000] |
| sweep:campaign:0.50 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 8.1 [8.042, 8.175] | 0.7289 [0.726, 0.731] | — | 0.0 [0.000, 0.000] | 11.9 [9.699, 14.167] |
| sweep:duty:1:10:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:10:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:2:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.4 [7.133, 7.733] | 0.9289 [0.925, 0.932] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:2:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.4 [7.133, 7.733] | 0.9289 [0.925, 0.932] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:3:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:3:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:5:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:1:5:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:duty:2:5:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 10.6667 [9.833, 11.333] | 0.9037 [0.896, 0.913] | — | 0.0 [0.000, 0.000] | 42.8 [42.400, 43.300] |
| sweep:duty:2:5:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 10.6667 [9.833, 11.333] | 0.9037 [0.896, 0.913] | — | 0.0 [0.000, 0.000] | 42.8 [42.400, 43.300] |
| sweep:duty:3:5:0.60 | op=absent|adj=oracle|noise=gaussian | beta_reputation | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.3333 [4.800, 5.833] | 0.9543 [0.949, 0.960] | — | 0.0 [0.000, 0.000] | 63.9667 [62.900, 65.033] |
| sweep:duty:3:5:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.3333 [4.800, 5.833] | 0.9543 [0.949, 0.960] | — | 0.0 [0.000, 0.000] | 84.1667 [84.067, 84.300] |
| sweep:lowslow:0.30 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.30 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.40 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.40 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.50 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.50 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.60 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.60 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.8667 [0.733, 0.967] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 15.9615 [13.923, 17.962] | 0.3926 [0.313, 0.468] | — | 0.0 [0.000, 0.000] | 7.6 [5.033, 10.267] |
| sweep:lowslow:0.70 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| sweep:lowslow:0.70 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| sweep:lowslow:0.80 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [2.767, 5.400] | 0.4444 [0.393, 0.498] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 8.4 [7.300, 9.633] |
| sweep:lowslow:0.80 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.3 [5.167, 5.467] | 0.9267 [0.923, 0.930] | — | 0.0 [0.000, 0.000] | 34.4 [33.067, 35.600] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 1.6e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 1.6e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 1.6e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.399 | 3.825 | -0.426 [-0.453, -0.396] | 1.9e-08 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.3 | 30 | 0.0 | 0.4 | -0.400 [-0.400, -0.400] | 1.7e-07 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.3 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.3 | 30 | 0.0 | 0.169 | -0.169 [-0.181, -0.156] | 6.3e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.3 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.3 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.3 | 30 | 3.315 | 3.825 | -0.510 [-0.546, -0.473] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.4 | 30 | 0.0 | 0.4 | -0.400 [-0.400, -0.400] | 1.7e-07 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.4 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.4 | 30 | 0.0 | 0.169 | -0.169 [-0.181, -0.156] | 6.3e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.4 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6.2e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.4 | 30 | 0.0 | 27.333 | -27.333 [-27.833, -26.833] | 6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.4 | 30 | 3.312 | 3.825 | -0.512 [-0.540, -0.482] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.6 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.6 | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 6.3e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.6 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.6 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.6 | 30 | 3.409 | 3.825 | -0.416 [-0.447, -0.382] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.7 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.7 | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 6.3e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.7 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.7 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 4.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.7 | 30 | 3.38 | 3.825 | -0.444 [-0.475, -0.411] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 6.3e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 6.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 100.0 | 27.333 | +72.667 [+72.167, +73.167] | 4.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.409 | 3.825 | -0.415 [-0.445, -0.385] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 9.8e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 6.1e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.349 | 3.689 | -0.340 [-0.378, -0.300] | 1.9e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.3 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.3 | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.3 | 30 | 3.338 | 3.689 | -0.351 [-0.388, -0.315] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.4 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.4 | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.4 | 30 | 3.349 | 3.689 | -0.341 [-0.389, -0.293] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.6 | 30 | 0.958 | 0.882 | +0.076 [+0.069, +0.083] | 4.9e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.6 | 30 | 0.999 | 0.885 | +0.113 [+0.108, +0.119] | 2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.6 | 30 | 0.033 | 6.167 | -6.133 [-6.333, -5.933] | 2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.6 | 30 | 0.033 | 7.167 | -7.133 [-7.333, -6.933] | 2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.6 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.6 | 30 | 41.367 | 0.0 | +41.367 [+40.833, +41.900] | 6e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.6 | 30 | 3.453 | 3.689 | -0.236 [-0.282, -0.190] | 9.3e-09 | -0.99 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.7 | 30 | 1.0 | 0.882 | +0.118 [+0.116, +0.121] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.7 | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.7 | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.7 | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.7 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.7 | 30 | 45.0 | 0.0 | +45.000 [+45.000, +45.000] | 1.7e-07 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.7 | 30 | 3.451 | 3.689 | -0.238 [-0.277, -0.198] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.882 | +0.118 [+0.116, +0.121] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 45.0 | 0.0 | +45.000 [+45.000, +45.000] | 1.7e-07 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.466 | 3.689 | -0.224 [-0.259, -0.189] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 3.9e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 9.2e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 1.6e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.315 | 4.112 | -0.796 [-1.034, -0.589] | 1.9e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.3 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.3 | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.3 | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.3 | 30 | 3.321 | 4.112 | -0.791 [-1.032, -0.584] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.4 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.4 | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.4 | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.4 | 30 | 3.297 | 4.112 | -0.815 [-1.051, -0.607] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.6 | 30 | 0.323 | 0.814 | -0.490 [-0.514, -0.467] | 4.9e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.6 | 30 | 0.461 | 0.9 | -0.439 [-0.471, -0.407] | 2.7e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.6 | 30 | 3.775 | 7.65 | -3.875 [-4.558, -3.150] | 4.1e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.6 | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.6 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 4.1e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.6 | 30 | 17.5 | 73.667 | -56.167 [-58.400, -53.800] | 6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.6 | 30 | 3.429 | 4.112 | -0.683 [-0.914, -0.484] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.7 | 30 | 1.0 | 0.814 | +0.186 [+0.181, +0.192] | 2.9e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.7 | 30 | 1.0 | 0.9 | +0.100 [+0.093, +0.107] | 2.6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.7 | 30 | 0.0 | 3.175 | -3.175 [-3.325, -3.025] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.7 | 30 | 0.0 | 4.225 | -4.225 [-4.375, -4.075] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.7 | 30 | 0.0 | 7.65 | -7.650 [-7.775, -7.525] | 4.1e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.7 | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.7 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 4.1e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.7 | 30 | 90.0 | 73.667 | +16.333 [+15.067, +17.767] | 4.5e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.7 | 30 | 3.497 | 4.112 | -0.615 [-0.850, -0.413] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.814 | +0.186 [+0.181, +0.192] | 2.9e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.9 | +0.100 [+0.093, +0.107] | 2.6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 3.175 | -3.175 [-3.325, -3.025] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 4.225 | -4.225 [-4.375, -4.075] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 7.65 | -7.650 [-7.775, -7.525] | 4.1e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 4.1e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 90.0 | 73.667 | +16.333 [+15.067, +17.767] | 4.5e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.481 | 4.112 | -0.630 [-0.865, -0.428] | 7.5e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.33 | 0.749 | -0.419 [-0.436, -0.402] | 1e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.469 | 0.819 | -0.350 [-0.378, -0.321] | 1e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt | 30 | 3.483 | 4.492 | -1.008 [-1.500, -0.483] | 0.0054 | -0.70 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt | 30 | 3.483 | 5.167 | -1.683 [-2.175, -1.150] | 0.00021 | -0.86 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 3.483 | 7.558 | -4.075 [-4.567, -3.550] | 1e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 5.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 6.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 13.9 | 52.167 | -38.267 [-39.100, -37.400] | 1.6e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.378 | 4.912 | -1.535 [-1.591, -1.480] | 1.9e-08 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.3 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.3 | 30 | 0.0 | 0.819 | -0.819 [-0.824, -0.814] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.3 | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.3 | 30 | 3.342 | 4.912 | -1.570 [-1.629, -1.512] | 7.5e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.4 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.3e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.4 | 30 | 0.0 | 0.819 | -0.819 [-0.824, -0.814] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.4 | 30 | 0.0 | 52.167 | -52.167 [-52.633, -51.700] | 6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.4 | 30 | 3.324 | 4.912 | -1.588 [-1.642, -1.532] | 7.5e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.6 | 30 | 1.0 | 0.749 | +0.251 [+0.248, +0.254] | 4.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.6 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 2.7e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.6 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.6 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 2.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.6 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 4.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.6 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.6 | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.6 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.6 | 30 | 70.0 | 52.167 | +17.833 [+17.367, +18.300] | 6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.6 | 30 | 3.452 | 4.912 | -1.460 [-1.514, -1.404] | 7.5e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.7 | 30 | 1.0 | 0.749 | +0.251 [+0.248, +0.254] | 2.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.7 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 2.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.7 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.7 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.7 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 4.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.7 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.7 | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.7 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.7 | 30 | 70.0 | 52.167 | +17.833 [+17.367, +18.300] | 4.5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.7 | 30 | 3.47 | 4.912 | -1.442 [-1.494, -1.388] | 7.5e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 1.0 | 0.749 | +0.251 [+0.248, +0.254] | 2.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 2.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 4.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.8 | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 70.0 | 52.167 | +17.833 [+17.367, +18.300] | 4.5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.441 | 4.912 | -1.471 [-1.523, -1.419] | 7.5e-09 | -1.00 |
| sweep:campaign:0.20|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| sweep:campaign:0.20|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.796 | -0.796 [-0.805, -0.787] | 3.5e-06 | -1.00 |
| sweep:campaign:0.20|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.695 | 3.751 | -0.056 [-0.095, -0.017] | 0.015 | -0.50 |
| sweep:campaign:0.25|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| sweep:campaign:0.25|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.87 | -0.870 [-0.876, -0.864] | 1.7e-06 | -1.00 |
| sweep:campaign:0.25|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 45.833 | -45.833 [-48.633, -42.867] | 7.1e-06 | -1.00 |
| sweep:campaign:0.25|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.698 | 3.837 | -0.140 [-0.173, -0.108] | 1.1e-07 | -0.98 |
| sweep:campaign:0.30|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| sweep:campaign:0.30|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 3.5e-06 | -1.00 |
| sweep:campaign:0.30|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 7.1e-06 | -1.00 |
| sweep:campaign:0.30|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.696 | 4.126 | -0.430 [-0.658, -0.236] | 1.8e-07 | -0.97 |
| sweep:campaign:0.35|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| sweep:campaign:0.35|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.918 | -0.918 [-0.921, -0.913] | 1.2e-06 | -1.00 |
| sweep:campaign:0.35|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 77.7 | -77.700 [-78.233, -77.167] | 7.1e-06 | -1.00 |
| sweep:campaign:0.35|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.711 | 4.064 | -0.354 [-0.536, -0.190] | 9.7e-06 | -0.88 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.542 | 1.0 | -0.458 [-0.567, -0.358] | 4.9e-06 | -1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|device_f1 | no_sharing | 27 | 0.72 | 1.0 | -0.280 [-0.359, -0.204] | 4.9e-05 | -1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 27 | 0.199 | 0.809 | -0.611 [-0.651, -0.569] | 2.8e-05 | -1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.161 | 0.889 | -0.727 [-0.764, -0.690] | 3.5e-06 | -1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 29 | 15.753 | 3.383 | +12.365 [+11.382, +13.428] | 1.3e-05 | +1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 27 | 17.957 | 4.508 | +13.475 [+12.784, +14.170] | 2.8e-05 | +1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 80.9 | -80.900 [-81.300, -80.467] | 7.1e-06 | -1.00 |
| sweep:campaign:0.40|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.75 | 3.858 | -0.109 [-0.140, -0.077] | 2.3e-06 | -0.92 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.704 | 0.829 | -0.125 [-0.127, -0.123] | 3.5e-06 | -1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.729 | 0.922 | -0.193 [-0.196, -0.191] | 2.3e-06 | -1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 5.1 | 3.0 | +2.100 [+2.042, +2.167] | 3.5e-06 | +1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 8.1 | 3.75 | +4.350 [+4.292, +4.417] | 3.5e-06 | +1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 28 | 16.36 | 5.0 | +11.360 [+10.458, +12.286] | 1.9e-05 | +1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 28 | 8.265 | 1.25 | +7.015 [+6.110, +7.946] | 1.9e-05 | +1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 11.9 | 86.0 | -74.100 [-76.267, -71.900] | 7.1e-06 | -1.00 |
| sweep:campaign:0.50|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.795 | 3.86 | -0.065 [-0.106, -0.024] | 0.014 | -0.55 |
| sweep:duty:1:10:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.806 | 3.656 | +0.150 [+0.122, +0.180] | 1.1e-08 | +1.00 |
| sweep:duty:1:2:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.904 | 3.729 | +0.175 [+0.149, +0.201] | 1.1e-08 | +1.00 |
| sweep:duty:1:3:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.811 | 3.638 | +0.173 [+0.150, +0.197] | 1.1e-08 | +1.00 |
| sweep:duty:1:5:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 3.836 | 3.645 | +0.191 [+0.165, +0.215] | 1.1e-08 | +1.00 |
| sweep:duty:2:5:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 5.693 | 5.559 | +0.135 [+0.104, +0.165] | 3.5e-08 | +0.97 |
| sweep:duty:3:5:0.60|op=absent|adj=oracle|noise=gaussian|tick_f1 | beta_reputation | 30 | 0.708 | 0.713 | -0.005 [-0.005, -0.005] | 2.8e-06 | -1.00 |
| sweep:duty:3:5:0.60|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | beta_reputation | 30 | 9.667 | 7.833 | +1.833 [+1.067, +2.667] | 0.00059 | +1.00 |
| sweep:duty:3:5:0.60|op=absent|adj=oracle|noise=gaussian|containment_mean | beta_reputation | 30 | 4.333 | 2.5 | +1.833 [+1.067, +2.667] | 0.00059 | +1.00 |
| sweep:duty:3:5:0.60|op=absent|adj=oracle|noise=gaussian|disruptive_actions | beta_reputation | 30 | 63.967 | 84.167 | -20.200 [-21.300, -19.133] | 1e-05 | -1.00 |
| sweep:duty:3:5:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | beta_reputation | 30 | 4.029 | 3.852 | +0.176 [+0.158, +0.194] | 1.1e-08 | +1.00 |
| sweep:lowslow:0.30|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.3 | 3.631 | -0.331 [-0.355, -0.309] | 1.9e-08 | -1.00 |
| sweep:lowslow:0.40|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.306 | 3.597 | -0.291 [-0.320, -0.257] | 1.9e-08 | -1.00 |
| sweep:lowslow:0.50|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.315 | 3.634 | -0.318 [-0.346, -0.292] | 1.9e-08 | -1.00 |
| sweep:lowslow:0.60|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.0 | 0.867 | -0.867 [-0.967, -0.733] | 2.1e-06 | -1.00 |
| sweep:lowslow:0.60|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.0 | 0.393 | -0.393 [-0.469, -0.316] | 1.1e-05 | -1.00 |
| sweep:lowslow:0.60|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 0.0 | 7.6 | -7.600 [-10.400, -5.100] | 4e-05 | -1.00 |
| sweep:lowslow:0.60|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.343 | 4.525 | -1.182 [-1.464, -0.913] | 1.9e-08 | -1.00 |
| sweep:lowslow:0.70|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 9.8e-07 | -1.00 |
| sweep:lowslow:0.70|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 6.1e-06 | -1.00 |
| sweep:lowslow:0.70|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.321 | 3.771 | -0.450 [-0.482, -0.419] | 1.9e-08 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt | 30 | 0.309 | 0.905 | -0.596 [-0.629, -0.561] | 1e-05 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.444 | 0.927 | -0.482 [-0.530, -0.431] | 1e-05 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt | 30 | 4.0 | 11.1 | -7.100 [-8.400, -5.700] | 1.6e-05 | -0.97 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt | 30 | 0.0 | 5.8 | -5.800 [-6.333, -5.300] | 6.7e-06 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt | 26 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 2e-06 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 8.4 | 34.4 | -26.000 [-27.200, -24.700] | 1.6e-05 | -1.00 |
| sweep:lowslow:0.80|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.379 | 3.822 | -0.443 [-0.468, -0.416] | 1.9e-08 | -1.00 |

Only comparisons significant after Holm correction are listed; all 616 are in `comparisons.csv`.
