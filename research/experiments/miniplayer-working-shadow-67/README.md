# Shared shadow remains zero

Half and quarter strengths improve exterior separation, but both fail compact glass, rim, E and original 22-pixel partial guards. Expanded passes alone do not satisfy the required family transfer. No partial pixel, tolerance, strength, glow or material change is introduced to manufacture a pass.

| Reference | Half-strength exterior RMSE | Half-strength partial RMSE | Current guard result |
| --- | ---: | ---: | --- |
| Expanded A | 12.088054 | 38.040215 | Pass |
| Expanded B | 12.531919 | 26.035206 | Pass |
| Compact A | 6.721442 | 23.844055 | Fail glass/rim/E/partial |
| Compact B | 8.438677 | 21.129807 | Fail glass/rim/E/partial |

All four half-strength full comparisons were inspected. The underlay looks closer outside the glass, but does not provide the bright reference rim or fix source returns. Every [guard regression](regressions.json), both strength sets and the [complete result](result.json) remain explicit. Shadow zero stays selected.

## Frozen underlay operation

The [protocol](protocol.json) reuses the original common shadow field and applies it only to retained premultiplied clear contribution. Shared sigma, offset and opacity seed are unchanged. Frozen pose, footprint and AA membership match. Four zero controls reproduce the working pre-foreground, completed pixels and scores exactly.

Every fully covered body and foreground pixel remains exact for both strengths. All original 16/22 partial cohorts remain scored. Source support transfers through unchanged coordinates, raw samples and inputs; no source query or new optical calculation is performed.

This is the existing Gaussian-distance exterior approximation, not recovered physical illumination. Original source mosaics remain conditional and may contain broad contextual lighting. No copied target shadow or new glow is used.

## Preserved earlier failure and accounting

Full strength from [study31](../miniplayer-working-shadow-31/README.md) is reused, not rerun. That study stopped because outer and imported scoring both charged the ledger. Its fifth half-step composite was not retained. This new declared task recomputes that one observation and completes the two remaining strengths; it does not rewrite the old budget or failure.

New usage is four identities, eight candidates and twelve score calls, with sixty metric Gaussians and twelve metric erosions. Two cached fields contain 560800 pixels; four original constructors cover 1121600 mask points. New rays, source queries, fields, filters and fits are zero.

Across both tasks, there are thirteen actual candidate entries, twelve retained candidate arrays and one originally unretained entry. Old duplicated reservations are not relabeled actual score calls. Local stage closure leaves foreground, dispersion and final review active under the [forward schedule](../miniplayer-working-blur-64/forward-schedule.json).
