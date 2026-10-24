# Reusable geometric bevel height

The existing bevel law now supplies one actual height over the same convex rounded-rectangle distance coordinate. Four synthetic configurations pass gradient and membership controls; the circle limit agrees with the existing circular bevel. No reference-specific front, source or image is selected.

## Shared surface

The adapter imports the existing scalar kernel. Height, gradient, radial derivatives, section and bounds describe that same surface. The same coordinate object can be shared by front and inferred back.

$$
\begin{aligned}
h(\rho)&=\eta\left(1-\rho^p\right),\qquad 0\le\rho\le1,\quad p\ge3,\\
\nabla h&=-\eta p\rho^{p-1}\nabla\rho,\\
H_{\max}&=\eta,\qquad M\le\frac{\eta p}{R}.
\end{aligned}
$$

The center is regular, the boundary is an explicit zero-height crease, and the global slope bound follows from the unit Lipschitz distance coordinate. Normals are never supplied independently. Only the exact unsmoothed coordinate is accepted.

## Fixed synthetic checks

The [protocol](protocol.json) runs from 10:09:43.974 to 10:21:43.974 UTC. Synthetic depths 0.1 / 0.05 and powers 3 / 8 are fixtures only. The [checkpoint](checkpoint.json), [result](result.json) and [ledger](ledger.json) retain execution times and counts.

| Check | Actual |
| --- | ---: |
| Synthetic configurations | 4 |
| Matched gradient points | 256 |
| Finite-difference height points, including base samples | 1280 |
| Existing circle-delegate points | 128 |
| Analytic direction-certificate points | 64 |
| Additional exact boundary checks | 4 |
| Traced rays, source queries, images and fits | 0 |

The direction fixtures evaluate the fixed-camera reflection formula algebraically; they do not call an optical primitive or trace a ray. Positive powers certify monotone height, so the restricted convex-distance escape certificate accepts this known kernel. No other type restriction changes.

## Research role

This prepares a perimeter-curvature question after the [three-direction review](../miniplayer-front-review-37/README.md). A future candidate must declare its geometry anchors, derive a compatible actual back, then pass complete forward/source checks. Synthetic correctness does not establish visible improvement or measured material behavior.
