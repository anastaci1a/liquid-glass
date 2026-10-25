# Pass 3: Earlier and later cap fade landmarks

The starting model and incumbent are retained. Every setting is evaluated on all four original references. A development seed is chosen only by equal-reference training loss; it is not an accepted replacement.

| Setting | Response | Width | Inward exponent | Strength | Training loss |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | white | 2.600000 | 2 | 0.891029889 | 0.002365022 |
| 1 | white | 2.600000 | 2 | 0.869459208 | 0.002362236 |

## All original outcomes

| Setting / reference | E | Partial RMSE | Failed original guards | Comparison / crops |
| --- | ---: | ---: | --- | --- |
| 0 / expanded A | 11.519202 | 42.904629 | glass, rim, held, E, partial | [Full](expanded-a-c0-comparison.png) / [Crops](expanded-a-c0-crops.png) |
| 0 / expanded B | 5.406661 | 26.053308 | None | [Full](expanded-b-c0-comparison.png) / [Crops](expanded-b-c0-crops.png) |
| 0 / compact A | 16.275222 | 19.773802 | exterior | [Full](compact-a-c0-comparison.png) / [Crops](compact-a-c0-crops.png) |
| 0 / compact B | 16.113713 | 22.370001 | partial, exterior | [Full](compact-b-c0-comparison.png) / [Crops](compact-b-c0-crops.png) |
| 1 / expanded A | 11.396496 | 48.670277 | glass, rim, held, E, partial | [Full](expanded-a-c1-comparison.png) / [Crops](expanded-a-c1-crops.png) |
| 1 / expanded B | 5.429885 | 22.749451 | None | [Full](expanded-b-c1-comparison.png) / [Crops](expanded-b-c1-crops.png) |
| 1 / compact A | 16.277950 | 30.637323 | partial, exterior | [Full](compact-a-c1-comparison.png) / [Crops](compact-a-c1-crops.png) |
| 1 / compact B | 16.094471 | 36.190857 | partial, exterior | [Full](compact-b-c1-comparison.png) / [Crops](compact-b-c1-crops.png) |

## Verification and scope

Four zero identities and original input/mask bindings pass. Orders eight and sixteen agree within the declared opacity threshold. Development setting 1 has the smallest training loss. Held pixels and foreground do not enter the strength fit. All original boundary, foreground, exterior and body failures remain.

No new rays, heights, source queries or optical filters run. The separate outline acts on the frozen completed image. The original 16/22-pixel partial cohorts remain unchanged. Source/geometry uncertainty and inherited incomplete radiance remain body-model limits.

The actual block starts at 2026-10-25T21:48:17.969078+00:00 and ends by 2026-10-25T22:08:17.969078+00:00. Scientific completion is 2026-10-25T21:49:47.620395+00:00. [Protocol](protocol.json), [result](result.json), [fits](fits.json) and [ledger](ledger.json) retain all settings and counters.

[First](first-hashes.json) and [last](last-hashes.json) hashes agree for this execution. The driver snapshot is retained for later code evolution. [Visual review](visual-review.json) records inspection and the pass decision.


The incoming proposal is pass-01 setting 2. The next development seed is pass-01 setting 2, chosen by training loss only. Neither seed status nor lower training error overrides original guard failures.
