# Common encoded color: four factors rejected

One equal-reference train-only direction fails the protected four-reference comparisons at every declared factor. Full strength improves compact aggregate error but over-whitens expanded bodies and clips channels. Smaller factors retain body, foreground or partial-boundary failures. No coefficient or model selection changes.

| Factor | Expanded A E | Expanded B E | Compact A E | Compact B E |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 8.190509 | 7.072735 | 22.547641 | 21.610871 |
| 1 | 13.179844 | 9.222504 | 17.007670 | 15.830890 |
| 0.5 | 9.284430 | 7.388112 | 18.935375 | 17.848910 |
| 0.25 | 8.252234 | 7.002130 | 20.576881 | 19.564061 |
| 0.125 | 8.090556 | 6.979129 | 21.526419 | 20.551846 |

## One shared proposal

Full-step gain is 0.5066036400254624 and bias is 0.4632497049724455. One Gauss–Newton quadratic uses the original 20000 training pixels with equal reference weighting. Held pixels and foreground are explicitly excluded. Hessian condition is 18.75167214.

Four original shallow pre-foreground, completed-image and score identities pass before fitting. The [proposal](proposal.json), [checkpoint](checkpoint.json), [input/code bindings](inputs-FIRST.json), [ledger](ledger.json) and [result](result.json) retain the exact calculation. No source, geometry, light, blur, mask or foreground parameter changes.

The full-step expanded A preview visibly over-whitens the body. Full-step clipping counts are 2852, 34550, 754 and 890 inside-subray RGB channels. Smaller factors have zero clipping but still fail. All original numerical-baseline, current-working20 and shallow42 guards are retained; no partial pixel or failure is waived.

All sixteen candidates, complete/pre-foreground arrays, comparisons and metrics remain beside this report. The result claims numerical rejection, not a complete visual review of every rejected image. No lower factor, second solve or replacement input is evaluated.

## Clock and accounting

The [protocol](protocol.json) starts at 11:05:00.076 UTC and ends at 11:25:00.076. Science finishes at 11:08:47.467. Publication exceeded that deadline; the [overrun record](publication-overrun.json) retains the actual limitation. One fit, at most four fixed factors and sixteen candidate composites are permitted. No new ray, height, source query, optical filter or baseline optical render runs.

## Future basis question, not executed

A later comparison could preserve the current white endpoint while testing a common response in linearized signal space:

$$
L_{\mathrm{incident}}=W\left[\tau\mathcal D(S)+(1-\tau)\right],\qquad
W=\mathcal D(g_0+b_0).
$$

This would change the response basis rather than add per-image coefficients. It is a mathematical signal proxy, not calibrated radiance or identified scattering. It requires its own declared controls and budget. No alternate operator is implemented or fitted during this stage.

The original incident width, shallow geometry and light four stay frozen for the required outline, shadow, foreground and dispersion assessments. The broader sequence remains active.
