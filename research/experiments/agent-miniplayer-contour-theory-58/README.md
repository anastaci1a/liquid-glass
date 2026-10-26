# Smooth shared contours: tangent continuity is not curvature continuity

**The current footprint cannot represent bowed long edges or curvature-blended joins.** Its joins already have continuous tangents; the missing property is continuous curvature. The requested ellipse-plus-disk special case is a coherent first shape checkpoint, with no new fitted amount. It does not preserve the old local cap curvature merely because its disk radius is retained.

Task 58 started at 00:20:48.371 UTC on 26 October 2026 and ends by 00:35:48.371 UTC, including versioning. The checkpoint was saved within four minutes. Source text is pinned to `b496caabad800218e4924a8cd79b59ac66e2d53c`. No numerical imports, arrays, rays, images, fits or implementation ran. Lead's later special-case request uses this same clock.

## What the frozen model represents

The active family records cap_join_width zero, minor half greater than radius and major half as its only member shape variable. `RoundedRectangleHarmonicBack.footprint` takes positive parts outside the inner rectangle and divides their Euclidean norm by radius. Its projected body is an ordinary inner rectangle dilated by a disk.

A unit-speed traversal has a continuous tangent and normal at each straight-to-circle join. It has zero curvature on a straight edge and curvature equal to inverse radius on a circular corner.

Thus it is geometrically tangent-continuous and admits a C1 regular parametrization, but not a C2 one across those joins. There is no visible tangent kink required by this model, yet curvature changes abruptly.

The long top and bottom boundaries are exactly straight. A change in height profile, optical normal or outline gradient cannot turn that fixed projected contour into an outwardly bowed long edge. Smoothness of a three-dimensional height function and smoothness of its two-dimensional support boundary are separate requirements.

The dormant capsule join smoother uses a C2 positive-part approximation and intentionally changes the footprint locally. It requires radius equal to minor half, unlike this frozen family. The active Bevel adapter and monotone-escape helper also reject nonzero join width.

Even if separately admitted, localized join smoothing would retain an exactly straight central region rather than provide a gently bowed full long edge.

## Family A: ellipse plus disk, with the existing extrema

Let A be major half, B the common minor half and R the common disk radius. Use the exact existing special-case mapping requested by lead, with no additional bow parameter:

$$
a=A-R,\qquad b=B-R,\qquad A\ge B>R>0,
\qquad K_A=E(a,b)\oplus D(R).
$$

Here E is the filled centered ellipse and D the filled disk. All design constants except A are common across compact and expanded. The support function and boundary parametrization are:

$$
S_A(\theta)=R+\sqrt{a^2\cos^2\theta+b^2\sin^2\theta},
\qquad \boldsymbol p(\theta)=S_A\boldsymbol n+S_A'\boldsymbol t,
$$

$$
\boldsymbol n=(\cos\theta,\sin\theta),\qquad
\boldsymbol t=(-\sin\theta,\cos\theta),
\qquad \boldsymbol p'=(S_A+S_A'')\boldsymbol t.
$$

For positive a and b, the curvature radius is strictly positive:

$$
q_A=S_A+S_A''=R+
\frac{a^2b^2}{(a^2\cos^2\theta+b^2\sin^2\theta)^{\frac32}}>0,
\qquad \kappa_A=\frac1{q_A}.
$$

The boundary is smooth and strictly convex everywhere, with no cap/body seam. Exact axis extrema remain plus/minus A horizontally and plus/minus B vertically. Opposite sides are related by 180-degree rotation. When A equals B, the inner ellipse becomes a circle and the resulting boundary is a circle of radius B. No circle test ran here.

Retaining R means retaining a Minkowski dilation radius. Every finite positive-axis ellipse contributes positive curvature radius, so the final local radius is not exactly R. In particular, cap curvature depends on A through this same family law. That is a derived consequence of the only length variable, not an independent compact tuning parameter.

### Direction of the contour change

Let I(a) be the horizontal center segment and Q(a,b) the old inner rectangle. Then:

$$
I(a)\subset E(a,b)\subset Q(a,b),
\qquad I(a)\oplus D(R)\subset K_A\subset Q(a,b)\oplus D(R).
$$

The new body lies inside the current rounded rectangle and touches the same four extrema. Between the horizontal segment ends, its upper boundary lies between R and B. Therefore the inward change relative to the old straight long edge is bounded by b, without estimating any pixel amount:

$$
0\le B-y_{K_A}(x)\le b,\qquad |x|\le a.
$$

The middle height stays B, while positions toward the old joins bend inward. Relative to a chord between two off-center points, the middle long edge bows outward.

This is compatible in direction with the reported compact join 92 intensity transitions, but those transitions remain image landmarks rather than a fitted silhouette. No parameter or numeric bow amount is derived from them.

The Hausdorff gap from the old rounded rectangle is also at most b: the old shape is the segment capsule plus a vertical segment of half-height b, while the new shape lies between them. This is a geometric inclusion bound, not a guarantee that any particular image feature will move by that bound.

If B equals R, the inner ellipse degenerates into a segment and smooth strict convexity is lost in the capsule limit. The current pinned case has B greater than R, so the proposed special case avoids that degeneracy. It is not valid to generalize the smoothness statement to all degenerate parameter limits.

## Family B: a strongly convex implicit oval

