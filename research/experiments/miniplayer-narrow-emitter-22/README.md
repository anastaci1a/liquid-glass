# Narrow angular light: thin line, worse boundary fidelity

The fixed narrow emitter produces a thinner visible perimeter, but over-brightens boundary samples and worsens rim error against the held broad-light model on every reference. Expanded partial-boundary error becomes substantially worse. The proposed scene is rejected; no second angular support or radiance is tried.

## One fixed scene question

The [protocol](protocol.json) starts at 06:51:39.588 and ends at 07:11:39.588 UTC. Geometry, primary interface powers, incident blur, common material half-step, source, masks, foreground and shadow zero remain unchanged. Both member lengths share one direction-only environment.

The white angular emitter spans 36–44 degrees from the viewing axis, with half-degree smooth shoulders and radiance eight. These values are declared before evaluation. The [existing scene function](../../../reconstruction/environment_radiance.py) receives actual reflected directions, never pixel positions, distance-to-edge masks or residuals.

Four half-step material identities reproduce exactly before changed candidates. The six shoulder controls pass. Existing whole-body and original-guard source proofs transfer because coordinates and incident kernels do not change. No optical path or source sample is reevaluated.

## Four-reference outcome

| Reference | Held broad-light E | Narrow-light E | Narrow partial RMSE | Display-clipped channels |
| --- | ---: | ---: | ---: | ---: |
| Expanded A | 7.88349 | 8.81586 | 61.59052 | 5616 |
| Expanded B | 6.14943 | 7.63997 | 28.86556 | 28366 |
| Compact A | 20.53188 | 23.64565 | 24.75468 | 1437 |
| Compact B | 19.68186 | 22.62235 | 28.88648 | 874 |

Every reference worsens glass, rim, held, total error, SSIM and original partial-boundary error against the held broad-light state. Interior and foreground values tie that state. Several original selected-family guards also fail. None is waived because the line looks thinner.

The brighter hypothetical scene deliberately permits ordinary display saturation. Counts above describe pre-display over-range channels, not source clipping or silently clamped ray coordinates. This experiment changes no fit-feasibility rule; it performs no fit. The original image guards remain unchanged.

## Inspect the visible difference

| Reference | Comparison | Exact metrics |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-comparison.png) | [Record](expanded-a-metrics.json) |
| Expanded B | [Image](expanded-b-comparison.png) | [Record](expanded-b-metrics.json) |
| Compact A | [Image](compact-a-comparison.png) | [Record](compact-a-metrics.json) |
| Compact B | [Image](compact-b-comparison.png) | [Record](compact-b-metrics.json) |

The line is narrow but too sharp and uneven relative to the reference. Cap texture and interior returns do not improve. Existing two-by-two quadrature resolves only four subrays per native pixel; this is not continuous pixel-area integration. A future sampling diagnostic must remain separate from optical parameter improvement.

## Work and retained limits

| Work | Actual |
| --- | ---: |
| Exact identity / changed composites | 4 / 4 |
| Score calls | 8 |
| Metric Gaussian operations / erosions | 40 / 8 |
| Original constructor mask points | 1121600 |
| Cached scene-direction evaluations, including controls | 2974176 |
| Decoded payload bytes | 931446416 |
| Rays, heights, source queries, filters, Fresnel evaluations and fits | 0 |

The [checkpoint](checkpoint.json), [ledger](ledger.json), [bindings](bindings.json) and [result](result.json) retain exact work and guards. Scene radiance is unobserved, the incident-material response is empirical, and later reflected power remains unassigned. Keep the selected family and previous held material separate. No complete-scene or fidelity acceptance follows.
