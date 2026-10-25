# Pass 5: Combined soft fade and color-preserving white blend

The starting model and incumbent are retained. Every setting is evaluated on all four original references. A development seed is chosen only by equal-reference training loss; it is not an accepted replacement.

| Setting | Response | Width | Inward exponent | Strength | Training loss |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | mixed_lift | 2.600000 | 1.5 | 1.000000000 | 0.002349541 |
| 1 | mixed_lift | 2.600000 | 1.5 | 1.000000000 | 0.002299379 |
| 2 | mixed_lift | 2.600000 | 1.5 | 1.000000000 | 0.002280363 |

## All original outcomes

| Setting / reference | E | Partial RMSE | Failed original guards | Comparison / crops |
| --- | ---: | ---: | --- | --- |
| 0 / expanded A | 10.105273 | 42.932625 | glass, rim, held, E, SSIM, partial | [Full](expanded-a-c0-comparison.png) / [Crops](expanded-a-c0-crops.png) |
| 0 / expanded B | 5.271661 | 24.368292 | None | [Full](expanded-b-c0-comparison.png) / [Crops](expanded-b-c0-crops.png) |
| 0 / compact A | 16.299240 | 18.588221 | exterior | [Full](compact-a-c0-comparison.png) / [Crops](compact-a-c0-crops.png) |
| 0 / compact B | 16.641220 | 19.773146 | exterior | [Full](compact-b-c0-comparison.png) / [Crops](compact-b-c0-crops.png) |
| 1 / expanded A | 10.595633 | 43.087021 | glass, rim, held, E, SSIM, partial | [Full](expanded-a-c1-comparison.png) / [Crops](expanded-a-c1-crops.png) |
| 1 / expanded B | 5.271888 | 24.368261 | None | [Full](expanded-b-c1-comparison.png) / [Crops](expanded-b-c1-crops.png) |
| 1 / compact A | 15.961110 | 19.048445 | exterior | [Full](compact-a-c1-comparison.png) / [Crops](compact-a-c1-crops.png) |
| 1 / compact B | 16.131995 | 22.317463 | partial, exterior | [Full](compact-b-c1-comparison.png) / [Crops](compact-b-c1-crops.png) |
| 2 / expanded A | 11.341108 | 43.267464 | glass, rim, held, E, SSIM, partial | [Full](expanded-a-c2-comparison.png) / [Crops](expanded-a-c2-crops.png) |
| 2 / expanded B | 5.272116 | 24.368229 | None | [Full](expanded-b-c2-comparison.png) / [Crops](expanded-b-c2-crops.png) |
| 2 / compact A | 15.682755 | 21.902969 | exterior | [Full](compact-a-c2-comparison.png) / [Crops](compact-a-c2-crops.png) |
| 2 / compact B | 15.739640 | 26.337376 | partial, exterior | [Full](compact-b-c2-comparison.png) / [Crops](compact-b-c2-crops.png) |

## Verification and scope

Four zero identities and original input/mask bindings pass. Orders eight and sixteen agree within the declared opacity threshold. Development setting 2 has the smallest training loss. Held pixels and foreground do not enter the strength fit. All original boundary, foreground, exterior and body failures remain.

No new rays, heights, source queries or optical filters run. The separate outline acts on the frozen completed image. The original 16/22-pixel partial cohorts remain unchanged. Source/geometry uncertainty and inherited incomplete radiance remain body-model limits.

The actual block starts at 2026-10-25T21:56:00.393782+00:00 and ends by 2026-10-25T22:16:00.393782+00:00. Scientific completion is 2026-10-25T21:56:07.162047+00:00. [Protocol](protocol.json), [result](result.json), [fits](fits.json) and [ledger](ledger.json) retain all settings and counters.

[First](first-hashes.json) and [last](last-hashes.json) hashes agree for this execution. The driver snapshot is retained for later code evolution. [Visual review](visual-review.json) records inspection and the pass decision.


The incoming proposal is pass-04 setting 0. The next development seed is pass-05 setting 2, chosen by training loss only. Neither seed status nor lower training error overrides original guard failures.
