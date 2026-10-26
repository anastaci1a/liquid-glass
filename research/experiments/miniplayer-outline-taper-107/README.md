# Hue-preserving horizontal outline taper

This single candidate removes the measurement-induced yellow hue shift. It reduces plateau and fade widths to 80% before applying the clarified thinner-left transition. The completed lens body, enlarged artwork, geometry, shadow and incident blur remain frozen at revision 106.

## Declared response

Coordinates are fractions of the complete pill width. Below the left endpoint, thickness is four sevenths of the globally reduced width. Above the right endpoint, it is the full globally reduced width. The transition is linear.

$$
t=\operatorname{clamp}\left(\frac{u-\frac{1097}{2530}}{\frac{1128}{2530}-\frac{1097}{2530}},0,1\right),\qquad s=0.8\left(\frac{4}{7}+\frac{3}{7}t\right).
$$

Plateau and fade scale together. A provisional one-percent reduction affects only positive HSV value increase on the thin side. It disappears linearly across the same interval. Saturation and hue remain unchanged by that adjustment.

$$
V'=V-0.01(1-t)\max(V-V_{\mathrm{input}},0).
$$

The color guide retains incident blur and refraction, before lens color grading and optical lighting. Color remains a pixel-guide response; thickness and brightness moments use full-pixel positive area weights. Opposing angular gaps retain their original definition.

## Verification and scope

The protocol declares one candidate per reference, two integration orders and unchanged original score masks. Baseline replay must reproduce revision 106 exactly. Independent SciPy and scalar HSV evaluation check the new response. Integration checks compare orders 16 and 32; this is a successive-order criterion, not a universal error bound.

No hue correction, artwork resize, optical tracing, source sampling, incident filtering, geometry fitting or selected-state adoption occurs in this task. The slight brightness amount is an explicit assumption, available for visual review.

[Protocol](protocol.json) · [Calibration](calibration.json) · [Comparison page](../../../guide/miniplayer-outline-taper.md)

## Control interpretation

| Control | Thick right | Thin left |
| --- | ---: | ---: |
| Plateau | 1.2 native pixels | 0.685714 native pixels |
| Fade scale | 1.6 native pixels | 0.914286 native pixels |
| Positive value increase | 100% | 99% |
| Hue correction | Zero | Zero |

The brightness reduction does not darken already-dimmed white. It removes one percent of positive value lift only. Width modulation and brightness reduction share the same normalized horizontal interval; neither depends on target pixels or reference identity.

## Integration recovery

Expanded's first 16/32 comparison exceeded the declared tolerance, before any candidate composite. The stopped evidence remains intact. A subsequent full-grid refinement was interrupted with its conservative ledger saved; no complete higher-order result is claimed from that attempt.

The continuation retains the original deadline and tolerance. It reuses expanded's saved moments. Pixels exceeding one quarter of the tolerance receive orders 64 and 96; all others retain order 32. Every original pixel remains scored. The decision uses numerical differences, never target colors.

[Initial failure](failure.json) · [Recovery](integration-recovery.json) · [Continuation protocol](adaptive-protocol.json)

## Result

Both members pass the adaptive successive-order criterion below 2.5e-7. All four independent completed-image replays are pixel-exact. Original body and artwork remain exact; clipping is zero. Expanded aggregate errors improve, while compact errors regress. No shared-family acceptance or selected-state change is claimed.

| Case | Previous E | Candidate E |
| --- | ---: | ---: |
| expanded A | 11.733664 | 10.165261 |
| expanded B | 4.807020 | 4.765453 |
| compact A | 14.993668 | 16.320839 |
| compact B | 15.635873 | 16.563987 |

[Results](results.json) · [Verification](verification.json) · [Integration](integration.json) · [Cumulative ledger](ledger.json)
