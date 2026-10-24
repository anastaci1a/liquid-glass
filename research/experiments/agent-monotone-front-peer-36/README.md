# Exact monotone-front escape certificate review

**Accept the symbolic additive certificate with strict scope.** The exact nonincreasing spline over the unsmoothed distance-to-inner-rectangle coordinate admits a direct-front escape proof that does not require concavity. Search29's circular specialization satisfies the structural assumptions. Actual launch direction, regularity, primary completeness and scene support remain separate gates.

## Clock and evidence

This read-only review began at 09:45:26.216 UTC on 24 October 2026. The hard deadline is 09:53:26.216, including checks and versioning. Definitions are pinned to immutable `6e12c53a85e786af6761ff0ed9946c591b0d1442`. No shared numerical module, optical primitive, height, fixture, source/cache array or reduction was executed.

Root32 reports a positive independent back construction but no forward image. Root33 stopped its first 15-point fixture at the existing sufficient Lipschitz reflection-escape guard, before native paths or RGB. That stop remains intact: failure of a sufficient inequality is neither a demonstrated reintersection nor physical impossibility.

Root is implementing concurrently. An initial file comparison noticed changing root solver bytes; this review therefore uses immutable Git definitions, not a moving worktree implementation. No merge, shared edit or implementation review of the new runtime code occurred.

## One symbolic proposal: restricted exact escape

Let the closed inner rectangle be convex and let radius be positive. Its distance coordinate and actual front height are

$$
\rho(\boldsymbol x)=\frac{\operatorname{dist}(\boldsymbol x,C)}{R},\qquad
H(\boldsymbol x)=\alpha f(\rho(\boldsymbol x)),\qquad \alpha>0.
$$

Require a nonnegative, nonincreasing height on the covered interval, with exact zero edge. Extend height by zero outside the footprint. The coordinate is convex because distance to a nonempty closed convex set is convex. This is the unsmoothed coordinate actually implemented by the rounded-rectangle footprint, including its circle limit.

At a regular entry, use the same actual graph gradient and upward outward normal. The orthographic camera is downward:

$$
\boldsymbol p=\nabla H,\qquad
\boldsymbol n=\frac{(-\boldsymbol p,1)}{\sqrt{1+\|\boldsymbol p\|^2}},\qquad
\boldsymbol v_{\rm in}=(0,0,-1).
$$

The physical reflected direction follows directly from that normal:

$$
\boldsymbol v_{\rm r}=\boldsymbol v_{\rm in}
-2(\boldsymbol v_{\rm in}\cdot\boldsymbol n)\boldsymbol n,
\qquad
\boldsymbol v_{{\rm r},xy}=\frac{-2\boldsymbol p}{1+\|\boldsymbol p\|^2},
\qquad
v_{{\rm r},z}=\frac{1-\|\boldsymbol p\|^2}{1+\|\boldsymbol p\|^2}.
$$

Because the radial derivative is nonpositive, the horizontal reflected direction is an outward nonnegative multiple of the coordinate gradient:

