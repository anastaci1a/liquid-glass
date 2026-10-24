# Fixed-white contrast does not qualify across the family

All four factors fail shared-family guards. The smallest factor improves aggregate E on every reference, yet protected cohorts still regress. Stronger steps visibly lighten compact backgrounds while over-whitening expanded A. No candidate is adopted, and no smaller factor or second solve runs.

| Factor | Expanded A E | Expanded B E | Compact A E | Compact B E |
| --- | ---: | ---: | ---: | ---: |
| Current | 7.883487 | 6.149430 | 20.531876 | 19.681863 |
| 1 | 12.084960 | 5.948186 | 16.709022 | 15.790272 |
| 0.5 | 8.943405 | 5.858523 | 17.948882 | 17.033157 |
| 0.25 | 8.065846 | 5.958191 | 19.100374 | 18.212983 |
| 0.125 | 7.880607 | 6.042811 | 19.784703 | 18.915250 |

The four full-step comparisons were inspected. Their common contrast change cannot simultaneously repair the expanded and compact appearance. The magnifier-like cap light and source-return errors remain. Compact A alone passes current guards at the smallest factor; this does not establish the required four-reference transfer.

## One declared material direction

The [protocol](protocol.json) fixes encoded white response and allows only one common scalar contrast direction:

$$
W=g_0+b_0,\qquad g=W-b.
$$

A train-only Gauss-Newton proposal in bias gives gain 0.48253315649856554 and bias 0.46360245575923686. White remains 0.9461356122578024. The existing bias domain and original four factors are predeclared. There are no independent channel, crop or image coefficients.

[Proposal](proposal.json), [checkpoint](checkpoint.json), [complete results](result.json) and individual metric records retain all original body, SSIM, foreground, exterior and partial-boundary outcomes. Legacy `held_guards` means current working20; `selected_guards` retains the earlier numerical baseline. Neither name changes the required masks or acceptance rule.

Four baseline pre-foreground/completed identities are exact before the fit. The original train excludes held and foreground. One solve uses 20000 train pixels and five proposal/feasibility checks. Sixteen actual composites and scores decide the result; the analytic local model is not an exact float32 finite-response or SSIM guarantee.

All actual clipping counts are zero. Geometry, source coordinates, incident blur, source inputs, foreground and light remain frozen. There are no new rays, source queries, fields or filters. The source proof transfers through unchanged paths and data, not through an assumption of hidden photographic truth.

This is empirical encoded contrast, not measured transmittance or a new physical white-light mechanism. The current working response stays unchanged. Outline and later stages proceed independently; color is assessed and negative, not silently skipped.

[Every retained guard regression](regressions.json) is recorded explicitly. The tiny aggregate improvement at the last factor does not waive local failures or create a pass count.
