# Intermediate joins, colored plateau and downward shadow

Two intermediate shared shapes and separate rim/shadow tests are complete. Incident blur remains included. The final brighter, color-bearing plateau avoids the raw-transfer dark line and retains more yellow. Original boundary and other local failures remain; working20 is unchanged.

[Interactive comparisons](../../../guide/miniplayer-middle-ground.md) include every setting, the previous proposal and native edge close-ups. [Feedback](../../feedback/miniplayer-middle-ground.md) preserves the explicit blur correction. Verbatim notes remain outside Git.

## Intermediate geometry

All native paths complete. Both references pass whole-body and original-guard finite-kernel support before RGB for each shape. Same-height derivative and unit-index controls pass. Extrema, physical height laws, original masks, foreground and incident sigma `6.075` remain fixed.

| Radius reduction from smooth94 | Expanded join inset | Compact join inset | Equal-reference mean E |
| --- | ---: | ---: | ---: |
| 0.75 pixel | 1.3457 px | 1.3044 px | 13.3109 |
| 1.25 pixels | 1.7764 px | 1.7138 px | 13.2387 |

Earlier smooth insets were approximately `0.68` and `0.66` pixels; the excessive stronger shape reached `2.41` and `2.31`. Top joins move down and bottom joins up. Outermost tips stay fixed. Inset is evaluated at the former join location, not fitted from target intensity.

The second intermediate is used for material tests because its mean error is lower. This uses evaluation evidence, not held-out validation. Neither shape passes every original guard. [Shape controls](shape-shadow-summary.json) retain all four contour levels.

## Source-color and profile tests

Three declared contrasts compare a graded guide, the blurred pre-grade refraction guide, and that pre-grade guide with a plateau. A full pre-grade transfer restores yellow but creates dark, saturated compact rims. It is retained as a negative rather than adopted.

The guide uses retained incident-blurred samples at actual refracted coordinates. It excludes the body neutral grade and added scene light. Original foreground handling is applied unchanged. No new source query, incident field or optical path is introduced during these display tests.

The final profile holds maximum local strength for `0.6` native pixel, then fades inward. Angular treatment remains unchanged. Positive full-pixel quadrature is not normalized to occupied area.

$$
\alpha(d,\theta)=A(\theta)\exp\!\left[-\left(\frac{\max(d-0.6,0)}{2.6}\right)^2\right],\qquad d\geq0.
$$

Outside the contour, opacity is zero. The plateau profile also changes the inward exponent from `1.5` to `2`; this is explicitly a profile contrast, not an isolated width estimate. Orders eight and sixteen differ by about `2.09e-6`. The declared order32 refinement reduces the successive difference below `2.82e-7` on both members.

## Brightness safeguard and peak

After reviewing the three color contrasts, two shared brightness floors were tested. A third and final follow-up raises peak exposure to three while retaining floor `0.24`. No per-control fit or further parameter search follows. This setting is shown first for its brighter yellow peak, not because it passes every guard.

Let the linear source-color endpoint be a vector and its luminance be computed with the standard declared coefficients. The response adds the minimum neutral contribution needed to reach the body-relative floor.

$$
\begin{aligned}
Y_B&=(0.2126,0.7152,0.0722)\cdot\mathbf B,\\
Y_E&=(0.2126,0.7152,0.0722)\cdot\mathbf E,\\
Y_{\min}&=Y_B+\beta(1-Y_B),\\
t&=\frac{\max(Y_{\min}-Y_E,0)}{1-Y_E},\\
\mathbf E_*&=\mathbf E+t(\mathbf 1-\mathbf E).
\end{aligned}
$$

A white endpoint uses zero neutral correction directly, avoiding division by zero. Pure white stays white. The final encoded image blends toward the encoded endpoint using the integrated rim strength. This is a bounded display response, not physical-radiance recovery or a measured Apple shader.

At native expanded-A `(1400,325)`, the final RGB is approximately `(243.4,216.7,133.8)` against `(248,224,116)`. At `(1400,501)`, it is `(253.9,229.6,165.1)` against `(255,252,122)`. The upper color is closer to yellow; lower green/blue errors remain. Reported hex observations have no supplied coordinates and are not assigned to these pixels.

## Directional shadow

Two offsets, fourteen and eighteen pixels downward, share width `32`, power `1.5` and strength `34/255`. Only uncovered AA contributions are darkened. Every lens sample and fully covered shadow pixel stays exact. The eighteen-pixel setting is retained for the final experimental combination without a strength fit.

Ideal white-input controls give `#DDDDDD` immediately below, `#E9E9E9` immediately above and `#F6F6F6` at `20.5` pixels above. These approximate the reported asymmetry but are not registered reference measurements. The source mosaics do not establish a unique physical light or shadow.

## Final result

| Reference | Previous proposal98 E | Final E | Original partial RMSE remains worse |
| --- | ---: | ---: | --- |
| Expanded A | 11.1280 | 9.5068 | Yes |
| Expanded B | 5.6279 | 5.4896 | Yes |
| Compact A | 16.0236 | 16.4327 | Yes |
| Compact B | 16.7582 | 16.3892 | Yes |

Three aggregate comparisons improve against proposal98; compact A worsens. All original sixteen-pixel expanded and twenty-two-pixel compact partial cohorts remain scored. Foreground, interior and returned-feature mismatches remain visible. No family qualifier, historical count change or selected-model replacement is claimed.

## Own verification and retained failures

The primary researcher inspected both intermediate shapes, all four raw-transfer panels and all four final panels. Final brighter-peak color compositions and original scores replay exactly. Original source, mask and foreground identities are preserved. Input/code epochs are bound separately; an appended response is not retroactively attributed to an older experiment.

The first geometry control unpacked four API values into three names. Four height points and four identity controls had run, but no rays. [Recovery accounting](recovery.json) preserves the attempt and repeated setup. The corrected run used a new output folder under the original deadline.

The first display verifier passed its array tolerance but demanded exact metrics from rearranged floating arithmetic. Its original failure remains. Continuation retained all seven completed outputs and every quadrature/shadow field. Array differences stay within `5.96e-8`, and original guard decisions agree; exactness is not claimed for that stage.

The first brightness-floor verifier omitted the production float32 endpoint storage before decoding it again. Its first candidate and failure remain. The corrected verifier includes that storage boundary and reproduces the final outputs exactly. Neither scientific response nor array tolerance was changed to obtain this result.

## Evidence

- [Original plan](plan.json), [display protocol](display/protocol.json) and [display continuation](display/continuation-contract.json).
- [Geometry0.75](native-r0.75-complete/geometry-result.json) and [geometry1.25](native-r1.25/geometry-result.json).
- [Display results](display/result.json) and [cumulative display ledger](display/ledger-resumed.json).
- [Brightness-floor review](brightness-floor/protocol.json), [results](brightness-floor/result.json) and [continuation](brightness-floor/continuation-contract.json).
- [Final brighter-peak result](peak-brightness/result.json), [ledger](peak-brightness/ledger.json) and [fixed color samples](peak-brightness/yellow-samples.json).
- [Exact presentation crops](publication-panels.json).

Native and display work remain separate. Two native settings use `4,486,400` native rays and sixteen fixture rays. The failed geometry setup is additional. Display ledgers retain repeated constructors, guide compositions and verification attempts; the original ledgers are never added twice to their cumulative continuations.
