# Restored body grading and doubled rim plateau

One held candidate restores the previous gain/bias and low-luminance body response, followed by original primary power and direct reflected-light composition. Only gain changes to make grading-stage white #E5E5E5. The calibrated outline endpoint remains unchanged, while its maximum-strength plateau doubles from one to two native pixels.

[Interactive comparisons](../../../guide/miniplayer-restored-grade.md)

## Fixed and changed controls

Bias remains 0.39083683534488656 and dark-tone lift remains 0.08. Gain becomes 0.507202380341388. Incident blur, geometry, registration, source support, shadow, foreground and artwork remain unchanged. Outline fade remains two native pixels. The right upper diagonal and left lower diagonal retain zero-contribution gaps.

The existing body response is:

$$
C_0=gC+b,\qquad C_{\mathrm{grade}}=C_0+a(1-Y)^3(1-C_0).
$$

Here Y is decoded input luminance. White has zero dark-tone lift, so gain plus bias sets its grading endpoint. Optical power and reflected light follow in linear light. Normal transmission alone maps this white to approximately 220.87 encoded levels; actual positions vary. No new final-color body map is used.

The outline retains the previous calibrated hue-preserving response. Its input remains incident-blurred refraction before body grading and assigned light, with ordered foreground retained. Its maximum white endpoint stays #FCFCFC. The yellow hue-preserved endpoint remains approximately #FEEB85, rather than the supplied #FEF985 sample.

## Verification scope

Four original selected identities and scores are reproduced before the candidate. New outline area integration compares orders 16 and 32 on the unchanged projected contour. The geometry participates only in overlay distance and coverage calculations; there are no new lens rays or source samples.

Candidate verification independently reconstructs the old body equation, sRGB conversion, optical composition, pixel integration and calibrated outline endpoint. Original masks, partial cohorts and metrics remain fixed. First/last consumed hashes bind the unchanged inputs and shared code. All scalar controls, images, arrays, ledgers and failure records are retained.

This is a display revision for user review. The selected model remains unchanged. Compact shares exactly the same controls; no per-reference tuning or image fit is performed. The reflected scene remains hypothetical and full radiance is incomplete.

## Outcome

Both overlay integrations pass the declared successive-order threshold. Maximum alpha differences are 4.762e-7 for expanded and 4.753e-7 for compact. All four independent complete replays are pixel-exact, with zero clipping and exact clear samples and diagonal gaps. No source query, blur field or lens ray was added.

| Case | Previous candidate E | Revised E |
| --- | ---: | ---: |
| expanded A | 10.541961 | 13.390896 |
| expanded B | 5.421172 | 9.771798 |
| compact A | 23.480990 | 17.579734 |
| compact B | 22.409857 | 18.417607 |

Compact improves against the previous anchor-map candidate; expanded regresses. All four full comparisons were inspected. The darker body and wider colored band are visible, while source-return, foreground and contour mismatches remain. This is not a full-family fidelity qualifier or a selected-state update.

Accounting includes 300,394,240 outline quadrature nodes, 301,515,840 distance points and 1,480,770 cached annular-direction evaluations. Four Studies, four identities, four candidates, four independent replays and eight score calls were used. Full category totals remain separate in render-ledger.json.