$$
\boldsymbol p=\alpha f'(\rho)\nabla\rho,\qquad
\boldsymbol v_{{\rm r},xy}=\lambda\nabla\rho,\qquad
\lambda=\frac{-2\alpha f'(\rho)}{1+\|\boldsymbol p\|^2}\ge0.
$$

For positive coordinate, distance to a convex set is differentiable. Its supporting-plane inequality proves the required monotonic direction without tracing:

$$
\rho(\boldsymbol x+t\boldsymbol v_{{\rm r},xy})
\ge\rho(\boldsymbol x)+t\nabla\rho(\boldsymbol x)\cdot\boldsymbol v_{{\rm r},xy}
\ge\rho(\boldsymbol x),\qquad t\ge0.
$$

Thus the graph height never exceeds the entry height along that horizontal ray. Beyond the projected edge the zero extension remains below it. If the actual reflected vertical component is strictly positive, then for every positive time

$$
z(t)=H(\boldsymbol x)+t v_{{\rm r},z}
>H(\boldsymbol x)
\ge H(\boldsymbol x+t\boldsymbol v_{{\rm r},xy}).
$$

The reflected ray strictly clears the front. The front's concavity is unnecessary; the independent back's concavity is also irrelevant to this front-only proof. For the stated nonnegative front and nonpositive back, staying above the front excludes entering that modeled glass through another boundary. Other scene objects and radiance are not certified.

## Center, edge and coefficient assumptions

At zero coordinate, distance may be nondifferentiable. Do not invent its gradient. The spline's exact zero center derivative makes the actual graph gradient zero across the inner rectangle and its boundary. Its reflected direction is vertical and strictly upward. The circle center is the corresponding singleton case.

For the cubic spline, positive knot spans and nonnegative derivative basis functions give a global sign certificate from the derivative control values:

$$
d_i=\frac{3(c_{i+1}-c_i)}{t_{i+4}-t_{i+1}}\le0.
$$

The exact canonical controls are nonincreasing, with the first two equal and final control zero. Their positivity, zero edge and zero center slope are already constructor conditions; monotonicity is an additional condition, not guaranteed by the general spline class. Positive physical scaling preserves all signs. No derivative, height or coefficient array was numerically evaluated here.

A projected edge or interior zero-height crease remains unresolved under the existing boundary convention. The theorem is not permission to assign it a normal. Downward or grazing reflection is also rejected by this certificate. Strict upwardness is equivalent to actual front-gradient magnitude below one, but no launch-specific magnitude was inspected or certified in this review.

## Literal Search29 applicability

Search29 uses the exact `SplineFootprintBack` with equal half-extents and radius. The inner rectangle becomes a singleton, so its coordinate is true radial distance divided by Search radius. Canonical height controls are multiplied by a positive physical scale, then the actual front uses positive `VerticalScaleBack(.5)` and solver scale one.

These operations preserve the same actual height-gradient chain and nonincreasing radial law. They meet the structural certificate. This does not assert every cached or future Search ray is upward, regular, complete, source-supported or visually correct. No Search surface, driver, map, material, source, mask or selected output changes.

## Interface and legacy semantics

Keep the old Lipschitz margin exactly as returned, even when it is nonpositive:

$$
m_{\rm old}=v_{{\rm r},z}-M\|\boldsymbol v_{{\rm r},xy}\|.
$$

Add a distinct per-ray escape-certified flag and method label. The old certificate remains sufficient; the monotone-coordinate proof supplies an additive alternative only when all its structural and regular-upward conditions hold. A negative raw margin must not be overwritten, clamped or relabeled as a positive clearance distance.

| Field or gate | Required meaning |
| --- | --- |
| Raw reflection-front clearance | Original Lipschitz diagnostic, unchanged |
| New escape-certified flag | Success of a specifically identified sufficient proof |
| New method label | Lipschitz, monotone coordinate, or uncertified |
| Regular entry and boundary flags | Existing membership/crease definitions remain unchanged |
| Primary complete | Original ordered-root, transmission and background-plane conditions still apply |
| Source support and environment | Separate; escape creates no radiance or source evidence |

The additive proof must not bypass primary front/back order, outgoing-back clearance, TIR status, polarization restrictions or source-first gates. It does not trace secondary reflections, certify a reflected scene, or retroactively pass root33. A future native execution needs its own declared pin and budget.

## Required rejection cases

| Case | Why this certificate does not apply |
| --- | --- |
| Smoothed joins or other coordinates | The exact convex-distance argument has not been established for them |
| Nonmonotone derivative controls | Outward motion need not lower the front |
| Arbitrary subclasses or overridden methods | A type name alone does not establish the same coordinate and height |
| Changed/mutable control or profile state | Constructor-era certification no longer binds the actual graph |
| Off-normal or perspective camera | Horizontal reflection need not be an outward coordinate-gradient multiple |
| Nonpositive reflected vertical direction | The strict rising-ray argument fails |
| Exact crease or zero thickness | Regular front event is unresolved under the retained contract |
| Independent normal or direction adjustment | The reflection sign derivation no longer follows from the actual height |

A future implementation should recognize exact validated shared types and positive scale wrappers, bind actual profile/control state, and reject unsupported overrides rather than relying on duck typing. No private wrapper or alternate intersector is needed. Only this one certificate/interface proposal is made; no fallback geometry or numerical fixture is proposed.
