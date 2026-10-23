# Incident blur: wider candidate, limited visual evidence

The fixed 1.25 multiplier passes every original guard comparison against experimental H1 D2 in both references. The 0.75 multiplier fails. The wider result changes only small existing boundary fragments; it does not recover the broad white returns. It is ready for primary review, not adopted. Historical pass09 and its much better reconstruction remain separate.

The [protocol](protocol.json) permits exactly two coupled widths. [Narrow results](narrow-result.json) and [wide results](wide-result.json) preserve every original glass, rim, held, interior, SSIM, E and exterior metric. Both candidates still fail historical error guards. No geometry, material tone, lighting, shadow, foreground, source or mask changed.

## Clock and pause

The stage began at 20:55:14.384 UTC with a fixed 21:15:14.384 deadline. The original latest stage deadline remains 21:30:40.688 UTC; the total deadline remains 23:50:40.688 UTC. No unused refraction time was transferred.

An explicit [pause](pause.json) began at 20:56:25.179 UTC. [Resumption](resume.json) was recorded at 20:58:37.483 UTC. No optical evaluation had started at the pause. The original deadline was not extended. The narrow pair finished at 21:00:48.492963 UTC; the wide pair finished at 21:01:22.540973 UTC. Packaging consumes the same stage allocation.

## Exact widths and operation order

Historical nominal widths were 4.339320119359 pixels in A and 4.008609810031 pixels in B. The legacy source lookup rounded these to quarter-pixel bins, producing effective seeds 4.25 and 4.00. This experiment multiplies those effective seeds directly. It introduces no new quantization and does not identify an exact common physical material.

$$
\begin{aligned}
\sigma_{\mathrm{trial}} &= m\,\sigma_{\mathrm{seed}},\\
r &= \left\lceil 3\sigma_{\mathrm{trial}}\right\rceil.
\end{aligned}
$$

| Case | Multiplier | Float width, native pixels | Finite radius | Width divided by original minor half extent |
| --- | ---: | ---: | ---: | ---: |
| A | 0.75 | 3.1875 | 10 | 0.0147228637413 |
| A | 1.00 seed | 4.25 | 13 | 0.0196304849885 |
| A | 1.25 | 5.3125 | 16 | 0.0245381062356 |
| B | 0.75 | 3.00 | 9 | 0.015 |
| B | 1.00 seed | 4.00 | 12 | 0.020 |
| B | 1.25 | 5.00 | 15 | 0.025 |

The pinned shared `incident_source_filter` supplies normalized ordinary Gaussian filtering before the cached refraction lookup. Clear subrays reuse the original unfiltered saved samples. Native antialiasing remains two-by-two. Output blur remains zero. This ordinary blur is distinct from dispersion, coverage antialiasing and a physical roughness model.

## Source-first support and isolation

The [largest-kernel proof](source-proof-FIRST.json) passed for both references before RGB. It covers every lens subray, every original guard dependency and all four bilinear texels. Both stored float64 positions and float32 OpenCV map positions were checked. Smaller radii follow by support inclusion. Undefined required support would have stopped the setting without repair.

The source remains modeled with observed confidence zero. Defined support does not validate hidden photographic content. Both full grids were supported. The source bytes, target bytes, masks, H1 coordinates, coverage and clear samples remain unchanged. No shared code or source domain was edited.

[run.py](run.py) imports only the existing filter and scoring machinery. It has no surface or tracer calls. Lens samples use the already certified coordinates in bounded chunks. Clear samples are copied bit-exactly. There are no foreground layers in these frozen cases, so pre-foreground and complete arrays coincide.

| Budget | Actual | Limit |
| --- | ---: | ---: |
| New rays | 0 | 0 |
| New height/footprint graph evaluations | 0 | 0 |
| New lens RGB queries | 3,643,100 | 4,000,000 |
| New clear RGB queries | 0 | 0 |
| New full material/composite observations | 4 | 4 |
| Baseline rerenders | 0 | 0 |
| Fits | 0 | 0 |

The [ledger](ledger.json) charges attempted lens queries before each case. No failed or repeated trial occurred. All four raw sample arrays have zero values below zero or above one. Display conversion alone clips to the image range; scoring uses unchanged raw float arrays.

## Paired guard results

| Case | Width multiplier | E | Rim RMSE | SSIM | All guards versus H1 |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 1.00 seed | 68.286560329 | 73.658172607 | 0.864096463 | Baseline |
| A | 0.75 | 68.356827811 | 73.787086487 | 0.864210546 | Fail |
| A | 1.25 | 68.163381752 | 73.432792664 | 0.864244938 | Pass |
| B | 1.00 seed | 36.215046603 | 36.279640198 | 0.935159802 | Baseline |
| B | 0.75 | 36.301218953 | 36.402973175 | 0.934289932 | Fail |
| B | 1.25 | 36.125294709 | 36.157924652 | 0.935845613 | Pass |

A exterior RMSE remains 12.615555763. B changes from 7.679680824 to 7.679679871. Clear samples remain exact: original exterior guard pixels can include partial lens coverage. This tiny aggregate change is not shadow progress. Every historical error guard still fails; B historical SSIM alone passes.

## Visible detail and local limits

Both full comparisons were inspected: [A](wide-a-comparison.png) and [B](wide-b-comparison.png). The wider width slightly broadens A's faint right boundary fragment and softens B's left crescent. Neither produces the large white upper/lower returns. The narrow result sharpens the same misplaced fragments rather than correcting correspondence.

The [A crop sheet](a-fixed-crops.png) and [B crop sheet](b-fixed-crops.png) preserve the historical crop coordinates. Each column is enlarged only twice, within its approved per-image limit. Columns show Apple, H1 seed, narrow and wide. [Saved-array diagnostics](diagnostic.json) retain RGB, luminance, chroma, signed RGB and adjacent-pixel detail measures.

A right-rim luminance RMSE changes from 65.545791 to 65.355492 at the wider width. Its maximum local RGB change is 6.381256 levels. B upper-left luminance RMSE changes from 23.885632 to 23.653680; lower-left changes from 43.166529 to 43.028691. These are local smoothing effects, not reconstructed illumination or validated physical boundary positions.

Local regressions remain recorded. A lower-left luminance RMSE changes from 43.359414419 to 43.359422156. A center luminance error also rises slightly. Flat-field changes are at most approximately 0.00003 RGB levels from finite floating-point filtering; they are not counted as visible improvements. No epsilon waiver was applied to the original guards.

The same fixed upper horizontal section in A remains at 172.591511 mean luminance versus 225.387448 in Apple. B remains at 195.570150 versus 231.592474. The wide width cannot explain these large missing returns. The original source-boundary identity, illumination and transition-state ambiguities remain.

Adjacent-pixel detail measures combine outline discontinuities, source boundaries, shading and missing features. They cannot independently identify a PSF or geometry. Reversal is not prohibited; the map is unchanged, and this stage does not reinterpret its folds as globally undesirable.

## Disposition and next proposal

Both fixed widths are complete. The wider candidate is numerically nonregressive against H1 and has a small local visual effect. Primary review must decide whether that effect merits an incremental component change. Until then, the original H1 source widths remain stable. No historical acceptance, scoring epoch or fidelity count changes.

The [colour protocol proposal](colour-proposal.json) is preparation only. It keeps the reviewed geometry and incident filter fixed, uses saved lens/clear arrays, and separates uniform material tone from missing geometric returns. No colour fit, calibration or new scientific stage has run. No third blur width is proposed.
