# Fixed circle-pixel reflected-component quadrature

**Valid nodes and paths; two nonempty pixels remain numerically unresolved.** Exactly twelve prescribed cardinal-neighbor pixels are evaluated at orders 8, 16 and 32. Inward-left and right-boundary reflected signals do not meet the predeclared 1e-7 successive-order comparison. No higher order, new partition, physical parameter or optical setting is attempted.

## Clock and shared implementation

The task began at 13:02:49.640 UTC on 24 October 2026. Its hard deadline is 13:14:49.640, including publication. The first contributing pixel passes its invariant checkpoint at 13:06:58.006, within five minutes. Short pin c95dd0e2 resolves to `c95dd0e2adca81c4c03f95a15fefde282d6d436c` in the shared repository.

That immutable commit merged cleanly as `bd0dc088`, then was immediately pushed and remote-verified before execution. The shared pixel rule is byte-identical to 46efa5a9. Passed independent circle-area controls44 are reused rather than repeated. Shared front, reflection, Fresnel and finite-emitter functions are imported unchanged; no rule or tracer is copied or forked.

## Frozen factory and twelve-pixel plan

The actual front is the exact shallow Search39 factory: true-circle convex-distance coordinate, radius 0.9972124917582454 in original L89 units, and shared Bevel front from root41 scaled by Search radius divided by family radius. Depth is 0.019857545736401052; power is 33.76385521939009. Height and gradient come from that same front, not independent normals.

The corrected native center is (1511.2043368857017, 672.8753258356955) and native radius is 88.75191176648384. The rule receives those actual native circle dimensions with both core extents zero. Each exact cardinal point is rounded to the nearest integer native center by floor(coordinate + 0.5), then offsets -1, 0 and +1 are applied radially.

| Direction | Inward pixel | Boundary-nearest pixel | Outward pixel |
| --- | --- | --- | --- |
| Upper | (1511, 585) | (1511, 584) | (1511, 583) |
| Lower | (1511, 761) | (1511, 762) | (1511, 763) |
| Left | (1423, 673) | (1422, 673) | (1421, 673) |
| Right | (1599, 673) | (1600, 673) | (1601, 673) |

Every prescribed pixel and all three fixed orders are retained, including empty pixels. No target/source RGB, cached image, refraction path or source query is read. Source samples, width and color are not used to construct this isolated reflection component. In particular color41 is not adopted.

## Actual optical component and escape

At each strictly interior native quadrature point, convert XY to original-L coordinates and evaluate only the actual front height/gradient. Use its unit upward normal and the shared reflection of the downward orthographic camera direction. Shared single-interface air/glass Fresnel power at index 1.5 supplies one unpolarized average; no repeated scalar-power approximation is introduced.

The finite42 panel remains global native z885, center (960, 540), radiance four, unchanged 30/80-degree pattern and ten-degree shoulders. Actual front world XY are the rule's native positions and world z is height times 89. Front points remain below the ideal nonoccluding camera launch plane z177. The panel is not recentered or scaled, and no inverse-square/cosine factor is added.

All actual reflections are outward and strictly upward, and every panel intersection is positive and forward. The fixed radial front is nonnegative and nonincreasing over a convex distance coordinate. Its height cannot rise along those outward horizontal directions, while each ray rises vertically; the reused monotone escape reasoning therefore applies.

Raw global-Lipschitz cone margins reach about -0.2453 and are retained without modification. Failure of that sufficient cone is not treated as a geometry failure. No point has an unresolved boundary flag or zero height. No node is nudged, dropped or given a fabricated normal.

Each pixel's linear reflected signal is the raw positive full-pixel-weight sum. Exterior has zero contribution to this lens-only component. There is no occupied-area normalization, weight clipping, encoded RGB conversion or composition with transmission/foreground. Later reflected power and observed scene truth remain outside scope.

## Fractional coverage and component stability

The table uses order32 raw coverage and linear reflected signal. Differences are absolute reflected-component units, not encoded RGB or image error. The 1e-7 comparison is a predeclared reporting criterion; agreement at these orders is not a rigorous error enclosure.

| Pixel | Raw coverage at order32 | Reflected signal at order32 | Absolute order16-to32 difference |
| --- | ---: | ---: | ---: |
| Upper inward | 0.9999999999999738 | 0.16346140769522216 | 0 |
| Upper boundary | 0.3758812247803658 | 0.06326988753234847 | 1.10e-15 |
| Lower inward | 0.9999999999999738 | 0.1648853110245423 | 0 |
| Lower boundary | 0.12653289617146912 | 0.021477627214138435 | 9.75e-11 |
| Left inward | 0.9999999999999964 | 0.15070752113422797 | 1.2620636091198456e-6 |
| Left boundary | 0.04701783570178749 | 0.008005337404138817 | 2.33e-15 |
| Right inward | 1.0000000000000062 | 0.16309660051544797 | 5.55e-17 |
| Right boundary | 0.4556916071050811 | 0.0744955702002867 | 1.4659900082342192e-6 |

All four outward pixels are empty with zero coverage and signal. They are not counted as evidence of optical convergence. Six of eight nonempty pixels meet the successive-order criterion; inward-left and right-boundary fail it. Their order8-to16 changes are 3.501342425576981e-6 and 2.6397309568076954e-6, respectively. No order64 or adaptive refinement follows.

Tiny raw full-coverage mass roundoff above or below one is preserved, not clamped or renormalized. This is consistent with the peer43 caution that positive finite-order weights do not imply exact geometric mass. Independent circle-area controls44 establish their own declared scope; they do not guarantee convergence of this spatially varying optical integrand.

## Accounting and preserved limits

| Work | Actual |
| --- | ---: |
| Fixed pixel/order calls | 12 pixels, three orders each |
| Generated quadrature nodes | 69,888 |
| Actual front height points, including boundary delegates | 139,776 |
| Reflection / Fresnel / panel points | 69,888 each |
| Conservative adapter units | 1,405,952 |
| Cached direct-reflection scalar comparisons | 0 |
| Refraction, source RGB, filters, composites, images and fits | 0 |

The initial broad node bound was 193,536. Before execution, the exact fixed phase partition gives the tighter reservation 69,888, including four zero-node outward pixels. Each call checks its reservation before optical bodies. Setup is charged 8,192 units; twenty conservative units per contributing node cover nested front/boundary/coordinate/bevel and optical/panel work. No counter reset occurs.

No cached42 scalar comparison is made: exact membership/scene are bound, but a native-pixel correspondence for the compact inside-only panel records is not established. A cache is not invented or reconstructed merely for comparison. Root49's AA2 scores, cap55's sampling conclusion and complete RGB controls56 are not rerun or modified.

Raw rule points/weights, actual normals/directions, panel hit points and scalar signals are retained. Component stability at twelve pixels is not full-circle, full-image, source-support, complete radiance or visual-fidelity acceptance. Selected Search and all historical failures remain unchanged. No subsequent optical setting is activated.
