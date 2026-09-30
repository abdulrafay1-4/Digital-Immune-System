# Experiment report: `fairness`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "fairness",
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
  "git_commit": "0f8d7c3563210f98016565104c1186b633797a58",
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
| r1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| r3 | op=absent|adj=oracle|noise=correlated | binary_zt@0.8+brake | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| r3 | op=absent|adj=oracle|noise=diurnal | binary_zt@0.8+brake | 30 | — | 0.026 [0.023, 0.030] | — | — | — | — | 0.026 [0.023, 0.030] | 2.3 [2.133, 2.500] |
| r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 60 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| r3 | op=absent|adj=oracle|noise=heavy_tail | binary_zt@0.8+brake | 30 | — | 0.084 [0.073, 0.095] | — | — | — | — | 0.084 [0.073, 0.095] | 5.3333 [4.767, 5.933] |
| r3 | op=absent|adj=oracle|noise=ton_iot | binary_zt@0.8+brake | 30 | — | 0.364 [0.337, 0.391] | — | — | — | — | 0.364 [0.337, 0.391] | 23.5 [21.800, 25.100] |
| r4 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.0 [8.000, 8.000] |
| r5 | op=absent|adj=oracle|noise=correlated | binary_zt@0.8+brake | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1 [0.100, 0.100] | 25.0 [25.000, 25.000] |
| r5 | op=absent|adj=oracle|noise=diurnal | binary_zt@0.8+brake | 30 | — | 0.4033 [0.401, 0.406] | — | — | — | — | 0.1047 [0.101, 0.108] | 25.3 [25.133, 25.500] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 90.9667 [90.033, 91.933] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt+brake | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1273 [0.123, 0.133] | 25.0 [25.000, 25.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 60 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1 [0.100, 0.100] | 25.0 [25.000, 25.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full | 60 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.159, 0.177] | 27.3333 [26.967, 27.700] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest | 30 | — | 0.7213 [0.705, 0.740] | — | — | — | — | 0.7213 [0.705, 0.740] | 136.9667 [134.999, 139.100] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | — | 0.308 [0.291, 0.325] | — | — | — | — | 0.308 [0.291, 0.325] | 21.4 [20.167, 22.533] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.005 | 30 | — | 0.5713 [0.553, 0.591] | — | — | — | — | 0.5713 [0.553, 0.591] | 117.4333 [116.100, 118.901] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.02 | 30 | — | 0.878 [0.863, 0.892] | — | — | — | — | 0.878 [0.863, 0.892] | 178.9667 [175.999, 181.800] |
| r5 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.05 | 30 | — | 0.9887 [0.984, 0.993] | — | — | — | — | 0.9887 [0.984, 0.993] | 283.3 [279.667, 287.033] |
| r5 | op=absent|adj=oracle|noise=heavy_tail | binary_zt@0.8+brake | 30 | — | 0.4547 [0.443, 0.467] | — | — | — | — | 0.1807 [0.169, 0.193] | 29.5667 [28.900, 30.267] |
| r5 | op=absent|adj=oracle|noise=ton_iot | binary_zt@0.8+brake | 30 | — | 0.6753 [0.653, 0.699] | — | — | — | — | 0.4887 [0.461, 0.514] | 51.8 [49.966, 53.533] |
| r6 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 91.1333 [90.133, 92.267] |
| r6 | op=absent|adj=oracle|noise=gaussian | binary_zt+brake | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2507 [0.243, 0.259] | 50.0 [50.000, 50.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2 [0.200, 0.200] | 50.0 [50.000, 50.000] |
| r6 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2973 [0.289, 0.306] | 52.1667 [51.667, 52.700] |
| s1 | op=absent|adj=oracle|noise=correlated | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 45.0 [45.000, 45.000] |
| s1 | op=absent|adj=oracle|noise=diurnal | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0061 [0.003, 0.010] | 0.9056 [0.850, 0.956] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0061 [0.003, 0.010] | 45.3 [45.133, 45.500] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt+brake | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.5 [3.000, 42.000] | 0.0067 [0.000, 0.018] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 0.1 [0.000, 0.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 45.0 [45.000, 45.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 60 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [7.033, 7.317] | 0.8852 [0.882, 0.888] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | isolation_forest | 30 | 1.0 [1.000, 1.000] | 0.434 [0.407, 0.461] | 0.0881 [0.083, 0.093] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.434 [0.407, 0.461] | 72.7333 [70.667, 74.800] |
| s1 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | 1.0 [1.000, 1.000] | 0.0667 [0.055, 0.079] | 0.4198 [0.371, 0.482] | 9.4 [6.667, 12.500] | 0.2311 [0.192, 0.270] | 0.0 [0.000, 0.000] | 0.0667 [0.055, 0.079] | 7.3 [6.300, 8.300] |
| s1 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.005 | 30 | 1.0 [1.000, 1.000] | 0.2313 [0.212, 0.250] | 0.1566 [0.145, 0.170] | 0.0333 [0.000, 0.100] | 0.9993 [0.998, 1.000] | 0.0 [0.000, 0.000] | 0.2313 [0.212, 0.250] | 56.3667 [55.032, 57.667] |
| s1 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.02 | 30 | 1.0 [1.000, 1.000] | 0.6925 [0.671, 0.714] | 0.0561 [0.054, 0.058] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.069 [0.000, 0.207] | 0.6925 [0.671, 0.714] | 104.2333 [101.100, 107.168] |
| s1 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.05 | 30 | 1.0 [1.000, 1.000] | 0.9442 [0.930, 0.956] | 0.0415 [0.041, 0.042] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.2759 [0.034, 0.552] | 0.9442 [0.930, 0.956] | 182.9667 [179.199, 186.600] |
| s1 | op=absent|adj=oracle|noise=heavy_tail | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0653 [0.054, 0.076] | 0.4287 [0.375, 0.489] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0653 [0.054, 0.076] | 48.2667 [47.733, 48.833] |
| s1 | op=absent|adj=oracle|noise=ton_iot | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.351 [0.323, 0.378] | 0.1088 [0.101, 0.118] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.351 [0.323, 0.378] | 66.1667 [64.500, 67.800] |
| s2 | op=absent|adj=oracle|noise=correlated | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=diurnal | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt+brake | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 90.0 [90.000, 90.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=heavy_tail | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0399 [0.030, 0.050] | 0.8283 [0.789, 0.867] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0399 [0.030, 0.050] | 91.8333 [91.333, 92.333] |
| s2 | op=absent|adj=oracle|noise=ton_iot | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.25 [0.227, 0.274] | 0.4206 [0.398, 0.444] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0333 [0.000, 0.083] | 0.25 [0.227, 0.274] | 102.6333 [101.567, 103.700] |
| s3 | op=absent|adj=oracle|noise=correlated | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=diurnal | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0065 [0.003, 0.011] | 0.9674 [0.947, 0.985] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0065 [0.003, 0.011] | 70.3 [70.133, 70.500] |
| s3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 70.0 [70.000, 70.000] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | isolation_forest | 30 | 1.0 [1.000, 1.000] | 0.4804 [0.453, 0.509] | 0.2701 [0.258, 0.283] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.1 [1.008, 3.434] | 0.4804 [0.453, 0.509] | 101.9 [99.767, 104.101] |
| s3 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.002 | 30 | 0.9833 [0.958, 1.000] | 0.0768 [0.064, 0.090] | 0.6993 [0.664, 0.740] | 3.3361 [2.811, 3.875] | 0.4305 [0.402, 0.460] | 0.2667 [0.000, 0.775] | 0.0768 [0.064, 0.090] | 17.0333 [15.900, 18.267] |
| s3 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.005 | 30 | 1.0 [1.000, 1.000] | 0.2587 [0.237, 0.280] | 0.4105 [0.389, 0.434] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.9417 [0.316, 1.733] | 0.2587 [0.237, 0.280] | 84.8667 [83.467, 86.267] |
| s3 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.02 | 30 | 1.0 [1.000, 1.000] | 0.7413 [0.720, 0.760] | 0.1909 [0.187, 0.196] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.9583 [4.300, 7.667] | 0.7413 [0.720, 0.760] | 138.2667 [135.133, 141.167] |
| s3 | op=absent|adj=oracle|noise=gaussian | isolation_forest@0.05 | 30 | 1.0 [1.000, 1.000] | 0.9659 [0.958, 0.974] | 0.1526 [0.152, 0.154] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 12.3917 [10.808, 14.017] | 0.9659 [0.958, 0.974] | 229.7 [226.633, 232.800] |
| s3 | op=absent|adj=oracle|noise=heavy_tail | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.0783 [0.066, 0.091] | 0.704 [0.669, 0.741] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.6167 [0.033, 1.484] | 0.0783 [0.066, 0.091] | 73.8667 [73.233, 74.467] |
| s3 | op=absent|adj=oracle|noise=ton_iot | binary_zt@0.8+brake | 30 | 1.0 [1.000, 1.000] | 0.3957 [0.367, 0.423] | 0.3119 [0.297, 0.329] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.925 [1.508, 4.320] | 0.3957 [0.367, 0.423] | 94.4 [92.567, 96.034] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 5.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 6.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 90.967 | 27.333 | +63.633 [+62.499, +64.833] | 6.5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.611 | 3.828 | -0.217 [-0.289, -0.136] | 2.7e-05 | -0.81 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt+brake | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt+brake | 30 | 0.127 | 0.169 | -0.041 [-0.053, -0.029] | 5.8e-05 | -0.91 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt+brake | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 8.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt+brake | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 6.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt+brake | 30 | 3.504 | 3.828 | -0.324 [-0.366, -0.280] | 7.5e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8+brake | 30 | 0.0 | 10.413 | -10.413 [-10.452, -10.377] | 3.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8+brake | 30 | 0.1 | 0.169 | -0.069 [-0.081, -0.056] | 8.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8+brake | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 1.1e-05 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8+brake | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8+brake | 30 | 3.449 | 3.828 | -0.378 [-0.414, -0.340] | 9.3e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest | 30 | 0.721 | 0.4 | +0.321 [+0.304, +0.339] | 4.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest | 30 | 16.396 | 10.413 | +5.982 [+4.625, +7.308] | 3.3e-06 | +0.98 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest | 30 | 0.721 | 0.169 | +0.553 [+0.529, +0.578] | 5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest | 30 | 136.967 | 27.333 | +109.633 [+107.533, +111.833] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest | 30 | 136.967 | 27.333 | +109.633 [+107.533, +111.833] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest | 30 | 10.628 | 3.828 | +6.800 [+6.723, +6.864] | 5.6e-09 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.308 | 0.4 | -0.092 [-0.109, -0.075] | 4.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.002 | 30 | 2.657 | 10.413 | -7.757 [-8.373, -7.115] | 1.9e-09 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.308 | 0.169 | +0.139 [+0.118, +0.160] | 4.6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 21.4 | 27.333 | -5.933 [-7.167, -4.800] | 4.8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 21.4 | 27.333 | -5.933 [-7.167, -4.800] | 4.9e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.975 | 3.828 | +7.147 [+7.034, +7.260] | 5.6e-09 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.005 | 30 | 0.571 | 0.4 | +0.171 [+0.153, +0.189] | 4.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.005 | 30 | 9.14 | 10.413 | -1.273 [-2.226, -0.342] | 0.028 | -0.46 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.005 | 30 | 0.571 | 0.169 | +0.403 [+0.379, +0.427] | 4.9e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.005 | 30 | 117.433 | 27.333 | +90.100 [+88.700, +91.633] | 5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.005 | 30 | 117.433 | 27.333 | +90.100 [+88.700, +91.633] | 5e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.005 | 30 | 11.177 | 3.828 | +7.349 [+7.190, +7.525] | 5.6e-09 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.02 | 30 | 0.878 | 0.4 | +0.478 [+0.463, +0.492] | 4.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.02 | 30 | 29.053 | 10.413 | +18.639 [+16.864, +20.297] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.02 | 30 | 0.878 | 0.169 | +0.709 [+0.687, +0.731] | 4.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.02 | 30 | 178.967 | 27.333 | +151.633 [+148.533, +154.533] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.02 | 30 | 178.967 | 27.333 | +151.633 [+148.533, +154.533] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.02 | 30 | 10.875 | 3.828 | +7.048 [+6.960, +7.157] | 5.6e-09 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.05 | 30 | 0.989 | 0.4 | +0.589 [+0.584, +0.593] | 2.8e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | isolation_forest@0.05 | 30 | 44.464 | 10.413 | +34.050 [+32.354, +35.740] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.05 | 30 | 0.989 | 0.169 | +0.820 [+0.806, +0.835] | 4.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.05 | 30 | 283.3 | 27.333 | +255.967 [+252.400, +259.733] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.05 | 30 | 283.3 | 27.333 | +255.967 [+252.400, +259.733] | 5.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.05 | 30 | 11.158 | 3.828 | +7.331 [+7.091, +7.639] | 5.6e-09 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt | 30 | 0.4 | 0.297 | +0.103 [+0.093, +0.111] | 5.9e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt | 30 | 91.133 | 52.167 | +38.967 [+37.867, +40.200] | 6.5e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 91.133 | 52.167 | +38.967 [+37.867, +40.200] | 6.5e-06 | +1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.463 | 5.507 | -2.045 [-2.224, -1.857] | 7.5e-09 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt+brake | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt+brake | 30 | 0.251 | 0.297 | -0.047 [-0.057, -0.036] | 1.4e-05 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt+brake | 30 | 50.0 | 52.167 | -2.167 [-2.700, -1.633] | 8.5e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt+brake | 30 | 50.0 | 52.167 | -2.167 [-2.700, -1.633] | 6.5e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt+brake | 30 | 3.471 | 5.507 | -2.036 [-2.217, -1.851] | 7.5e-09 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8+brake | 30 | 0.0 | 10.413 | -10.413 [-10.457, -10.373] | 3.1e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8+brake | 30 | 0.2 | 0.297 | -0.097 [-0.107, -0.089] | 7.4e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8+brake | 30 | 50.0 | 52.167 | -2.167 [-2.700, -1.633] | 1.1e-05 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8+brake | 30 | 50.0 | 52.167 | -2.167 [-2.700, -1.633] | 6e-06 | -1.00 |
| r6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8+brake | 30 | 3.461 | 5.507 | -2.046 [-2.224, -1.859] | 9.3e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 1.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 1.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.463 | 3.931 | -0.469 [-0.586, -0.360] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt+brake | 30 | 0.067 | 1.0 | -0.933 [-1.000, -0.833] | 1.2e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt+brake | 30 | 0.007 | 0.885 | -0.879 [-0.886, -0.869] | 1.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt+brake | 30 | 3.523 | 3.931 | -0.408 [-0.511, -0.322] | 7.5e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8+brake | 30 | 1.0 | 0.882 | +0.118 [+0.116, +0.121] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8+brake | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8+brake | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8+brake | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8+brake | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 1.3e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8+brake | 30 | 45.0 | 0.0 | +45.000 [+45.000, +45.000] | 2.2e-07 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8+brake | 30 | 3.524 | 3.931 | -0.407 [-0.513, -0.315] | 9.3e-09 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest | 30 | 0.434 | 0.0 | +0.434 [+0.408, +0.460] | 4.9e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest | 30 | 0.088 | 1.0 | -0.912 [-0.917, -0.907] | 3.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest | 30 | 0.766 | 0.882 | -0.115 [-0.129, -0.101] | 3.5e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 8.6e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest | 30 | 0.434 | 0.0 | +0.434 [+0.408, +0.460] | 5e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest | 30 | 27.567 | 0.0 | +27.567 [+25.567, +29.533] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest | 30 | 72.733 | 0.0 | +72.733 [+70.700, +74.733] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest | 30 | 10.665 | 3.931 | +6.734 [+6.630, +6.827] | 5.6e-09 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.067 | 0.0 | +0.067 [+0.056, +0.078] | 4.6e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.002 | 30 | 0.42 | 1.0 | -0.580 [-0.630, -0.521] | 3.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.002 | 30 | 0.146 | 0.882 | -0.735 [-0.758, -0.712] | 3.5e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.002 | 30 | 0.231 | 0.885 | -0.654 [-0.693, -0.615] | 3.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.002 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 8.6e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.067 | 0.0 | +0.067 [+0.056, +0.078] | 4.6e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 3.4 | 0.0 | +3.400 [+2.800, +4.033] | 4.8e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 7.3 | 0.0 | +7.300 [+6.300, +8.333] | 4.9e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 10.872 | 3.931 | +6.941 [+6.760, +7.115] | 5.6e-09 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.005 | 30 | 0.231 | 0.0 | +0.231 [+0.212, +0.250] | 4.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.005 | 30 | 0.157 | 1.0 | -0.843 [-0.855, -0.830] | 3.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.005 | 30 | 0.857 | 0.882 | -0.025 [-0.036, -0.013] | 0.00083 | -0.70 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.005 | 30 | 0.999 | 0.885 | +0.114 [+0.110, +0.119] | 1.4e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.005 | 30 | 0.033 | 6.167 | -6.133 [-6.333, -5.933] | 1.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.005 | 30 | 0.033 | 7.167 | -7.133 [-7.333, -6.933] | 1.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.005 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 8.6e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.005 | 30 | 0.231 | 0.0 | +0.231 [+0.212, +0.250] | 4.9e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.005 | 30 | 12.9 | 0.0 | +12.900 [+11.733, +14.100] | 5e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.005 | 30 | 56.367 | 0.0 | +56.367 [+55.067, +57.733] | 5e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.005 | 30 | 10.664 | 3.931 | +6.733 [+6.640, +6.816] | 5.6e-09 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.02 | 30 | 0.693 | 0.0 | +0.693 [+0.670, +0.714] | 4.4e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.02 | 30 | 0.056 | 1.0 | -0.944 [-0.946, -0.942] | 3.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.02 | 30 | 0.605 | 0.882 | -0.276 [-0.289, -0.264] | 3.4e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.02 | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.02 | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.02 | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.02 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 8.6e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.02 | 30 | 0.693 | 0.0 | +0.693 [+0.670, +0.714] | 4.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.02 | 30 | 58.8 | 0.0 | +58.800 [+55.833, +61.633] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.02 | 30 | 104.233 | 0.0 | +104.233 [+101.233, +107.133] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.02 | 30 | 11.171 | 3.931 | +7.239 [+7.001, +7.505] | 5.6e-09 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.05 | 30 | 0.944 | 0.0 | +0.944 [+0.930, +0.957] | 2.8e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.05 | 30 | 0.041 | 1.0 | -0.959 [-0.959, -0.958] | 2.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.05 | 30 | 0.396 | 0.882 | -0.486 [-0.493, -0.478] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.05 | 30 | 1.0 | 0.885 | +0.115 [+0.110, +0.119] | 1.2e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.05 | 30 | 0.0 | 6.167 | -6.167 [-6.367, -5.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.05 | 30 | 0.0 | 7.167 | -7.167 [-7.367, -6.967] | 1.2e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.05 | 30 | 0.0 | 4.0 | -4.000 [-4.000, -4.000] | 8.6e-08 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.05 | 30 | 0.944 | 0.0 | +0.944 [+0.930, +0.957] | 4.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.05 | 30 | 137.067 | 0.0 | +137.067 [+133.367, +140.533] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.05 | 30 | 182.967 | 0.0 | +182.967 [+179.200, +186.533] | 5.1e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.05 | 30 | 11.218 | 3.931 | +7.287 [+7.086, +7.497] | 5.6e-09 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 8.6e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 1.4e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6.5e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt | 30 | 3.373 | 4.329 | -0.956 [-1.280, -0.679] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt+brake | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 8.6e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt+brake | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 1.4e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt+brake | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 6.5e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt+brake | 30 | 3.358 | 4.329 | -0.971 [-1.281, -0.701] | 7.5e-09 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8+brake | 30 | 1.0 | 0.814 | +0.186 [+0.181, +0.192] | 2.9e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8+brake | 30 | 1.0 | 0.9 | +0.100 [+0.093, +0.107] | 2.6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8+brake | 30 | 0.0 | 3.175 | -3.175 [-3.325, -3.025] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8+brake | 30 | 0.0 | 4.225 | -4.225 [-4.375, -4.075] | 2.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8+brake | 30 | 0.0 | 7.65 | -7.650 [-7.775, -7.525] | 4.1e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8+brake | 30 | 0.0 | 3.425 | -3.425 [-3.508, -3.342] | 2.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8+brake | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 4.1e-07 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8+brake | 30 | 90.0 | 73.667 | +16.333 [+15.067, +17.767] | 6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8+brake | 30 | 3.509 | 4.329 | -0.821 [-1.136, -0.546] | 9.3e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8+brake | 30 | 1.0 | 0.749 | +0.251 [+0.248, +0.254] | 2.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8+brake | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 2.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8+brake | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8+brake | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8+brake | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 4.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8+brake | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | binary_zt@0.8+brake | 30 | 0.0 | 9.3 | -9.300 [-9.417, -9.183] | 3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8+brake | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8+brake | 30 | 70.0 | 52.167 | +17.833 [+17.367, +18.300] | 6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8+brake | 30 | 3.479 | 5.29 | -1.811 [-1.967, -1.684] | 9.3e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest | 30 | 0.48 | 0.0 | +0.480 [+0.451, +0.509] | 4.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest | 30 | 0.27 | 1.0 | -0.730 [-0.742, -0.717] | 3.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest | 30 | 0.815 | 0.749 | +0.067 [+0.055, +0.078] | 3.5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 1.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest | 30 | 2.1 | 9.3 | -7.200 [-8.333, -5.883] | 5.7e-06 | -0.98 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest | 30 | 0.48 | 0.0 | +0.480 [+0.451, +0.509] | 5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest | 30 | 30.067 | 0.0 | +30.067 [+28.033, +32.100] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest | 30 | 101.9 | 52.167 | +49.733 [+47.700, +51.867] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest | 30 | 11.095 | 5.29 | +5.805 [+5.547, +6.071] | 5.6e-09 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.002 | 30 | 0.077 | 0.0 | +0.077 [+0.064, +0.090] | 4.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.002 | 30 | 0.699 | 1.0 | -0.301 [-0.337, -0.261] | 3.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.002 | 30 | 0.298 | 0.749 | -0.451 [-0.472, -0.430] | 3.5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.002 | 30 | 0.43 | 0.819 | -0.389 [-0.419, -0.357] | 3.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.002 | 30 | 3.336 | 4.492 | -1.156 [-1.711, -0.583] | 0.0034 | -0.66 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.002 | 30 | 3.336 | 5.167 | -1.831 [-2.392, -1.256] | 6.1e-05 | -0.87 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest@0.002 | 30 | 3.336 | 7.558 | -4.222 [-4.775, -3.653] | 3.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest@0.002 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 1.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest@0.002 | 30 | 0.267 | 9.3 | -9.033 [-9.383, -8.458] | 2.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.002 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.002 | 30 | 0.077 | 0.0 | +0.077 [+0.064, +0.090] | 4.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.002 | 30 | 3.7 | 0.0 | +3.700 [+3.067, +4.367] | 4.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.002 | 30 | 17.033 | 52.167 | -35.133 [-36.467, -33.800] | 4.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.002 | 30 | 11.172 | 5.29 | +5.882 [+5.490, +6.293] | 5.6e-09 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.005 | 30 | 0.259 | 0.0 | +0.259 [+0.237, +0.280] | 4.7e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.005 | 30 | 0.41 | 1.0 | -0.590 [-0.611, -0.566] | 3.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.005 | 30 | 0.905 | 0.749 | +0.156 [+0.146, +0.165] | 3.5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.005 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.005 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.005 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest@0.005 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest@0.005 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 1.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest@0.005 | 30 | 0.942 | 9.3 | -8.358 [-9.017, -7.550] | 2.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.005 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.005 | 30 | 0.259 | 0.0 | +0.259 [+0.237, +0.280] | 4.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.005 | 30 | 14.0 | 0.0 | +14.000 [+12.800, +15.267] | 5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.005 | 30 | 84.867 | 52.167 | +32.700 [+31.400, +34.100] | 5e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.005 | 30 | 10.933 | 5.29 | +5.644 [+5.422, +5.859] | 5.6e-09 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.02 | 30 | 0.741 | 0.0 | +0.741 [+0.720, +0.760] | 4.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.02 | 30 | 0.191 | 1.0 | -0.809 [-0.813, -0.804] | 3.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.02 | 30 | 0.673 | 0.749 | -0.076 [-0.086, -0.064] | 3.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.02 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.02 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.02 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest@0.02 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest@0.02 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 1.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest@0.02 | 30 | 5.958 | 9.3 | -3.342 [-4.992, -1.650] | 0.0039 | -0.67 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.02 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.02 | 30 | 0.741 | 0.0 | +0.741 [+0.720, +0.760] | 4.7e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.02 | 30 | 64.167 | 0.0 | +64.167 [+61.300, +66.834] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.02 | 30 | 138.267 | 52.167 | +86.100 [+83.067, +88.933] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.02 | 30 | 11.176 | 5.29 | +5.886 [+5.663, +6.096] | 5.6e-09 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_fpr | isolation_forest@0.05 | 30 | 0.966 | 0.0 | +0.966 [+0.958, +0.974] | 2.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | isolation_forest@0.05 | 30 | 0.153 | 1.0 | -0.847 [-0.848, -0.846] | 2.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | isolation_forest@0.05 | 30 | 0.468 | 0.749 | -0.281 [-0.288, -0.275] | 3.7e-09 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | isolation_forest@0.05 | 30 | 1.0 | 0.819 | +0.181 [+0.176, +0.186] | 1.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | isolation_forest@0.05 | 30 | 0.0 | 4.492 | -4.492 [-4.583, -4.400] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | isolation_forest@0.05 | 30 | 0.0 | 5.167 | -5.167 [-5.258, -5.075] | 1.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | isolation_forest@0.05 | 30 | 0.0 | 7.558 | -7.558 [-7.650, -7.467] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | isolation_forest@0.05 | 30 | 0.0 | 2.392 | -2.392 [-2.450, -2.342] | 1.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | isolation_forest@0.05 | 30 | 12.392 | 9.3 | +3.092 [+1.442, +4.717] | 0.0023 | +0.68 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | isolation_forest@0.05 | 30 | 0.0 | 4.464 | -4.464 [-4.550, -4.381] | 1.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | isolation_forest@0.05 | 30 | 0.966 | 0.0 | +0.966 [+0.958, +0.974] | 4.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|availability_cost | isolation_forest@0.05 | 30 | 150.033 | 0.0 | +150.033 [+147.200, +152.700] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | isolation_forest@0.05 | 30 | 229.7 | 52.167 | +177.533 [+174.433, +180.567] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | isolation_forest@0.05 | 30 | 11.062 | 5.29 | +5.772 [+5.578, +5.966] | 5.6e-09 | +1.00 |

Only comparisons significant after Holm correction are listed; all 392 are in `comparisons.csv`.
