# Music Search dispersion: unidentified in the retained evidence

**Assessed; no spectral setting is selected.** The saved residual contains channel and chroma structure, but the colored mosaic, misplaced returns, encoded tone and missing illumination confound it. These observations neither identify a wavelength-dependent refractive index nor establish absent dispersion. No optical calculation or image generation occurred.

This independent block began on 24 October 2026 at 02:08:01.661 UTC, after foreground commit `033971b3` was pushed and remote-verified. Its deadline is 02:18:01.661, including checks and versioning. The Search ceiling remains 04:25:20.608. See [protocol](protocol.json), [direct reductions](result.json) and [first-read hashes](first-read-hashes.json).

## Frozen state and counted image-plane work

The selected state is original H1 D2, incident sigma 6.75/radius 21, AA2, accepted shared neutral tone, original fixed vector/style and shadow zero. The rejected widths and shadow strengths are not substituted. The original source mosaic, target, known mask, scoring masks and four defect rectangles remain unchanged.

| Rectangle | Original-frame bounds | Fully covered original glass pixels per reference |
| --- | --- | ---: |
| Upper rim | [1440,576,1580,620] | 3,359 |
| Left cap | [1418,630,1455,718] | 2,342 |
| Lower return | [1440,728,1580,764] | 3,215 |
| Glyph | [1467,626,1563,722] | 0 after original foreground exclusion |

Each rectangle reads seven saved fields: native source, target, accepted pre-foreground output, coverage, original glass mask, original foreground mask and known mask. Counting every rectangular pixel, including later exclusions and overlaps, gives 331,408 observations against a 350,000 cap. The retained complete output equals pre-foreground outside the original foreground region; no new compositor is needed.

Both known non-foreground and fully covered original-glass cohorts are reported. Partial pixels remain counted in the broader diagnostic and original scientific guards. Selecting a full-coverage diagnostic subset does not change any score. The glyph rectangle correctly has no dispersion cohort after foreground exclusion; no alternative mask or ink threshold is invented.

Source-plane RGB values are existing unwarped mosaic content. They are not a new optical lookup, reconstructed hidden observation or assumed correspondence to the same target coordinate. Direct adjacent-pixel differences reuse those saved values without smoothing, a filter, cross-correlation or channel-registration fit.

## Direct residual structure

All following values use encoded levels from 0 to 255. Luminance uses the fixed diagnostic weights 0.2126, 0.7152 and 0.0722. Chroma is the remaining RGB vector after subtracting that encoded luminance. Neither quantity is calibrated spectral radiance.

| Reference / full-coverage cohort | RGB RMSE | Luma RMSE | Chroma RMSE | Signed RGB residual |
| --- | ---: | ---: | ---: | --- |
| A upper rim | 22.7356 | 19.2698 | 11.5681 | [-5.7080, 2.6643, 9.0377] |
| A left cap | 21.7458 | 19.8115 | 8.7620 | [-8.0909, -7.5717, -6.7963] |
| A lower return | 17.7499 | 17.6852 | 7.4859 | [-6.4459, -3.2821, 2.7312] |
| B upper rim | 22.5589 | 19.7038 | 12.3062 | [-4.5370, 8.1927, 14.6141] |
| B left cap | 15.1145 | 14.7444 | 7.4036 | [-5.0099, 1.6794, 4.9452] |
| B lower return | 30.2755 | 25.3205 | 17.5639 | [-4.0278, 18.9955, 30.8107] |

The B lower-return channel RMSE values are 10.1303, 30.3292 and 41.5613. This large green/blue excess is compatible with an overly pale, misplaced white feature under the accepted common tone. It does not measure a blue ray displacement. The earlier [correspondence record](../agent-music-search-correspondence-02/README.md) allows lower lettering to contribute conditionally but does not identify the target return.

A's left-cap signed residual is nearly neutral, while B's is not. That difference does not establish absent dispersion on A or a spectral law on B. The backgrounds differ strongly in color and structure, and their target/source correspondence is not independently known.

| Cohort | Target adjacent-luma RMS | Selected adjacent-luma RMS | Target adjacent-chroma RMS | Selected adjacent-chroma RMS |
| --- | ---: | ---: | ---: | ---: |
| A upper rim | 4.0777 | 1.1215 | 2.6152 | 0.5972 |
| A lower return | 5.2717 | 0.1047 | 3.2520 | 0.0619 |
| B upper rim | 4.4736 | 0.8571 | 2.8759 | 0.4709 |
| B lower return | 5.9939 | 0.5069 | 3.7863 | 0.2882 |

The selected image has much less local variation, but missing light and incorrect feature placement confound any PSF inference. Ordinary blur was assessed separately and its fixed alternatives were rejected. Large blur, a nearly neutral crop or low chroma variation does not prove that physical dispersion is absent.

The native source itself is strongly colored. For the lower-return cohorts, source chroma RMS is 63.7230 on A and 53.2520 on B; target values are 39.9942 and 35.5615. These source-plane summaries describe available content, not the incident values of a newly evaluated ray. They demonstrate a substantial color confound without attributing the residual to a unique mechanism.

## Transfer limits and discriminating evidence

The reviewed canonical Search recipe and retained Search experiment records provide no matched spectral-isolation result under this geometry, incident kernel, tone, source and mask scope. Historical empirical RGB coefficients, gamma and output blur are different operators. Results from other colored controls or the clear play lens cannot establish Search's dispersion state.

The source is a conditional temporal mosaic. Its registration, video encoding and unmeasured camera/channel PSFs remain uncertainties. The outline audit also lacks observed front-environment radiance and a complete reflected-path scene. A colored bright rim could mix source color, missing reflection or illumination with transmission; no wavelength-index law is selected from those possibilities.

A useful future discriminant would require an independently supported source feature with reproducible channel displacement in the corresponding transmitted reference feature. The effect must be distinguishable from common positional error, source color, channel PSF/codec and missing light across usable observations. The current lower and upper white returns do not supply that established correspondence.

This identifies missing evidence, not a new search, spectral test or demand for an invented source. No coupled index direction, amplitude, sign or spectral setting is justified now. Dispersion stays unidentified. The selected geometry, incident width, neutral tone, foreground and shadow zero remain unchanged.

## Closure scope

The assessment uses zero rays, heights, direction/Fresnel calculations, optical RGB queries, fields, material filters, rasterizations, composites, rendered images or fits. It performs only the declared saved-pixel reductions and metadata/hash review. No crop, mask, threshold, source or coefficient changes.

After this record is sealed and pushed, only a final-review protocol may be prepared. The final review itself needs its bounded authority. It must cover all eight stages, selected state, clocks, cumulative work, retained negatives and source/provenance limitations. No final media, target rotation or automatic fit follows.
