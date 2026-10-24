# Reconstructing a back surface behind a fixed curved front

**A positive, single-valued back profile is constructed without reading image RGB.** Its actual height derivative satisfies the intended source-plane correspondence at all 1,025 design nodes. Dense forward tracing, complete source support and visible validation remain required. This is not a new rendered or accepted model.

| Evidence | Record |
| --- | --- |
| Fixed question, optical parameters and limits | [Protocol](protocol.json) |
| Same-front derivative checkpoint | [Checkpoint](checkpoint.json) |
| One ODE solve | [Solver](solver.json) |
| Actual height and derivative data | [Back profile](back-profile.json) |
| Snell checks using that height derivative | [Nodal validation](nodal-validation.json) |
| Work, bounds and remaining limits | [Result](result.json) |

## Purpose and inputs

The split-surface experiment creates an outer reflection but moves background content. This calculation keeps its curved front fixed and determines a coherent back that preserves the selected physical map. That map is a design prior, not photographic ground truth or permission to warp sampled pixels.

The shared selected spline, radius, index 1.5 and background distance 2.1 original length units are frozen. Both miniplayer lengths must consume the same reconstructed profile. No color, foreground, source, mask or illumination parameter is fitted.

## Actual optical constraint

Let the input radius be measured from the fixed inner rectangle. The front is half the selected height. The unknown back height is evaluated at the actual back-intersection radius.

$$
\begin{aligned}
F(r)&=\frac{h_{\mathrm{selected}}(r)}{2},\\
z_f&=F(r),\qquad z_b=-B(s),\\
b(r)&=B(s(r)),\qquad k(r)=\frac{v_r(r)}{v_z(r)},\\
s(r)&=r-k(r)\left[b(r)+F(r)\right].
\end{aligned}
$$

The internal direction comes from shared Snell refraction at the actual front gradient. The desired source-plane location comes from the selected physical model. It determines the outgoing direction from the proposed back point.

$$
\begin{aligned}
\boldsymbol{w}(r)
&=\frac{\left(u(r)-s(r),\,-D+b(r)\right)}
{\sqrt{\left(u(r)-s(r)\right)^2+\left(D-b(r)\right)^2}},\\
m(r)=B'(s(r))
&=\frac{n v_r-w_r}{n v_z-w_z}.
\end{aligned}
$$

Differentiating the actual intersection relation gives one ordinary differential equation. The denominator must remain on the declared nonsingular branch.

$$
\begin{aligned}
b'(r)&=\frac{m\left[1-kF'-k'(b+F)\right]}{1+mk},\\
b(R)&=0,\qquad s'(r)>0.
\end{aligned}
$$

The edge condition uses the one-sided optical limit. An exact zero-thickness crease is not treated as a transmitted ray. The source map and normals are never substituted after actual tracing.

## One constructed physical surface

The ODE solve uses 2,525 solver evaluations. Post-solve node checks bring the charged equation total to 3,550. The back-radius mapping stays ordered; its minimum sampled derivative is 0.96627. The resulting Hermite height is positive inside, zero at the edge and has exactly zero center derivative.

| Intended-surface bound | Conservative value |
| --- | ---: |
| Maximum back height | 0.0727170633252 |
| Maximum slope | 0.393433531918 |
| Maximum nodal direction error | 6.662e-16 |
| Maximum nodal source-plane error | 8.882e-16 original length units |

Cubic Hermite interpolation defines a single height function. Its analytic derivative supplies every future back normal; the stored node slopes are constraints on that same polynomial, not a separate shading-normal field.

Exact rational Bernstein controls bound the intended polynomial's nonnegativity, height and derivative. Adjacent pieces share endpoint height and derivative data, giving a coherent C1 profile. Those bounds do not enclose every floating-point evaluation or establish uniqueness among all possible lens designs.

## Accounting and decision

Nodal validation supplements two initially uncharged vectorized Hermite checks. The conservative totals are 14,795 scalar profile queries and 8,155 shared Snell points, within the declared 20,000 and 10,200 limits. The original ledger remains unchanged; no solve is repeated.

There are zero native image-grid rays, source queries, images or RGB fits. The profile is a candidate actual surface, not a refraction-map patch. A separate forward experiment must trace its own intersections and audit whole-body/all-guard finite source footprints before sampling.
