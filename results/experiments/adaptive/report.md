# Experiment report: `adaptive`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "adaptive",
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
| a1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a10 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 225.0 [225.000, 225.000] |
| a10 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 225.0 [225.000, 225.000] |
| a10 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0 [3.000, 3.000] | 0.975 [0.975, 0.975] | — | 0.0 [0.000, 0.000] | 210.5 [210.267, 210.733] |
| a10 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a11 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| a11 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| a11 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a11 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a12 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 17.0 [17.000, 17.000] | 0.7872 [0.787, 0.787] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a12 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 17.0 [17.000, 17.000] | 0.7872 [0.787, 0.787] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a12 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 17.0 [17.000, 17.000] | 0.7872 [0.787, 0.787] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a12 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 20.0 [20.000, 20.000] | 0.7447 [0.745, 0.745] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a13 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| a13 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.4 [71.800, 74.833] |
| a13 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a13 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.0 [19.833, 24.167] | 0.4833 [0.426, 0.535] | — | 0.0 [0.000, 0.000] | 15.1 [11.700, 18.400] |
| a2 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 22.0 [19.833, 24.167] | 0.4833 [0.426, 0.535] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a2 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a2 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.0667 [5.933, 6.200] | 0.9261 [0.924, 0.928] | — | 0.0 [0.000, 0.000] | 49.6 [49.267, 49.933] |
| a3 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.0667 [5.933, 6.200] | 0.9261 [0.924, 0.928] | — | 0.0 [0.000, 0.000] | 49.6 [49.267, 49.933] |
| a3 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.0667 [5.933, 6.200] | 0.9261 [0.924, 0.928] | — | 0.0 [0.000, 0.000] | 49.6 [49.267, 49.933] |
| a3 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a4 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.1 [6.000, 6.233] | 0.918 [0.915, 0.920] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a4 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.1 [6.000, 6.233] | 0.918 [0.915, 0.920] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a4 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 6.1 [6.000, 6.233] | 0.918 [0.915, 0.920] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a4 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a5 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 26.9667 [26.900, 27.000] |
| a5 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 26.9667 [26.900, 27.000] |
| a5 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.0 [3.000, 3.000] | 0.9643 [0.964, 0.964] | — | 0.0 [0.000, 0.000] | 26.9667 [26.900, 27.000] |
| a5 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a6 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| a6 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.3033 [4.272, 4.336] | 0.9342 [0.933, 0.935] | — | 0.0 [0.000, 0.000] | 297.1 [296.033, 298.033] |
| a6 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a6 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a7 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.4667 [3.300, 3.633] | 0.9575 [0.952, 0.963] | — | 0.0 [0.000, 0.000] | 39.8333 [39.700, 39.967] |
| a7 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.4667 [3.300, 3.633] | 0.9325 [0.927, 0.938] | — | 0.0 [0.000, 0.000] | 38.8667 [38.700, 39.000] |
| a7 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.8333 [5.700, 5.933] | 0.8292 [0.826, 0.833] | — | 0.0 [0.000, 0.000] | 36.2333 [36.067, 36.400] |
| a7 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a8 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.775 [2.633, 2.900] | 0.9742 [0.970, 0.979] | — | 0.0 [0.000, 0.000] | 124.0333 [124.000, 124.100] |
| a8 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.775 [2.633, 2.900] | 0.9742 [0.970, 0.979] | — | 0.0 [0.000, 0.000] | 124.0333 [124.000, 124.100] |
| a8 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 8.0583 [8.017, 8.108] | 0.7981 [0.796, 0.799] | — | 0.0 [0.000, 0.000] | 19.7333 [16.500, 22.867] |
| a8 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a9 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 81.0 [81.000, 81.000] |
| a9 | op=absent|adj=oracle|noise=gaussian | no_memory | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 2.0 [2.000, 2.000] | 1.0 [1.000, 1.000] | — | 0.0 [0.000, 0.000] | 81.0 [81.000, 81.000] |
| a9 | op=absent|adj=oracle|noise=gaussian | no_sharing | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.0 [4.000, 4.000] | 0.92 [0.920, 0.920] | — | 0.0 [0.000, 0.000] | 75.0 [75.000, 75.000] |
| a9 | op=absent|adj=oracle|noise=gaussian | static_trust | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| a10|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.902 | 0.894 | +0.008 [+0.008, +0.008] | 6.7e-06 | +1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.975 | 1.0 | -0.025 [-0.025, -0.025] | 5.6e-07 | -1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 2.0 | 1.0 | +1.000 [+1.000, +1.000] | 5.6e-07 | +1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 3.0 | 2.0 | +1.000 [+1.000, +1.000] | 5.2e-07 | +1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 3.013 | 2.0 | +1.013 [+1.005, +1.023] | 3.7e-06 | +1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 210.5 | 225.0 | -14.500 [-14.733, -14.233] | 1e-05 | -1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 225.0 | -225.000 [-225.000, -225.000] | 5.6e-07 | -1.00 |
| a10|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 3.834 | 4.075 | -0.242 [-0.274, -0.209] | 2.4e-08 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.934 | -0.934 [-0.935, -0.933] | 1.2e-05 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 297.1 | -297.100 [-298.100, -296.033] | 1.6e-05 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 7.276 | 7.808 | -0.531 [-0.573, -0.491] | 2.4e-08 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.934 | -0.934 [-0.935, -0.933] | 6.6e-06 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 297.1 | -297.100 [-298.100, -296.033] | 1.1e-05 | -1.00 |
| a11|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 7.539 | 7.808 | -0.269 [-0.324, -0.215] | 2.4e-08 | -1.00 |
| a12|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.745 | 0.787 | -0.043 [-0.043, -0.043] | 5.6e-07 | -1.00 |
| a12|op=absent|adj=oracle|noise=gaussian|latency_response_mean | static_trust | 30 | 20.0 | 17.0 | +3.000 [+3.000, +3.000] | 5.2e-07 | +1.00 |
| a12|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.286 | 2.244 | +0.042 [+0.025, +0.059] | 0.00093 | +0.83 |
| a13|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.764 | 4.116 | -0.352 [-0.600, -0.141] | 0.0067 | -0.68 |
| a13|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a13|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 1.1e-05 | -1.00 |
| a13|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 1.6e-05 | -1.00 |
| a13|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.693 | 4.116 | -0.423 [-0.675, -0.205] | 3.8e-05 | -0.87 |
| a13|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a13|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.9 | -0.900 [-0.907, -0.893] | 6.6e-06 | -1.00 |
| a13|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 73.667 | -73.667 [-74.933, -72.233] | 1.1e-05 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_memory | 30 | 0.0 | 15.1 | -15.100 [-18.300, -11.900] | 2.7e-05 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 28.69 | 34.122 | -5.433 [-7.558, -3.387] | 0.0002 | -0.82 |
| a2|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.483 | -0.483 [-0.535, -0.428] | 1.2e-05 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 15.1 | -15.100 [-18.300, -11.900] | 1.6e-05 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 28.415 | 34.122 | -5.707 [-7.944, -3.563] | 0.00045 | -0.79 |
| a2|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.483 | -0.483 [-0.535, -0.428] | 6.6e-06 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 15.1 | -15.100 [-18.300, -11.900] | 1.1e-05 | -1.00 |
| a2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 29.211 | 34.122 | -4.911 [-7.103, -2.777] | 0.014 | -0.63 |
| a3|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a3|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.926 | -0.926 [-0.928, -0.924] | 1.6e-06 | -1.00 |
| a3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 49.6 | -49.600 [-49.933, -49.267] | 4.4e-06 | -1.00 |
| a4|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a4|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.918 | -0.918 [-0.920, -0.915] | 1.3e-06 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.909 | 0.929 | -0.019 [-0.019, -0.019] | 4.3e-07 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.964 | 1.0 | -0.036 [-0.036, -0.036] | 5.6e-07 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 3.0 | 2.0 | +1.000 [+1.000, +1.000] | 5.2e-07 | +1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.033 | 1.033 | -1.000 [-1.000, -1.000] | 4.3e-07 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 26.967 | -26.967 [-27.000, -26.900] | 7.5e-07 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 56.868 | 360.595 | -303.727 [-488.760, -150.507] | 2.4e-08 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|device_tpr | no_sharing | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.0 | 0.934 | -0.934 [-0.935, -0.933] | 1.2e-05 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 0.0 | 297.1 | -297.100 [-298.100, -296.033] | 1.6e-05 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 77.553 | 360.595 | -283.042 [-470.471, -127.436] | 1.3e-05 | -0.90 |
| a6|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.934 | -0.934 [-0.935, -0.933] | 6.6e-06 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 297.1 | -297.100 [-298.100, -296.033] | 1.1e-05 | -1.00 |
| a6|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 136.416 | 360.595 | -224.179 [-409.415, -68.943] | 0.026 | -0.59 |
| a7|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_memory | 30 | 0.809 | 0.824 | -0.014 [-0.014, -0.014] | 1e-05 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|response_coverage | no_memory | 30 | 0.932 | 0.958 | -0.025 [-0.025, -0.025] | 1.1e-05 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_memory | 30 | 38.867 | 39.833 | -0.967 [-1.000, -0.900] | 9.4e-07 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_memory | 30 | 3.051 | 16.498 | -13.447 [-17.101, -9.731] | 2.4e-08 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.756 | 0.824 | -0.068 [-0.071, -0.064] | 8.2e-06 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.829 | 0.958 | -0.128 [-0.134, -0.123] | 9.4e-06 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 3.9 | 2.467 | +1.433 [+1.267, +1.600] | 8.7e-06 | +1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 5.833 | 3.467 | +2.367 [+2.167, +2.567] | 7.5e-06 | +1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 5.933 | 5.133 | +0.800 [+0.633, +0.933] | 8.6e-06 | +1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 30 | 0.1 | 1.667 | -1.567 [-1.767, -1.367] | 7.4e-06 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 36.233 | 39.833 | -3.600 [-3.800, -3.367] | 1e-05 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | no_sharing | 30 | 3.083 | 16.498 | -13.415 [-17.066, -9.714] | 2.4e-08 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.958 | -0.958 [-0.963, -0.952] | 5.9e-06 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 39.833 | -39.833 [-39.967, -39.700] | 2.3e-06 | -1.00 |
| a7|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 3.051 | 16.498 | -13.447 [-17.087, -9.744] | 2.4e-08 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.784 | 0.875 | -0.091 [-0.093, -0.088] | 6.7e-06 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.798 | 0.974 | -0.176 [-0.181, -0.172] | 9e-06 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 5.058 | 1.775 | +3.283 [+3.150, +3.433] | 9e-06 | +1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 8.058 | 2.775 | +5.283 [+5.150, +5.433] | 7.5e-06 | +1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 29 | 19.79 | 3.992 | +15.799 [+14.468, +17.224] | 1.8e-05 | +1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|containment_mean | no_sharing | 29 | 11.753 | 1.217 | +10.555 [+9.195, +12.020] | 2e-05 | +1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 19.733 | 124.033 | -104.300 [-107.467, -101.167] | 1.6e-05 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 0.974 | -0.974 [-0.979, -0.970] | 3.5e-06 | -1.00 |
| a8|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 124.033 | -124.033 [-124.100, -124.000] | 7.5e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|tick_f1 | no_sharing | 30 | 0.824 | 0.868 | -0.044 [-0.044, -0.044] | 4.3e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|response_coverage | no_sharing | 30 | 0.92 | 1.0 | -0.080 [-0.080, -0.080] | 5.6e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | no_sharing | 30 | 3.0 | 1.0 | +2.000 [+2.000, +2.000] | 5.6e-07 | +1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|latency_response_mean | no_sharing | 30 | 4.0 | 2.0 | +2.000 [+2.000, +2.000] | 5.2e-07 | +1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | no_sharing | 30 | 5.0 | 3.0 | +2.000 [+2.000, +2.000] | 4.3e-07 | +1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|disruptive_actions | no_sharing | 30 | 75.0 | 81.0 | -6.000 [-6.000, -6.000] | 5.6e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|device_tpr | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|response_coverage | static_trust | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 5.6e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|disruptive_actions | static_trust | 30 | 0.0 | 81.0 | -81.000 [-81.000, -81.000] | 5.6e-07 | -1.00 |
| a9|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | static_trust | 30 | 2.365 | 2.438 | -0.073 [-0.106, -0.040] | 0.0017 | -0.74 |

Only comparisons significant after Holm correction are listed; all 597 are in `comparisons.csv`.
