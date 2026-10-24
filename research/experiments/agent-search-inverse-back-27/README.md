# Search inverse back: positive actual-height construction

**One positive, single-valued back profile is constructed behind the fixed half-H1 front.** Its actual Hermite height and derivative reproduce the original physical H1 source-plane map at the 1,025 design nodes. This is a mathematical construction, not a rendered or accepted Search replacement. No source or target RGB is read.

## Clock, inputs and ownership

The task began at 06:40:37.049 UTC and ends by 07:00:37.049 UTC. The five-minute [checkpoint](checkpoint.json) passed at 06:45:26.037 UTC, before 06:45:37.049 UTC. One solve follows; no prior budget, setting or failed study is restarted.

The shared Snell core is byte-identical to `e695699c`. The one-dimensional Hermite evaluator is the immutable root dependency from `6564032c`. Only own construction records are written. No shared core, height adapter, source, scoring mask, material, style or original case changes.

| Fixed quantity | Value |
| --- | --- |
| Original-L radius | 0.9972124917582454 |
| Original normalization | 89 native pixels |
| Original H1 radial depth and crown | 0.15 and 0.4 |
| Index and background distance | 1.5 and 2 original L |
| Front | Half original radius-scaled H1 actual height |
| Design map | Original flat-front physical H1 Snell map |
| Unknown | One actual back height, not a sampled-coordinate correction |

Original pose and all original source/material conventions remain frozen metadata. The old physical map is a design prior, not evidence that its white-feature placement matches Apple. No miniplayer spline coefficients or tone are imported.

## Exact radial convention and edge limit

The original shared law combines the cubic radial bevel and quadratic crown harmonically. Factoring their common edge zero provides an algebraically identical scalar profile without evaluating indeterminate edge weights.

$$
\begin{aligned}
u&=\frac{r}{R},&A(u)&=1+u+u^2,&C(u)&=1+u,\\
Q(u)&=dA(u)+cC(u),&N(u)&=dc(1-u)A(u)C(u),\\
h(r)&=\frac{N(u)}{Q(u)}.
\end{aligned}
$$

The derivatives in the following block differentiate the polynomials with respect to the normalized scalar coordinate. Physical-radius derivatives retain the exact radius chain rule.

