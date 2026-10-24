# Outline sampling: four-by-four integration does not fix the mismatch

Higher quadrature slightly changes cap pixels but leaves the main perimeter mismatch. The compact straight-edge errors are almost unchanged. This is a numerical sampling result, not an optical improvement, a blur adjustment or a new scoring epoch. The original two-by-two protocol remains fixed.

## Controlled question

The [protocol](protocol.json) starts at 07:05:44.129 and ends at 07:25:44.129 UTC. The [checkpoint](checkpoint.json) passed at 07:09:12.043. All sixteen cached two-by-two tile identities reproduce exactly before new rays. Each tile has zero overlap with the original foreground boxes.

Four native 32-by-24 patches per member cover the left cap, right cap, upper straight edge and lower straight edge. Their centers derive from frozen geometry, without target-error selection. The same eight geometric patches serve both references, giving sixteen paired material integrations.

A [pre-execution accounting clarification](preflight-accounting.json) corrects that paired integration count. The [initial declaration](protocol-as-declared.json) is retained. No evaluation preceded the correction; original ray/source limits, checkpoint and deadline stay unchanged.

Only samples per native pixel axis change. Actual inverse surfaces, interface powers, narrow light, common held material, incident filter, source, masks, pose and shadow remain fixed. Every new normal and intersection comes from the same geometry used previously.

## Local measurements

| Reference | Left-cap RGB RMSE, AA2 → AA4 | Right-cap RGB RMSE, AA2 → AA4 | Lower-straight RGB RMSE, AA2 → AA4 |
| --- | ---: | ---: | ---: |
| Expanded A | 7.172 → 7.014 | 18.248 → 18.191 | 16.652 → 16.668 |
| Expanded B | 6.404 → 6.549 | 10.407 → 10.373 | 15.893 → 15.914 |
| Compact A | 21.613 → 21.615 | 23.679 → 23.591 | 41.347 → 41.347 |
| Compact B | 20.004 → 20.005 | 24.187 → 24.048 | 37.875 → 37.875 |

The original glass mask selects each local measurement. No changed coverage cohort replaces it. All sixteen RGB RMSE and MAE records are in the [result](result.json), including upper-edge ties and local regressions. These are patch measurements; no full-image guard or fidelity score is computed.

## Inspect at twice native size

| Reference | Reference / AA2 / AA4 |
| --- | --- |
| Expanded A | [Patch sheet](expanded-a-sampling-2x.png) |
| Expanded B | [Patch sheet](expanded-b-sampling-2x.png) |
| Compact A | [Patch sheet](compact-a-sampling-2x.png) |
| Compact B | [Patch sheet](compact-b-sampling-2x.png) |

The thin line remains different from the reference after improved sampling. Cap aliasing is not the main cause of the weak straight perimeter. Four-by-four integration is still finite quadrature; it does not establish continuous pixel-area truth or identify an optical PSF.

The [full-body narrow-light comparisons](../miniplayer-narrow-emitter-22/README.md) retain context. Nothing is enlarged beyond twice native size in these diagnostic patch sheets. No full-frame high-resolution render or motion is generated.

## Support and work

All four fresh source gates pass before fields or RGB. Each new whole-body and original-scored subray in the patches checks finite radius-21 incident support and all four bilinear corners. No unsupported required sample exists. Unscored exterior would remain unavailable; none is unsupported in these patches.

| Work | Actual |
| --- | ---: |
| Exact cached identity tiles | 16 |
| New four-by-four geometric rays | 98304 |
| Height/other surface point queries | 2163228 |
| Conservative adapter units | 43264560 |
| Source-audit subrays | 196608 |
| Known-mask corner lookups | 1572864 |
| Incident fields / known erosions | 4 / 8 |
| RGB queries | 196608 |
| Cached/new scene-direction queries | 73873 |
| New paired material tile integrations | 16 |
| Original constructor mask points | 1121600 |
| Profile-bound segments | 2048 |

The [source proof](source-FIRST.json) and [persistent ledger](ledger.json) preserve the phase ordering and separate categories. There is no fit, independent normal, output filter, source completion, foreground change or altered baseline. The next geometric question must address actual perimeter transport or scene structure, not hide this mismatch through blur or sampling.
