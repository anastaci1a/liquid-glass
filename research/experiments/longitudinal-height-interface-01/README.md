# Reusable longitudinal height modulation

The shared wrapper passes three height-only tests. It changes an actual surface and its complete gradient together. It does not alter tracing, supply independent normals or select a Navigation model.

## Purpose

The transferred footprint spline has no longitudinal curvature in its straight body. A multiplicative height factor provides one geometric discriminator. Neither its sign nor amplitude is identified by the saved images.

The implementation is [LongitudinalHeight](../../../reconstruction/longitudinal_height.py). Its base must provide a nonnegative height, global height/slope bounds and an exact boundary classifier. The footprint must lie within the declared longitudinal half-extent.

## Surface and gradient

For the base height and longitudinal half-extent:

$$
\begin{aligned}
f_\epsilon(x)&=1+\epsilon\frac{x^2}{a^2},\\
h_\epsilon(x,y)&=f_\epsilon(x)h_0(x,y),\\
\nabla h_\epsilon&=f_\epsilon\nabla h_0+
\frac{2\epsilon xh_0}{a^2}\begin{pmatrix}1\\0\end{pmatrix}.
\end{aligned}
$$

The section method evaluates that same height and gradient. The multiplier is strictly positive throughout the footprint under the constructor's restriction:

$$
|\epsilon|<1,\qquad |x|\leq a.
$$

Zero-height edges and unresolved creases therefore retain the base boundary classifier. Zero strength returns the base height/gradient directly. The wrapper changes neither the footprint nor coverage rules.

## Conservative certificate

With base height bound H, slope bound M and absolute modulation e:

$$
\begin{aligned}
e&=|\epsilon|,\\
0\leq h_\epsilon&\leq H_\epsilon=(1+e)H,\\
\lVert\nabla h_\epsilon\rVert&\leq
M_\epsilon=(1+e)M+\frac{2eH}{a}.
\end{aligned}
$$

The caller must separately establish the shared flat-front primary certificate:

$$
(n^2-1)M_\epsilon^2<1,\qquad D>H_\epsilon.
$$

These conditions assume the original convex footprint and normal-incidence flat front. They do not establish convex solid occupancy, reflected-path validity, source availability or fidelity. The constructor does not silently certify optical parameters it never receives.

## Controls and scope

| Control | Result |
| --- | --- |
| Analytic gradient against finite differences | Pass |
| Zero-strength height/gradient identity | Exact |
| Boundary classifier and transverse center section | Exact |
| Mirroring and uniform physical scaling | Pass |
| Section height equals evaluated surface | Exact |
| Invalid strength rejection | Pass |

[Tests](../../../reconstruction/test_longitudinal_height.py) use the existing positive spline at fixed strengths zero and ±0.1. These are software controls, not fitted or accepted optical settings. The finite points do not replace the analytic global bound.

[Protocol](protocol.json) declares a twelve-minute cap and at most 1,000 base height/boundary evaluations. [Results](result.json) record the actual count and completion time. There are zero rays, source queries, images or fits.

No selected model changes. A future observation needs an explicit budget, independently checked actual paths and whole-body/all-guard finite source support before RGB.
