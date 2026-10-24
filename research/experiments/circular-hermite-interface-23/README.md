# Circular interface for the shared actual-height tracer

The existing harmonic circle now exposes an explicit radius coordinate to the same Hermite-back and independent-front tracer used by miniplayer. Original harmonic heights, gradients, membership and boundary results remain exact at three tested radii. No ray, source, image or fit is evaluated here.

The [eight-minute protocol](protocol.json) limits this change to an adapter in [the existing height module](../../../reconstruction/hermite_height_back.py). It introduces no circular shader or alternate tracing system. Radius changes lateral coordinates only; height remains in original physical length units.

$$
\begin{aligned}
\rho(x,y)&=\sqrt{\left(\frac{x}{R}\right)^2+\left(\frac{y}{R}\right)^2},\\
\boldsymbol\nabla B&=\frac{B'(R\rho)}{R\rho}(x,y).
\end{aligned}
$$

The actual front delegates directly to the original harmonic height and its derivatives, including the radius chain rule. The constructed Hermite back uses this same footprint object. Its gradient comes from its own actual polynomial; the interface does not supply independent normals or infer a refraction warp.

| Control | Result |
| --- | --- |
| Tested radii | 0.9, 0.9972124917582454, 1.1 |
| Original height/gradient/membership/boundary | Exact at all 54 points per radius |
| Search profile read-only binding | Unchanged first/last hash |
| Hermite gradient finite-difference error | At most 6.36e-12 |
| Height/footprint interface point charges | 827 |
| Rays, RGB, rendered images and fits | 0 |

The point ledger includes two unused reserved final checks. It describes declared interface observations, not every arithmetic operation or nested delegate. One profile construction separately checks its 1024 intended-polynomial Bernstein segments. No performance conclusion follows from these counters.

The [test record](result.json) binds [Search's constructed profile](../agent-search-inverse-back-27/README.md). The test now defaults to that tracked copy; its bytes match the read-only original used as run. Positive height and slope bounds do not establish complete forward paths or source support. A separate bounded forward observation must still check actual ordered roots, normal conventions, every required source footprint and original guards before RGB.

No convex-solid intersector is added or licensed for the Hermite graph. Existing circular closed solids and their membership contracts remain unchanged. The implementation and local scalar controls establish only the shared interface required for the next Search observation.
