# What each mechanism costs (plan section 55)

Generated from `rows.jsonl`; regenerate, never edit.

| arm | description | seed | tick_ms_p50 | tick_ms_p95 | cpu_seconds | rss_mb | messages_per_device_tick | memory_read_ms_p50 | device_tpr |
|---|---|---|---|---|---|---|---|---|---|
| full | every mechanism | 20000 | 3.451 | 5.674 | 0.2648 | 130.6 | 2.02 | 0.02742 | 1 |
| full | every mechanism | 20001 | 3.425 | 3.566 | 0.2367 | 151.7 | 2.02 | 0.02125 | 1 |
| full | every mechanism | 20002 | 3.427 | 3.601 | 0.2373 | 171.8 | 2.02 | 0.02154 | 1 |
| full_mediated | + mediated memory access (in-process broker) | 20000 | 3.498 | 4.733 | 0.2537 | 193.1 | 2.02 | 0.05446 | 1 |
| full_mediated | + mediated memory access (in-process broker) | 20001 | 3.495 | 3.622 | 0.2383 | 213.2 | 2.02 | 0.04642 | 1 |
| full_mediated | + mediated memory access (in-process broker) | 20002 | 3.476 | 3.65 | 0.2395 | 233.2 | 2.02 | 0.04683 | 1 |
| full_mcp | + mediated memory access over MCP | 20000 | 4.063 | 5.308 | 0.2673 | 274.6 | 2.02 | 0.7527 | 1 |
| full_mcp | + mediated memory access over MCP | 20001 | 3.977 | 4.249 | 0.2512 | 294.9 | 2.02 | 0.6083 | 1 |
| full_mcp | + mediated memory access over MCP | 20002 | 3.976 | 4.185 | 0.2495 | 315.3 | 2.02 | 0.5946 | 1 |
| no_memory | - immune memory | 20000 | 3.423 | 3.513 | 0.1987 | 335.3 | 2.02 | — | 1 |
| no_memory | - immune memory | 20001 | 3.424 | 3.561 | 0.1998 | 356.1 | 2.02 | — | 1 |
| no_memory | - immune memory | 20002 | 3.422 | 3.531 | 0.1993 | 376 | 2.02 | — | 1 |
| no_sharing | - fleet-level correlation | 20000 | 3.333 | 3.576 | 0.2386 | 396.8 | 2.02 | 0.02108 | 0 |
| no_sharing | - fleet-level correlation | 20001 | 3.31 | 3.48 | 0.2356 | 416.6 | 2.02 | 0.02096 | 0 |
| no_sharing | - fleet-level correlation | 20002 | 3.283 | 3.462 | 0.2337 | 436.4 | 2.02 | 0.02063 | 0 |
| equal_weighting | - reliability weighting | 20000 | 3.447 | 4.631 | 0.251 | 457.2 | 2.02 | 0.02283 | 1 |
| equal_weighting | - reliability weighting | 20001 | 3.459 | 3.59 | 0.2376 | 477.3 | 2.02 | 0.02092 | 1 |
| equal_weighting | - reliability weighting | 20002 | 3.434 | 3.573 | 0.2369 | 497.3 | 2.02 | 0.02058 | 1 |
| no_quorum | - quorum on memory writes | 20000 | 3.439 | 4.732 | 0.2516 | 517.3 | 2.02 | 0.02775 | 1 |
| no_quorum | - quorum on memory writes | 20001 | 3.483 | 3.636 | 0.2417 | 537.3 | 2.02 | 0.0235 | 1 |
| no_quorum | - quorum on memory writes | 20002 | 3.432 | 3.599 | 0.2397 | 557 | 2.02 | 0.02046 | 1 |
| no_recovery | - self-healing | 20000 | 3.258 | 4.523 | 0.2431 | 577 | 2.02 | 0.02587 | 1 |
| no_recovery | - self-healing | 20001 | 3.253 | 3.351 | 0.2295 | 597.2 | 2.02 | 0.02058 | 1 |
| no_recovery | - self-healing | 20002 | 3.242 | 3.414 | 0.2293 | 617.2 | 2.02 | 0.02062 | 1 |
| binary_zt | none of it: a per-report policy decision | 20000 | 2.946 | 3.146 | 0.1837 | 636.9 | 2.02 | — | 0 |
| binary_zt | none of it: a per-report policy decision | 20001 | 2.948 | 3.173 | 0.1839 | 656.4 | 2.02 | — | 0 |
| binary_zt | none of it: a per-report policy decision | 20002 | 2.963 | 3.167 | 0.1841 | 676.3 | 2.02 | — | 0 |
| full+attested | + attested telemetry (device-signed context) | 20000 | 3.488 | 4.741 | 0.9931 | 696.6 | 2.02 | 0.03563 | 1 |
| full+attested | + attested telemetry (device-signed context) | 20001 | 3.544 | 3.699 | 0.9866 | 717.8 | 2.02 | 0.02946 | 1 |
| full+attested | + attested telemetry (device-signed context) | 20002 | 3.491 | 3.677 | 0.9673 | 739.1 | 2.02 | 0.02892 | 1 |
