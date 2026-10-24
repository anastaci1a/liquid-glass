# Working contact shadow: negative pair and incomplete strengths

Full-strength contact shadow improves exterior error but fails the current working family's paired boundary guards. Expanded A passes; expanded B and both compact references worsen glass, rim, total error and partial-boundary error. Shadow zero remains selected.

## Fixed visible question

This tests the missing dark exterior underlay, separately from bright rim light. The [protocol](protocol.json) preserves the current two-surface geometry, material, incident blur, direct reflection and foreground. Only the original contact-shadow field multiplies the clear-premultiplied contribution. Fully covered pixels remain exact.

| Reference | Exterior RMSE | Partial-boundary RMSE | Current-working guard result |
| --- | ---: | ---: | --- |
| Expanded A | 8.729733 | 35.849358 | Pass |
| Expanded B | 6.727588 | 26.625469 | Fail |
| Compact A | 6.590001 | 23.897432 | Fail |
| Compact B | 5.907800 | 21.208725 | Fail |

The field improves the dark exterior separation. It cannot supply the reference's thin bright rim or correct return positions. The original 16- and 22-pixel cohorts remain scored; no failure is waived.

## Accounting stop

The task started at 09:34:40.099 UTC with a 09:49:40.099 deadline. Four exact zero-shadow and score identities passed at 09:35:00.643. One full-strength four-reference pair completed before the driver stopped during the next strength.

The driver and imported score helper both charged each score. Sixteen conservative reservations therefore correspond to eight completed score calls, forty metric Gaussians and eight metric erosions. The next outer reservation failed before scoring. The immutable [ledger](ledger.json) retains its conservative counts.

Five candidate composites were entered. Four complete outputs were saved; the fifth was calculated but not retained before the failed score reservation. Half and quarter strengths are incomplete, not negative numerical results. The driver was not repaired or retried.

The [execution record](execution.txt), [result](result.json), [checkpoint](checkpoint.json) and [bindings](bindings.json) preserve the failure and input identities. No new optical ray, source query, shadow field, filter or fit ran.

## Evidence

| Reference | Comparison | Measurements |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-factor1-comparison.png) | [Metrics](expanded-a-factor1-metrics.json) |
| Expanded B | [Image](expanded-b-factor1-comparison.png) | [Metrics](expanded-b-factor1-metrics.json) |
| Compact A | [Image](compact-a-factor1-comparison.png) | [Metrics](compact-a-factor1-metrics.json) |
| Compact B | [Image](compact-b-factor1-comparison.png) | [Metrics](compact-b-factor1-metrics.json) |

No current-working or historical acceptance changes. Bright-outline geometry and scene radiance remain separate unresolved questions.
