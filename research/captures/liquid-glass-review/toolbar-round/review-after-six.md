# Procedural review after six substantive experiments

No successful pass has been counted by agent. Experiments1–3 and first review are immutable;4 was the small combined candidate,5 completed its bounded bracket,6 generated a shadow. Subsequent native/HQ repeats are verification, not additional improvement passes. Two script failures during shadow reporting (OpenCV1D remap width limit and float64 Sobel output limitation) are preserved by the original scripts and were corrected without changing sources/masks; neither is a valid extra optical experiment.

## Crown/blur bracket

Initial bracket: softness .04/.06/.08/.10 × post_sigma .25/.5/.75/1.0 native px. Because the minimum touched the upper blur/softness bounds, extend to .08/.10/.12 × .75/1.0/1.25/1.5. The completed bracket supports an interior choice: softness .10 / blur1.25px, E6.998512744608, glass6.044535160065, rim8.832458496094. Softness .08 and .12 both have worse E at1.25; blur1.0 and1.5 both have worse E at .10. Source blur, all normal/tangential/material coefficients and source pixels remain unchanged.

The selected footprint still uses the existing smooth convex implicit-boundary primitive, not recovered physical height or a globally exact Euclidean signed-distance field. Spatial filtering is ordinary color blur, independent of dispersion; α remains sharp and separate. One combined improvement is one pending pass, not a pass for each grid point or shadow fit.

## Shadow

Fit a neutral attenuation field `a=opacity * Gaussian_sigma(coverage)(x-offset)`; output `glass*alpha + source*(1-a)*(1-alpha)`. All four parameters are shared globally in normalized L units. No target RGB is sampled into the model; target is used only to fit these four coefficients against the original frozen exterior mask. Opacity is solved analytically at each nonlinear trial, clipped0–.4. Width .012–.3L, offset x±.05L/y[-.1,.15]L; three Powell starts converge to the same result.

Selected opacity .219680649874; sigma .299999947760L; offset[-.002930886319,.007772858575]L. Native L170 means sigma51px, dx−.498px/dy1.321px. Fixed exterior RMSE19.272913277567→11.469442019668. No conditional glass value changed during this shadow fit. Shadow width reaches its explicit .3L bound: do NOT claim the width, opacity or light rig is uniquely identified. The fixed35px exterior only partially constrains a broad shadow; retain this limitation for primary review rather than silently increasing model freedom.

Far-band diagnostics were added without changing the acceptance mask: RMSE35–55px21.6271→15.7654;55–80px21.4535→18.2716. They improve, so the new shadow does not merely move visible error just outside the gate. No photographic-reference residual or original shadow is copied.

The frozen original glass mask contains some pixels partially covered by the new footprint (minimum generated alpha .625). Its conditional material scores remain the exact historical protocol and must stay labeled that way. Complete-composite advisory scores also improve (glass5.972587/rim8.680297), so hidden coverage changes are not used to conceal a regression. Do not silently substitute those better numbers into the frozen conditional-glass ledger.

## Verification and pending review

Independent primary had verified the EARLIER .08/.5 candidate and all emitted subpixel lookups. Current .10/1.25 plus shadow requires a NEW independent primary replay and visual/source checks; no prior acceptance is inherited. Agent native shadow repeat using padded, crop-independent Gaussian shape coverage matches exterior RMSE to8.3e-8. Five unit regressions pass (incumbent-map recovery, no dark blur boundary on uniform glass, symmetry, shadow crop independence, zero-opacity identity). New correct d crop preserves the earlier incorrect crop as historical diagnostic evidence. Canonical glyphs remain exclusively lead's task.
