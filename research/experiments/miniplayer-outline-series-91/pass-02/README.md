# Pass 2: White versus color-preserving brightness response

The starting model and incumbent are retained. Every setting is evaluated on all four original references. A development seed is chosen only by equal-reference training loss; it is not an accepted replacement.

| Setting | Response | Width | Inward exponent | Strength | Training loss |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | encoded_lift | 2.600000 | 2 | 1.000000000 | 0.002486082 |
| 1 | linear_lift | 2.600000 | 2 | 1.000000000 | 0.002481881 |

## All original outcomes

| Setting / reference | E | Partial RMSE | Failed original guards | Comparison / crops |
| --- | ---: | ---: | --- | --- |
| 0 / expanded A | 10.001663 | 42.899204 | glass, rim, held, E, SSIM, partial | [Full](expanded-a-c0-comparison.png) / [Crops](expanded-a-c0-crops.png) |
| 0 / expanded B | 5.429469 | 24.326937 | None | [Full](expanded-b-c0-comparison.png) / [Crops](expanded-b-c0-crops.png) |
| 0 / compact A | 17.004157 | 20.667059 | exterior | [Full](compact-a-c0-comparison.png) / [Crops](compact-a-c0-crops.png) |
| 0 / compact B | 17.487903 | 19.321196 | exterior | [Full](compact-b-c0-comparison.png) / [Crops](compact-b-c0-crops.png) |
| 1 / expanded A | 10.020314 | 42.912579 | glass, rim, held, E, SSIM, partial | [Full](expanded-a-c1-comparison.png) / [Crops](expanded-a-c1-crops.png) |
| 1 / expanded B | 5.429470 | 24.326929 | None | [Full](expanded-b-c1-comparison.png) / [Crops](expanded-b-c1-crops.png) |
| 1 / compact A | 16.979898 | 20.585821 | exterior | [Full](compact-a-c1-comparison.png) / [Crops](compact-a-c1-crops.png) |
| 1 / compact B | 17.456362 | 19.302948 | exterior | [Full](compact-b-c1-comparison.png) / [Crops](compact-b-c1-crops.png) |

## Verification and scope

Four zero identities and original input/mask bindings pass. Orders eight and sixteen agree within the declared opacity threshold. Development setting 1 has the smallest training loss. Held pixels and foreground do not enter the strength fit. All original boundary, foreground, exterior and body failures remain.

No new rays, heights, source queries or optical filters run. The separate outline acts on the frozen completed image. The original 16/22-pixel partial cohorts remain unchanged. Source/geometry uncertainty and inherited incomplete radiance remain body-model limits.

The actual block starts at 2026-10-25T21:46:04.703383+00:00 and ends by 2026-10-25T22:06:04.703383+00:00. Scientific completion is 2026-10-25T21:46:09.631191+00:00. [Protocol](protocol.json), [result](result.json), [fits](fits.json) and [ledger](ledger.json) retain all settings and counters.

[First](first-hashes.json) and [last](last-hashes.json) hashes agree for this execution. The driver snapshot is retained for later code evolution. [Visual review](visual-review.json) records inspection and the pass decision.


The incoming proposal is pass-01 setting 2. The next development seed is pass-01 setting 2, chosen by training loss only. Neither seed status nor lower training error overrides original guard failures.
