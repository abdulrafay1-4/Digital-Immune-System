# TON_IoT held-out results

Calibration: aggregate `mean`, calibration AUC {'mean': 0.828824617781673, 'max': 0.7596114519427403}, dataset SHA-256 `65d5465df1809b98...`.

## Window level (held-out half)

14371 windows, 180 with attack traffic. AUC of network disturbance **0.719**; Isolation Forest on the same features 0.821.

| Threshold (benign calibration quantile) | Detection | False alarm |
|---|---:|---:|
| q95 | 0.278 | 0.055 |
| q99 | 0.150 | 0.044 |

| Attack type | Windows | Median disturbance | Detection at q95 |
|---|---:|---:|---:|
| backdoor | 32 | 0.239 | 0.344 |
| ddos | 6 | 0.208 | 0.333 |
| dos | 6 | 0.644 | 0.833 |
| injection | 17 | 0.237 | 0.412 |
| mitm | 51 | 0.000 | 0.216 |
| password | 10 | 0.382 | 1.000 |
| ransomware | 54 | 0.000 | 0.000 |
| xss | 4 | 0.424 | 1.000 |

## Devices replayed through the closed loop

28 hosts, 17 of them attackers, 420 ticks (one per active 5-minute window), seeds 20000--20009. Network dimension from the capture; identity, behaviour and device synthetic and healthy.

| Arm | device_tpr | device_fpr | tick_precision | tick_recall | response_coverage | latency_response_mean | false_restriction_rate | availability_cost | containment_rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| static_trust | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| no_sharing | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| no_memory | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| binary_response | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| no_recovery | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| binary_zt | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| beta_reputation | 0.000 | 0.000 | — | 0.000 | 0.000 | — | 0.000 | 0.000 | 0.000 |
| isolation_forest | 0.994 | 0.991 | 0.040 | 0.071 | 0.172 | 47.557 | 0.991 | 135.300 | 0.994 |
