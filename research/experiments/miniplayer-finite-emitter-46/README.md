# Finite emitter: spatial variation, mixed fidelity

A single finite light plane creates real cap/position variation without changing refraction. Both compact references improve against shallow42, but expanded errors worsen. The current-working and original protected guards still fail. No lighting distance is identified and no family replacement is adopted.

| Reference | Shallow far-field E | Finite-panel E | Result against shallow42 |
| --- | ---: | ---: | --- |
| Expanded A | 8.190509 | 10.898802 | Body/SSIM regressions |
| Expanded B | 7.072735 | 7.405899 | Body and forward-guard regressions |
| Compact A | 22.547641 | 20.143621 | All guards pass |
| Compact B | 21.610871 | 19.342706 | All guards pass |

All four comparisons were inspected. Cap brightness varies more than under the position-invariant angular emitter. The expanded caps become too pale, while compact rim/cap structure and body remain imperfect. Original/current-working guard failures remain in every metric record. Clipping counts are zero.

## Explicit scene and paths

The unchanged actual front position and reflected direction define a forward intersection with a white annular panel. The panel is at global native z885, centered at x960/y540. Its radial emission texture uses the same angular profile as the earlier far-field emitter. Radiance remains four.

$$
\begin{aligned}
t&=\frac{z_{\mathrm{panel}}-p_z}{d_z},\\
\boldsymbol q&=\boldsymbol p+t\boldsymbol d,\qquad t>0,\\
\theta_{\mathrm{texture}}
&=\arctan\!\left(\frac{\lVert\boldsymbol q_{xy}-\boldsymbol c_{xy}\rVert}{z_{\mathrm{panel}}}\right).
\end{aligned}
$$

The texture vector is a panel lookup, never a changed optical direction. Fresnel power, normals, source coordinates and lens geometry are untouched. The same global panel applies to every case; it is not recentered on each icon.

Orthographic camera rays launch at z177, above the glass and below the emitter. The ideal sampling plane is not an occluder. Background pixels remain a frozen emissive plane, so this experiment introduces neither backdrop relighting nor a generated shadow.

The light is an explicit hypothesis, not an observed environment. Later reflected power remains unassigned. This establishes a realizable illumination alternative, not calibrated radiance or full scene completeness.

## Evidence and controls

| Reference | Comparison | Measurements |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-comparison.png) | [Metrics](expanded-a-metrics.json) |
| Expanded B | [Image](expanded-b-comparison.png) | [Metrics](expanded-b-metrics.json) |
| Compact A | [Image](compact-a-comparison.png) | [Metrics](compact-a-metrics.json) |
| Compact B | [Image](compact-b-comparison.png) | [Metrics](compact-b-metrics.json) |

Thirty-two synthetic intersections check analytic plane hits, translation covariance, missed directions and the far-field limit. Four shallow42 pre-foreground, complete-image and score identities pass before candidates. Existing source proof transfers because background paths, kernels and source bytes stay fixed.

The actual panel hit positions and travel parameters are retained for both lengths. [Scene checkpoint](scene-checkpoint.json), [identity checkpoint](checkpoint.json), [bindings](bindings.json), [ledger](ledger.json) and [result](result.json) distinguish the claims.

## Clock and work

The [protocol](protocol.json) starts at 11:44:21.671 UTC and ends at 12:04:21.671. Science finishes at 11:45:20.875. Work includes 1487085 explicit reflected light-plane segments and the same number of old angular-emitter evaluations. No new lens ray, source RGB query, field, filter or fit runs.

Four candidates, four identities, four Study constructors, 1121600 mask points, eight scores, forty metric Gaussians and eight metric erosions run. Lens/source coordinates are never replaced by the lighting calculation.

A separate farther scale/distance setting can distinguish parallax strength while keeping apparent emitter shape and radiance fixed. It must retain this result and every original guard rather than retuning light per control.