$$
\begin{aligned}
h'(r)&=\frac{N'Q-NQ'}{R Q^2},\\
h''(r)&=\frac{1}{R^2}\left[\frac{N''}{Q}-\frac{NQ''+2N'Q'}{Q^2}+\frac{2N(Q')^2}{Q^3}\right].
\end{aligned}
$$

These are analytic derivatives of the same actual height, not fitted normal fields. The checkpoint compares the interior height and gradient against `HarmonicCircularBack` with the radius chain rule. Finite differences only check the second derivative and optical derivative; they never define a normal.

| Check | Maximum absolute error |
| --- | ---: |
| Height versus original API | 1.388e-17 |
| First derivative versus original API | 1.111e-16 |
| Second derivative versus finite differences | 5.192e-11 |
| Optical ratio derivative versus finite differences | 7.815e-12 |

At the exact edge, the original harmonic helper returns zero weights because both input heights vanish. Those weights are not used as a normal. The factored expression supplies a one-sided optical design limit only. The edge node and its vector Snell calculation are not a regular tangent ray or a rendered pixel.

## Physical inverse equation

Let the fixed front height be half the original height. The shared Snell direction inside glass defines a radial-to-vertical ratio. The unknown back is evaluated at the actual back-intersection radius, rather than at the camera input radius.

$$
\begin{aligned}
F(r)&=\frac{h(r)}{2},&k(r)&=\frac{v_r}{v_z},\\
b(r)&=B(s(r)),&s(r)&=r-k(r)[b(r)+F(r)].
\end{aligned}
$$

The desired source coordinate is computed solely from the original flat-front H1 physical ray. It never uses source color, target brightness or an image displacement field. The desired outgoing unit vector comes from the proposed back point and that fixed source-plane coordinate.

$$
\begin{aligned}
\boldsymbol w&=\frac{(u_{\mathrm{source}}-s,\,0,\,-D+b)}{\sqrt{(u_{\mathrm{source}}-s)^2+(D-b)^2}},\\
m=B'(s)&=\frac{n v_r-w_r}{n v_z-w_z},\\
b'(r)&=\frac{m[1-kF'-k'(b+F)]}{1+mk},\qquad b(R)=0.
\end{aligned}
$$

The actual front derivative also determines the optical ratio derivative. Its sign and radius scaling are checked against shared Snell evaluations before the solve.

$$
\begin{aligned}
\alpha&=\arctan F',&\beta&=\arcsin\!\left(\frac{\sin\alpha}{n}\right),\\
k&=-\tan(\alpha-\beta),\\
k'&=-(1+k^2)\left(1-\frac{\cos\alpha}{n\cos\beta}\right)\frac{F''}{1+(F')^2}.
\end{aligned}
$$

One DOP853 solve integrates backward from the edge limit. Its Snell denominator and radius-map branch remain on the declared admissible branch. Stored back radii are strictly ordered, and every sampled radius-map derivative is positive. This is not an interval certificate of the ODE solution between samples.

## Constructed surface and validation

| Construction result | Value |
| --- | ---: |
| Design nodes | 1025 |
| Maximum intended back height | 0.0529015124883 |
| Global intended slope bound | 0.148486264220 |
| Minimum sampled radius-map derivative | 0.996442245706 |
| Maximum nodal Snell direction error | 5.552e-16 |
| Maximum nodal source-plane error, original L | 3.331e-16 |

The back has exact zero edge height, positive interior node heights and exact zero center derivative. Cubic Hermite interpolation defines one height; the same polynomial supplies its derivative. All endpoint value and derivative queries reproduce their stored constraints exactly. No derivative-only normal adjustment is introduced.

Exact rational Bernstein controls certify nonnegative intended polynomial segments and global height/slope bounds. Positive interior endpoints ensure positive interior height. These are bounds on the intended real polynomial defined by stored coefficients, not enclosures of every floating-point evaluation.

The 1,025-node shared Snell check uses the actual Hermite height and gradient. It establishes nodal consistency only. No dense forward path, actual native silhouette, whole-body source support or image fidelity is certified.

## Prospective primary clearance

The [clearance record](prospective-clearance.json) derives conservative scalar sufficient conditions for a future shared two-graph primary implementation. It does not invoke a tracer or certify a reflected scene.

| Prospective bound | Value |
| --- | ---: |
| Front slope | 0.401118120066 |
| Internal/back clearance | 0.972130482149 |
| Internal/front clearance | 0.939215826322 |
| Back transmission sine bound | 0.411747089216 |
| Outgoing/back no-reentry clearance | 0.760589043722 |
| Direct-front escape clearance | 0.445615175125 |

For completeness, the angular sufficient bounds use the maximum front/back slopes and fixed index. Positive bounds require no assumption that the constructed back is concave.

$$
\begin{aligned}
a_f&=\arctan M_f,&a_b&=\arctan M_b,\\
\delta&=a_f-\arcsin\!\left(\frac{\sin a_f}{n}\right),\\
\theta&=a_b+\arcsin\!\left(n\sin(a_b+\delta)\right),\\
c_{\mathrm{out}}&=\cos\theta-M_b\sin\theta,\\
c_{\mathrm{front}}&=\cos(2a_f)-M_f\sin(2a_f).
\end{aligned}
$$

Background distance exceeds the complete back-height bound. Actual floating-point forward paths and full contributing source kernels would still require their own future gates before any RGB.

## Forward interface and visible limitations

No new shared adapter is implemented. The current generic `HermiteFootprintBack` requires a certified footprint-coordinate interface; bare `HarmonicCircularBack` does not expose that interface. A root-owned circular/radius contract must be agreed before a forward experiment. This construction supplies the one-dimensional actual profile, not a private bypass.

The front is unchanged from the earlier Search split-surface experiment, preserved on the research branch. Therefore its retained direct-front directions still miss the unchanged annular scene on that native lattice. This is an inherited front-only observation, not a new direction calculation. Preserving the old physical map also does not repair its already uncertain feature correspondence.

Missing rim light, unobserved environment, source uncertainty and old historical/protocol disclosures remain. No selected geometry, accepted tone, incident width, masks, style or historical count changes. There is no image or fidelity acceptance.

## Work and decision

| Charged work | Actual | Cap |
| --- | ---: | ---: |
| RHS calls, including 1025 node checks | 2977 | 8000 |
| Scalar profile/derivative queries | 13310 | 20000 |
| Shared Snell points | 7009 | 22000 |
| Bound segments | 1024 | 1024 |
| Design nodes | 1025 | 1025 |
| Solves | 1 | 1 |
| Native grids, source/RGB reads, fields, images and fits | 0 | 0 |

The solve itself uses 1,952 RHS evaluations. The remaining RHS calls are the declared node checks. All four Hermite endpoint/validation query batches are charged before evaluation. Conservative original-API delegate counts and analytic triplet queries share one persistent ledger. No failed solve, retry, parameter change or hidden supplement occurs.

Keep the [profile](back-profile.json), [design nodes](design-nodes.json), [nodal validation](nodal-validation.json) and every limit sealed. Any shared adapter or forward observation requires separate review; none is activated by this result.
