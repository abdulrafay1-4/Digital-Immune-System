# Experiment report: `sensitivity`

Generated from `rows.jsonl`; regenerate, never edit.

## Manifest

```json
{
  "suite": "sensitivity",
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
| a1 | op=absent|adj=oracle|noise=gaussian | full[brake=0.25] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[brake=none] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[cap=none] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[cohort=none] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=1] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=5] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[k=1] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[k=3] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.6] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 18.6 [16.000, 22.102] | 0.4867 [0.442, 0.531] | 4.0 [4.000, 4.000] | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.8] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 10.0 [10.000, 10.000] | 0.9 [0.900, 0.900] | — | 0.0 [0.000, 0.000] | 14.1 [6.532, 22.934] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[rep_up=0.95] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0 [7.000, 7.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.5] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.30,0.40,0.30] | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 50.5 [40.000, 61.000] | 0.0122 [0.000, 0.032] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.40,0.25,0.35] | 30 | 0.0667 [0.000, 0.167] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 35.5 [19.000, 52.000] | 0.0411 [0.000, 0.109] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| a1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.50,0.30,0.20] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[brake=0.25] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.3387 [0.331, 0.347] | 67.3333 [66.833, 67.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[brake=none] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.4 [0.400, 0.400] | 101.9667 [101.400, 102.533] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[cap=none] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[cohort=none] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.062 [0.053, 0.071] | 9.1 [7.800, 10.400] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=1] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1053 [0.102, 0.109] | 8.3333 [7.700, 8.933] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=5] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1893 [0.175, 0.204] | 37.3333 [36.833, 37.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[k=1] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[k=3] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.6] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2633 [0.251, 0.276] | 30.2667 [29.800, 30.800] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.8] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.24 [0.231, 0.249] | 24.3333 [23.733, 24.800] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1467 [0.137, 0.158] | 35.5333 [34.099, 37.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[rep_up=0.95] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.5] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1687 [0.156, 0.181] | 27.3333 [26.833, 27.833] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[weights=0.30,0.40,0.30] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.2353 [0.226, 0.245] | 30.0 [30.000, 30.000] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[weights=0.40,0.25,0.35] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.1827 [0.174, 0.191] | 20.4 [20.133, 20.733] |
| r5 | op=absent|adj=oracle|noise=gaussian | full[weights=0.50,0.30,0.20] | 30 | — | 0.4 [0.400, 0.400] | — | — | — | — | 0.224 [0.214, 0.234] | 25.0 [25.000, 25.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[brake=0.25] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[brake=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[cap=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[cohort=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=5] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[k=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[k=3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.6] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.6667 [5.467, 5.867] | 0.9185 [0.914, 0.923] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.8] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 9.5667 [9.333, 9.833] | 0.8319 [0.826, 0.837] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1 [6.867, 7.300] | 0.8867 [0.882, 0.892] | — | 0.0 [0.000, 0.000] | 0.1333 [0.000, 0.400] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[rep_up=0.95] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.0 [5.000, 5.000] | 0.9333 [0.933, 0.933] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.5] | 30 | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] | — | — | 0.0 [0.000, 0.000] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.30,0.40,0.30] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 13.3333 [10.566, 16.067] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.40,0.25,0.35] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 36.7667 [36.567, 37.000] |
| s1 | op=absent|adj=oracle|noise=gaussian | full[weights=0.50,0.30,0.20] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.1667 [6.967, 7.333] | 0.8852 [0.881, 0.890] | — | 0.0 [0.000, 0.000] | 0.0 [0.000, 0.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[brake=0.25] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[brake=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[cap=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[cohort=none] | 30 | 0.7 [0.625, 0.775] | 0.0 [0.000, 0.000] | 0.8029 [0.741, 0.857] | 16.1722 [15.405, 16.925] | 0.2126 [0.180, 0.244] | — | 0.0 [0.000, 0.000] | 4.7333 [3.133, 6.433] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.8944 [0.885, 0.903] | — | 0.0 [0.000, 0.000] | 55.6333 [53.400, 57.733] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=5] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9007 [0.894, 0.908] | — | 0.0 [0.000, 0.000] | 75.2 [74.600, 75.800] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[k=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[k=3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.6] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.7417 [3.725, 3.750] | 0.9219 [0.920, 0.923] | — | 0.0 [0.000, 0.000] | 77.1 [75.667, 78.133] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.8] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.375, 5.600] | 0.8356 [0.827, 0.844] | — | 0.0 [0.000, 0.000] | 63.8667 [61.900, 65.667] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.175 [4.025, 4.325] | 0.8833 [0.871, 0.896] | — | 0.0 [0.000, 0.000] | 71.1333 [69.067, 73.000] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[rep_up=0.95] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9 [0.893, 0.907] | — | 0.0 [0.000, 0.000] | 73.6667 [72.233, 74.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.8583 [4.758, 4.958] | 0.873 [0.869, 0.877] | — | 0.0 [0.000, 0.000] | 73.5333 [73.033, 74.067] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.5] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.225 [4.067, 4.375] | 0.9011 [0.894, 0.908] | — | 0.0 [0.000, 0.000] | 75.4 [74.933, 75.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[weights=0.30,0.40,0.30] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.175 [4.025, 4.333] | 0.9033 [0.896, 0.910] | — | 0.0 [0.000, 0.000] | 80.2333 [79.566, 80.900] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[weights=0.40,0.25,0.35] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.2333 [4.083, 4.383] | 0.9007 [0.894, 0.907] | — | 0.0 [0.000, 0.000] | 76.3667 [75.467, 77.200] |
| s2 | op=absent|adj=oracle|noise=gaussian | full[weights=0.50,0.30,0.20] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 4.25 [4.100, 4.400] | 0.8989 [0.892, 0.906] | — | 0.0 [0.000, 0.000] | 20.3333 [17.099, 23.733] |
| s3 | op=absent|adj=oracle|noise=gaussian | full | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[brake=0.25] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[brake=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[cap=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[cohort=none] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 7.25 [7.150, 7.367] | 0.0 [0.000, 0.000] | 43.7667 [43.400, 44.133] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[hysteresis=5] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 12.6667 [12.533, 12.783] | 0.0 [0.000, 0.000] | 60.1667 [59.700, 60.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[k=1] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[k=3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3 [9.183, 9.433] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.6] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.9583 [3.892, 4.025] | 0.8881 [0.884, 0.892] | 8.2833 [8.150, 8.433] | 0.0 [0.000, 0.000] | 57.4667 [57.100, 57.833] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[lambda=0.8] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 7.0833 [7.000, 7.158] | 0.7095 [0.705, 0.714] | 11.85 [11.750, 11.950] | 0.0 [0.000, 0.000] | 47.6667 [47.267, 48.067] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[lambda_up=0.85] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.025 [4.950, 5.108] | 0.8271 [0.822, 0.831] | 15.25 [15.083, 15.417] | 0.0 [0.000, 0.000] | 57.7 [57.200, 58.200] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[rep_up=0.95] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 14.7667 [14.600, 14.933] | 0.0 [0.000, 0.000] | 52.1667 [51.700, 52.633] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.3] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 3.5167 [3.417, 3.608] | 0.9133 [0.908, 0.919] | 10.0167 [9.900, 10.133] | 0.0 [0.000, 0.000] | 61.8333 [61.467, 62.200] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[threshold=0.5] | 30 | 0.425 [0.325, 0.533] | 0.0 [0.000, 0.000] | 0.6461 [0.567, 0.726] | 14.93 [14.180, 15.737] | 0.1248 [0.092, 0.159] | 8.9688 [8.688, 9.250] | 0.0 [0.000, 0.000] | 1.3 [0.567, 2.200] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[weights=0.30,0.40,0.30] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1667 [5.075, 5.258] | 0.819 [0.814, 0.824] | 9.3667 [9.250, 9.483] | 0.0 [0.000, 0.000] | 54.7667 [54.267, 55.267] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[weights=0.40,0.25,0.35] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.4917 [5.400, 5.583] | 0.8005 [0.795, 0.806] | 14.4833 [14.333, 14.633] | 0.0 [0.000, 0.000] | 53.1 [52.733, 53.500] |
| s3 | op=absent|adj=oracle|noise=gaussian | full[weights=0.50,0.30,0.20] | 30 | 1.0 [1.000, 1.000] | 0.0 [0.000, 0.000] | 1.0 [1.000, 1.000] | 5.1333 [5.058, 5.208] | 0.821 [0.817, 0.825] | 8.2667 [8.167, 8.383] | 0.0 [0.000, 0.000] | 47.2667 [46.833, 47.700] |

## Paired comparisons against `full` (Wilcoxon signed-rank, Holm-corrected)

| comparison | arm | n | mean arm | mean full | difference [95% CI] | p (Holm) | rank-biserial |
|---|---|---|---|---|---|---|---|
| a1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[brake=0.25] | 30 | 3.629 | 3.6 | +0.029 [+0.011, +0.046] | 0.029 | +0.57 |
| a1|op=absent|adj=oracle|noise=gaussian|device_tpr | full[lambda=0.6] | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 1.7e-07 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.6] | 30 | 0.487 | 0.0 | +0.487 [+0.442, +0.530] | 4.7e-06 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|device_tpr | full[lambda_up=0.85] | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 1.7e-07 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda_up=0.85] | 30 | 0.9 | 0.0 | +0.900 [+0.900, +0.900] | 1.7e-07 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda_up=0.85] | 30 | 14.1 | 0.0 | +14.100 [+6.233, +23.133] | 0.036 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[lambda_up=0.85] | 30 | 3.735 | 3.6 | +0.135 [+0.109, +0.163] | 1.9e-08 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|device_tpr | full[threshold=0.3] | 30 | 1.0 | 0.0 | +1.000 [+1.000, +1.000] | 1.7e-07 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.3] | 30 | 0.933 | 0.0 | +0.933 [+0.933, +0.933] | 1.7e-07 | +1.00 |
| a1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[threshold=0.3] | 30 | 3.692 | 3.6 | +0.092 [+0.057, +0.124] | 0.00035 | +0.78 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[brake=0.25] | 30 | 0.339 | 0.169 | +0.170 [+0.158, +0.182] | 8.3e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[brake=0.25] | 30 | 67.333 | 27.333 | +40.000 [+40.000, +40.000] | 2.2e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[brake=0.25] | 30 | 67.333 | 27.333 | +40.000 [+40.000, +40.000] | 2.2e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[brake=none] | 30 | 0.4 | 0.169 | +0.231 [+0.219, +0.244] | 7.8e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[brake=none] | 30 | 101.967 | 27.333 | +74.633 [+74.433, +74.800] | 3.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[brake=none] | 30 | 101.967 | 27.333 | +74.633 [+74.433, +74.800] | 3.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[brake=none] | 30 | 3.761 | 3.798 | -0.037 [-0.061, -0.015] | 0.019 | -0.59 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[cohort=none] | 30 | 8.125 | 10.413 | -2.288 [-2.328, -2.252] | 1.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[cohort=none] | 30 | 0.062 | 0.169 | -0.107 [-0.125, -0.088] | 8.5e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[cohort=none] | 30 | 9.1 | 27.333 | -18.233 [-19.333, -17.133] | 8.4e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[cohort=none] | 30 | 9.1 | 27.333 | -18.233 [-19.333, -17.133] | 8.4e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[cohort=none] | 30 | 3.667 | 3.798 | -0.131 [-0.166, -0.096] | 5.1e-07 | -0.95 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[hysteresis=1] | 30 | 7.373 | 10.413 | -3.040 [-3.085, -2.995] | 1.7e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[hysteresis=1] | 30 | 0.105 | 0.169 | -0.063 [-0.076, -0.051] | 1.1e-05 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[hysteresis=1] | 30 | 8.333 | 27.333 | -19.000 [-19.333, -18.667] | 6.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[hysteresis=1] | 30 | 8.333 | 27.333 | -19.000 [-19.333, -18.667] | 4.9e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[hysteresis=5] | 30 | 14.145 | 10.413 | +3.732 [+3.690, +3.772] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[hysteresis=5] | 30 | 0.189 | 0.169 | +0.021 [+0.015, +0.027] | 7e-05 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[hysteresis=5] | 30 | 37.333 | 27.333 | +10.000 [+10.000, +10.000] | 2.2e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[hysteresis=5] | 30 | 37.333 | 27.333 | +10.000 [+10.000, +10.000] | 2.2e-07 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[lambda=0.6] | 30 | 9.058 | 10.413 | -1.355 [-1.400, -1.310] | 1.7e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[lambda=0.6] | 30 | 0.263 | 0.169 | +0.095 [+0.079, +0.112] | 8.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[lambda=0.6] | 30 | 30.267 | 27.333 | +2.933 [+2.367, +3.533] | 9.2e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.6] | 30 | 30.267 | 27.333 | +2.933 [+2.367, +3.533] | 7.6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[lambda=0.8] | 30 | 11.537 | 10.413 | +1.123 [+1.075, +1.173] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[lambda=0.8] | 30 | 0.24 | 0.169 | +0.071 [+0.056, +0.087] | 1.2e-05 | +0.99 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[lambda=0.8] | 30 | 24.333 | 27.333 | -3.000 [-3.833, -2.267] | 9.3e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.8] | 30 | 24.333 | 27.333 | -3.000 [-3.833, -2.267] | 7.8e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[lambda_up=0.85] | 30 | 15.487 | 10.413 | +5.073 [+5.012, +5.135] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[lambda_up=0.85] | 30 | 0.147 | 0.169 | -0.022 [-0.035, -0.008] | 0.011 | -0.68 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[lambda_up=0.85] | 30 | 35.533 | 27.333 | +8.200 [+6.900, +9.501] | 8.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda_up=0.85] | 30 | 35.533 | 27.333 | +8.200 [+6.900, +9.501] | 7.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[lambda_up=0.85] | 30 | 3.903 | 3.798 | +0.105 [+0.081, +0.129] | 2.2e-08 | +0.99 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[rep_up=0.95] | 30 | 16.02 | 10.413 | +5.607 [+5.558, +5.657] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[weights=0.30,0.40,0.30] | 30 | 10.982 | 10.413 | +0.568 [+0.532, +0.603] | 1.6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[weights=0.30,0.40,0.30] | 30 | 0.235 | 0.169 | +0.067 [+0.055, +0.079] | 8.3e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[weights=0.30,0.40,0.30] | 30 | 30.0 | 27.333 | +2.667 [+2.167, +3.167] | 9.1e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.30,0.40,0.30] | 30 | 30.0 | 27.333 | +2.667 [+2.167, +3.167] | 6.4e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[weights=0.40,0.25,0.35] | 30 | 14.95 | 10.413 | +4.537 [+4.488, +4.587] | 1.7e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[weights=0.40,0.25,0.35] | 30 | 20.4 | 27.333 | -6.933 [-7.433, -6.433] | 7.6e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.40,0.25,0.35] | 30 | 20.4 | 27.333 | -6.933 [-7.433, -6.433] | 6.1e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[weights=0.40,0.25,0.35] | 30 | 3.846 | 3.798 | +0.048 [+0.019, +0.077] | 0.014 | +0.60 |
| r5|op=absent|adj=oracle|noise=gaussian|benign_mttr_mean | full[weights=0.50,0.30,0.20] | 30 | 9.917 | 10.413 | -0.497 [-0.538, -0.457] | 1.7e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|false_restriction_rate | full[weights=0.50,0.30,0.20] | 30 | 0.224 | 0.169 | +0.055 [+0.043, +0.069] | 9.6e-06 | +1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|availability_cost | full[weights=0.50,0.30,0.20] | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 1.1e-05 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.50,0.30,0.20] | 30 | 25.0 | 27.333 | -2.333 [-2.833, -1.833] | 7.7e-06 | -1.00 |
| r5|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[weights=0.50,0.30,0.20] | 30 | 3.754 | 3.798 | -0.044 [-0.073, -0.013] | 0.047 | -0.54 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[brake=none] | 30 | 3.703 | 3.75 | -0.047 [-0.079, -0.015] | 0.042 | -0.53 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[cap=none] | 30 | 3.677 | 3.75 | -0.074 [-0.118, -0.036] | 0.0021 | -0.70 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[hysteresis=1] | 30 | 0.903 | 0.882 | +0.021 [+0.021, +0.021] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[hysteresis=5] | 30 | 0.861 | 0.882 | -0.020 [-0.020, -0.020] | 1.7e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[hysteresis=5] | 30 | 3.656 | 3.75 | -0.094 [-0.138, -0.052] | 0.00012 | -0.82 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.6] | 30 | 0.901 | 0.882 | +0.019 [+0.017, +0.022] | 5.3e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.6] | 30 | 0.919 | 0.885 | +0.033 [+0.029, +0.038] | 4.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.6] | 30 | 4.667 | 6.167 | -1.500 [-1.700, -1.300] | 3.5e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.6] | 30 | 5.667 | 7.167 | -1.500 [-1.700, -1.300] | 3.5e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[lambda=0.6] | 30 | 2.933 | 4.0 | -1.067 [-1.167, -1.000] | 4.1e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.8] | 30 | 0.849 | 0.882 | -0.033 [-0.037, -0.028] | 4.6e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.8] | 30 | 0.832 | 0.885 | -0.053 [-0.060, -0.047] | 5.6e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.8] | 30 | 8.567 | 6.167 | +2.400 [+2.100, +2.700] | 4.8e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.8] | 30 | 9.567 | 7.167 | +2.400 [+2.100, +2.700] | 3.6e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda_up=0.85] | 30 | 0.873 | 0.882 | -0.008 [-0.010, -0.006] | 9.1e-05 | -0.86 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[lambda_up=0.85] | 30 | 3.699 | 3.75 | -0.051 [-0.087, -0.017] | 0.026 | -0.51 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[threshold=0.3] | 30 | 0.899 | 0.882 | +0.017 [+0.015, +0.020] | 2.3e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.3] | 30 | 0.933 | 0.885 | +0.048 [+0.044, +0.053] | 1.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[threshold=0.3] | 30 | 3.0 | 6.167 | -3.167 [-3.367, -2.967] | 2.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[threshold=0.3] | 30 | 5.0 | 7.167 | -2.167 [-2.367, -1.967] | 2.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[threshold=0.3] | 30 | 3.696 | 3.75 | -0.054 [-0.087, -0.022] | 0.015 | -0.59 |
| s1|op=absent|adj=oracle|noise=gaussian|device_tpr | full[threshold=0.5] | 30 | 0.0 | 1.0 | -1.000 [-1.000, -1.000] | 1.7e-07 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.5] | 30 | 0.0 | 0.885 | -0.885 [-0.890, -0.881] | 2.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[threshold=0.5] | 30 | 3.715 | 3.75 | -0.035 [-0.150, +0.156] | 0.0024 | -0.69 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.30,0.40,0.30] | 30 | 13.333 | 0.0 | +13.333 [+10.667, +16.033] | 6.4e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[weights=0.40,0.25,0.35] | 30 | 0.861 | 0.882 | -0.020 [-0.020, -0.020] | 2.3e-06 | -1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.40,0.25,0.35] | 30 | 36.767 | 0.0 | +36.767 [+36.567, +36.967] | 3.7e-06 | +1.00 |
| s1|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[weights=0.40,0.25,0.35] | 30 | 3.792 | 3.75 | +0.042 [+0.016, +0.067] | 0.014 | +0.61 |
| s2|op=absent|adj=oracle|noise=gaussian|device_tpr | full[cohort=none] | 30 | 0.7 | 1.0 | -0.300 [-0.375, -0.225] | 2.1e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|device_f1 | full[cohort=none] | 30 | 0.803 | 1.0 | -0.197 [-0.257, -0.142] | 1.6e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[cohort=none] | 29 | 0.244 | 0.814 | -0.570 [-0.606, -0.534] | 1.1e-08 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | full[cohort=none] | 30 | 0.213 | 0.9 | -0.687 [-0.721, -0.654] | 6.9e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[cohort=none] | 30 | 14.719 | 3.175 | +11.544 [+10.669, +12.458] | 6.8e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[cohort=none] | 30 | 16.172 | 4.225 | +11.947 [+11.150, +12.789] | 5.2e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[cohort=none] | 20 | 20.475 | 7.65 | +12.825 [+12.213, +13.463] | 0.00018 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[cohort=none] | 30 | 4.733 | 73.667 | -68.933 [-71.267, -66.300] | 8.4e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[cohort=none] | 30 | 5.036 | 4.101 | +0.935 [+0.529, +1.323] | 0.0014 | +0.71 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[hysteresis=1] | 30 | 0.827 | 0.814 | +0.014 [+0.005, +0.022] | 0.0028 | +0.63 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[hysteresis=1] | 30 | 55.633 | 73.667 | -18.033 [-19.500, -16.600] | 5e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[hysteresis=1] | 30 | 6.276 | 4.101 | +2.174 [+1.599, +2.766] | 1e-06 | +0.94 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[hysteresis=5] | 30 | 3.819 | 4.101 | -0.283 [-0.472, -0.110] | 0.0088 | -0.62 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.6] | 30 | 0.828 | 0.814 | +0.015 [+0.010, +0.019] | 7.7e-05 | +0.98 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.6] | 30 | 0.922 | 0.9 | +0.022 [+0.015, +0.028] | 3.4e-05 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.6] | 30 | 2.742 | 3.175 | -0.433 [-0.583, -0.283] | 6.7e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.6] | 30 | 3.742 | 4.225 | -0.483 [-0.625, -0.333] | 6.8e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[lambda=0.6] | 30 | 6.967 | 7.65 | -0.683 [-0.817, -0.525] | 7.1e-06 | -0.94 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[lambda=0.6] | 30 | 3.225 | 3.425 | -0.200 [-0.300, -0.092] | 0.0017 | -0.76 |
| s2|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[lambda=0.6] | 27 | 2.439 | 3.0 | -0.577 [-0.676, -0.475] | 1.1e-05 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.6] | 30 | 77.1 | 73.667 | +3.433 [+2.500, +4.367] | 2.9e-05 | +0.93 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.8] | 30 | 0.769 | 0.814 | -0.045 [-0.052, -0.039] | 4.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.8] | 30 | 0.836 | 0.9 | -0.064 [-0.073, -0.057] | 5.6e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.8] | 30 | 4.4 | 3.175 | +1.225 [+1.058, +1.392] | 4.8e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.8] | 30 | 5.492 | 4.225 | +1.267 [+1.125, +1.408] | 3.6e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[lambda=0.8] | 30 | 9.133 | 7.65 | +1.483 [+1.358, +1.617] | 3e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[lambda=0.8] | 30 | 3.642 | 3.425 | +0.217 [+0.133, +0.308] | 0.00063 | +0.89 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.8] | 30 | 63.867 | 73.667 | -9.800 [-11.800, -7.700] | 1e-05 | -0.97 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda_up=0.85] | 30 | 0.793 | 0.814 | -0.020 [-0.030, -0.011] | 0.00083 | -0.79 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda_up=0.85] | 30 | 0.883 | 0.9 | -0.017 [-0.029, -0.006] | 0.049 | -0.71 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[lambda_up=0.85] | 30 | 4.962 | 4.101 | +0.861 [+0.465, +1.267] | 0.0017 | +0.69 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[threshold=0.3] | 30 | 0.804 | 0.814 | -0.010 [-0.015, -0.006] | 0.00072 | -0.75 |
| s2|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.3] | 30 | 0.873 | 0.9 | -0.027 [-0.034, -0.020] | 3.2e-06 | -0.98 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[threshold=0.3] | 30 | 3.658 | 3.175 | +0.483 [+0.350, +0.617] | 2.2e-05 | +0.98 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[threshold=0.3] | 30 | 4.858 | 4.225 | +0.633 [+0.483, +0.775] | 5.3e-06 | +0.98 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[threshold=0.3] | 30 | 7.883 | 7.65 | +0.233 [+0.125, +0.342] | 0.00062 | +0.74 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[threshold=0.3] | 30 | 3.025 | 3.425 | -0.400 [-0.500, -0.300] | 9.8e-06 | -0.96 |
| s2|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[weights=0.30,0.40,0.30] | 30 | 0.817 | 0.814 | +0.004 [+0.001, +0.007] | 0.043 | +0.91 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.30,0.40,0.30] | 30 | 6.333 | 7.65 | -1.317 [-1.400, -1.233] | 3.7e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.30,0.40,0.30] | 30 | 2.158 | 3.425 | -1.267 [-1.350, -1.192] | 3.7e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.30,0.40,0.30] | 30 | 80.233 | 73.667 | +6.567 [+5.567, +7.767] | 6.4e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.40,0.25,0.35] | 30 | 7.125 | 7.65 | -0.525 [-0.592, -0.450] | 3.8e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.40,0.25,0.35] | 30 | 2.892 | 3.425 | -0.533 [-0.608, -0.458] | 3.4e-06 | -1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.40,0.25,0.35] | 30 | 76.367 | 73.667 | +2.700 [+1.767, +3.767] | 2.4e-05 | +0.94 |
| s2|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.50,0.30,0.20] | 30 | 15.017 | 7.65 | +7.367 [+6.569, +8.186] | 3e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.50,0.30,0.20] | 30 | 10.783 | 3.425 | +7.358 [+6.553, +8.169] | 2.9e-06 | +1.00 |
| s2|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.50,0.30,0.20] | 30 | 20.333 | 73.667 | -53.333 [-57.333, -49.067] | 7.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[hysteresis=1] | 30 | 0.797 | 0.749 | +0.048 [+0.048, +0.049] | 3.3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[hysteresis=1] | 30 | 7.25 | 9.3 | -2.050 [-2.100, -2.000] | 1.4e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[hysteresis=1] | 30 | 43.767 | 52.167 | -8.400 [-8.567, -8.233] | 3.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[hysteresis=5] | 30 | 0.706 | 0.749 | -0.043 [-0.043, -0.043] | 3.3e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[hysteresis=5] | 30 | 12.667 | 9.3 | +3.367 [+3.217, +3.517] | 1.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[hysteresis=5] | 30 | 60.167 | 52.167 | +8.000 [+8.000, +8.000] | 2.2e-07 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[k=1] | 30 | 5.586 | 4.901 | +0.685 [+0.310, +1.138] | 0.00069 | +0.75 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.6] | 30 | 0.792 | 0.749 | +0.044 [+0.041, +0.046] | 5.3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.6] | 30 | 0.888 | 0.819 | +0.069 [+0.064, +0.074] | 4.7e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.6] | 30 | 3.275 | 4.492 | -1.217 [-1.300, -1.133] | 4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.6] | 30 | 3.958 | 5.167 | -1.208 [-1.292, -1.125] | 3.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[lambda=0.6] | 30 | 6.267 | 7.558 | -1.292 [-1.383, -1.200] | 2.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[lambda=0.6] | 30 | 8.283 | 9.3 | -1.017 [-1.150, -0.883] | 2.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[lambda=0.6] | 30 | 3.25 | 4.464 | -1.214 [-1.292, -1.139] | 3.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.6] | 30 | 57.467 | 52.167 | +5.300 [+4.767, +5.833] | 7.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda=0.8] | 30 | 0.654 | 0.749 | -0.095 [-0.100, -0.091] | 4.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda=0.8] | 30 | 0.71 | 0.819 | -0.110 [-0.115, -0.104] | 5.6e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda=0.8] | 30 | 6.375 | 4.492 | +1.883 [+1.775, +1.992] | 4.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda=0.8] | 30 | 7.083 | 5.167 | +1.917 [+1.817, +2.017] | 3.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[lambda=0.8] | 30 | 9.542 | 7.558 | +1.983 [+1.858, +2.108] | 3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[lambda=0.8] | 30 | 11.85 | 9.3 | +2.550 [+2.433, +2.667] | 9.4e-07 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[lambda=0.8] | 30 | 6.85 | 4.464 | +2.386 [+2.278, +2.486] | 4.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda=0.8] | 30 | 47.667 | 52.167 | -4.500 [-5.067, -3.900] | 7.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[lambda_up=0.85] | 30 | 0.729 | 0.749 | -0.020 [-0.022, -0.017] | 6.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[lambda_up=0.85] | 30 | 0.827 | 0.819 | +0.008 [+0.004, +0.012] | 0.0057 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[lambda_up=0.85] | 30 | 4.283 | 4.492 | -0.208 [-0.292, -0.133] | 0.00066 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[lambda_up=0.85] | 30 | 5.025 | 5.167 | -0.142 [-0.217, -0.075] | 0.0075 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[lambda_up=0.85] | 30 | 7.317 | 7.558 | -0.242 [-0.333, -0.158] | 0.00022 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | full[lambda_up=0.85] | 30 | 2.292 | 2.392 | -0.100 [-0.150, -0.050] | 0.014 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[lambda_up=0.85] | 30 | 15.25 | 9.3 | +5.950 [+5.783, +6.117] | 1.3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[lambda_up=0.85] | 30 | 10.083 | 4.464 | +5.619 [+5.486, +5.744] | 4.6e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[lambda_up=0.85] | 30 | 57.7 | 52.167 | +5.533 [+4.967, +6.100] | 7.7e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[lambda_up=0.85] | 30 | 5.1 | 4.901 | +0.199 [+0.054, +0.342] | 0.026 | +0.49 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[rep_up=0.95] | 30 | 14.767 | 9.3 | +5.467 [+5.333, +5.600] | 1.2e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[threshold=0.3] | 30 | 0.785 | 0.749 | +0.036 [+0.032, +0.040] | 5.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.3] | 30 | 0.913 | 0.819 | +0.094 [+0.089, +0.100] | 3.1e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[threshold=0.3] | 30 | 2.442 | 4.492 | -2.050 [-2.150, -1.958] | 3.8e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[threshold=0.3] | 30 | 3.517 | 5.167 | -1.650 [-1.758, -1.550] | 3.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[threshold=0.3] | 30 | 6.192 | 7.558 | -1.367 [-1.475, -1.267] | 2.9e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | full[threshold=0.3] | 30 | 2.675 | 2.392 | +0.283 [+0.150, +0.400] | 0.00062 | +0.77 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[threshold=0.3] | 30 | 10.017 | 9.3 | +0.717 [+0.583, +0.850] | 1.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[threshold=0.3] | 30 | 4.656 | 4.464 | +0.192 [+0.131, +0.253] | 0.00012 | +0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[threshold=0.3] | 30 | 61.833 | 52.167 | +9.667 [+9.167, +10.167] | 7.8e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_tpr | full[threshold=0.5] | 30 | 0.425 | 1.0 | -0.575 [-0.675, -0.475] | 5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|device_f1 | full[threshold=0.5] | 25 | 0.646 | 1.0 | -0.354 [-0.432, -0.275] | 3.5e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[threshold=0.5] | 23 | 0.159 | 0.749 | -0.589 [-0.623, -0.555] | 8.1e-05 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[threshold=0.5] | 30 | 0.125 | 0.819 | -0.694 [-0.727, -0.661] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_flag_mean | full[threshold=0.5] | 28 | 13.929 | 4.492 | +9.455 [+8.708, +10.217] | 1.5e-05 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[threshold=0.5] | 25 | 14.93 | 5.167 | +9.770 [+8.960, +10.640] | 3.7e-05 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[threshold=0.5] | 8 | 16.375 | 7.558 | +8.844 [+7.281, +10.345] | 0.016 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[threshold=0.5] | 16 | 8.969 | 9.3 | -0.469 [-0.812, -0.125] | 0.041 | -0.69 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[threshold=0.5] | 25 | 4.19 | 4.464 | -0.280 [-0.367, -0.193] | 0.00018 | -0.93 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[threshold=0.5] | 30 | 1.3 | 52.167 | -50.867 [-51.767, -49.867] | 8.1e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[threshold=0.5] | 30 | 3.866 | 4.901 | -1.035 [-1.246, -0.796] | 6.5e-07 | -0.95 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[weights=0.30,0.40,0.30] | 30 | 0.743 | 0.749 | -0.006 [-0.008, -0.005] | 7.8e-05 | -0.91 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.30,0.40,0.30] | 30 | 7.192 | 7.558 | -0.367 [-0.425, -0.308] | 3.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.30,0.40,0.30] | 30 | 2.025 | 2.392 | -0.367 [-0.425, -0.308] | 3.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|trust_restoration_mean | full[weights=0.30,0.40,0.30] | 30 | 4.317 | 4.464 | -0.147 [-0.217, -0.086] | 0.0021 | -0.99 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.30,0.40,0.30] | 30 | 54.767 | 52.167 | +2.600 [+2.300, +2.900] | 6.4e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[weights=0.30,0.40,0.30] | 30 | 5.065 | 4.901 | +0.164 [+0.063, +0.264] | 0.0073 | +0.64 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[weights=0.40,0.25,0.35] | 30 | 0.665 | 0.749 | -0.084 [-0.087, -0.082] | 5.2e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|response_coverage | full[weights=0.40,0.25,0.35] | 30 | 0.8 | 0.819 | -0.019 [-0.021, -0.016] | 5e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_response_mean | full[weights=0.40,0.25,0.35] | 30 | 5.492 | 5.167 | +0.325 [+0.283, +0.367] | 2.2e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.40,0.25,0.35] | 30 | 7.225 | 7.558 | -0.333 [-0.408, -0.258] | 8.9e-06 | -0.97 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.40,0.25,0.35] | 30 | 1.733 | 2.392 | -0.658 [-0.742, -0.567] | 3.4e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[weights=0.40,0.25,0.35] | 30 | 14.483 | 9.3 | +5.183 [+5.033, +5.333] | 1.2e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.40,0.25,0.35] | 30 | 53.1 | 52.167 | +0.933 [+0.567, +1.300] | 0.00048 | +0.86 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_f1 | full[weights=0.50,0.30,0.20] | 30 | 0.752 | 0.749 | +0.004 [+0.002, +0.005] | 0.00053 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|latency_restrict_mean | full[weights=0.50,0.30,0.20] | 30 | 8.683 | 7.558 | +1.125 [+1.008, +1.250] | 3e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|containment_mean | full[weights=0.50,0.30,0.20] | 30 | 3.55 | 2.392 | +1.158 [+1.042, +1.283] | 2.9e-06 | +1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|mttr_mean | full[weights=0.50,0.30,0.20] | 30 | 8.267 | 9.3 | -1.033 [-1.150, -0.917] | 6e-07 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|disruptive_actions | full[weights=0.50,0.30,0.20] | 30 | 47.267 | 52.167 | -4.900 [-5.433, -4.367] | 7.7e-06 | -1.00 |
| s3|op=absent|adj=oracle|noise=gaussian|tick_ms_p95 | full[weights=0.50,0.30,0.20] | 30 | 5.879 | 4.901 | +0.978 [+0.327, +1.752] | 0.047 | +0.54 |

Only comparisons significant after Holm correction are listed; all 1201 are in `comparisons.csv`.
