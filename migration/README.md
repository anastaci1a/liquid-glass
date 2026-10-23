# Migration

Research history and substantive local evidence now live in this repository. Localica cutover is prepared in an isolated clone; final merge verification is recorded in `cutover.json`.

## Provenance

| Item | Record |
| --- | --- |
| Original repository | `anastaci1a/localica` |
| Source main for cutover | `05fccdfee194098018856b18f2843bd19f1201b6` |
| Latest imported geometry branch | `research/geometric-playback-222` at `e9fcd3a7` |
| History extraction | 726 source subtree/author/date comparisons; 108 retained branches. |
| Old → extracted commits | `commit-map.tsv`, `ref-map.tsv`, `selected-source-refs.json` |
| Final source file destinations | `cutover-files.json` |
| Local file dispositions | `local-material-manifest.json` |
| Evidence objects and aliases | `../research/evidence/index.json` |
| Validation | `checks.json` |

The first extraction mapped `docs/liquid-glass/` to `docs/`. Subsequent tracked moves separate `guide/`, `lab/` and `reconstruction/`. Original history and IDs remain traceable; no source history was rewritten.

## Local material

Raw arrays, reference excerpts, figures, media, frozen reports, generated publishing snapshots and container-only baseline evidence are indexed and hash-verified. Project-owned source/scripts remain under `research/captures/` where they are historical rather than canonical modules.

Research-related user feedback is distilled into short records, with selected original lines retained as evidence. Unrelated application feedback and private conversation/session transports are excluded.

Downloaded font/software packages, whole original videos, installed dependencies, caches and machine credentials are not project-owned research. Their recorded provenance remains; no unique experiment is discarded as a cache.

## Recovery copies

| Location | Purpose |
| --- | --- |
| `../migration-backups/20261023T005817Z/` | Original refs bundle, dirty patches and filesystem/container snapshots. |
| `../migration-backups/closure-20261023/` | Final read-only inventory and scope checks. |
| `../validation-checkout/` | Actual detached validation worktree. |
| `../cutover/localica/` | Isolated source-cutover clone; active app checkout untouched. |

Captures preserve immutable versions. They do not claim that another session was frozen. The final inventory found unchanged source refs and retained the same substantive dirty research files.

## Boundaries

No app behavior, release, source history rewrite or site deployment is part of this migration. Existing published reconstruction URLs remain served by Localica's historical Pages output.

Sessionsation and helper interaction remain prohibited. Neither session was relocated or controlled. A future session-directory update is an administrative action for Ana, not an unfinished research-file migration.
