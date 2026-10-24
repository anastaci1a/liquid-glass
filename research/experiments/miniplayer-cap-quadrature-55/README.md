# Cap integration recovers missed fractional reflection

The thirty-six fixed cap pixels have a maximum order16-to32 direct-signal difference below ten parts per billion. Original AA2 misses a nonzero reflected contribution in one expanded edge pixel. The compact cap also has a material fractional-coverage error under uniform sampling. This is a numerical correction, not new optical fidelity.

| Fixed boundary pixel | Covered fraction | Original AA2 signal | Uniform AA8 signal | Partitioned order32 signal |
| --- | ---: | ---: | ---: | ---: |
| Expanded (1601, 413) | 0.12317758 | 0 | 0.02122103 | 0.02090123 |
| Compact (1394, 673) | 0.54048921 | 0.08359165 | 0.08365223 | 0.09055187 |

Values are linear direct white-reflection components, not encoded RGB or full-image error. Full pixel area remains the denominator. No weight renormalization or target-dependent correction is used. Exact physical surface, normal, Fresnel power and world-space panel48 generate the integrand.

The [protocol](protocol.json) selects two geometric anchors per length: the rightmost point and upper-right arc at forty-five degrees. Each receives a fixed three-by-three pixel neighborhood and exactly three quadrature orders. [Results](result.json) retain all masses and signals, including empty pixels. The [first cap checkpoint](checkpoint.json) passed within its five-minute cap.

The rule reuses [known-area controls54](../geometric-pixel-quadrature-54/README.md). All contributing nodes are strictly inside and have positive actual front height; normals and forward panel intersections are valid. No unresolved crease is assigned color. The maximum order16-to32 signal difference is 0.000000009710 on expanded; compact is below 0.000000000000007.

## Accounting and limits

There are 181440 quadrature/front/reflection/Fresnel/panel points and 3628800 conservative adapter units. The cached comparison reads 54 scalar direct-signal values. It repeatedly decodes 54 small 576-value float64 tiles, totaling 248832 array payload bytes; this decoding was not a separately capped as-run category. The scalar counter remains unchanged.

Source RGB, full composites and fits are zero. No new surface, lighting strength, source or mask is tested. Original AA2 images and scores stay immutable. The selected tests demonstrate component convergence at fixed pixels, not a global integration certificate.

Full RGB needs actual refracted paths and finite source/kernel support at every new quadrature node. It also needs a consistent clear complement and foreground ordering. Combining this reflected integral with old AA2 transmission would not establish a converged reconstruction. The next bounded gate must test complete RGB integration before changing gallery images.
