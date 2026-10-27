# Eased horizontal outline thickness

Status: one fixed candidate completed; visual review pending. Color B at 120% from revision 112 is the chosen review baseline. One revised horizontal profile is being tested across both miniplayer lengths and all four references.

## Feedback and interpretation

The narrow left treatment may reflect a single reference's appearance. The proposed replacement retains the thin left endpoint but spreads the transition across the pill. Raw wording is preserved locally outside Git; this report records the executable interpretation.

| Full-width location | Thickness factor relative to revision 112's 100% |
| --- | ---: |
| Left through 127/1668 | 4/7 |
| 127/1668 to 1534/1668 | Cubic smoothstep to 1.20 |
| 1534/1668 to 1574/1668 | Linear transition from 1.20 to 1.45 |
| 1574/1668 through right | 1.45 |

Plateau and fade both scale. The prior 80% base factor remains. Fractions refer to the complete projected endcap-to-endcap width. The exact supplied horizontal positions govern the transition, including any part lying on a curved cap.

Brightness reduction retains its existing magnitude: one percent of positive HSV value lift. It holds at maximum through 127/1668, then follows cubic smoothstep to zero at the center. Color B's hue and saturation response remains fixed.

## Frozen evidence

Geometry, optical paths, source blur, body grading, artwork, shadow and opposing angular gaps remain fixed. Revision 112's Color B/120% arrays provide exact identity controls. The retained blurred source guide drives the same color endpoint. No new source filtering or optical transport is authorized.

## Verification protocol

[Protocol](protocol.json) declares one candidate per reference, a 100-minute total window and bounded quadrature work. Scalar controls verify knots, monotonicity and independent formulas before integration. Orders 16/32 select uncertain pixels for 64/96 refinement; the successive-order criterion is one millionth. This is not a rigorous integration error bound.

Four cached identities and four independent composition checks precede publication. Finite guide support and unchanged exterior/body pixels are checked. Native comparison panels retain the Apple reference, chosen baseline and candidate. No new aggregate scoring or full-fidelity claim is proposed.

## Result

All four chosen-baseline identities are pixel-exact. All four independent composition replays are pixel-exact. Source guides are finite everywhere the revised outline contributes, and pixels outside its support retain the completed body exactly. Color B is unchanged.

Expanded refinement covers 1,120 pixels; its final successive-order difference is 3.3001e-8. Compact refinement covers 844 pixels with a 2.9424e-8 difference. Remaining pixels meet the predeclared coarse criterion. These are numerical consistency checks, not a certified global error bound.

All four full comparisons and the expanded upper/lower right-transition crops were inspected. The extended taper and right-tip treatment are visible. Existing source-return, text and body differences remain. No aggregate rescoring or all-guard improvement is claimed. The chosen Color B/120% comparison remains available beside the candidate.

[Interactive comparisons](../../../guide/miniplayer-outline-eased-width.md) include 48 full and cropped slider panels. [Integration](integration.json), [results](results.json), [work counters](ledger.json), [input hashes](render-hashes.json) and [completion](finished.json) retain the numerical evidence.
