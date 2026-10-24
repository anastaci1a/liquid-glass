# Geometric area integration stabilizes the tested straight-side signal

Twenty-one area/covariance fixtures pass. The twelve fixed upper/lower straight-body pixels have stable direct-reflected signal at Gauss orders 8, 16 and 32. The maximum order16-to32 difference is below one part in ten quadrillion. This is a numerical integration result, not a new optical fit or full-image convergence claim.

| Claim | Evidence and scope |
| --- | --- |
| Known area | Full, empty, tangent, half-covered side, fractional side and complete disk controls pass |
| Covariance | Translation, mirrors, axis exchange and uniform physical scaling pass |
| Membership | All generated positive-weight nodes lie strictly inside the actual ordinary footprint |
| Reflected component | Twelve fixed pixels across both lengths; actual surface normals, Fresnel and panel48 |
| Unverified | Whole cap signal, interior narrow lobes, new-node refracted source support and full RGB integration |

The [protocol](protocol.json), [checkpoint](checkpoint.json), [result](result.json) and [ledger](ledger.json) preserve the exact clock and counters. Controls use 21 fixtures and 60928 total quadrature nodes. Optical evaluation uses 37632 front points, 752640 conservative adapter units and 37632 reflection/Fresnel/panel evaluations each. Source RGB, full composites and fits are zero.

## Rule and implementation

The shared [pixel rule](../../../reconstruction/pixel_quadrature.py) integrates the actual rounded-rectangle intersection with a camera pixel. It splits x at core/cap joins and every crossing with the y partitions, including center cuts. Clipped y intervals receive positive Gauss weights. Cap pieces use a circular parameter and its absolute Jacobian.

$$
x=c_x\mathbin{\pm}\left(k_x+R\cos\theta\right),\qquad
\left|\frac{dx}{d\theta}\right|=R\sin\theta.
$$

The lens-only contribution divides by full pixel area, not covered area:

$$
\overline I_P=\frac{1}{|P|}\int_{P\cap\Omega}I(x,y)\,dx\,dy.
$$

The constant-one test therefore gives fractional coverage. Exterior contributes zero to this component. No weight renormalization, target/error mask, source warp, independent normal adjustment or optical blur change is used. Native-center cuts are numerical partitions, not asserted preimages of refracted-source bilinear knots.

## Limits and next gate

The complete-disk area matches its analytic value; general curved-pixel area still has finite-order error. Positivity alone is not an area or optical convergence certificate. Unrepresentable crease nodes must stop an optical evaluation, not receive fabricated normals. The current fixed nodes are regular.

The [independent method review](https://github.com/anastaci1a/liquid-glass/tree/research/agent-music-search-223/research/experiments/agent-boundary-quadrature-peer-43) identifies the same partition and normalization requirements. Its record is on the separate research branch; integration into the primary record remains pending. The implementation includes every y-partition crossing and does not claim generic source-knot splitting.

No full image mixes these new weights with old AA2 transmission. Original AA2 evidence and scores remain unchanged. A subsequent cap test and fresh finite-source proof at new nodes are required before using this rule for a reconstruction. The same rule must apply to every eligible geometric boundary pixel, independently of reference residuals.
