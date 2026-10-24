# First internal return: ordered paths with TIR

**Sparse geometry and power pass.** All 64 fixed launches reach the actual front without a convex-solid assumption. Each length has 20 blocked transmissions and 12 upward emissions. This is not an outline image or a fidelity improvement.

## Why ordering is valid

The actual surfaces are the unchanged power-eight front and co-designed Hermite back. Both vanish on the same convex projected boundary. The back is nonconvex; the shared convex-only intersector is not called.

For the upward back-reflected direction, both global height clearances are positive:

$$
\mu_{\mathrm{front}}=v_z-M_{\mathrm{front}}\lVert\boldsymbol{v}_{xy}\rVert>0,\qquad
\mu_{\mathrm{back}}=v_z-M_{\mathrm{back}}\lVert\boldsymbol{v}_{xy}\rVert>0.
$$

The front level increases strictly along the original ray. Back clearance also increases, excluding another back event. Leaving the common footprint before reaching the front would require both positive and negative ray height at its zero-height boundary. Therefore the next front event is unique.

The scalar lower bounds are 0.40903 and 0.59060. Actual sampled margins are larger. Bisection uses the original ray, no origin shift, and normals differentiated from the same front height.

## Transmission is a separate question

The [preceding assertion failure](../miniplayer-first-return-82/README.md) incorrectly required universal transmission. The corrected audit uses actual incidence against the tilted normal, retains TIR, and saves outputs before checking interpretation.

| Measurement | Expanded | Compact |
| --- | --- | --- |
| Launches | 32 | 32 |
| TIR/blocked transmissions | 20 | 20 |
| Upward transmitted branches | 12 | 12 |
| Maximum root residual | 2.33e-12 | 2.54e-12 |
| Maximum bracket width | 8.19e-12 | 8.18e-12 |
| Maximum emitted power | 0.036864 | 0.036864 |
| Maximum retained power | 0.0413123 | 0.0413147 |
| Maximum total power error | 6.67e-16 | 3.34e-16 |

Power is normalized to unit incident power. These sparse extrema and equal-launch averages are not image weights or bounds on every native ray. The existing coherency-matrix interface carries basis changes and TIR phase; no repeated unpolarized-average approximation is used.

## Retention and accounting

Both path archives retain selected indices, actual cached input events, new points/normals/brackets, every interface direction, blocked status, coherency matrices and remaining power. The [result](result.json) and [ledger](ledger.json) contain exact numerical values.

This run uses 64 return segments, 192 polarized interface points, 2,496 surface callbacks and 49,920 conservative nested surface units. Source, scene and RGB evaluations are zero. The [cumulative ledger](cumulative-ledger.json) includes both stopped predecessors; their work is not erased.

The expanded checkpoint completed at 18:24:33 UTC and the same process continued compact without waiting. The original outer deadline remains 18:43:01 UTC. Earlier failed checkpoints and the setup failure remain separately recorded.

## Limits and next observation

The first-return calculation is now usable on these certified graphs. It is not a general nonconvex intersector. Later internally reflected power remains unassigned, and no scene radiance has been evaluated.

A bounded native first-return observation can test whether the existing annular environment illuminates these emitted directions. Keep all geometry, incident blur, material, source and foreground fixed. Reuse the unchanged primary source proof; retain every TIR branch and later tail. Do not infer a rim fix from power alone.
