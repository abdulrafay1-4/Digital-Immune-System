# The MCP server under the attacks the MCP security literature names

Generated from `rows.jsonl`; regenerate, never edit.

| attack | tool | honest | trials | accepted | refused_because |
|---|---|---|---|---|---|
| honest read | recall | True | 1000 | 1000 | — |
| honest proposal | propose | True | 1000 | 1000 | — |
| reader signs as the curator | propose | False | 1000 | 0 | bad_signature 1000 |
| unregistered key claims the curator | propose | False | 1000 | 0 | bad_signature 1000 |
| unregistered caller | recall | False | 1000 | 0 | unknown_caller 1000 |
| signed call altered in transit | recall | False | 1000 | 0 | bad_signature 1000 |
| HIGH claimed after untrusted input | recall | False | 1000 | 0 | provenance_too_low 1000 |
| replay in the same tick | propose | False | 1000 | 0 | replayed_call 1000 |
| replay in a later tick | propose | False | 1000 | 0 | stale_call 1000 |
| read beyond 4 per tick | recall | False | 1000 | 0 | over_call_budget 1000 |
| poisoned label recalled | recall | False | 1000 | 0 | label dropped 1000 |
| honest verdict, signed by the console | adjudicate | True | 1000 | 1000 | — |
| verdict not signed by the console | adjudicate | False | 1000 | 0 | bad_verdict 1000 |
| console's signature moved to another record | adjudicate | False | 1000 | 0 | bad_verdict 1000 |
| verdict relayed by a caller other than the core | adjudicate | False | 1000 | 0 | not_the_core 1000 |
| relayed verdict replayed | adjudicate | False | 1000 | 0 | stale_call 1000 |
| decided record flipped by a later verdict | adjudicate | False | 1000 | 0 | already_adjudicated 1000 |
| verdict for a record that does not exist | adjudicate | False | 1000 | 0 | unknown_record 1000 |
| tool description changed (rug pull) | manifest | False | 1000 | 0 | manifest refused 1000 |
