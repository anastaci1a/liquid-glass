# Research method

## Physical model

Use explicit surfaces, camera/view geometry, indices, background placement and complete ray paths. Intersections, normals and visualized sections must use the same geometry.

Empirical maps may diagnose or initialize a solid. They do not authorize independent normal corrections, residual warps or sampled-pixel adjustments.

| Convention | Value |
| --- | --- |
| Scale | Fixed minor half-extent, denoted by `L`. |
| Image axes | x right; y down |
| Depth | Positive toward viewer; front at zero; solid behind it. |
| Background | Parallel plane at declared distance behind the front. |

See the [geometric contract](../../guide/geometric-optics.md) for certificates and implementation scope.

[Pass budgets, checkpoints and rotation](passes.md) define the operational research cycle. The [current refinement sequence](refinement-sequence.md) sets target order.

Ordinary material blur filters the incident background before tracing its sampled appearance. Initialize from each element’s historical softness, then refine. Keep antialiasing separate.

## Isolated pipeline

| Stage | Question |
| --- | --- |
| Refraction | Do source features follow the correct geometric paths? |
| Blur | Is material softness correct, independently of sampling? |
| Color | Is the shared material response plausible? |
| Outline | Do boundary light and geometry agree? |
| Shadow / glow | Does generated exterior behavior improve without guard regressions? |
| Icon shape / material | Is original foreground geometry and response correct? |
| Dispersion, where supported | Is spectral transport independently identifiable? |
| Final review | What improved, failed, transferred or remains uncertain? |

Use real wall-clock blocks and fixed trial budgets. Review after at most three substantive hypotheses, including rejects. Stop at the declared limit; do not manufacture a numerical pass.

## Evidence

Visible reference agreement is primary. Record exact crops, local and overall measurements, source confidence, failures and uncertainty. Preserve original reference/background guards.

Mathematical correctness, visual fidelity, shared-model transfer and performance are separate claims. Reuse valid unchanged evidence; avoid repeated final-media generation during unresolved research.
