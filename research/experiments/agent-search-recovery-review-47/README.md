# Search task 46 recovery review

This is a read-only recovery of public experiment records. Task 46 is not restarted. Its original deadline remains 24 October 2026 at 13:27:44.320 UTC. Recovery task 47 started at 19:35:41.916 UTC and must finish by 19:45:41.916 UTC, including versioning.

## Recoverable evidence

The existing task 46 directory contains exactly three files: `protocol.json`, `first-hashes.json` and `check.py`. Their sizes and SHA256 digests are preserved in `first-inventory.json`. They remain untracked in the existing worktree and are excluded from this recovery commit. No existing file is repaired, moved, staged or deleted.

The protocol preserves the original twelve cardinal pixels, subdivisions 2 and 4, order 16, full-pixel weight scaling, fixed shallow front and finite panel. It records the original clock and caps. The hash receipt records intended dependencies. These are preparation evidence, not a completed numerical result or a verified as-run ledger.

## Durable-record gap

The directory contains no `reservation.json`, `area-controls.json`, `checkpoint.json`, `current.json`, `records.json`, `result.json` or raw quadrature archive. Absence of a checkpoint does not establish that no science ran. The review does not execute the driver, regenerate bounds or reconstruct missing results.

Source inspection finds a concrete durability limitation. Lines 26–29 calculate and assert a static reservation before line 30 writes it. The protected execution block begins at line 39. An earlier import, hash, setup or reservation failure can therefore escape the result-writing `finally` block at lines 63–64. This is a possible failure route, not proof of the historical route taken.

The initial ledger exists only in process memory. Later counters and outputs would be written only if those code paths were reached. Without a durable invocation receipt, traceback, reservation or ledger in the inspected public records, this review cannot certify which calls ran, which assertion failed, actual counts, interruption time or successful completion.

## Accounting and scientific status

| Item | Recoverable status |
| --- | --- |
| Original task 46 start/deadline | Preserved in its protocol |
| Intended settings and caps | Preserved; no cap increase |
| Dependency receipt | Preserved; current-byte matches reported separately |
| Static reservation values | Not persisted; not recomputed |
| Actual numerical usage | Unknown from inspected public records |
| Area fixture outcomes | Unrecoverable from inspected public records |
| Twelve-pixel subdivision results | Unrecoverable from inspected public records |
| Task 45 two unresolved pixels | Remain unresolved evidence; no replacement result |
| Task 47 optical/image evaluations | Zero |

No zero-use ledger is invented for task 46. Its numerical refinement question remains unanswered in the recoverable records. This is a recovery and instrumentation limitation, not an optical negative or evidence that the geometry is invalid. No selected Search state, original score, source confidence or historical count changes.

Task 45 remains separately sealed as `5538fdd0`. The separate miniplayer first-return result 85 and stable peak-pixel quadrature 86 are not imported as Search conclusions. Current shared main is not merged or evaluated.

## Next decision

A next actual scientific question has been requested through Sessionsation before packaging. No new execution is activated here. Any future numerical task needs fresh authority and its own clock; it must preserve task 46 and distinguish intended reservation from measured usage. This review does not implement a replacement driver.

## Review controls

The first and last inventories must match exactly. Only this new recovery folder is staged. Public record hashing and source-text inspection are the only evidence operations. Documentation and private-data checks are recorded separately. Session transport receipts stay outside the repository, and unrelated dirty files remain untouched.
