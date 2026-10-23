# Research working rules

## Scope

Develop reusable, explainable mathematical models of Apple's Liquid Glass. Separate observation, assumption, derivation, numerical verification and perceptual judgment.

## Ownership

| Responsibility | Scope |
| --- | --- |
| Shared-system maintainer | Geometry, ray transport, reusable materials and integration. |
| Control-family researcher | Element adapters, reference cases and bounded evidence. |
| Independent reviewer | Reproduction, guard checks, uncertainty and transfer claims. |

Agree interfaces and file ownership before overlapping edits. Use linked Git worktrees for additional checkouts. Current work is solo; other sessions and session-management tools remain outside task authority.

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

Commit coherent code, configuration and evidence. Check private data and redistribution scope, push every new commit immediately, and verify the remote branch tip.

Keep credentials, session dumps, dependencies and downloaded software packages out of Git. Use indexed artifacts for numerical and media evidence.