As one distinct alternative only, fix a common even integer p greater than two and a common lambda strictly between zero and one. Keep B fixed and vary only A:

$$
F_A(x,y)=(1-\lambda)\left[\left(\frac{x}{A}\right)^p+
\left(\frac{y}{B}\right)^p\right]
+\lambda\left[\left(\frac{x}{A}\right)^2+
\left(\frac{y}{B}\right)^2\right]-1.
$$

The filled body is F at most zero. Its Hessian is bounded below by the positive quadratic contribution:

$$
\nabla^2F_A\succeq2\lambda\operatorname{diag}(A^{-2},B^{-2})\succ0.
$$

Its only critical point is the interior center, so the boundary is regular, smooth and strictly convex. Axis extrema remain A and B; long edges have positive rather than exactly zero curvature. At the upper midpoint, for example:

$$
\kappa(0,B)=\frac{2\lambda B}{A^2\bigl[p(1-\lambda)+2\lambda\bigr]}>0.
$$

This family couples cap shape and body bow differently from A. Lambda and p would be shared system constants, not per-reference settings, but the reference evidence here identifies neither.

It does not retain the old radius parameter or give an exact circle merely by setting A equal to B for a general p. Do not silently reuse circle or radius claims.

Family A is the preferred initial checkpoint because its exact requested mapping reuses existing extrema and disk radius without a new fitted amount. Family B is a coherent fallback theory, not an additional authorized trial. Neither is adopted or implemented by this report.

## Consequences for actual geometry

A new projected contour requires an explicit shared inside/crease contract and actual height coordinate. Reusing old height coefficients on a different normalized coordinate generally changes the whole actual height law, not merely a narrow edge. Positions, intersections, sections and gradients must all consume that same new law. No independent optical-normal adjustment is legitimate.

One possible coordinate is the gauge of the new centrally symmetric convex body. For A at least B, both proposed bodies contain the centered disk of radius B, giving a symbolic global gauge bound:

$$
\rho(\boldsymbol x)=\inf\{t>0:\boldsymbol x\in tK\},
\qquad |\rho(\boldsymbol x)-\rho(\boldsymbol y)|
\le\frac{\lVert\boldsymbol x-\boldsymbol y\rVert}{B}.
$$

For an actual height H composed with rho, the chain rule and a sufficient slope bound would be:

$$
\nabla h=H'(\rho)\nabla\rho,
\qquad \lVert\nabla h\rVert\le\frac{\sup|H'|}{B}.
$$

The gauge is not differentiable at its center in general. A vanishing first profile derivative can supply C1 center regularity; C2 needs compatible stronger behavior, such as a flat core or sufficient vanishing second-order terms. Smooth boundary alone does not establish smooth height at the center. Existing Hermite and front profiles need explicit reconsideration under the chosen coordinate.

No gauge evaluation, intersection algorithm or adapter is supplied here. The old coordinate had a flat inner rectangle, so simply interpreting its saved rho as the new gauge would be wrong. Source coordinates, predicted coverage and existing source proofs do not transfer merely because outer extrema remain unchanged.

## Overlay, quadrature and certificates

The post-refraction overlay remains a separate display effect. If its contour alone changes while body geometry stays frozen, label that as an independent projected-overlay hypothesis. If the actual body contour changes, projected support, ray membership and height geometry must change coherently. These are different scopes; neither is activated here.

The current rectangle signed-distance formula and cap-angle convention do not become distances/normals of either new contour. Native overlay widths need actual contour distance. A true signed distance remains 1-Lipschitz, so the mathematical tail argument can be re-established, but the old distance values, fields and active bands are invalid for the changed footprint.

The shared pixel rule explicitly supports only the unsmoothed rounded rectangle. Its straight/core/circular-arc partitions and Jacobian cannot integrate the new contour unchanged. A new positive full-pixel-area rule needs independently justified clipping, joins or extrema, actual curve Jacobian, symmetry/area controls and convergence checks. Dropping old quadrature nodes outside a new shape is not a replacement proof.

Convex projected support can retain the form of ordered graph-root and no-side-reentry arguments, but only with new actual height bounds, strict directional margins, common boundary-zero conditions and complete path checks. Smooth contour curvature does not prove that the full three-dimensional front/back solid is convex. The nonconcave-back restriction remains.

The direct-front monotone escape argument can extend mathematically to a certified convex gauge with a nonincreasing height profile and an actual strictly upward reflected ray. Convexity bounds the coordinate along its outward direction; the rising ray stays above the front. Plateaus, nonmonotone profiles and nonupward directions still require separate treatment.

Existing runtime helper types explicitly restrict this certificate to the old unsmoothed coordinate, so an approved shared extension is necessary.

Any future changed-map rendering requires fresh whole-body/all-original-guard kernel and bilinear source support, including straight misses. Original reference masks and historical scores remain immutable. No claim of recovered Apple geometry follows from a smoothness certificate or the reported intensity landmarks.

## Preservation and checks

The frozen model, all historical failures and untracked task 46 remain unchanged. Root owns reference/join inspection and every shared implementation. This review uses source text and symbolic derivations only, with zero numerical imports, arrays, rays, images, fits or code implementation. Checkpoint and the special-case recommendation were sent before packaging; first/last pinned hashes and documentation/privacy checks accompany versioning.
