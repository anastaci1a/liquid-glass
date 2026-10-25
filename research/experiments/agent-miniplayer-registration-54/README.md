# Sizing before outline: current contours are not reliably contradicted

**Retain the frozen working 20 sizing and poses for the outline cycle.** Existing references and profiles do not support a reliable shared minor/radius correction or per-reference translation. They contain conflicting backing and brightness landmarks. This is an uncertainty finding, not proof of subpixel registration accuracy.

Task 54 started at 21:34:36.501 UTC on 25 October 2026, with checkpoint due 21:38:36.501 and sealing due 21:46:36.501 UTC. The saved checkpoint precedes inspection. No geometry, source, material, mask, outline width/strength or pose changed. Root owns the five outline passes and comparison page.

## Fixed reference access and budget

Four existing working 20 comparison sheets were viewed. Their left panels contain the original reference crops. Expanded panels are Lanczos-resized for presentation; compact panels retain native width. They supply visual context only. Native landmark coordinates below come from original rim73 profile records, never inferred from display scaling.

The four entire comparison PNGs total 2257148 decoded pixels, conservatively charged against the five-million target-pixel limit. Four complete target PNGs would exceed that cap and were not decoded. No source PNG, new image, plot or candidate was created. This limits full-frame context; the original control reference regions remain visible in saved panels.

Exactly 32 historical profiles are retained: top/bottom center, left/right tips and four diagonal cap sections for each reference. Each uses the original 25 quarter-pixel rows from minus three to plus three native pixels. The 800 saved rows are copied unchanged; there is no new target sampling, threshold search, pose fit or profile alignment.

## Frozen family geometry

Original normalization is 88.5 native pixels. Both members share minor half 89.6065300440 and radius 88.8864179815 native pixels; only major half differs. These are the working 20 family values, not a new per-control geometry fit.

| Member | Center native XY | Major half | Frozen extrema X / Y |
| --- | --- | --- | --- |
| Expanded |961.20865,413.14454 |639.41453 |321.79412…1600.62318 /323.53801…502.75107 |
| Compact |959.80966,672.71545 |434.23083 |525.57883…1394.04049 /583.10892…762.32198 |

Expanded center comes from the preserved accepted geometry summary. Compact center uses original case center plus the accepted pass03 translation in the original unit. Historical pass03 material, radius/join refinements are not silently imported into the shared working family. The exact records and algebra are bound in `frozen-contours.json`.

## Native landmark intervals

Negative distance is inward along the frozen two-dimensional silhouette normal. The brackets below describe visible intensity transitions in existing profiles. They are not fitted edges, confidence intervals, physical-alpha measurements or proven silhouette locations. A dash means no isolated edge can be distinguished reliably from backing in that fixed window.

| Section | Expanded A | Expanded B | Compact A | Compact B |
| --- | --- | --- | --- | --- |
| Top center |−1…+1 |−1…+1 |−1…+1 |— |
| Bottom center |−1…+1 |−1…+1 |−2…0 |−2…0 |
| Left tip |0…+2 |−1…+2, weak |— |−2…0 |
| Right tip |−1…+1 |−1…+1, weak |— |−1…+1 |
| Corner 45, lower right |−1…+1, weak |−1…+1, weak |−1…+1 |— |
| Corner 135, lower left |0…+2 |— |−2…0 |−1…+1 |
| Corner 225, upper left |0…+3, compound |0…+2, weak |−1…+1 |— |
| Corner 315, upper right |−1…+1 |— |0…+2 |0…+2 |

`landmark-intervals.json` records all 32 outline positions, outward normals and corresponding absolute native endpoint pairs. For example, expanded top-center bracket is y 322.53801…324.53801; compact bottom-center is y 760.32198…762.32198. Expanded left-tip bracket spans x 319.79412…321.79412. Bounds are descriptive, intentionally wider than the quarter-pixel sample spacing.

The compact top-center A profile has a pronounced interior brightness peak and a transition near the frozen contour. B instead rises into a bright exterior plateau, with no separable edge. Compact right-tip A is nearly flat against its exterior backing, whereas B shows a strong transition. A per-reference pose correction cannot be recovered from the absence of contrast.

Compact bottom transitions start inward of the frozen contour, while upper-right transitions extend outward. Expanded A left-tip transition is outward, but its top and right transitions bracket the frozen contour. Such heterogeneous offsets do not provide a coherent radius, minor-half or translation correction. Their causes include refraction returns, finite image blur and background edges.

## Bright rim is not silhouette

Rim73's restricted-window peak often lies at minus 1.5 or plus 1.5 pixels, exactly at its search-window boundary. Such a peak is not a resolved maximum or width estimate. The new requested gradient is intentionally brightest at the far rim, but target RGB can also include bright transmitted content and a varying backdrop.

The original full-frame target at each position is not a direct alpha mask. Typography, card gutters and white backgrounds create intensity transitions independent of the control boundary. Foreground-box avoidance in the saved profiles removes direct glyph crossings there, but not backing typography or refraction. No brightness-to-alpha conversion is justified.

For a hypothetical translation, opposite normals would see opposite signed offsets; a common minor-half change would move upper and lower extrema coherently outward or inward. The retained intervals are too broad and confounded to identify either pattern uniquely. No simultaneous objective or pixel fit was attempted.

$$
\delta d_{\mathrm{translation}}=\boldsymbol n\cdot\delta\boldsymbol c,
\qquad
\boldsymbol p(d)=\boldsymbol p_0+d\boldsymbol n.
$$

This is geometric interpretation only. It does not turn the manually bracketed intensity intervals into model residuals. Nor does it establish that current dimensions are exact; subpixel deviations and subtle nonordinary silhouette shape remain unresolved.

## Recommendation and preservation

Proceed with root's declared outline hypotheses while keeping current contours and original scoring masks frozen. Report size/placement uncertainty explicitly rather than using a bright-ridge peak as a pose target. Do not add per-reference translation or a shared radius correction from this audit. The family requirement that only length varies remains intact.

The approved wider initial outline and angular fade direction are root-owned next-stage inputs. This review neither tunes them nor authorizes another geometry. All historical failures, partial cohorts, source limitations, accepted counts and untracked task 46 remain preserved.

## Accounting and checks

There are zero new profiles or samples. Thirty-two saved profiles contain 800 selected rows, with 12800 scalar observations conservatively reserved for inspection, native-coordinate mapping and metadata comparisons. Viewing four existing comparison sheets decodes 2257148 image cells, below the declared cap. No source reads, optical calls, height evaluations, fits, masks or candidate composites ran.

Input/factory/pose/figure/profile hashes are checked at first and last read. Documentation and privacy checks precede own-folder versioning. Checkpoint and recommendation were delivered through Sessionsation before packaging. No successor task is activated by this report.
