# Incident material: closer body tone, no four-reference qualifier

One shared neutral incident-material direction improves the visible body tone, but none of its four declared factors passes every original guard. The half-step is useful as a held comparison. Expanded A's 16-pixel boundary still worsens; expanded B's artwork and artist guards also fail against the selected family. No coefficients are adopted.

## Fixed scope

The [protocol](protocol.json) starts at 06:44:18.373 and ends at 07:04:18.373 UTC. Four exact [identity controls](checkpoint.json) passed at 06:44:58.686 before fitting. A source-generation assertion failed before numerical execution; its [setup note](setup-note.json) preserves the event without resetting the clock.

Actual inverse surfaces, traced coordinates, primary interface power, direct-front light strength four, incident sigma 6.75, source, masks, coverage, foreground and shadow zero remain fixed. Both miniplayer lengths share every glass parameter except major half-length. The material is applied to incident samples before transmission power and AA.

$$
C_{\mathrm{incident}}=\operatorname{clip}(gS+b,0,1).
$$

The same common gain and bias serve all references and channels. The explicit [interface-power operation](../miniplayer-interface-power-19/README.md) remains unchanged. This is an encoded material proxy under a stated linearization, not measured radiance or uniquely identified transmittance.

## One proposal and four fixed factors

Equal-reference training uses 5000 original train pixels per reference, excluding held and foreground pixels. One Gauss–Newton quadratic gives gain 0.5144083153060457 and bias 0.45264991160600004. Its condition number is 19.09853. No second solve or coefficient search occurs.

| Factor | Expanded A E | Expanded B E | Compact A E | Compact B E | Four-reference qualifier |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 12.42622 | 8.42875 | 15.62215 | 14.54909 | No |
| 0.5 | 7.88349 | 6.14943 | 20.53188 | 19.68186 | No |
| 0.25 | 9.50463 | 7.14159 | 24.43932 | 23.70930 | No |
| 0.125 | 11.08583 | 8.06476 | 26.58505 | 25.90593 | No |

The half-step's expanded A partial RMSE is 40.32683, versus selected 26.54980 and explicit-power 35.64325. Expanded B's original artwork and artist boxes also worsen against the selected family. Smaller steps retain failures; full-step expanded interior, foreground and boundary regressions remain recorded. Clipping counts are zero throughout.

## Visible result and limits

The half-step makes the compact body's tone substantially closer. Expanded body neutrality also improves. Thin lower-perimeter light, cap texture, return placement and original foreground backing remain imperfect. The current broad cap highlight should not be mistaken for a fully reproduced outline.

| Reference | Half-step comparison | Exact metrics |
| --- | --- | --- |
| Expanded A | [Image](expanded-a-factor0.5-comparison.png) | [Record](expanded-a-factor0.5-metrics.json) |
| Expanded B | [Image](expanded-b-factor0.5-comparison.png) | [Record](expanded-b-factor0.5-metrics.json) |
| Compact A | [Image](compact-a-factor0.5-comparison.png) | [Record](compact-a-factor0.5-metrics.json) |
| Compact B | [Image](compact-b-factor0.5-comparison.png) | [Record](compact-b-factor0.5-metrics.json) |

All fixed crop RGB and signed luminance errors remain in each candidate record. This is a common-family calibration, not held-out color validation: compact participates in training. Refraction-map preservation is a separate mathematical claim; source confidence remains conditional rather than photographic truth.

## Work and decision

| Work | Actual |
| --- | ---: |
| Shared train pixels | 20000 |
| Fits | 1 |
| Proposal and factor checks | 19 |
| Exact identity composites | 4 |
| Candidate composites / score calls | 16 / 16 |
| Metric Gaussians / erosions | 80 / 16 |
| Cached environment directions | 1487085 |
| Original mask constructor pixels | 1121600 |
| Rays, heights, source queries, optical filters and Fresnel evaluations | 0 |

The [proposal](proposal.json), [result](result.json) and [ledger](ledger.json) retain every factor and guard. Original input, source-support and path evidence transfers because those stages are unchanged. Keep selected and held states separate; complete the joint interpretation review before another illumination or geometry proposal.
