# A coherent back exists behind the perimeter-slope front

One positive, single-valued back surface is constructed behind the fixed eighth-power front. Its actual Hermite derivative and shared Snell equations reproduce the physical correspondence prior at all design nodes. This is a geometry result, not a rendered improvement, photographic reconstruction or selected model.

| Intended-surface result | Value |
| --- | ---: |
| Front center height | 0.0690909601310 original L |
| Maximum back height bound | 0.0733547240347 original L |
| Back slope bound | 0.2688862952993 |
| Minimum sampled input-to-back radius derivative | 0.9751851076454 |
| Maximum nodal direction error | 7.772e−16 |
| Maximum nodal source-plane error | 9.992e−16 original L |

The [perimeter-front image75](../miniplayer-perimeter-front-75/README.md) moves a visible band outward but also changes refraction. This construction asks whether the same actual front can coexist with transport preservation. The design prior is the canonical flat-front spline map used by inverse17, not target-image correspondence or exact working20 pixel identity.

## Shared physical construction

The unchanged rounded footprint supplies the radial distance from its inner rectangle. Both miniplayer lengths consume one back profile, one front, one index and one background distance. Only major length differs. No source, mask, pose, color, light or foreground value is fitted.

$$
\begin{aligned}
F(r)&=H\left[1-\left(\frac{r}{R}\right)^8\right],\\
z_{\mathrm{front}}&=F(r),\qquad z_{\mathrm{back}}=-B(s),\\
b(r)&=B(s(r)),\qquad k(r)=\frac{v_r(r)}{v_z(r)},\\
s(r)&=r-k(r)\left[b(r)+F(r)\right].
\end{aligned}
$$

The internal direction comes from shared Snell refraction at the derivative of this exact front. The desired source radius comes from the earlier physical flat-front model. Together they determine the required outgoing direction from the proposed back point.

$$
\begin{aligned}
\boldsymbol w(r)
&=\frac{\begin{pmatrix}u(r)-s(r)\\-D+b(r)\end{pmatrix}}
{\sqrt{[u(r)-s(r)]^2+[D-b(r)]^2}},\\
m(r)=B'(s(r))
&=\frac{nv_r-w_r}{nv_z-w_z},\\
b'(r)
&=\frac{m\left[1-kF'-k'(b+F)\right]}{1+mk},\\
b(R)&=0.
\end{aligned}
$$

One backward ODE solve reconstructs the height. The boundary condition uses a one-sided zero-thickness limit; an exact crease is not an actual transmitted ray. The design branch stays nonsingular at evaluated states, and sampled exit radii remain ordered.

## Global surface checks and nodal optics

The final cubic Hermite profile has strictly ordered radii, positive interior heights, exact zero edge height and exact zero center derivative. Shared endpoint heights and derivatives define one C1 surface. Exact-rational Bernstein controls certify nonnegative intended-polynomial height and bound its maximum height and slope.

Normals come only from that polynomial's derivative. Stored node derivatives constrain the same height; they are not an independently sampled normal field. The source map guides construction and is never substituted after tracing.

[Nodal validation](nodal-validation.json) evaluates the actual shared Hermite implementation and shared Snell law. All 1,025 heights/derivatives reproduce their nodes exactly. Of these, 1,024 are strict-interior constraints and one is an algebraic edge limit. The direction and source errors in the table include that explicitly labeled limit.

Sufficient primary-front, primary-back and direct-front-reflection clearance bounds are positive. They do not establish outgoing escape, whole-image support or later reflected transport. Sampled design-radius monotonicity and global polynomial positivity are distinct claims; neither is recast as a complete global ODE error certificate.

## Inspectable evidence

| Evidence | Record |
| --- | --- |
| Fixed question, clock, budget and tolerances | [Protocol](protocol.json) |
| Front-derivative checkpoint | [Checkpoint](checkpoint.json) |
| One numerical solve and termination | [Solver](solver.json) |
| Actual shared-profile data | [JSON](back-profile.json), [CSV](back-profile.csv) |
| Construction constraints | [Design nodes](design-nodes.json) |
| Actual derivative and Snell checks | [Nodal validation](nodal-validation.json) |
| Exact dependencies | [First hashes](first-hashes.json), [last hashes](last-hashes.json) |
| Work and remaining limits | [Result](result.json) |

The solve uses relative tolerance 1e−9, absolute tolerance 1e−11 and maximum step one hundred twenty-eighth of the radius. One solve runs, without smoothing, clipping, node repair, a second front setting or an RGB objective. This does not establish uniqueness among realizable surfaces.

## Clock and accounting

Start is 16:10:06.640 UTC; the hard end is 16:35:06.640. The derivative checkpoint passes at 16:10:12.084, before the five-minute limit. The numerical result finishes at 16:10:16.793. Packaging and publication keep the same clock.

ODE work is 2324 solver evaluations plus 1025 post-solve constraint evaluations, totaling 3349 charged equations. Fifteen finite-difference kinematic checks are separate. Shared Snell points total 7753; scalar profile queries total 12142 and conservative surface units 242840. Polynomial certification covers 1024 segments.

Native rays, source queries, RGB reads, optical images and RGB fits are zero. The exact earlier method is reused with a different actual front. Old profiles, selected working20, historical acceptance and every negative image remain unchanged.

## Required forward question

A new observation must trace its own intersections against this actual height, check the complete physical branches, and audit every whole-body/original-guard finite source footprint before RGB. The new correspondence must be measured against the old paths; it must never be overwritten with the design prior.

Only that forward test can establish whether transport preservation survives interpolation and pixel integration, and whether the outer band improves the reference rim. Incident blur, response, scene, original masks and all partial/foreground guards remain fixed for that question. No full-fidelity or count claim follows from construction alone.
