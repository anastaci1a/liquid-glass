# Complete RGB integration passes the fixed cap gate

All new physical paths and finite source footprints pass before any RGB sampling. The fixed thirty-six cap pixels are stable between positive quadrature orders 16 and 32: maximum encoded-channel change is approximately 0.00026 of an eight-bit level. This clears a local numerical gate, not full-image convergence or visible-model acceptance.

| Reference | Maximum normalized RGB change, order 16 to 32 |
| --- | ---: |
| Expanded A | 0.00000101629 |
| Expanded B | 0.000000004345 |
| Compact A | 0.000000014643 |
| Compact B | 0.000000002512 |

The [protocol](protocol.json) freezes exactly the cap55 pixels, shallow41/42 surfaces, finite48 light, material and incident sigma 6.75. [Source proof](source-FIRST.json) and [checkpoint](checkpoint.json) precede every changed field and RGB query. [Results](result.json) and [pixel arrays](pixel-colors.npz) retain all three orders. No target residual or parameter fit selects a node.

## Consistent pixel area

The complete pre-foreground pixel integrates clear background over the full pixel, then replaces its covered portion with the encoded glass signal:

$$
\overline{\boldsymbol C}_P=
\frac{1}{|P|}\int_P\boldsymbol C_{\rm clear}\,dA
+\frac{1}{|P|}\int_{P\cap\Omega}
\left(\boldsymbol C_{\rm glass}-\boldsymbol C_{\rm clear}\right)\,dA.
$$

Native integer pixel centers partition the original bilinear source at its knots. Four quadrant-center samples give the full clear integral exactly for that declared interpolant. Positive geometry-partitioned quadrature evaluates the covered correction. No old AA2 lens contribution is mixed with a new reflected component.

The existing response is encoded RGB, followed by decoding, primary power and direct reflection, then re-encoding before pixel integration. This preserves the declared historical operator order; it is not a new claim that the encoded pixel integral is calibrated sensor radiometry. Foreground is not applied in this pixel-only test.

## Validity and accounting

Every actual front/back intersection completes with regular membership. All primary bilinear texels have their full radius 21 incident-kernel support in both original sources. Direct clear nodes and quadrant samples are also known. Conditional mosaic support is not observed hidden photographic truth. All actual encoded clipping counts are zero.

There are 181440 new paths, 7257600 surface-point queries and 145152000 conservative adapter units. Source auditing and sampling each cover 726048 points; mask auditing uses 2904192 lookups. Four incident fields and eight known-mask erosions are separate from 1121600 original constructor mask points. No full composite, score, foreground rasterization or fit runs.

Known area controls and the shared optical core are reused; they are not re-executed as new fixtures. Panel support covers 181440 actual reflected directions. The local integrator requires no source completion, boundary adjustment, independent normal correction or optical-blur change.

The next rendering step must apply one common geometric integration policy to every eligible boundary pixel and audit every new node first. Original AA2 evidence remains immutable. Local convergence does not establish cap-wide, interior-lobe, whole-image or full-radiance correctness.
