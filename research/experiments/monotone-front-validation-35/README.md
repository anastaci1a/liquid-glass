# Monotone front escape: fixed fixtures pass

All 120 new fixture/comparator rays pass. Every pre-existing output field is byte-exact for the half-height working front. Full-height fronts complete at indices one and 1.5 for both lengths. Four synthetic applicability/rejection cases pass. No native image or source work runs.

## Exact geometric argument

The footprint coordinate is distance to the inner convex rectangle, divided by radius. Nonpositive spline derivative controls make height nonincreasing. Under the fixed downward orthographic camera, actual reflection travels horizontally outward and strictly upward.

$$
\begin{aligned}
\rho(\boldsymbol x+t\boldsymbol v_{xy})
&\ge\rho(\boldsymbol x)+t\nabla\rho(\boldsymbol x)\cdot\boldsymbol v_{xy}
\ge\rho(\boldsymbol x),\\
h\!\left(\rho(\boldsymbol x+t\boldsymbol v_{xy})\right)
&\le h\!\left(\rho(\boldsymbol x)\right)
<z(0)+t v_z,\qquad t>0.
\end{aligned}
$$

The certificate rejects smoothed joins, nonmonotone splines, uncertified types and nonpositive vertical travel. At a flat plateau it requires zero horizontal travel. The proof assumes the same surface-derived normal and actual fixed-camera reflection; it does not authorize independently supplied directions.

The original Lipschitz margin remains raw, including negative values on newly certified paths. A distinct method identifies the alternative proof. The additive escape-certified flag marks regular entries only; it does not imply exit completion or source support. That metadata flag was added after these numerical fixtures; it changes no numerical calculation.

## Preserved prerequisite and clock

The [earlier comparator setup failure](../monotone-front-escape-34/README.md) remains unchanged. Its thirty reservations are separate. This validation uses the immutable comparator's own wrapper type, then the current wrapper for current code. It does not alter the scientific surface or tracer equations.

The new block starts at 09:49:30.491 UTC and retains the earlier 09:59:33.061 deadline. No additional wall time was allocated. New ray reservations are 120; cumulative reservations including the failed prerequisite are 150. The [protocol](protocol.json), [checkpoint](checkpoint.json), [ledger](ledger.json) and [result](result.json) record the actual scope.

| Work | Actual |
| --- | ---: |
| New fixture/comparator rays | 120 |
| Surface points / conservative adapter units | 4800 / 96000 |
| Bound segments | 4096 |
| Synthetic certificate cases | 4 |
| Native rays, source queries, images and fits | 0 |

These fixtures establish the certificate for the declared class and launches. They do not establish visible fidelity, continuous pixel integration, unknown reflected environment or later branch transport.
