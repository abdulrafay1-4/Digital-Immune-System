# What each mechanism costs (plan section 55)

Generated from `rows.jsonl`; regenerate, never edit.

| arm | description | seed | tick_ms_p50 | tick_ms_p95 | cpu_seconds | rss_mb | messages_per_device_tick | memory_read_ms_p50 | device_tpr |
|---|---|---|---|---|---|---|---|---|---|
| full | every mechanism | 20000 | 3.554 | 5.815 | 0.2636 | 131.9 | 2.02 | 0.03083 | 1 |
| full | every mechanism | 20001 | 3.362 | 3.627 | 0.2342 | 152.1 | 2.02 | 0.02287 | 1 |
| full | every mechanism | 20002 | 3.403 | 3.582 | 0.2321 | 173 | 2.02 | 0.02342 | 1 |
| full_replicated_fusion | + trust fusion replicated three times | 20000 | 4.46 | 5.815 | 0.2924 | 193.2 | 2.02 | 0.02917 | 1 |
| full_replicated_fusion | + trust fusion replicated three times | 20001 | 4.471 | 4.678 | 0.2776 | 214.1 | 2.02 | 0.02287 | 1 |
| full_replicated_fusion | + trust fusion replicated three times | 20002 | 4.541 | 4.899 | 0.2828 | 234.3 | 2.02 | 0.03117 | 1 |
