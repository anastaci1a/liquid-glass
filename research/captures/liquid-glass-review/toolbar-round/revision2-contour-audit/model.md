# Queue31: independent toolbar silhouette evidence, before shape fitting

Reuse audit of prior evidence FIRST: reproduce.py declares regular center[960,542],
half[392,170], radius170 without a toolbar contour measurement/uncertainty dataset.
The current softness.10 was selected in the earlier image-score bracket, NOT
independently measured silhouette. pass03 cap-join/crown variants are geometry
experiments/preferences, not toolbar contour measurements. contour.json measures
the SLIDER at center[763.5,548.57]/half[118.5,56.5], not this toolbar. Selector
white-ridge fits likewise belong to a different element. No duplicate extraction
of those other elements, and no substitution of their softness/pose here.

Accepted source/map/material/foreground/native masks and epoch stay fixed;
candidate29 remains frozen pending primary review.31 is measurement only, not
shape optimization or a new optical fit. The intended boundary is not directly
observed alpha: white highlight ridge, outer intensity edge and physical alpha
boundary can differ. Shadow/blur/lighting/text overlaps must remain explicit.

Predeclare before NEW target profile extraction:
- Generate original accepted crowned boundary geometrically, then sample it at
approximately2nativepx arc spacing. Analytic outward normals. It only defines
search windows/orientation; no pose/size/softness fitting, no photometric residual
optimization or moving scoring masks.
- Raw native TARGET luminance profiles t[-8,12]nativepx outward at.125px spacing,
explicit full-fraction bilinear measurement. This is reference analysis only,
not changing the rendering sampler/epoch. Pixel data have native resolution;
subpixel extrema are proxies, not extra independently observed detail.
- Keep raw source/target profiles, all rejection flags and existing glyph boxes.
Exclude profiles crossing foreground boxes expanded4px. Exterior text/edge guards
come from BOTH frozen source and target t[3,12] profiles: min luminance and range.
Base cut .70/.08; sensitivity grid mincut.65/.70/.75 × range.06/.08/.10. These
are fixed before results, never chosen to maximize a shape/optical score. A source
model can hide text; paired target guard remains necessary. No masks are rewritten.
- Distinct observable proxies: brightest ridge t[-4,4]; strongest outward-negative
gradient t[-2,6]; outer ridge-to-background level crossings at.25/.50/.75 peak
contrast. Background is median t[8,12]. Require ridge prominence>=.01normalized
RGB and interior window extrema; preserve ambiguous/missing/edge-window cases.
Measurement smoothing0/.5/1nativepx is sensitivity analysis only, not an optical
blur coefficient or a source edit. No proxy is silently declared physical alpha.
- Signed residual is observed proxy t relative to ORIGINAL accepted boundary;
positive outward. Report top/bottom/left/right and shoulders separately, overlap
exclusions, contrast/threshold/smoothing sensitivity. Bootstrap32px arc blocks,
1000resamples,95%median intervals to reflect local correlations, not pixel counts.
Do not interpret a global mean with cancelling signs as measured shape agreement.
- A stable same-sign residual must survive independent observable/threshold and
block uncertainty before32 chooses a nominal measured footprint. If ridge/edge
proxies straddle the boundary or bias is unknown, report missing alpha/lighting
evidence rather than fit a convenient curve. No common crown/pose correction
render is authorized from an ambiguous ridge alone. Source support must be valid
and primary review required for32; masks/history/input/optics remain untouched.

Source inventory and raw case/protocol hashes retained in report. No new image
registration, typography fitting, reference effects or additional element study.
Request15 sent before31 (49011e3a-495c-45c0-934b-45eeaf57d84c); request next steps
again before32 while31 continues, per standing queue. Explicit Ana pause wins.
