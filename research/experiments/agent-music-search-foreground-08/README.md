# Music Search foreground: fixed implementation verified, fidelity unresolved

**Assessed; no foreground change is selected.** The accepted magnifier is a clean geometric trace, not an authenticated Apple SF outline. Its bytes, placement and style match the frozen cases. The large glyph-box error improvement follows a body-tone change with the symbol untouched. Residual shape, weight, pose and material fidelity remain unresolved.

This block began on 24 October 2026 at 02:03:39.277 UTC. Its deadline is 02:13:39.277, including checks and versioning. The overall Search ceiling remains 04:25:20.608. See [protocol](protocol.json), [result](result.json) and [first-read hashes](first-read-hashes.json). No optical operation, rasterization, composite, fit or new image ran.

## Exact input and compositing contract

Both cases use SVG SHA256 `da95145b096fc39155c93be845ba7a50c27bc97184874970d28df684d754aa49`. Its source record labels a clean symmetric vector trace from the official Music video and explicitly sets original-vector identity false. The geometry contains a circular ring and a rounded diagonal handle; it contains no photograph, raster alpha, gray texture or filter.

| Frozen input | Value |
| --- | --- |
| Foreground box | [1467,626,1563,722] |
| Vector placement | [1470.9009527995063,630.7918309178898,1554.4080442125164,714.2989223308999] |
| Accepted color | [0.23791402964793887,0.2092211291437152,0.2142868270726464] |
| Accepted opacity | 0.5959399154311875 |
| Bare layer color/opacity | Black / 0.4187133312225342; overridden by accepted style |
| Ordered layers | One fixed vector layer; no artwork or transmission layer |

Reading `vector_foreground.py` verifies the solid-vector validation and integer-pixel-center placement convention. Its existing implementation rasterizes four times per output dimension, then area-reduces coverage. That describes the frozen method only; this assessment does not invoke it or regenerate alpha.

`Study.apply_foreground` reads the accepted style override, uses the original vector coverage multiplied by opacity, then blends into the current backing. There is no nonlinear style-response entry and no transmission calibration layer in either Search case. Navigation's different foreground response is not substituted.

$$
\mathbf{C}=(1-oA)\mathbf{B}+oA\mathbf{c}.
$$

The expression describes the existing ordered compositor. No output is generated from it here. Body geometry, source, incident sigma 6.75/radius 21, accepted neutral tone and shadow zero remain unchanged. Existing exact identity controls are reused by matching their immutable input/code records, not rerun.

## Saved glyph cohorts and retained errors

The original completed-image foreground guard is the half-open 96-by-96 box, or 9,216 pixels per reference. It measures the symbol and its backing together. The original glass exclusion uses the inclusive box convention. Neither mask is rebuilt, changed or interpreted as an ink-only alpha mask.

Six saved cohorts per reference were inspected: target, unit pre-foreground, unit complete, accepted-tone pre-foreground, accepted-tone complete and geometric coverage. This totals 110,592 native pixel observations, below the 225,600 cap. Full archive decoding is not counted as an optical source query; only these declared cohorts were analyzed.

Every pixel in both glyph boxes has full physical coverage. All 9,216 backing and completed pixels per reference change between unit response and accepted tone, while SVG, style and placement remain identical. This supports attributing the observed aggregate improvement to the changed backing rather than a new foreground shape or coefficient.

| Retained metric | A | B |
| --- | ---: | ---: |
| Unit-body glyph guard RMSE | 39.6060905456543 | 57.5569953918457 |
| Accepted-tone glyph guard RMSE | 13.477656364440918 | 10.046533584594727 |
| Accepted fixed-crop luma RMSE | 11.453292098514266 | 8.476299616270113 |
| Accepted fixed-crop chroma RMSE | 7.049799188670307 | 5.861874306074153 |

Those exact guard and diagnostic numbers are copied from preserved results, not newly fitted scores. The float64 advisory crop RGB values differ slightly from the native float32 guards; both remain labeled. The fixed crop's interior-detail cohort is empty because the original glass mask excludes foreground. No replacement mask is invented.

The previously inspected [A glyph crop](../agent-music-search-neutral-05/a-fixed-crops.png) and [B glyph crop](../agent-music-search-neutral-05/b-fixed-crops.png) retain reference and selected output. Their visible ink and backing differences are not an isolated measurement of authentic symbol weight. Large source-feature, rim-light and body-response errors remain nearby and under the partially transparent symbol.

## Decision and next evidence

The clean trace is a valid implementation input with explicit provenance limits. Exact rendering identity does not establish exact Apple geometry, pose, opacity, color or material. Conversely, a glyph-box residual cannot by itself justify a new font, heavier stroke, tint or opacity because the guard includes the changing backdrop.

No isolated intervention is justified from this record alone. A future proposal would need a named reproducible ink-edge or material discrepancy separable from the current backing and illumination errors, using independent retained evidence. This is a missing identification prerequisite, not a request for new font searches or a fitted screenshot matte.

Foreground fidelity remains unresolved, not absent or satisfactory. The assessment changes no input, coefficient, mask, historical count or accepted component. After this record is sealed and pushed, the independently authorized saved-dispersion block starts with its own actual clock; no unused time transfers.
