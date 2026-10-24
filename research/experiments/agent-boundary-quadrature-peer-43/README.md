# Positive geometric boundary quadrature: independent review

**Conditionally sound area rule, with missing partition details.** The absolute cap Jacobian, positive nested Gauss weights, full-pixel normalization and zero exterior are correct for a lens-only component. Complete subrectangle breakpoints and independent area/convergence controls remain prerequisites. No integration implementation, optical evaluation, image or score change is accepted by this review.

## Clock and frozen evidence

The review began at 12:34:58.924 UTC on 24 October 2026. Its hard deadline is 12:44:58.924, including checks and publication. Evidence is immutable main `0951e9622121144469d81084f6118a447b5ce46e`, read through Git blobs without merging, hydrating or decoding arrays. Prior own tracked files and sealed manifest bytes are bound separately.

Root49's six AA2 subray identities are exact, but AA4/AA8 direct-reflection tiles are not converged. Its cap differences remain about 0.021 in linear reflected signal. Those are component sampling differences, not RGB errors or optical gains. Its original scores and publication-overrun disclosure remain unchanged. Search42's SSIM and partial failures also remain sealed and unadopted.

## Exact footprint and clipping

Use native units consistently. For half-extents A and B, radius R, center C and nonnegative core extents, define

$$
c_x=A-R,\qquad c_y=B-R,\qquad
u=x-C_x,\qquad v=y-C_y,
$$

$$
\Omega=\left\{(u,v):\max(|u|-c_x,0)^2+\max(|v|-c_y,0)^2\le R^2\right\}.
$$

Require positive radius no larger than either half-extent. Smoothed joins, crowned gauges or other approximate capsules are outside this exact rule. For fixed horizontal coordinate, the vertical half-extent is

$$
g(u)=
\begin{cases}
B,& |u|\le c_x,\\
c_y+\sqrt{R^2-(|u|-c_x)^2},&c_x<|u|\le A.
\end{cases}
$$

For a pixel or subrectangle vertical interval, intersect it with the symmetric true footprint interval. Empty intervals contribute zero, not an invented sample:

$$
\ell(u)=\max(v_{\min},-g(u)),\qquad
h(u)=\min(v_{\max},g(u)),\qquad h(u)>\ell(u).
$$

## Missing partition details

First partition the pixel at applicable core-coordinate joins and the proposed native center cuts. Then find cap intersections with every edge of every resulting subrectangle. Computing intersections only with the original outer pixel edges can miss the new horizontal centerline's cap crossing, where a clipped interval enters, exits or switches its limiting formula.

For any horizontal subrectangle cut at local v, a corner intersection can occur at the following horizontal coordinates when the radicand is valid:

$$
u=\pm\left(c_x+\sqrt{R^2-(|v|-c_y)^2}\right),\qquad
c_y\le |v|\le B.
$$

Include bounding-box entry/exit coordinates and horizontal branch changes at the core extents. Split vertical integration at applicable core y joins, center cuts and any genuinely declared native interpolation knots. Deduplicate coincident partition coordinates without dropping area. In circle or capsule limits, zero core extents coincide with sign branches; do not create overlapping mirrored pieces.

A native pixel-center split resolves knots only for a function explicitly bilinear on that native integer grid. A refracted source texture has knot preimages where its source coordinates cross texel lines; these are generally curved and not the camera pixel center. Root49's analytic direct-reflection/panel signal has no such source-bilinear requirement. Center subdivision is harmless, but not a generic smoothness certificate.

## Cap orientation and positive weights

On either horizontal cap branch, the proposed change of variable is correct:

$$
x=C_x\pm(c_x+R\cos\theta),\qquad
g=c_y+R\sin\theta,\qquad
\left|\frac{dx}{d\theta}\right|=R\sin\theta,\qquad
0\le\theta\le\frac{\pi}{2}.
$$

Right-cap x decreases as the angle increases; left-cap x increases. Sort the transformed bounds and use the absolute Jacobian. The lower boundary uses the negative vertical branch. A y interval may span both halves, so clipping must retain both limits rather than use only the upper arc formula.

