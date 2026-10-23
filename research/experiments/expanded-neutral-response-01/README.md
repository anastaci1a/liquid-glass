# Expanded playback: white-preserving colour response

Status: rejected after four declared native pairs. The selected neutral response stays unchanged. No colour or geometry acceptance is claimed.

## One shared direction

Reduce contrast while preserving the incident-white response:

$$
C_{\delta}(S)=(g_0-\delta)S+(b_0+\delta),\qquad C_{\delta}(1)=g_0+b_0.
$$

The same coefficients apply to all RGB channels and both references. Geometry, source width 6.75 native pixels, AA2, masks, foreground and exterior stay fixed.

One closed-form TRAIN-only fit proposes a change of 0.16690393391041375. Held pixels and foreground/artwork are excluded from fitting. Actual clipping, AA and the original foreground compositor decide every candidate.

## Result

| Step factor | A E | B E | Strict blocker |
| --- | ---: | ---: | --- |
| Baseline | 45.423695 | 18.219819 | — |
| Full | 40.059105 | 17.666129 | B rim, play and forward |
| Half | 41.539039 | 17.771328 | B play and forward |
| Quarter | 43.211913 | 17.953808 | B play and forward |
| Eighth | 44.255031 | 18.076576 | B play and forward |

All A guards pass. The rejected B symbol changes are retained exactly; there is no fifth backtrack or precision allowance. The half-step has admissible body metrics but remains an unaccepted diagnostic.

[Complete results](result.json) preserve every recipe, array and guard. [Proposal](proposal.json) records training counts and the common white point. No source query or geometric ray was repeated.

All lens channels remain unclipped. Unit-white float32 response is unchanged. This is empirical encoded colour grading, not measured radiance, a recovered Apple material or a refraction correction.

## Foreground provenance

The [reconciliation](foreground-provenance.json) distinguishes the frozen physical case's inline ink colours from historical full-recipe style overrides. No override was adopted during these comparisons.

Original vectors, placement, source and masks remain fixed. Future foreground work must report any style change separately; it cannot silently redefine the failed colour guards.

## Next stage

Outline uses the same actual surface and supported transport. Unknown illumination and unresolved paths remain limitations, not evidence that the outline effect is absent.
