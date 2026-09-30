# Experiment report: `robustness`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "robustness",
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
    "tolerance"
  ],
  "merged_into_rows": 2610
}
```

## Means with bootstrap 95% CI

| scenario | variant | arm | runs | device_tpr | device_fpr | device_f1 | latency_response_mean | response_coverage | mttr_mean | false_restriction_rate | disruptive_actions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a12 | op=absent|adj=oracle|noise=gaussian | full[zeta=0] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.04 [0.040, 0.040] | — | — | — | — | 0.04 [0.040, 0.040] | 76.5667 [76.100, 77.000] |
| drop:r3 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.04 [0.040, 0.040] | — | — | — | — | 0.04 [0.040, 0.040] | 21.7 [21.533, 21.867] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0011 [0.000, 0.003] | 0.9889 [0.967, 1.000] | 20.3 [20.000, 20.700] | 0.7404 [0.735, 0.745] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0011 [0.000, 0.003] | 0.9889 [0.967, 1.000] | 17.2 [17.000, 17.500] | 0.7844 [0.780, 0.787] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 0.3333 [0.167, 0.500] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 34.0 [28.700, 39.102] | 0.1801 [0.093, 0.279] | — | 0.0 [0.000, 0.000] | 1.1333 [0.000, 2.467] |
| loss:0.01:a12 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.5333 [0.508, 0.560] | 0.1161 [0.111, 0.121] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0667 [0.000, 0.200] | 0.5333 [0.508, 0.560] | 69.0667 [67.767, 70.400] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 2.0 [2.000, 2.000] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 46.4667 [46.233, 46.667] |
| loss:0.01:r3 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.4633 [0.442, 0.485] | — | — | — | — | 0.4633 [0.442, 0.485] | 30.4333 [28.733, 32.133] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0167 [0.000, 0.042] | 0.9993 [0.998, 1.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 89.0667 [88.766, 89.367] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 10.2417 [10.083, 10.425] | 0.6337 [0.626, 0.641] | — | 0.0 [0.000, 0.000] | 45.6667 [44.400, 46.800] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.2417 [4.083, 4.400] | 0.8993 [0.892, 0.907] | — | 0.0 [0.000, 0.000] | 72.5667 [71.100, 73.900] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.075 [6.025, 6.125] | 0.3911 [0.386, 0.397] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | 11.7333 [11.567, 11.900] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0333 [3.008, 3.067] | 0.9541 [0.953, 0.955] | — | 0.0 [0.000, 0.000] | 88.9 [88.600, 89.233] |
| loss:0.01:s2 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.3159 [0.291, 0.341] | 0.3618 [0.344, 0.380] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0583 [0.000, 0.125] | 0.3159 [0.291, 0.341] | 107.7 [106.400, 109.033] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0069 [0.001, 0.014] | 0.9389 [0.883, 0.989] | 20.5667 [20.200, 21.000] | 0.7305 [0.721, 0.739] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0092 [0.002, 0.017] | 0.9222 [0.861, 0.978] | 17.9333 [17.400, 18.533] | 0.7695 [0.758, 0.779] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 0.7667 [0.600, 0.900] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 33.0 [26.779, 40.087] | 0.422 [0.318, 0.528] | — | 0.0 [0.000, 0.000] | 5.9667 [3.100, 9.033] |
| loss:0.05:a12 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.969 [0.959, 0.979] | 0.0665 [0.066, 0.067] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.2759 [0.000, 0.621] | 0.969 [0.959, 0.979] | 163.5333 [159.933, 167.201] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 1.9333 [1.833, 2.000] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.0053 [0.001, 0.012] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.008 [0.002, 0.017] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 44.5333 [43.967, 45.067] |
| loss:0.05:r3 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.9473 [0.931, 0.960] | — | — | — | — | 0.9473 [0.931, 0.960] | 148.8333 [144.366, 153.667] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.0417 [0.008, 0.083] | 0.9981 [0.996, 1.000] | 0.0667 [0.025, 0.117] | 0.0 [0.000, 0.000] | 85.6 [85.000, 86.200] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0029 [0.001, 0.006] | 0.9852 [0.970, 0.996] | 10.8667 [10.617, 11.117] | 0.6059 [0.595, 0.617] | — | 0.0 [0.000, 0.000] | 40.5667 [39.166, 41.967] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0029 [0.001, 0.006] | 0.9852 [0.970, 0.996] | 4.3583 [4.200, 4.517] | 0.8937 [0.887, 0.901] | — | 0.0 [0.000, 0.000] | 67.8667 [66.267, 69.334] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.325 [6.241, 6.417] | 0.3611 [0.353, 0.369] | 0.0667 [0.025, 0.117] | 0.0 [0.000, 0.000] | 10.8333 [10.600, 11.067] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.15 [3.083, 3.217] | 0.9489 [0.946, 0.952] | — | 0.0 [0.000, 0.000] | 84.4667 [83.867, 85.100] |
| loss:0.05:s2 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.8667 [0.845, 0.886] | 0.1677 [0.164, 0.172] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.3528 [0.214, 0.486] | 0.8667 [0.845, 0.886] | 183.1 [179.632, 186.733] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0023 [0.000, 0.006] | 0.9778 [0.944, 1.000] | 21.8667 [20.700, 23.400] | 0.7014 [0.677, 0.724] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0023 [0.000, 0.006] | 0.9778 [0.944, 1.000] | 19.2333 [18.066, 20.900] | 0.7418 [0.716, 0.765] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 0.9 [0.767, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 30.6296 [25.888, 35.631] | 0.5248 [0.433, 0.612] | — | 0.0 [0.000, 0.000] | 11.3333 [7.966, 14.667] |
| loss:0.1:a12 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 1.0 [1.000, 1.000] | 0.0645 [0.065, 0.065] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 1.0 [0.444, 1.593] | 1.0 [1.000, 1.000] | 280.3333 [275.933, 284.668] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 1.9 [1.767, 2.000] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | — | 0.0013 [0.000, 0.003] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.002 [0.000, 0.004] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 41.9333 [41.267, 42.600] |
| loss:0.1:r3 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | — | 0.9973 [0.995, 0.999] | — | — | — | — | 0.9973 [0.995, 0.999] | 293.0 [287.398, 298.601] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | binary_zt@0.8 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.125 [0.058, 0.200] | 0.993 [0.990, 0.996] | 0.1833 [0.108, 0.267] | 0.0 [0.000, 0.000] | 80.9 [79.867, 81.934] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | cusum@0.15:6.4 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 11.9667 [11.625, 12.308] | 0.557 [0.542, 0.572] | — | 0.0 [0.000, 0.000] | 33.1 [31.467, 34.700] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.6833 [4.475, 4.892] | 0.8793 [0.870, 0.889] | — | 0.0 [0.000, 0.000] | 61.4333 [59.600, 63.167] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | page_cusum@0.05:1.6 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.7417 [6.550, 6.950] | 0.3344 [0.324, 0.344] | 0.1833 [0.108, 0.267] | 0.0 [0.000, 0.000] | 10.0333 [9.733, 10.333] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | stopping_response | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.3417 [3.242, 3.442] | 0.9404 [0.936, 0.945] | — | 0.0 [0.000, 0.000] | 78.8 [77.833, 79.800] |
| loss:0.1:s2 | op=absent|adj=oracle|noise=gaussian | tolerance | 30 | 1.0 [1.000, 1.000] | 0.9855 [0.980, 0.991] | 0.15 [0.149, 0.151] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 0.7611 [0.528, 1.028] | 0.9855 [0.980, 0.991] | 273.8667 [269.033, 278.533] |
| r1 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.1 [0.100, 0.100] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r1 | op=absent|adj=oracle|noise=gaussian | full[zeta=0] | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r2 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 3.0 [3.000, 3.000] | 0.9667 [0.967, 0.967] | 16.6111 [16.500, 16.722] | 0.0 [0.000, 0.000] | 92.7667 [92.433, 93.067] |
| r2 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | 1.0 [1.000, 1.000] | 0.1064 [0.106, 0.106] | 0.5455 [0.545, 0.545] | 2.9 [2.767, 3.000] | 0.97 [0.967, 0.974] | 11.3667 [11.211, 11.511] | 0.0 [0.000, 0.000] | 92.4 [91.800, 93.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@20 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@3 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@40 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@5 | 30 | — | 0.0 [0.000, 0.000] | — | — | — | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 6.6 [6.367, 6.867] |
| r4 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 7.0 [7.000, 7.000] |
| r4 | op=absent|adj=oracle|noise=gaussian | penalty_healing@20 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 20.0667 [16.567, 23.533] |
| r4 | op=absent|adj=oracle|noise=gaussian | penalty_healing@3 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 8.1667 [7.500, 8.833] |
| r4 | op=absent|adj=oracle|noise=gaussian | penalty_healing@40 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 34.0667 [27.233, 40.867] |
| r4 | op=absent|adj=oracle|noise=gaussian | penalty_healing@5 | 30 | — | 0.02 [0.020, 0.020] | — | — | — | — | 0.02 [0.020, 0.020] | 9.5667 [8.567, 10.533] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1467 [0.137, 0.158] | 35.5333 [34.099, 37.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | penalty_healing@20 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2447 [0.225, 0.263] | 127.3333 [126.833, 127.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | penalty_healing@3 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2 [0.184, 0.216] | 42.3333 [41.833, 42.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | penalty_healing@40 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2593 [0.239, 0.279] | 227.3333 [226.833, 227.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | penalty_healing@5 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.212 [0.196, 0.227] | 52.3333 [51.833, 52.833] |
| r6 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2867 [0.274, 0.299] | 64.5333 [62.867, 66.233] |
| r6 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2967 [0.287, 0.306] | 52.1667 [51.667, 52.700] |
| r6 | op=absent|adj=oracle|noise=gaussian | penalty_healing@20 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2887 [0.273, 0.303] | 248.7667 [245.100, 251.600] |
| r6 | op=absent|adj=oracle|noise=gaussian | penalty_healing@3 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2813 [0.267, 0.295] | 81.6667 [80.900, 82.400] |
| r6 | op=absent|adj=oracle|noise=gaussian | penalty_healing@40 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2887 [0.273, 0.303] | 348.1667 [343.832, 351.534] |
| r6 | op=absent|adj=oracle|noise=gaussian | penalty_healing@5 | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.286 [0.271, 0.300] | 101.3333 [100.267, 102.267] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[zeta=0] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[zeta=0] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[zeta=0] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@20 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1917 [5.108, 5.275] | 0.8176 [0.813, 0.822] | 14.3667 [12.183, 16.817] | 0.0 [0.000, 0.000] | 67.9333 [63.866, 72.567] |
| s3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@3 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 10.1167 [9.650, 10.633] | 0.0 [0.000, 0.000] | 59.5333 [58.466, 60.733] |
| s3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@40 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1917 [5.108, 5.275] | 0.8176 [0.813, 0.822] | 9.1607 [9.054, 9.304] | 0.0 [0.000, 0.000] | 80.0667 [71.398, 89.900] |
| s3 | op=absent|adj=oracle|noise=gaussian | penalty_healing@5 | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 10.35 [9.750, 11.050] | 0.0 [0.000, 0.000] | 59.9333 [58.600, 61.401] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| drop:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 2.2e-06 | -1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.238 | 3.514 | -0.276 [-0.322, -0.210] | 1.8e-05 | -0.87 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 1.8 | 8.3 | -6.500 [-7.033, -5.967] | 5.2e-06 | -1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.611 | 3.514 | +0.097 [+0.074, +0.123] | 1.3e-07 | +0.98 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | page_cusum@0.05:1.6 | 30 | 0.0 | 0.02 | -0.020 [-0.020, -0.020] | 4.3e-07 | -1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 2.2e-06 | -1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.421 | 3.514 | -0.093 [-0.138, -0.044] | 0.0076 | -0.66 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response | 30 | 0.04 | 0.02 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.04 | 0.0 | +0.040 [+0.040, +0.040] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 76.567 | 0.0 | +76.567 [+76.133, +77.033] | 1.3e-05 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 76.567 | 0.0 | +76.567 [+76.133, +77.033] | 1.3e-05 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.719 | 3.514 | +0.206 [+0.121, +0.301] | 0.00011 | +0.83 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.04 | 0.02 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 30 | 0.0 | 8.3 | -8.300 [-8.467, -8.133] | 2.2e-06 | -1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.04 | 0.0 | +0.040 [+0.040, +0.040] | 4.3e-07 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 21.7 | 0.0 | +21.700 [+21.533, +21.867] | 5.5e-06 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 21.7 | 0.0 | +21.700 [+21.533, +21.867] | 5.5e-06 | +1.00 |
| drop:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.433 | 3.514 | -0.080 [-0.097, -0.065] | 1.9e-08 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.8 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.0 | 0.784 | -0.784 [-0.787, -0.780] | 6.1e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 2.125 | 2.246 | -0.120 [-0.227, -0.010] | 0.0071 | -0.55 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.74 | 0.784 | -0.044 [-0.047, -0.043] | 8.7e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 20.3 | 17.2 | +3.100 [+3.000, +3.300] | 4.1e-07 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | page_cusum@0.05:1.6 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.0 | 0.784 | -0.784 [-0.787, -0.780] | 6.1e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | stopping_response | 30 | 0.333 | 1.0 | -0.667 [-0.833, -0.500] | 6.7e-05 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.18 | 0.784 | -0.604 [-0.693, -0.506] | 5.4e-06 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | stopping_response | 10 | 34.0 | 14.2 | +19.700 [+13.800, +25.100] | 0.016 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 10 | 34.0 | 17.2 | +16.700 [+10.800, +22.100] | 0.007 | +0.96 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 2.143 | 2.246 | -0.103 [-0.166, -0.050] | 0.00062 | -0.77 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.533 | 0.001 | +0.532 [+0.507, +0.559] | 8.3e-06 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.116 | 0.989 | -0.873 [-0.888, -0.848] | 5.8e-06 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.784 | +0.216 [+0.213, +0.220] | 6.1e-07 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 14.2 | -14.200 [-14.500, -14.000] | 6.1e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 17.2 | -17.200 [-17.500, -17.000] | 6.1e-07 | -1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.533 | 0.0 | +0.533 [+0.509, +0.560] | 7.4e-06 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 21.8 | 0.0 | +21.800 [+20.467, +23.167] | 1.5e-05 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 69.067 | 0.0 | +69.067 [+67.800, +70.367] | 1.5e-05 | +1.00 |
| loss:0.01:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 2.141 | 2.246 | -0.105 [-0.166, -0.056] | 4.2e-05 | -0.84 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.0 | 8.433 | -8.433 [-8.633, -8.233] | 2.3e-06 | -1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 2.0 | 0.0 | +2.000 [+2.000, +2.000] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.349 | 3.585 | -0.235 [-0.363, -0.086] | 0.00051 | -0.74 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 1.833 | 8.433 | -6.600 [-7.167, -6.033] | 5.2e-06 | -1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.859 | 3.585 | +0.274 [+0.188, +0.367] | 1.9e-05 | +0.88 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 8.433 | -8.433 [-8.633, -8.233] | 2.3e-06 | -1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 46.467 | 0.0 | +46.467 [+46.233, +46.667] | 9.1e-06 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 46.467 | 0.0 | +46.467 [+46.233, +46.667] | 9.1e-06 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.781 | 3.585 | +0.197 [+0.061, +0.343] | 0.015 | +0.60 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.463 | 0.0 | +0.463 [+0.443, +0.485] | 8.3e-06 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.463 | 0.0 | +0.463 [+0.443, +0.485] | 7.4e-06 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 30.433 | 0.0 | +30.433 [+28.733, +32.167] | 1.5e-05 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 30.433 | 0.0 | +30.433 [+28.733, +32.167] | 1.5e-05 | +1.00 |
| loss:0.01:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.466 | 3.585 | -0.118 [-0.188, -0.059] | 1.9e-06 | -0.93 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 0.995 | 0.809 | +0.186 [+0.180, +0.191] | 1e-05 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.999 | 0.899 | +0.100 [+0.093, +0.107] | 4.3e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.017 | 3.183 | -3.167 [-3.333, -3.008] | 8.1e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.017 | 4.242 | -4.225 [-4.383, -4.058] | 8.5e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.017 | 7.75 | -7.733 [-7.883, -7.591] | 4.6e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 3.508 | -3.508 [-3.600, -3.417] | 4.2e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 1.2e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 89.067 | 72.567 | +16.500 [+15.200, +17.967] | 9.8e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.312 | 3.997 | -0.685 [-0.923, -0.475] | 1.9e-08 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | cusum@0.15:6.4 | 30 | 0.629 | 0.809 | -0.180 [-0.187, -0.174] | 8.6e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.634 | 0.899 | -0.266 [-0.275, -0.256] | 6.5e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | cusum@0.15:6.4 | 30 | 9.15 | 3.183 | +5.967 [+5.792, +6.142] | 9.3e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 10.242 | 4.242 | +6.000 [+5.808, +6.208] | 4.8e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | cusum@0.15:6.4 | 30 | 14.85 | 7.75 | +7.100 [+6.833, +7.392] | 5e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | cusum@0.15:6.4 | 30 | 4.608 | 3.508 | +1.100 [+0.883, +1.350] | 4.8e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 45.667 | 72.567 | -26.900 [-27.967, -25.867] | 1.6e-05 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | page_cusum@0.05:1.6 | 30 | 0.231 | 0.809 | -0.579 [-0.584, -0.573] | 8.6e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.391 | 0.899 | -0.508 [-0.517, -0.499] | 4.7e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | page_cusum@0.05:1.6 | 30 | 6.075 | 3.183 | +2.892 [+2.742, +3.042] | 8.4e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | page_cusum@0.05:1.6 | 30 | 6.075 | 4.242 | +1.833 [+1.692, +1.983] | 8.2e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | page_cusum@0.05:1.6 | 30 | 6.075 | 7.75 | -1.675 [-1.800, -1.550] | 4.6e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 3.508 | -3.508 [-3.600, -3.417] | 4.2e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | page_cusum@0.05:1.6 | 27 | 0.0 | 3.0 | -3.000 [-3.000, -3.000] | 1.2e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 11.733 | 72.567 | -60.833 [-62.167, -59.333] | 1.6e-05 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 30 | 0.843 | 0.809 | +0.034 [+0.029, +0.039] | 1e-05 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.954 | 0.899 | +0.055 [+0.047, +0.062] | 7.2e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 30 | 3.033 | 4.242 | -1.208 [-1.367, -1.050] | 8.6e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | stopping_response | 30 | 4.05 | 7.75 | -3.700 [-3.842, -3.558] | 9.1e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | stopping_response | 30 | 1.017 | 3.508 | -2.492 [-2.583, -2.400] | 8.2e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 88.9 | 72.567 | +16.333 [+15.067, +17.767] | 1.3e-05 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.316 | 0.0 | +0.316 [+0.293, +0.341] | 8.3e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.362 | 1.0 | -0.638 [-0.656, -0.621] | 5.8e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 30 | 0.911 | 0.809 | +0.102 [+0.093, +0.109] | 5.2e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.899 | +0.101 [+0.093, +0.108] | 4.3e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 3.183 | -3.183 [-3.342, -3.025] | 4e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 4.242 | -4.242 [-4.392, -4.083] | 4e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | tolerance | 30 | 0.0 | 7.75 | -7.750 [-7.892, -7.608] | 9.5e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | tolerance | 30 | 0.0 | 3.508 | -3.508 [-3.600, -3.417] | 8.5e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | tolerance | 27 | 0.058 | 3.0 | -2.935 [-3.000, -2.861] | 4e-06 | -1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.316 | 0.0 | +0.316 [+0.293, +0.341] | 7.4e-06 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 17.0 | 0.0 | +17.000 [+15.700, +18.367] | 1.5e-05 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 107.7 | 72.567 | +35.133 [+33.200, +37.300] | 1.5e-05 | +1.00 |
| loss:0.01:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.554 | 3.997 | -0.443 [-0.673, -0.236] | 1.9e-08 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.8 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.0 | 0.77 | -0.770 [-0.779, -0.758] | 2.9e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 1.925 | 2.104 | -0.179 [-0.191, -0.169] | 1.9e-08 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.73 | 0.77 | -0.039 [-0.044, -0.033] | 4.8e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 20.567 | 17.933 | +2.633 [+2.267, +2.933] | 1.4e-06 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 2.163 | 2.104 | +0.058 [+0.047, +0.069] | 9.2e-07 | +0.95 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | page_cusum@0.05:1.6 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.0 | 0.77 | -0.770 [-0.779, -0.758] | 2.9e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 15 | 0.071 | 0.052 | +0.028 [+0.015, +0.041] | 0.0052 | +0.88 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.422 | 0.77 | -0.348 [-0.460, -0.235] | 9.1e-05 | -0.90 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | stopping_response | 23 | 33.0 | 14.5 | +18.478 [+11.913, +25.566] | 0.00046 | +0.95 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 23 | 33.0 | 17.933 | +14.913 [+8.217, +22.175] | 0.0057 | +0.74 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 5.967 | 0.0 | +5.967 [+3.100, +9.067] | 0.0071 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 2.408 | 2.104 | +0.304 [+0.165, +0.463] | 3.1e-06 | +0.93 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.969 | 0.009 | +0.960 [+0.947, +0.972] | 8.3e-06 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.066 | 0.922 | -0.856 [-0.911, -0.795] | 5.8e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 17 | 0.448 | 0.052 | +0.394 [+0.375, +0.413] | 3.1e-05 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.77 | +0.230 [+0.221, +0.242] | 2.9e-06 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 14.5 | -14.500 [-14.900, -14.100] | 1.3e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 17.933 | -17.933 [-18.567, -17.400] | 2.5e-06 | -1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.969 | 0.0 | +0.969 [+0.959, +0.978] | 7.4e-06 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 114.867 | 0.0 | +114.867 [+111.300, +118.567] | 1.5e-05 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 163.533 | 0.0 | +163.533 [+159.933, +167.233] | 1.5e-05 | +1.00 |
| loss:0.05:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 2.19 | 2.104 | +0.086 [+0.063, +0.114] | 1.9e-08 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.02 | 0.008 | +0.012 [+0.003, +0.018] | 0.0016 | +0.71 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.067 | 8.9 | -8.833 [-9.367, -8.433] | 2.3e-06 | -1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 1.933 | 0.0 | +1.933 [+1.833, +2.000] | 8.1e-07 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 1.933 | 0.0 | +1.933 [+1.833, +2.000] | 8.1e-07 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.138 | 3.453 | -0.315 [-0.333, -0.299] | 1.9e-08 | -1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 2.333 | 8.9 | -6.567 [-7.234, -5.833] | 5.2e-06 | -1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.489 | 3.453 | +0.036 [+0.018, +0.051] | 0.0011 | +0.79 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.067 | 8.9 | -8.833 [-9.367, -8.433] | 2.3e-06 | -1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response | 30 | 0.02 | 0.008 | +0.012 [+0.003, +0.018] | 0.0014 | +0.71 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 44.533 | 0.0 | +44.533 [+43.967, +45.067] | 1.3e-05 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 44.533 | 0.0 | +44.533 [+43.967, +45.067] | 1.3e-05 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.947 | 0.008 | +0.939 [+0.917, +0.956] | 8.3e-06 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 29 | 28.655 | 8.9 | +19.793 [+14.103, +25.207] | 6e-05 | +0.89 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.947 | 0.0 | +0.947 [+0.931, +0.960] | 7.4e-06 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 148.833 | 0.0 | +148.833 [+144.233, +153.700] | 1.5e-05 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 148.833 | 0.0 | +148.833 [+144.233, +153.700] | 1.5e-05 | +1.00 |
| loss:0.05:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.481 | 3.453 | +0.027 [+0.005, +0.049] | 0.027 | +0.51 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 0.975 | 0.788 | +0.187 [+0.181, +0.193] | 1e-05 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.998 | 0.894 | +0.104 [+0.097, +0.112] | 4.3e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.042 | 3.242 | -3.200 [-3.392, -3.008] | 8.1e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.042 | 4.358 | -4.317 [-4.492, -4.133] | 8.5e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.042 | 8.075 | -8.033 [-8.233, -7.825] | 4.6e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 3.717 | -3.717 [-3.908, -3.542] | 4.2e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 25 | 0.067 | 3.0 | -2.920 [-2.970, -2.860] | 2.3e-05 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 85.6 | 67.867 | +17.733 [+16.433, +19.133] | 9.8e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.254 | 4.062 | -0.809 [-1.009, -0.622] | 1.9e-08 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | cusum@0.15:6.4 | 30 | 0.592 | 0.788 | -0.196 [-0.205, -0.187] | 1.1e-08 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.606 | 0.894 | -0.288 [-0.301, -0.275] | 6.5e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | cusum@0.15:6.4 | 30 | 9.592 | 3.242 | +6.350 [+6.092, +6.617] | 9.3e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 10.867 | 4.358 | +6.508 [+6.225, +6.808] | 4.8e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | cusum@0.15:6.4 | 30 | 15.625 | 8.075 | +7.550 [+7.258, +7.875] | 5e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | cusum@0.15:6.4 | 30 | 4.758 | 3.717 | +1.042 [+0.783, +1.300] | 9.7e-06 | +0.96 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 40.567 | 67.867 | -27.300 [-28.333, -26.267] | 1.6e-05 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | page_cusum@0.05:1.6 | 30 | 0.215 | 0.788 | -0.573 [-0.580, -0.566] | 8.6e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.361 | 0.894 | -0.533 [-0.543, -0.522] | 4.7e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | page_cusum@0.05:1.6 | 30 | 6.325 | 3.242 | +3.083 [+2.900, +3.267] | 8.4e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | page_cusum@0.05:1.6 | 30 | 6.325 | 4.358 | +1.967 [+1.800, +2.133] | 8.2e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | page_cusum@0.05:1.6 | 30 | 6.325 | 8.075 | -1.750 [-1.933, -1.567] | 4.6e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 3.717 | -3.717 [-3.908, -3.542] | 4.2e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | page_cusum@0.05:1.6 | 25 | 0.067 | 3.0 | -2.920 [-2.970, -2.860] | 2.3e-05 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 10.833 | 67.867 | -57.033 [-58.467, -55.533] | 1.6e-05 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.585 | 4.062 | -0.477 [-0.693, -0.277] | 0.0017 | -0.74 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 30 | 0.825 | 0.788 | +0.037 [+0.031, +0.043] | 1e-05 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.949 | 0.894 | +0.055 [+0.047, +0.062] | 7.2e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 30 | 3.15 | 4.358 | -1.208 [-1.367, -1.050] | 8.6e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | stopping_response | 30 | 4.2 | 8.075 | -3.875 [-4.083, -3.667] | 9.1e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | stopping_response | 30 | 1.05 | 3.717 | -2.667 [-2.850, -2.500] | 8.2e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 84.467 | 67.867 | +16.600 [+15.267, +17.967] | 1.3e-05 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.59 | 4.062 | -0.473 [-0.669, -0.289] | 8.3e-05 | -0.85 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.867 | 0.003 | +0.864 [+0.841, +0.884] | 8.3e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.168 | 0.985 | -0.818 [-0.831, -0.800] | 5.8e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 30 | 0.66 | 0.788 | -0.128 [-0.140, -0.116] | 1.1e-08 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.894 | +0.106 [+0.099, +0.113] | 4.3e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 3.242 | -3.242 [-3.417, -3.067] | 4e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 4.358 | -4.358 [-4.517, -4.200] | 4e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | tolerance | 30 | 0.0 | 8.075 | -8.075 [-8.267, -7.875] | 9.5e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | tolerance | 30 | 0.0 | 3.717 | -3.717 [-3.908, -3.542] | 8.5e-06 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | tolerance | 25 | 0.353 | 3.0 | -2.637 [-2.780, -2.487] | 5.1e-05 | -1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.867 | 0.0 | +0.867 [+0.846, +0.886] | 7.4e-06 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 89.233 | 0.0 | +89.233 [+85.466, +93.067] | 1.5e-05 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 183.1 | 67.867 | +115.233 [+111.433, +119.067] | 1.5e-05 | +1.00 |
| loss:0.05:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.559 | 4.062 | -0.503 [-0.705, -0.316] | 5.6e-07 | -0.96 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | binary_zt@0.8 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.0 | 0.742 | -0.742 [-0.764, -0.716] | 4.3e-06 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 1.865 | 2.097 | -0.232 [-0.300, -0.187] | 1.9e-08 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.701 | 0.742 | -0.040 [-0.048, -0.033] | 6.5e-06 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 21.867 | 19.233 | +2.633 [+2.100, +3.133] | 4.6e-06 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 2.161 | 2.097 | +0.065 [-0.028, +0.150] | 0.018 | +0.60 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|device_tpr | page_cusum@0.05:1.6 | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 2.6e-07 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.0 | 0.742 | -0.742 [-0.764, -0.716] | 4.3e-06 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 25 | 0.103 | 0.069 | +0.037 [+0.024, +0.051] | 0.00027 | +0.90 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.525 | 0.742 | -0.217 [-0.322, -0.118] | 0.00092 | -0.73 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | stopping_response | 27 | 30.63 | 15.0 | +15.519 [+10.444, +20.852] | 0.00016 | +0.94 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 27 | 30.63 | 19.233 | +11.148 [+5.296, +17.074] | 0.007 | +0.64 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 11.333 | 0.0 | +11.333 [+7.867, +14.767] | 0.00011 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 1.0 | 0.002 | +0.998 [+0.994, +1.000] | 9.1e-07 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.065 | 0.978 | -0.913 [-0.935, -0.880] | 6.1e-07 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 25 | 0.288 | 0.069 | +0.219 [+0.203, +0.233] | 2.4e-07 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.742 | +0.258 [+0.236, +0.284] | 4.3e-06 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 15.0 | -15.000 [-15.600, -14.500] | 2.3e-06 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 19.233 | -19.233 [-20.900, -18.033] | 3.8e-06 | -1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 4.3e-07 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 230.1 | 0.0 | +230.100 [+225.433, +234.567] | 1.5e-05 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 280.333 | 0.0 | +280.333 [+275.767, +284.733] | 1.5e-05 | +1.00 |
| loss:0.1:a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 2.162 | 2.097 | +0.066 [+0.001, +0.104] | 2.2e-05 | +0.87 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | binary_zt@0.8 | 30 | 0.02 | 0.002 | +0.018 [+0.016, +0.020] | 1.9e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | binary_zt@0.8 | 30 | 0.133 | 8.7 | -8.567 [-9.067, -7.833] | 2.3e-06 | -1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | binary_zt@0.8 | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | binary_zt@0.8 | 30 | 1.9 | 0.0 | +1.900 [+1.767, +2.000] | 1e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 1.9 | 0.0 | +1.900 [+1.767, +2.000] | 1e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.018 | 3.346 | -0.328 [-0.372, -0.293] | 1.9e-08 | -1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | cusum@0.15:6.4 | 30 | 1.9 | 8.7 | -6.800 [-7.467, -6.067] | 5.2e-06 | -1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | cusum@0.15:6.4 | 30 | 3.369 | 3.346 | +0.024 [-0.028, +0.063] | 0.022 | +0.58 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | page_cusum@0.05:1.6 | 30 | 0.133 | 8.7 | -8.567 [-9.067, -7.833] | 2.3e-06 | -1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | stopping_response | 30 | 0.02 | 0.002 | +0.018 [+0.016, +0.020] | 1.7e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | stopping_response | 30 | 0.02 | 0.0 | +0.020 [+0.020, +0.020] | 4.3e-07 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | stopping_response | 30 | 41.933 | 0.0 | +41.933 [+41.233, +42.600] | 1.3e-05 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 41.933 | 0.0 | +41.933 [+41.233, +42.600] | 1.3e-05 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.997 | 0.002 | +0.995 [+0.992, +0.998] | 3.2e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | tolerance | 28 | 39.321 | 8.7 | +30.714 [+26.429, +34.286] | 1.4e-05 | +0.99 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.997 | 0.0 | +0.997 [+0.995, +0.999] | 1.6e-06 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 293.0 | 0.0 | +293.000 [+287.500, +298.500] | 1.5e-05 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 293.0 | 0.0 | +293.000 [+287.500, +298.500] | 1.5e-05 | +1.00 |
| loss:0.1:r3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | tolerance | 30 | 3.468 | 3.346 | +0.122 [+0.074, +0.159] | 0.00016 | +0.85 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | binary_zt@0.8 | 30 | 0.946 | 0.764 | +0.183 [+0.176, +0.189] | 1e-05 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | binary_zt@0.8 | 30 | 0.993 | 0.879 | +0.114 [+0.105, +0.122] | 4.3e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | binary_zt@0.8 | 30 | 0.125 | 3.458 | -3.333 [-3.567, -3.100] | 8.1e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | binary_zt@0.8 | 30 | 0.125 | 4.683 | -4.558 [-4.775, -4.333] | 8.5e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | binary_zt@0.8 | 30 | 0.125 | 8.65 | -8.525 [-8.758, -8.283] | 4.6e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | binary_zt@0.8 | 30 | 0.0 | 3.967 | -3.967 [-4.159, -3.775] | 4.2e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | binary_zt@0.8 | 19 | 0.183 | 3.0 | -2.868 [-2.947, -2.763] | 0.00032 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | binary_zt@0.8 | 30 | 80.9 | 61.433 | +19.467 [+17.900, +21.133] | 9.8e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | binary_zt@0.8 | 30 | 3.395 | 3.868 | -0.474 [-0.899, -0.002] | 0.0032 | -0.64 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | cusum@0.15:6.4 | 30 | 0.542 | 0.764 | -0.222 [-0.232, -0.213] | 8.6e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | cusum@0.15:6.4 | 30 | 0.557 | 0.879 | -0.322 [-0.337, -0.308] | 6.5e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | cusum@0.15:6.4 | 30 | 10.367 | 3.458 | +6.908 [+6.617, +7.200] | 9.3e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | cusum@0.15:6.4 | 30 | 11.967 | 4.683 | +7.283 [+6.958, +7.617] | 4.8e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | cusum@0.15:6.4 | 30 | 16.836 | 8.65 | +8.186 [+7.819, +8.561] | 5e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | cusum@0.15:6.4 | 30 | 4.931 | 3.967 | +0.964 [+0.583, +1.361] | 9.4e-05 | +0.83 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | cusum@0.15:6.4 | 30 | 33.1 | 61.433 | -28.333 [-29.633, -26.967] | 1.6e-05 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | page_cusum@0.05:1.6 | 30 | 0.2 | 0.764 | -0.563 [-0.571, -0.555] | 1.1e-08 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | page_cusum@0.05:1.6 | 30 | 0.334 | 0.879 | -0.545 [-0.555, -0.534] | 4.7e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | page_cusum@0.05:1.6 | 30 | 6.742 | 3.458 | +3.283 [+3.050, +3.508] | 8.4e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | page_cusum@0.05:1.6 | 30 | 6.742 | 4.683 | +2.058 [+1.850, +2.275] | 8.2e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | page_cusum@0.05:1.6 | 30 | 6.742 | 8.65 | -1.908 [-2.108, -1.717] | 4.6e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | page_cusum@0.05:1.6 | 30 | 0.0 | 3.967 | -3.967 [-4.159, -3.775] | 4.2e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | page_cusum@0.05:1.6 | 19 | 0.183 | 3.0 | -2.868 [-2.947, -2.763] | 0.00032 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | page_cusum@0.05:1.6 | 30 | 10.033 | 61.433 | -51.400 [-53.067, -49.667] | 1.6e-05 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | page_cusum@0.05:1.6 | 30 | 3.284 | 3.868 | -0.584 [-0.858, -0.330] | 1.6e-06 | -0.94 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | stopping_response | 30 | 0.8 | 0.764 | +0.037 [+0.031, +0.042] | 1e-05 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | stopping_response | 30 | 0.94 | 0.879 | +0.061 [+0.053, +0.069] | 7.2e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | stopping_response | 30 | 3.342 | 4.683 | -1.342 [-1.525, -1.158] | 8.6e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | stopping_response | 30 | 4.533 | 8.65 | -4.117 [-4.333, -3.908] | 9.1e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | stopping_response | 30 | 1.192 | 3.967 | -2.775 [-2.967, -2.592] | 8.2e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | stopping_response | 30 | 78.8 | 61.433 | +17.367 [+15.867, +18.933] | 1.3e-05 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | stopping_response | 30 | 3.424 | 3.868 | -0.444 [-0.712, -0.194] | 0.012 | -0.63 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|device_fpr | tolerance | 30 | 0.986 | 0.0 | +0.986 [+0.980, +0.991] | 7.4e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|device_f1 | tolerance | 30 | 0.15 | 1.0 | -0.850 [-0.851, -0.849] | 5.3e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | tolerance | 30 | 0.495 | 0.764 | -0.268 [-0.280, -0.257] | 1.1e-08 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|response_coverage | tolerance | 30 | 1.0 | 0.879 | +0.121 [+0.111, +0.130] | 4.3e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | tolerance | 30 | 0.0 | 3.458 | -3.458 [-3.692, -3.225] | 4e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | tolerance | 30 | 0.0 | 4.683 | -4.683 [-4.900, -4.467] | 4e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | tolerance | 30 | 0.0 | 8.65 | -8.650 [-8.900, -8.392] | 9.5e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|containment_mean | tolerance | 30 | 0.0 | 3.967 | -3.967 [-4.159, -3.775] | 8.5e-06 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | tolerance | 19 | 0.761 | 3.0 | -2.478 [-2.671, -2.268] | 0.0005 | -1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | tolerance | 30 | 0.986 | 0.0 | +0.986 [+0.980, +0.991] | 7.4e-06 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|availability_cost | tolerance | 30 | 176.533 | 0.0 | +176.533 [+171.700, +181.133] | 1.5e-05 | +1.00 |
| loss:0.1:s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | tolerance | 30 | 273.867 | 61.433 | +212.433 [+206.900, +217.633] | 1.5e-05 | +1.00 |

Only comparisons significant after Holm correction are listed; all 649 are in `comparisons.csv`.
