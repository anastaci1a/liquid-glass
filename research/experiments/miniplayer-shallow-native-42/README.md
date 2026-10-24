# Shallow front: thinner contour, insufficient rim light

The shallow actual front makes the contour visibly thinner than the previous broad-band trial. Its rim remains too faint, and all four aggregate errors worsen against the current working family. Body, foreground and boundary failures remain. This is a held geometry result, not an adopted family improvement.

## Fixed physical change

The [actual front/back construction](../miniplayer-shallow-front-41/README.md) reduces front sag to 0.02 original length units while retaining the edge-slope bound. The bevel exponent follows from those anchors. The new inferred back preserves the same physical source correspondence prior. Normals and roots come from the surfaces; no screen-space correction is used.

| Reference | Working E | Candidate E | Frozen partial RMSE |
| --- | ---: | ---: | ---: |
| Expanded A | 7.883487 | 8.190509 | 45.105331 |
| Expanded B | 6.149430 | 7.072735 | 26.735561 |
| Compact A | 20.531876 | 22.547641 | 20.586746 |
| Compact B | 19.681863 | 21.610871 | 19.843792 |

All SSIM values and most body guards regress. Compact partial-boundary errors improve; expanded partial errors worsen. Original numerical-baseline and current-working guards stay separate. Every original foreground and 16/22-pixel partial cohort remains scored.

## Inspectable evidence

All four full comparisons were inspected. The thinner line still lacks reference brightness, localized cap bloom and correct return structure. Some body colors remain too dark or saturated. Thinness alone does not establish full outline fidelity or physical identification.

| Reference | Full comparison | Fixed 2× crops | Metrics |
| --- | --- | --- | --- |
| Expanded A | [Image](expanded-a-light4-comparison.png) | [Crops](expanded-a-light4-crops.png) | [Record](expanded-a-light4-metrics.json) |
| Expanded B | [Image](expanded-b-light4-comparison.png) | [Crops](expanded-b-light4-crops.png) | [Record](expanded-b-light4-metrics.json) |
| Compact A | [Image](compact-a-light4-comparison.png) | [Crops](compact-a-light4-crops.png) | [Record](compact-a-light4-metrics.json) |
| Compact B | [Image](compact-b-light4-comparison.png) | [Crops](compact-b-light4-crops.png) | [Record](compact-b-light4-metrics.json) |

## Source and path proof

Fresh [expanded](expanded-source-FIRST.json) and [compact](compact-source-FIRST.json) whole/all-guard finite-kernel source audits pass before RGB. Four zero-change identities and thirty actual-pair fixtures pass. All raw clipping counts are zero. Actual source coordinates differ from the physical prior by less than 0.00072 native pixel.

Unknown unscored exterior stays unavailable. Conditional source support is not hidden photographic truth. The reflected environment remains hypothetical; later reflected power is unassigned. No measured radiometry or complete scene is claimed.

The [protocol](protocol.json) starts at 10:28:33.910 UTC and ends at 10:53:33.910. Science finishes at 10:30:45.214. [Checkpoint](checkpoint.json), [ledger](ledger.json), [result](result.json) and [input hashes](input-hashes.json) preserve exact work and unchanged references.

Work includes 2243200 native rays, thirty fixtures, 62509075 surface points, 1250181500 conservative adapter units, 4486400 source-audit subrays, 35891200 corner lookups and 4465400 RGB queries. Four fields, eight erosions, four candidates, four identities and eight scores run. No fit runs.

## Next isolated question

The geometry now produces a narrow but weak contour under the frozen annular environment. A separately declared single emitter-strength change can test brightness without another surface or material adjustment. Such a test remains conditional on the assumed environment and must preserve all local failures and clipping records.