Each nonempty clipped interval receives positive Gauss weights multiplied by its affine interval factor. The horizontal cap weights also carry the Jacobian; straight pieces use their ordinary horizontal interval factor. All factors are nonnegative. Native coordinates give weights in native pixel-area units; a normalized-coordinate implementation must retain the corresponding area scale.

The cap-tip Jacobian vanishes while the vertical chord opens with a square root in x.

This substitution regularizes that geometric endpoint; it does not imply a smooth optical signal. At the core join, split the branch explicitly. Zero-area tangencies need no optical event. Exact physical creases remain unresolved; interior Gauss nodes must not be rounded onto them and assigned fabricated normals.

## Normalization and singularity limits

The lens-only pixel value is the covered-domain integral divided by the full native pixel area, not its occupied fraction:

$$
\overline I_P=\frac{1}{|P|}\int_{P\cap\Omega}I(x,y)\,dx\,dy.
$$

For an ordinary unit native pixel, full area is one. Exterior contribution to this component is zero. A constant-one integrand should produce covered area fraction; occupied-area normalization would instead brighten every nonempty sliver to one. That is incorrect. No target/error mask enters the domain or eligibility rule.

Positive finite-order quadrature does not by itself produce exact covered-area mass or guarantee a computed mass below one. Curved interval factors still require convergence or certified area error controls. Do not repair this by renormalizing to occupied area, clipping weights or moving nodes.

Thin slivers whose interior nodes cannot be represented need an explicit numerical/error policy, not silent deletion or epsilon nudging.

## Necessary controls before optical claims

| Control | Required check |
| --- | --- |
| Circle limit | Both core extents zero; exact disk/rectangle areas, quadrants, axial and off-axis pixels |
| Straight sides | Interior/exterior rectangles, half-covered straight edges and exact side joins |
| Translation | Integer shifts and fractional pixel phase; shape translates without target alignment |
| Symmetry | Left/right, upper/lower, axis exchange; orientation must not reverse weight sign |
| Positive area | Nonnegative weights, correct full/empty area, analytic circular-segment area and vanishing slivers |
| Partition topology | Every subrectangle edge/center cut crossing, coincident joins and no overlap or gap |
| Optical convergence | Fixed physical integrand at successive declared rules, including narrow interior lobes |
| Validity/source support | Every actual contributing path and finite-kernel/bilinear footprint, separately certified |

The native lattice's fractional translation legitimately changes individual pixel coverage; the control is exact translated-domain agreement and conservation, not identical values at fixed unshifted pixels. Circle two-dimensional areas require their own controls; the older straight-body one-dimensional substitution is not a proof for circular pixels.

## Component correctness versus fidelity

Apply the same rule to every eligible geometric boundary pixel, independently of residuals, target masks or low apparent energy.

Boundary refinement alone does not establish interior convergence: a narrow reflected lobe, finite-panel texture transition, Fresnel/path branch or refraction caustic can vary sharply within fully covered pixels. Geometry splits address the footprint jump, not every integrand feature.

The panel's angular shoulder transitions and nonlinear source-texture knot preimages are additional integrand issues. They may need separate smooth-piece/error treatment; no parameter search is justified by this review. A quadrature node with unresolved geometry, transmission or radiance is not exterior and must not be silently assigned zero. Unknown source support is a different failure from zero covered area.

Future reflected-component tests can avoid source RGB entirely, but must still verify actual path/normal/panel validity and convergence. Full RGB reconstruction would require new-node source support, including the whole finite incident kernel and four bilinear texels; old AA2 proofs do not automatically transfer. Primary sampling, secondary scene support and radiance completeness remain distinct.

A converged reflected-component integral would not establish full RGB convergence or fix the physically wrong light distribution. Do not mix new component weights with old AA2 coverage/transmission and claim a converged full image.

Original scores, selected models and epochs remain immutable until a separately reviewed integration protocol permits a comparison. No integrator, tracing fork, fixture, image or optical setting ran here.
