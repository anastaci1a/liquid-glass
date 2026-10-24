# More positive paths cannot repair the current expanded rim

**Conditional obstruction.** Completing observation 85 with additional nonnegative reflected light cannot recover the prior 78 rim error on expanded A or B. More than 97% of current expanded-rim squared error already comes from channels that are too bright. This is not a global impossibility claim about Liquid Glass or other geometries/materials.

## Fixed question

The [first-return observation](../miniplayer-first-return-native-85/README.md) creates an incorrect inset contour. Its [peak-pixel convergence](../miniplayer-return-convergence-86/README.md) does not explain that band as a sampling artifact. This saved-image audit asks whether adding only the remaining positive paths could repair the result without changing its existing prefix.

The source, geometry, tone, scene contribution already present, native 2-by-2 integration and original masks remain fixed. No optical function, source query, field, fit, new composite or score call runs. Original glass pixels are verified outside every actual foreground-layer box.

## Monotone completion bound

In the declared incoherent-path model, new radiance is nonnegative. Encoding and clipping are monotone, and camera weights are positive. Therefore the fixed completed prefix cannot become darker on these unpainted original glass pixels:

$$
\boldsymbol{C}_{\mathrm{completed}}\succeq\boldsymbol{C}_{85}.
$$

Even an unrealistically flexible completion that independently fixes every under-bright channel cannot remove an existing positive residual. For an unchanged cohort, its optimistic error floor is

$$
\mathrm{RMSE}_{\mathrm{floor}}(\Omega)=255\sqrt{
\frac{1}{3|\Omega|}\sum_{p\in\Omega}\sum_c
\left[\max\!\left(C_{85,p,c}-T_{p,c},0\right)\right]^2}.
$$

This lower bound need not be attainable by any real scene. It deliberately gives later paths more freedom than the physical model does.

## Original-rim result

| Reference | Prior78 RGB RMSE | Current85 RGB RMSE | Optimistic completion floor | Existing SSE that cannot be removed |
| --- | --- | --- | --- | --- |
| Expanded A | 16.28825 | 24.16564 | 23.86792 | 97.55% |
| Expanded B | 8.84267 | 15.70287 | 15.47711 | 97.15% |
| Compact A | 18.75851 | 20.89374 | 13.87035 | 44.07% |
| Compact B | 16.45910 | 19.56143 | 14.38569 | 54.08% |

The expanded floors exceed the prior rim errors by wide margins. Thus merely adding nonnegative continuations to 85 cannot satisfy that matched rim comparison. Compact has under-bright regions that could benefit; this bound alone does not rule out their improvement. The shared family still cannot remove its expanded obstruction that way.

These are float64 unweighted RGB reductions on the same stored float 32 images and original rim masks. They are not the weighted aggregate E or replacement native scores. Expanded rim cohorts contain 45,766 pixels each; compact cohorts contain 31,757 each. All original 16/22-pixel partial cohorts are also reported unchanged.

Some positive error predates the first return: prior 78 already has misplaced features and lighting mismatch. The bound includes all current-prefix excess and does not attribute every error to the added branch.

## Inspectable maps

| Reference | Reference, existing prefix and positive-excess map |
| --- | --- |
| Expanded A | [Full-body diagnostic](expanded-a-diagnostic.png) |
| Expanded B | [Full-body diagnostic](expanded-b-diagnostic.png) |
| Compact A | [Full-body diagnostic](compact-a-diagnostic.png) |
| Compact B | [Full-body diagnostic](compact-b-diagnostic.png) |

The third panel is an error map, not a reconstruction. Red indicates positive excess, saturated visually at 32 levels; exact values remain in data. Gray marks pixels outside the original diagnostic glass cohort, including foreground boxes. Their error is not asserted zero. No reference or model pixels are repaired.

## Accounting and timing

[Result](result.json) and per-reference records contain glass/rim/held/interior/partial statistics for both prefixes. Exact positive-channel residual maps and original masks are retained in the four data archives. First/last input hashes match.

| Work | Actual |
| --- | --- |
| Cached numerical payload | 42,788,800 bytes |
| Target RGB pixels decoded | 8,294,400 |
| Residual entries | 6,729,600 |
| Classification/reduction entries | 25,739,760 |
| Diagnostic figures | 4 |
| Rays, source RGB queries, fields, filters, optical evaluations, fits | 0 |

Qualitative planning is conservatively accounted from the earlier 19:59:09 UTC clock anchor. The protocol was declared at 20:12:41 UTC before implementation and array evaluation. The first-case checkpoint passed at 20:15:01 UTC. The computational deadline is 20:27:41 UTC, within the earlier 30-minute outer cap; neither clock is reset.

## Implication and limits

The frozen prefix must change if this expanded-rim regression is to be repaired. Geometry, material, scene interpretation and source uncertainty remain possible explanations; this audit does not identify the correct one. Further tracing may improve mathematical completeness, but it is not a sole visible-fidelity remedy here.

This conclusion assumes nonnegative incoherent additions to the existing prefix. It does not cover destructive cross-path interference, changed absorption/exposure, altered geometry, replaced source or changed compositing. It also does not certify continuous pixel integration or provide a floating-point interval enclosure.

The original native protocol, source estimates, uncertainties, masks, scores, current working selection and historical acceptance counts remain unchanged. No new scene or geometry setting is activated.
