# Raised-perimeter primary geometry checkpoint

The single prescribed back passes its global primary-path bound and bounded geometry controls. Its actual height produces outward transmitted directions in the central interior band and inward directions in the outer band. This is a geometric discriminator only. There are no native grids, source queries, images, fits or fidelity acceptance.

The declared clock is 20:36:09–20:46:09 UTC on 23 October 2026. Main controls completed at 20:39:09. The original refraction deadline remains 21:10:40.688. No parameter or distance was adjusted. The pinned shared numerical code remains unchanged; the lead's broader primary-height certificate was reviewed read-only.

## One height and its exact gradient

The existing crowned footprint, full level gradient, softness and poses are preserved. Inside the footprint, the prescribed heights are

$$
h_1=0.4(1-T)(0.1+T),\qquad
h_2=0.4\left(1-\frac{x^2}{a^2}\right),\qquad
h=\frac{h_1h_2}{h_1+h_2}.
$$

Their actual gradients are

$$
\nabla h_1=0.4(0.9-2T)\nabla T,\qquad
\nabla h_2=\left(-\frac{0.8x}{a^2},0\right).
$$

The shared harmonic operator supplies both weights, giving

$$
\nabla h=
\frac{h_2^2}{(h_1+h_2)^2}\nabla h_1+
\frac{h_1^2}{(h_1+h_2)^2}\nabla h_2.
$$

The same height and gradient define sections and back intersections. There is no separate normal field, displacement correction or convex-solid assumption. Normal incidence through the flat front and the approved index/background are preserved:

$$
z_{\mathrm{front}}=0,\qquad z_{\mathrm{back}}=-h,\qquad n=1.5,\qquad D=2L.
$$

## Global certificate and regularity

Both component heights are nonnegative inside the frozen footprint. Their maxima and the shared harmonic monotonicity give

$$
0\leq h_1\leq0.121,\qquad
0\leq h_2\leq0.4,\qquad
h\leq\frac{0.121\cdot0.4}{0.121+0.4}=0.0928982726.
$$

The original footprint remains convex: its nonnegative convex longitudinal coordinate composed with the two-dimensional Euclidean norm defines convex sublevel sets. This is a footprint claim, not a claim that the raised-back solid is convex.

The level is smooth at the center, where its gradient vanishes. The harmonic denominator is positive in the interior, so there are no interior joins or center singularities. The front/back crease remains an unresolved boundary; global smoothness across that crease is not asserted. At exact long-axis poles both heights vanish, and the shared tracer returns unresolved coordinates.

Writing the existing radial level and its certified gradient bound as

$$
\rho=\sqrt{T},\qquad \lVert\nabla\rho\rVert\leq G,
$$

the prescribed bound follows from

$$
\frac{\partial h_1}{\partial\rho}=0.8\rho(0.9-2\rho^2),\qquad
\left|\frac{\partial h_1}{\partial\rho}\right|\leq0.88,\qquad
M=\max\left(0.88G,\frac{0.8}{a}\right).
$$

For both actual cases the bound is strictly subcritical:

$$
G=0.9889003324,\quad M=0.8702322925,\quad
(n^2-1)M^2=0.9466303036<1.
$$

The approved primary-height certificate therefore gives

$$
-d_z-M\lVert\mathbf d_{xy}\rVert
\geq\sqrt{1-(n^2-1)M^2}=0.2310188226>0.
$$

The plane lies at least 1.9071017274L below the deepest possible back. The Lipschitz clearance argument excludes later primary back intersections; convexity of the footprint excludes side reentry. This certificate does not cover reflected paths or a curved front. The nonconvex solid was never passed to the convex ordered-boundary API.

## Bounded controls

| Check | Result |
| --- | --- |
| Full-gradient finite differences | Maximum error 3.23e-11 |
| Mirrors, accepted pose and uniform scale | Pass |
| Original footprint rule on fixture points | Exact |
| Center gradient and interior bands | Pass |
| Exact long-axis poles and circle tangencies | Unresolved, as required |
| Independent direct radial fixture | Maximum path difference 2.23e-16 |
| Sampled post-exit clearance | Positive excess over certified bound |
| Saved central transmitted directions | Outward interior, inward outer, downward throughout |

The circle fixture uses the same radial arithmetic and one actual height:

$$
r=\operatorname{hypot}(x,y),\qquad T=r^2,\qquad
h_2=0.4(1-r^2).
$$

Its direct radial gradient is derived independently from the quotient, not from an independent normal. Sampled clearance controls supplement the global certificate; they do not replace it. [Exact results](geometry-result.json), [saved direction checks](cached-direction-check.json) and sections are retained.

## Budgets, masks and limits

The checkpoint used 1,522 fixture/comparator rays and 9,350 height evaluations. It also read two footprint endpoint derivatives for the initial bound. Cumulative totals are 9,704 fixture/comparator rays, 7,473,600 native rays and four historical experimental images. No new native image was produced.

Existing source, contour parameters and scoring-mask artifacts remain byte-identical. Coverage uses the same footprint rule and matches on the bounded fixture; no prohibited full native coverage grid was regenerated. Source validity for a future changed map remains untested and requires a fresh complete source-first proof before RGB.

The outward band directly addresses the earlier direction limitation as a hypothesis. Its width, strength and visible correspondence to Apple are not established. The source remains modeled with observed confidence zero, and transition-state ambiguity persists. No native image or calibration follows until primary review.
