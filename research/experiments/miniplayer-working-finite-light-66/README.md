# Finite lights do not repair the working family's rim

Both fixed world-space emitter placements fail shared-family guards. The farther plane improves compact body aggregates but leaves expanded cap/light failures. The nearer plane spreads excessive light through expanded ends. Neither recovers the reference's thin bright perimeter; no new light, gain, blur or surface adjustment follows.

| Reference | Current directional E | Plane 885 E | Plane 1770 E |
| --- | ---: | ---: | ---: |
| Expanded A | 7.883487 | 18.431055 | 12.870884 |
| Expanded B | 6.149430 | 11.634386 | 7.750338 |
| Compact A | 20.531876 | 19.905017 | 18.361779 |
| Compact B | 19.681863 | 19.746384 | 18.143070 |

All eight full comparisons were inspected. Some compact tone becomes closer, while return positions and cap shape remain wrong. Expanded light becomes too broad and bright. Original body, SSIM, foreground, exterior, partial-boundary and fixed-crop outcomes remain in [results](result.json) and individual metric records. Aggregate reductions do not waive those failures.

## One shared physical scene

The [protocol](protocol.json) freezes working20 surfaces, traced normals/directions, source coordinates, primary power, common material, incident blur, foreground and masks. Only the direct reflected scene changes. Both members use the same global plane center, radiance and emission texture; neither light is recentered or refitted for compact.

Two annular planes sit at native world heights 885 and 1770, centered at (960,540), with radiance 4. Their texture has 30/80-degree limits and 10-degree shoulders. Plane dimensions scale with height to retain angular appearance from the world origin. This is not a fixed-size distance-only test. The ideal camera launch plane remains 177.

Actual world-space reflection hits come from the retained geometric front point and direction:

$$
t=\frac{H-p_z}{d_z}>0,\qquad
\boldsymbol p_{\rm hit}=\boldsymbol p+t\boldsymbol d.
$$

The unchanged [finite-emitter utility](../../../reconstruction/environment_radiance.py) evaluates radiance at that hit. No inverse-square or extra cosine factor is inserted into specular radiance. No direction, normal, source query or rendered pixel is independently displaced.

## Identity, source and budget

Four pre-foreground, complete-image and native score identities reproduce working20 exactly before new candidates. Retained path/source hashes match [sealed committed inputs](retained-input-hashes-FIRST.json). Every new scene intersection is positive and forward; the actual front remains below camera and emitter. The [checkpoint](checkpoint.json) retains extrema and bindings.

Source validity transfers only because the actual source coordinates, finite incident kernel, data and styles do not change. No optical source lookup or filter is rerun. This does not establish hidden photographic truth, recover the real environment or validate later reflected branches.

Usage is 2974170 new panel intersections, 1487085 cached angular queries, four identities, eight candidates and twelve score calls. The field uses actual front Fresnel power without new Fresnel evaluation. New lens rays, source queries, filters and fits are zero. Actual clipping is zero for every candidate.

Exact unit signals and completed arrays are retained. Full new hit-point arrays are reproducible from the original positions/directions and scene recipe but not archived. Both retain their original global coordinates; no per-reference light parameter is introduced.

The directional baseline and two finite planes complete this scene-placement comparison. No fourth condition is warranted. The public working family stays unchanged. Outline is assessed and unresolved, not omitted or declared satisfactory. Its later reflected power and actual illumination remain unassigned; original AA2 measurements are not continuous-boundary convergence claims.

[Explicit guard regressions](regressions.json) preserve each failed cohort. Geometry, mathematical consistency, visible fidelity and model transfer remain separate claims.
