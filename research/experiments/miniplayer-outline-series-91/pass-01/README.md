# Pass 1: Width and common strength

The starting model and incumbent are retained. Every setting is evaluated on all four original references. A development seed is chosen only by equal-reference training loss; it is not an accepted replacement.

| Setting | Response | Width | Inward exponent | Strength | Training loss |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | white | 1.950000 | 2 | 1.000000000 | 0.002581027 |
| 1 | white | 2.275000 | 2 | 0.957416172 | 0.002455013 |
| 2 | white | 2.600000 | 2 | 0.885012549 | 0.002357471 |

## All original outcomes

| Setting / reference | E | Partial RMSE | Failed original guards | Comparison / crops |
| --- | ---: | ---: | --- | --- |
| 0 / expanded A | 10.623969 | 43.532742 | glass, rim, held, E, partial | [Full](expanded-a-c0-comparison.png) / [Crops](expanded-a-c0-crops.png) |
| 0 / expanded B | 5.787662 | 24.348297 | None | [Full](expanded-b-c0-comparison.png) / [Crops](expanded-b-c0-crops.png) |
| 0 / compact A | 17.871034 | 26.600721 | partial, exterior | [Full](compact-a-c0-comparison.png) / [Crops](compact-a-c0-crops.png) |
| 0 / compact B | 17.392010 | 31.499126 | partial, exterior | [Full](compact-b-c0-comparison.png) / [Crops](compact-b-c0-crops.png) |
| 1 / expanded A | 11.193238 | 43.380714 | glass, rim, held, E, partial | [Full](expanded-a-c1-comparison.png) / [Crops](expanded-a-c1-crops.png) |
| 1 / expanded B | 5.597833 | 24.407228 | None | [Full](expanded-b-c1-comparison.png) / [Crops](expanded-b-c1-crops.png) |
| 1 / compact A | 16.935727 | 26.063082 | partial, exterior | [Full](compact-a-c1-comparison.png) / [Crops](compact-a-c1-crops.png) |
| 1 / compact B | 16.627361 | 30.923748 | partial, exterior | [Full](compact-b-c1-comparison.png) / [Crops](compact-b-c1-crops.png) |
| 2 / expanded A | 11.464145 | 43.070637 | glass, rim, held, E, partial | [Full](expanded-a-c2-comparison.png) / [Crops](expanded-a-c2-crops.png) |
| 2 / expanded B | 5.414001 | 24.522381 | None | [Full](expanded-b-c2-comparison.png) / [Crops](expanded-b-c2-crops.png) |
| 2 / compact A | 16.225227 | 24.563820 | partial, exterior | [Full](compact-a-c2-comparison.png) / [Crops](compact-a-c2-crops.png) |
| 2 / compact B | 16.057566 | 29.292046 | partial, exterior | [Full](compact-b-c2-comparison.png) / [Crops](compact-b-c2-crops.png) |

## Verification and scope

Four zero identities and original input/mask bindings pass. Orders eight and sixteen agree within the declared opacity threshold. Development setting 2 has the smallest training loss. Held pixels and foreground do not enter the strength fit. All original boundary, foreground, exterior and body failures remain.

No new rays, heights, source queries or optical filters run. The separate outline acts on the frozen completed image. The original 16/22-pixel partial cohorts remain unchanged. Source/geometry uncertainty and inherited incomplete radiance remain body-model limits.

The actual block starts at 2026-10-25T21:40:40.963314+00:00 and ends by 2026-10-25T22:00:40.963314+00:00. Scientific completion is 2026-10-25T21:43:26.397923+00:00. [Protocol](protocol.json), [result](result.json), [fits](fits.json) and [ledger](ledger.json) retain all settings and counters.

[First](first-hashes.json) and [last](last-hashes.json) hashes agree for this execution. The driver snapshot is retained for later code evolution. [Visual review](visual-review.json) records inspection and the pass decision.
