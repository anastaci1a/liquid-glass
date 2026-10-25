# Research working rules

## Scope

Develop reusable, explainable mathematical models of Apple's Liquid Glass. Separate observation, assumption, derivation, numerical verification and perceptual judgment.

## Ownership

| Responsibility | Scope |
| --- | --- |
| Shared-system maintainer | Geometry, ray transport, reusable materials and integration. |
| Control-family researcher | Element adapters, reference cases and bounded evidence. |
| Independent reviewer | Reproduction, guard checks, uncertainty and transfer claims. |

Agree interfaces and file ownership before overlapping edits. Use linked Git worktrees for additional checkouts. Respect task-specific collaboration limits. Use approved management tools only for explicitly authorized coordination.

## Existing-session communication

Use Sessionsation for authorized session-to-session tasks. Keep the existing visible sessions and isolated worktrees; do not substitute terminal input or launch a replacement helper.

Use Steer Submit for every message in both directions between the lead and researcher. Never use Queue: delayed messages create stale backlogs. Use explicit in-turn Steer for an active turn and immediate Submit for an idle session, under current native guards. If neither is available, report the blocker without a Queue fallback.

Communicate in plain prose only. Do not send diffs, patches, code blocks, file contents, attachments or embedded artifacts. Reference relevant files, modules, commits and reports by name or path instead. Split longer messages into short paragraphs, each covering one point.

A native acceptance receipt confirms delivery acceptance, not execution or completion. Check native working/idle observations and the assigned experiment’s ready flag. Review ready evidence promptly, including when reply scanning is inconclusive. Read-only artifact inspection supports review; tasks and decisions still go through Sessionsation.

### Native recovery and evidence

Distinguish a live native attachment from its terminal host. An unavailable host can block relaunch while the existing native process still supports message recovery. Use current Sessionsation capabilities; never infer that ordinary Queue or Submit can resume a failed turn.

| Observed state | Authorized route |
| --- | --- |
| Idle | Immediate Submit under current guards; never Queue. |
| Working | Explicit in-turn Steer with a freshly resolved turn and runtime; never Queue. |
| Errored or interrupted, process retained | Explicit native Resume with the current previous-turn, runtime and stop-token guards. |
| Process exited | A separately validated launch plan and existing authorization; no automatic replacement session. |

The stop-token key must be present. It may be null only when the current observation supplies no token. Revalidate through Sessionsation; do not guess identifiers or reuse stale preconditions. A recovery message must explicitly preserve expired experiments and define its new bounded task.

Native acceptance, input consumption, execution and completion are separate facts. An explicit start can be rejected because automatic dispatch already consumed the item. Observe the original receipt and exact-turn checkpoints before concluding what ran; do not resend accepted or uncertain input.

Retain the original UUID and request before sending. For contention, inspect the receipt or retry only the identical request when the installed contract permits it. Never create a replacement UUID to bypass an uncertain delivery. Read-only checkpoint association alone is not message-delivery proof.

Keep session identifiers and transport payloads outside the public repository. Record scientific ownership, actual receipt clocks, budgets and evidence in project documents.

## Experiments

- Preserve accepted baselines, reference inputs, masks and negative evidence.
- Follow the [method](../research/method/README.md) and [recording standards](../DOCUMENTATION.md).
- Declare time/evaluation limits, checkpoints and stop conditions before execution.
- Review a hypothesis after at most three substantive proposals, including rejects.
- Judge the named visible defect; disclose local regressions and source uncertainty.
- Derive intersections, normals and sections from the same physical surface.
- Do not introduce independent normal corrections, displacement patches or residual warps.

## Recording

Keep current findings and the next proposed experiment in `research/current/`. Save work in progress with an explicit status and reproducible inputs.

Closing a bounded experiment does not end an authorized research sequence. Resume the agreed next task after status questions or related documentation work unless the user pauses the sequence.

Commit coherent code, configuration and evidence. Check private data and redistribution scope, push every new commit immediately, and verify the remote branch tip.

Keep credentials, session dumps, dependencies and downloaded software packages out of Git. Use indexed artifacts for numerical and media evidence.
