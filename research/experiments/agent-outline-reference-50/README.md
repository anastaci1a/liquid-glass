# Reference review: an extremely thin composited rim

Recommend one outer-anchored white overlay with a very short smooth inward fade, tested on the frozen body. Do not produce a detached inner line or a sharp inner cutoff. Constant all-around opacity is an initial hypothesis, not a recovered property. These references do not justify directional opacity tuning or importing a dark outline from another control.

Task 50 starts at 20:31:07.261 UTC on 25 October 2026 and ends by 20:46:07.261 UTC, including versioning. The checkpoint is recorded separately. Immutable input pin is `59bfc23b26e16d00201128c0cb9773431f9331e0`. Primary inputs were read only; there was no merge or shared edit.

## Scope and user interpretation

The user explicitly describes the outline as a separate effect composited over the body, excluded from refraction. The desired maximum is at the outer rim, with transparency increasing extremely quickly and smoothly inward along the local edge normal. The user is uncertain whether the compact rim has constant strength around its entire perimeter.

This review accepts that effect separation as the current implementation direction. It does not identify an optical reflection mechanism, recover physical alpha or establish an exact native width. Refraction, material, masks, sources, foreground, previous scores and all historical negatives remain unchanged.

## Evidence inspected

The four original expanded/compact A/B target images and all four saved twelve-panel rim 73 sheets were inspected. The retained profiles contain 48 fixed sections, sampled historically from minus six to plus six native pixels at quarter-pixel intervals. No new image sample, profile, derivative, threshold, alignment or reduction was generated here.

Rim73 uses the frozen projected rounded rectangle. Negative signed distance is inward. Its restricted peak window is minus 1.5 to plus 1.5 native pixels. Some peaks land on that window boundary, so neither their position nor width is identified. The saved AA2 coverage is a numerical model field, not observed alpha.

Original target/case hashes match rim 73's pinned receipt. Its scientific records and saved profile sheets match the immutable Git pin, including hydrated LFS object hashes. First/last review hashes are retained. The source images themselves are not inspected or reconstructed; only already-saved target references and profiles are used.

## Thin fade versus inset band

The original compact references show a delicate perimeter line, especially against colored or dark backing. Their broader white returns and interior brightness changes do not all follow that perimeter. Those structures should not be absorbed into an enlarged overlay width.

The user rejects the current doubled contour; the replacement effect should not preserve a second inner maximum merely to match aggregate error.

An outer maximum with a continuous inward fade is consistent with the requested appearance. It is not equivalent to adding a narrow constant-opacity stroke with a hard inside edge, nor to broadening the existing optical inset band. Keep the body frozen during the overlay discriminator so any new contour can be attributed correctly.

## Saved landmarks and confounds

All following numbers are attributed to rim 73's existing `result.json`; they are not newly measured.

| Fixed section | Reference prominence above both side means | Largest reference-minus-working excess | Interpretation limit |
| --- | --- | --- | --- |
| Compact A, top center | 56.5542 levels | 54.3741 levels | Distinct local peak, but contour registration remains frozen |
| Compact B, top center | −0.0063 levels | 53.1140 levels | Bright exterior transition, not an isolated white ridge |
| Compact B, upper-left diagonal | 6.9385 levels | 88.4266 levels | Large mismatch does not imply large overlay opacity |
| Compact A, lower-right diagonal | 62.9483 levels | 77.1883 levels | Strong local highlight with backing and return ambiguity |
| Expanded A, upper-left diagonal | 66.5544 levels | 70.7547 levels | Local brightness is not measured alpha or source identity |
| Expanded A, lower-left diagonal | −4.3529 levels | −17.6777 levels | Existing working body is already too bright in this rim window |

Compact A and B share the contour yet see very different backing. In B, the top edge lies near a white exterior field; its profile rises into that field rather than forming a separate peak. Colored cards, white lettering, bright card gutters, refraction returns, material veil and local blur all change apparent rim contrast.

Expanded A's lower/corner sections include regions where the working result is already brighter than the target. Expanded B also has negative excess at selected lower/corner locations. A nonnegative white overlay cannot correct those local over-bright regions. Retain them as failures of a complete explanation rather than introducing a dark term or changing refraction within this task.

The original profiles avoid foreground-box intersections. That removes direct glyph/artwork crossings at those samples, but does not remove backing typography, material differences, registration uncertainty or scene-dependent returns. The observations provide no clean estimate of a common overlay coefficient.

## Uniform white does not mean uniform visible brightness

A uniform opacity can yield different visible increments on different backgrounds. For illustration only, a white top-composite has the channelwise algebra:

$$
C_{\mathrm{out}}=(1-\alpha)C_{\mathrm{body}}+\alpha\boldsymbol1,
\qquad
\Delta C=\alpha(\boldsymbol1-C_{\mathrm{body}}).
$$

This is symbolic compositing logic, not a fitted response or a prescribed encoded/linear-space choice. It explains why brightness variation around the rim does not by itself refute constant opacity. The shared implementation must declare its actual color space and composition order separately.

Conversely, a white-only top-composite cannot darken an already bright body. Negative residuals therefore limit the proposed effect's ability to explain every observed edge. They do not independently prove that the reference contains a dark overlay. Different controls may use different treatments, as the user noted; this review makes no cross-control uniformity claim.

## Actionable recommendation

Use one geometric inward-distance fade anchored at the frozen outer silhouette, with no second peak and no hard inner edge. Start with the requested all-around white hypothesis and expose its local failures. Keep exact old scoring and partial cohorts. Do not select a width, strength, directional mask or color from this reference-only review.

The primary visual checks should be the thin exterior contour and absence of a doubled inner line, separately from broad return placement and body tone. Compare both backing states at the same frozen pose. The brightest profile sample need not coincide with the physical silhouette because target antialiasing, registration and backing remain confounded.

There is no new geometry or successor task here. Root owns the shared overlay and its frozen-body miniplayer test. This report supplies a reference interpretation and cautions, not a rendering implementation, automatic adoption or successful-fidelity count.

## Checks and clock

Recommendation and checkpoint were sent through Sessionsation before packaging. First/last input hashes, preservation of old files, documentation and privacy checks are recorded separately. No new optics, sampling, source/RGB query, filter, fit, composite, image export or plot ran. Viewing existing images is the only image access.

The initial login shell changed the requested working directory and made a bare Git status fail. Subsequent repository operations use the explicit existing worktree with a non-login shell. No worktree, branch, session or account was changed. The original task clock is retained.
