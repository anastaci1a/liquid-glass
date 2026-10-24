# Inset-band peak pixels are numerically stable

**Fixed-cohort convergence passes.** Order 8 versus 16 changes by at most 0.000209 of an 8-bit level. Native 2-by-2 differs from order 16 by at most 0.10881 level. This supports the [visible inset-band negative](../miniplayer-first-return-native-85/README.md) on the tested pixels; it does not establish whole-image convergence.

## Fixed selection and model

Sixteen original-rim pixels per length are selected without target RGB. Four model-defined regions cover upper/lower straight body and left/right caps. Each contributes its four greatest cached first-return pixel means, with deterministic row-major ties. Both original rim masks must include every selected pixel.

The actual front, back, index, distance, source, incident blur, material and annular scene remain those of experiment 85. Only integration order changes. Existing positive camera-pixel quadrature supplies raw weights; there is no renormalization, optical fit, target-based selection or altered normal.

## Result

| Reference | Maximum8-to16 change | Maximum native2-by-2-to16 change |
| --- | --- | --- |
| Expanded A | 0.000209 | 0.097301 |
| Expanded B | 0.000063 | 0.054101 |
| Compact A | 0.000080 | 0.102838 |
| Compact B | 0.000080 | 0.108804 |

Values are maximum RGB channel changes in 8-bit levels over the sixteen selected pixels. All meet the predeclared 0.1-level 8-to-16 criterion. Native 2-by-2 is preserved as the original comparison, not replaced by an optical gain.

The integral and convergence measure use the unchanged encoded-subray integration convention:

$$
\boldsymbol{I}^{(n)}=\sum_j w_j^{(n)}\boldsymbol{c}_j^{(n)},\qquad
\delta_{\mathrm{8,16}}=255\left\lVert\boldsymbol{I}^{(16)}-\boldsymbol{I}^{(8)}\right\rVert_{\infty}.
$$

Every raw weight is positive; the strictly interior pixel weights sum to one within the declared tolerance. Orders 4, 8 and 16 are the only evaluated settings. This is numerical integration of the existing model, not a physical camera-response identification.

## Source and physical paths

Every new primary and first-return path passes before RGB. Both references have fresh finite 43-by-43 incident-kernel plus four-texel bilinear support at every new node. This source proof covers only the selected cohort, not a new whole-image grid.

TIR and remaining internal power are retained. Every actual emitted first-return branch points upward. Both direct-front and emitted-return environment queries are charged. The original source mosaics remain conditional modeled availability, not hidden photographic truth.

## Accounting and retention

| Work | Actual |
| --- | --- |
| Selected pixels / raw pixel rules | 32 / 96 |
| New primary / return segments | 43,008 / 43,008 |
| Surface callbacks / conservative nested units | 3,397,632 / 67,952,640 |
| Polarized interface points | 129,024 |
| Source audits / mask-corner lookups | 86,016 / 344,064 |
| Source RGB / environment queries | 86,016 / 86,016 |
| Incident fields / finite-mask erosions | 4 / 8 |
| Target RGB, composites, images and fits | 0 |

The [result](result.json) retains every pixel difference, 4-to-8 behavior and exact counts. The [selection](selection.json) retains native coordinates and regions. Path archives retain positive rules, actual events, normals, emitted directions, blocked status and remaining power. RGB archives retain each encoded node and its integrated value.

The first source-gate checkpoint completed at 18:50:15 UTC. The same process continued to color evaluation without waiting. The original 19:08:50 UTC deadline is unchanged. Scientific completion is recorded in the result; publication verification is separate.

## Implication and limits

The wrong band survives refinement on these deliberately selected model peaks. Sampling error there is too small to explain the visible discrepancy. Do not fit another light intensity or blur this band away on that basis.

Other pixels, especially critical transitions and the silhouette, are outside this convergence claim. Existing full-image scores, sources, masks, foreground, counts and the working-family selection remain unchanged. No full-pipeline or fidelity acceptance is added.
