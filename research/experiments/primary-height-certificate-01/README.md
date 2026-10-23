# A broader primary-height certificate

Status: analytic primary-path certificate with fixed numerical controls. No new Apple surface, image, fit or fidelity acceptance.

Concavity is sufficient but not necessary for the shared flat-front tracer. A global subcritical height-slope bound already excludes later back or side intersections for its primary orthographic path.

## Assumptions

| Quantity | Requirement |
| --- | --- |
| Footprint | Convex planar domain. |
| Front | Plane at zero; orthographic incidence along negative z. |
| Back | One nonnegative, globally Lipschitz height, differentiable at each regular launch. |
| Normals | Derivatives of that same height. |
| Background | Plane below the maximum back depth. |
| Creases / zero thickness | Unresolved, as in the existing tracer. |

With unit ambient index, write the relative glass index and global bound as

$$
n\geq1,\qquad \lVert\nabla h\rVert\leq M,\qquad
(n^2-1)M^2<1,\qquad D>\max h.
$$

The solid is

$$
K=\left\{(x,y,z):(x,y)\in\Omega,\ -h(x,y)\leq z\leq0\right\}.
$$

The solid need not be convex. The footprint must be convex; these are different requirements.

## Derivation

Normal front incidence leaves the internal primary ray vertical. Its unique graph exit is the back point directly below the launch. At a regular exit define the local slope angle, refracted angle and downward deviation:

$$
\theta=\arctan\lVert\nabla h\rVert,\qquad
\beta=\arcsin(n\sin\theta),\qquad
\phi=\beta-\theta.
$$

The bound makes the transmitted branch real and strictly downward. The deviation increases with the local slope. For its maximum,

$$
\theta_M=\arctan M,\qquad
\phi_M=\arcsin(n\sin\theta_M)-\theta_M.
$$

For any resulting unit exit direction, the downward clearance rate obeys

$$
-d_z-M\lVert\mathbf{d}_{xy}\rVert
\geq \cos\phi_M-M\sin\phi_M
=\sqrt{1-(n^2-1)M^2}>0.
$$

Global Lipschitz continuity now bounds the back beneath the entire outgoing segment, while its planar projection remains inside the footprint:

$$
-z(t)-h(\mathbf{x}_{xy}(t))
\geq t\left(-d_z-M\lVert\mathbf{d}_{xy}\rVert\right)>0,\qquad t>0.
$$

Thus the ray remains strictly below the back. After its projection leaves the convex footprint, the straight projected ray cannot re-enter it. There is no later back or side hit. No concavity assumption appears in this argument.

This is a primary-path proof. It does not certify a curved front, oblique incidence or multiply reflected paths in a nonconvex solid. The existing convex ordered-boundary tracer must not receive such a solid under this certificate.

## Fixed controls

[Protocol](protocol.json) declares a 15-minute cap, 2,048 fixture/comparator rays and 500,000 height evaluations. [Results](result.json) use 1,032 charged rays and 36,120 height evaluations, with no RGB or images.

One decreasing polynomial has changing curvature sign:

$$
h(r)=s\left[0.04(1-r^2)+0.08(1-r^2)^2\right],\qquad s\in\{1,4.5\}.
$$

A second has a genuine raised annulus:

$$
h(r)=0.1(1-r^2)(0.1+r^2).
$$

The global bounds follow from polynomial derivative extrema on the unit disk:

$$
h'_{\mathrm{redistributed}}(r)=s(-0.4r+0.32r^3),\qquad
M_{\mathrm{redistributed}}=0.1721325931647741s,
$$

$$
h'_{\mathrm{annular}}(r)=0.2r(0.9-2r^2),\qquad
M_{\mathrm{annular}}=0.22,\qquad
\max h_{\mathrm{annular}}=0.03025.
$$

All four fixed configurations pass independent Snell-angle comparison, same-polynomial gradient checks and sampled post-exit clearance bounds. The unit-index annular control is identity. The global proof supplies the claim; sampled controls alone would not.

This removes an unnecessary modeling restriction. It does not establish that either polynomial resembles an Apple lens, fixes a return or supports a particular background. Those require separate physical parameters, source proofs and visible comparisons.
