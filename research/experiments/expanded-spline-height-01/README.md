# Expanded playback: positive spline-height projection

Status: useful geometric initialization, not an image improvement. No RGB queries, images, source changes or adoption.

## Question

The concavity-constrained height left a diagnostic map residual. A fixed raised-perimeter height changed direction but failed visible transfer. This trial asks whether a nonnegative height with unconstrained curvature sign fits the same normal-component diagnostic better, while preserving certified primary paths.

The original rounded footprint and pose remain fixed. One actual cubic spline supplies height, derivatives, sections and Snell normals. Its coefficients are physical heights, not source-coordinate displacements.

## Certificate

For the nonnegative clamped cubic basis,

$$
h(\rho)=\sum_i c_i B_{i,3}(\rho),\qquad
0\leq h(\rho)\leq\max_i c_i.
$$

Positive controls except the final zero keep every regular interior height positive. Equal first two controls give zero radial center slope. Simple interior knots give a twice continuously differentiable radial profile; the rounded footprint's inner joins guarantee only a globally continuous first derivative.

The derivative basis has control values

$$
d_i=\frac{3(c_{i+1}-c_i)}{t_{i+4}-t_{i+1}},\qquad
h'(\rho)=\sum_i d_i \widetilde{B}_{i,2}(\rho),\qquad
\left|h'(\rho)\right|\leq\max_i|d_i|.
$$

For the frozen radius and rounded coordinate,

$$
\lVert\nabla\rho\rVert\leq\frac{1}{R},\qquad
\lVert\nabla h\rVert\leq\frac{\max_i|d_i|}{R}.
$$

Height positivity and the derivative-control bound are global basis properties. They do not depend on sparse image sampling or an assumed concave solid. The [primary-height certificate](../primary-height-certificate-01/README.md) applies; reflected paths remain outside its scope.

## One bounded projection

One start uses 129 saved diagnostic normal positions, fixed index 1.5 and background distance 2.1L. The distance is the previous geometric-projection prior, not a newly fitted Apple measurement. No target RGB enters the objective.

| Measurement | Result |
| --- | ---: |
| Model proposals | 96 |
| Actually traced calibration rays | 11,352 |
| Geometry fixture/comparator rays | 390 |
| Runtime-counted adapter calls, combined | 23,676 |
| Maximum-height bound | 0.138182L |
| Global slope bound | 0.672342 |
| Diagnostic normal MSE | 0.0146079 |
| Earlier concave projection MSE | 0.0211650 |

The best evaluated feasible surface reduces this particular map residual by about 31%. The basis and parameter count also differ from the old curvature model; this does not isolate concavity alone as the cause. It still misses diagnostic structure. The solver stopped at its declared evaluation cap and did not report convergence.

[Every proposed vector](inference.json), feasibility decision and actually evaluated best is retained. Infeasible proposals are not traced. There is no second start, hidden probe or reconstructed probe history.

## Controls and limits

[Checkpoint](checkpoint.json) passes same-height finite differences, mirror/scale/circle comparisons, unit-index identity and miss/crease statuses. Maximum gradient discrepancy is below 8.46e-11.

The [protocol](protocol.json) counts nested boundary adapter calls at runtime before execution. The combined cap is 60,000; the completed count is 23,676. Two additional basis/domain tests make 258 direct scalar-profile checks, with zero adapter calls or rays.

The empirical diagnostic is not optical truth or a guaranteed realizable full two-dimensional map. A lower normal-component residual does not establish better text correspondence, colour, outline or foreground fidelity. The prior compatibility limitations remain.

Whole-body source support and paired RGB observation have not run for this candidate. They require a separately declared phase with complete graph-call accounting; this geometry-only task authorizes neither an image nor a baseline change.
