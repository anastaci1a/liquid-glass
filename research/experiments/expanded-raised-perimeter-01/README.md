# Expanded playback: one raised-perimeter back

Status: useful paired negative, with a procedural budget failure. The candidate is not adopted. No backtrack or material rescue follows.

## Visible hypothesis

A real raised-perimeter back creates an outward-gradient interior band and an inward-gradient outer band. This tests a different source-return mechanism from the earlier monotone concave backs, using the [primary-height certificate](../primary-height-certificate-01/README.md).

The original rounded footprint, pose, source, masks and vectors stay fixed. The same scalar profile is proposed for the separate crowned-slider adapter; different footprints do not imply identical materials or successful transfer.

For the squared footprint coordinate, the actual back is

$$
h_1=0.4(1-T)(0.1+T),\qquad
h_2=0.4\left(1-\frac{x^2}{a^2}\right),\qquad
h=\frac{h_1h_2}{h_1+h_2}.
$$

The flat front, index 1.5 and background distance 2L remain fixed. Every normal is derived from this height. Incident blur stays 6.75 native pixels, AA stays 2 by 2, and the selected common neutral response stays unchanged.

## Result

| Native measurement | H1 A | Candidate A | H1 B | Candidate B |
| --- | ---: | ---: | ---: | ---: |
| E | 45.423695 | 41.422024 | 18.219819 | 19.028390 |
| Glass RMSE | 38.077415 | 34.822212 | 15.106259 | 16.050404 |
| Rim RMSE | 59.115406 | 53.757900 | 23.959860 | 24.613602 |

A improves body error but fails SSIM and title. B worsens body, SSIM and several foreground guards. Original exterior scores and coverage remain exact. Raw lens clipping is zero.

Both full-body comparisons were inspected: [A](a-comparison.png), [B](b-comparison.png). A's coloured background return changes, but cap/body structures remain wrong. B's text/card relationship is still misplaced. The mechanism does not resolve the paired visible defect; lower A error alone is insufficient.

[All scores and guards](result.json) remain available with native samples, pre-foreground images and complete arrays. Historical image fits and the selected H1 geometric state stay separate and unchanged.

## Geometry and source checks

Sparse geometry controls pass gradient, mirror, scale, circle, miss and crease checks. The global slope bound is 0.876175, below the critical limit; maximum height is 0.092899L. Only primary paths are certified. The nonconvex solid is not sent to the convex multiple-reflection tracer.

One native grid contains 1,360,000 rays. Both source audits pass before RGB: 890,848 whole-body subrays and 1,076,505 required-union subrays per reference, including every original foreground/artwork and exterior guard. The finite radius-21 incident kernel and all bilinear texels are checked.

The 10,500 unsupported unscored subrays per reference remain unavailable. There is no source completion, clamping or target-context copy. Domain support does not establish hidden photographic truth.

The [longitudinal](longitudinal-cached-paths.svg) and [transverse](transverse-cached-paths.svg) views use cached back points and actual primary paths. Their axes are independently scaled and labelled; no decorative separate lens is used.

## Procedural failure

The [protocol](protocol.json) allowed the native grid but also declared an unscoped 200,000-height-evaluation cap. The grid requires 2,720,000 adapter height calls. These limits are internally inconsistent; under the conservative global reading the cap was exceeded.

[Budget audit](budget-audit.json) preserves the error. Sparse checkpoint counters also omitted nested adapter calls; [count review](count-review.json) reconstructs 3,975 checkpoint calls and conservatively charges profile QA. No completed control was repeated to repair the record.

All scientific work stopped after the fixed pair. Publication packages existing evidence only. This run must not be certified as fully in-budget or promoted to an accepted pass, even independently of its guard failures.

Future native protocols must reserve every adapter call before launch and explicitly scope phase budgets. The original protocol and as-run scripts are retained; there is no retroactive budget reset.
