# Shared circular solid: fixed nonunit radius

**Geometry contract passes; no image or radiance acceptance.** `CircularHeightSolid` now accepts a positive fixed radius for its existing certified circular backs. The default unit-radius behavior is preserved exactly in the committed-comparator controls.

| Evidence | Record |
| --- | --- |
| Predeclared task and budgets | [Protocol](protocol.json) |
| Budgeted controls and immutable comparator | [Check](check.py) |
| Counts, errors and source hashes | [Result](result.json) |
| Shared implementation | [Geometric optics](../../../reconstruction/geometric_optics.py) |

## One physical solid

The supplied back retains its original height units. The radius rescales its lateral coordinates and therefore changes its physical slopes consistently:

$$
\begin{aligned}
h_R(x,y)&=h_1\left(\frac{x}{R},\frac{y}{R}\right),\\
\nabla h_R(x,y)&=\frac{1}{R}\nabla h_1\left(\frac{x}{R},\frac{y}{R}\right),\\
H_R&=H_1,\qquad M_R=\frac{M_1}{R}.
\end{aligned}
$$

The closed occupancy and its active gradient use that same height:

$$
\begin{aligned}
F_R(x,y,z)&=\max\left(z,-z-h_R(x,y),\frac{x^2+y^2}{R^2}-1\right),\\
\mathcal{S}_R&=\{(x,y,z):F_R(x,y,z)\le0\}.
\end{aligned}
$$

A positive linear coordinate scaling preserves the certified height's concavity. The negative height, flat-front constraint and circular-cylinder constraint are convex. Their intersection remains a convex solid. This argument does not apply to the selected nonconcave expanded-playback spline.

Normals are normalized active gradients of this level function. No independent normal field, displacement or screen-space correction is added. Ambiguous front/back edge creases retain unresolved status.

## Consistent interface

`CircularHeightSolid(back, radius=R)` scales height queries, gradients, footprint occupancy, strict front membership, enclosing box and boundary/crease checks together. Its center and maximum thickness retain the original height units.

Only the already supported certified back classes are accepted. An arbitrary private `RadiusBack` is still rejected; use its underlying supported circular back and the fixed radius parameter instead. This is equivalent geometry, not a type-check bypass.

The supported families are `HarmonicCircularBack`, `CircularBevel` and `RadialCurvatureBack`. Positive radius changes shape aspect relative to fixed thickness. A change of physical normalization must scale all lengths consistently and remains a separate operation.

## Checks and actual work

| Control | Result |
| --- | --- |
| Three back families, four fixed radii | 12 valid configurations |
| Zero, negative, NaN and infinite radii | Four rejected configurations |
| Default unit behavior against committed class | Levels, gradients, fronts and crease status exact |
| Gradient finite differences | Maximum error 2.155e-11 |
| Ordered regular segment exits | All 96 complete |
| Exit residual / bracket maxima | 2.510e-12 / 5.161e-12 |
| Actual height-control / level points | 5,964 / 5,352 |
| Images, source queries and fits | Zero |

The four radii include the frozen Search radius ratio 0.9972124917582454. The controls test both front-to-back segments and back-reflected segments using the actual back normal. Their 48 reflected directions are fixture work, not a rendered or complete multi-bounce scene.

The ordinary intersection solver and Snell/Fresnel functions are unchanged. The control code enforces budgets before evaluation and refuses a repeated result. The original default source is loaded from its pinned Git commit without creating an alternate research renderer.

## What remains incomplete

Search's selected images, geometry, tone, blur, masks and historical counts remain unchanged. The new wrapper has not been adopted into an image or a reflected-path scene. Existing primary source support does not certify secondary endpoints.

Observed environment radiance remains missing. Later transport requires complete ordered events, explicit unresolved paths and appropriate polarization handling. The interface fix supplies none of those observations and does not justify an invented bright border.
