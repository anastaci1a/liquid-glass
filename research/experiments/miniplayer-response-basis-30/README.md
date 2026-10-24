# Whole-response conversion: useful material-role negative

A global normal-incidence conversion preserves the earlier encoded response analytically. It does not produce an accepted family improvement. Expanded B passes original guards; expanded A and both compact references retain failures. The working model and all historical inputs remain unchanged.

## One fixed question

The [protocol](protocol.json) starts at 09:31:15.774 UTC and ends at 09:43:15.774. One coefficient pair follows from the existing response and normal transmission. No target fit, factor search or angle-dependent compensation is used.

$$
\begin{aligned}
k&=T_0^{\frac{1}{2.4}},\\
g_{\mathrm{new}}&=\frac{g_{\mathrm{old}}}{k},\\
b_{\mathrm{new}}&=\frac{b_{\mathrm{old}}+0.055}{k}-0.055.
\end{aligned}
$$

Both complete coefficient ranges stay above the nonlinear sRGB threshold and below clipping. The identity applies at normal transmission only. Actual angle-dependent transmission, direct-front reflection and all traced geometry remain physical and unchanged.

## Result

| Reference | Candidate E | Failures against original numerical baseline |
| --- | ---: | --- |
| Expanded A | 10.532118 | Interior, partial boundary, title |
| Expanded B | 7.367907 | None |
| Compact A | 24.142821 | Interior, title, artist |
| Compact B | 23.343662 | Interior, artist |

Eight synthetic points agree within 1.12 × 10⁻¹⁶. Four current-working pre-foreground, completed-image and score identities pass before candidates. Zero channels clip. [Calibration](basis-calibration.json), [checkpoint](checkpoint.json), [result](result.json) and [ledger](ledger.json) retain exact values.

The result's legacy keys `canonical_guards` and `hybrid_guards` mean the original numerical baseline and current working model. No legacy key changes the acceptance rule.

| Reference | Comparison | Measurements |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-comparison.png) | [Metrics](expanded-a-metrics.json) |
| Expanded B | [Image](expanded-b-comparison.png) | [Metrics](expanded-b-metrics.json) |
| Compact A | [Image](compact-a-comparison.png) | [Metrics](compact-a-metrics.json) |
| Compact B | [Image](compact-b-comparison.png) | [Metrics](compact-b-metrics.json) |

## Interpretation

The expanded comparison retains a broad lower highlight and mismatched cap/return structure. Correcting the material basis cannot repair those geometric or illumination differences. Normal-incidence response preservation is not a radiometric identification or outline improvement.

The [white-only test](../miniplayer-white-retention-29/README.md) and this whole-response test answer different calibration questions. Neither justifies a per-reference adjustment, extra fit or hidden pixel correction. A further outline experiment must address a named visible defect independently.

Four identities, four candidates, four mask constructors and eight scores ran. No new ray, source query, optical filter or fit ran. The unassigned reflected tail and hypothetical environment remain explicit limitations.
