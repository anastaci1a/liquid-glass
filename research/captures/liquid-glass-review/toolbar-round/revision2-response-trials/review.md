# First private numerical qualifier — primary acceptance PENDING

STOPPED fitting after the first native joint proposal. E6.870490597950 →
6.790203130095, reduction1.168584203853% (> .5%); required E<=6.836138144960.
Original source6c68/target5bb5/masksda7d/epochd1d864 and native AA4×4 unchanged.
progress_gate numerical observation passes, but accepted=false because independent
replay, source review and lead visual acceptance remain pending. Zero new counted
passes; accepted revision2 and two verified toolbar improvements remain current.

|Original guard|Accepted rev2|Private proposal|
|---|---|---|
|glass|5.843130589|5.796156406|
|rim|8.813648224|8.677568436|
|exterior|11.469442017|11.466962523|
|archive full box|13.242044387|13.142080481|
|plus full box|3.667139624|3.304110822|

Exact proposal: gamma1.0456395525912732 shared acrossRGB/allpositions, applied
AFTER existing encoded clear/sourceGaussian blend BEFORE affine/clipped material;
common rim-gain+.006, common RGB bias+.003, common core-gain+.006. Existing14
lighting coefficients fixed. Original map/crown/pose, ordinary widths/transition,
source pixels, generated shadow and solid SVG geometry/color/placement unchanged.
No arbitrary crop/reference/channel curve, dispersion or source correction.
This is an empirical intensity/material proposal, NOT recovered physical optics.

Material/source ambiguity is material:28 found99.8615% of observed gamma-tangent
energy within the existing23material-coefficient span and strong source-alternative
confounding. The current trial does NOT prove gamma is required instead of common
material recalibration or uncertain source photometry/PSF. No material-only native
ablation was run after the qualifier; wait primary review before further fitting.

Advisory original crops: upper conditional9.20072→9.13472; d3.11043→2.89472;
UNDERSIDE WORSENS5.073945→5.483195 (~8.07%). Full visible underside5.06231→5.47054.
Fresh HQ comparisons show the contrast change; original d-curvature/crown transport
is unchanged and underside soft-reflection goal remains unresolved. Thus this
numeric qualifier is not claimed a visual acceptance or a solution to all feedback.
Lead should inspect underside carefully. No crop mask/metric was changed to hide it.

Controls before native proposal: exact gamma1/zero-offset small-crop baseline,
power endpoints and dense monotonicity at gamma.8/1/1.25, analytic monotonicity over
the FULL input interval and all bounded positive gains(min.25896638), neutral
uniform0/.43/1 plus scale2 within1.49e-7. Positive output/AA kernels preserve
nondecreasing response; source-independent lighting/clipping retained.

Fresh evidence: native8 diagnostic E6.785228789193 (advisory, never replacement
gate). Three padded fresh4×HQ candidate crops with true per-output4×4 optical
sampling, generated shadow and independently rasterized same solid SVGs. Native
reference enlarged4× is explicitly labeled, not fabricated HQ reference. Upper/
underside accepted HQfloat arrays reused from immutable queue9, hashes retained;
one fresh accepted d-crop HQ comparison. No duplicate completed baseline test.
All candidate arrays persist before reporting. Source/target/SVG hashes checked.
Map/code/shape/source widths identical, so primary's139059200fullHQ-coordinate
domain proof transfers; explicitly labeled INHERITED. Fresh crop proof checks
37165056 emitted coordinate pairs (including overlap, not claimed unique), finite
sourceGaussian radius44+bilinear1 margins>=296.53125nativepx. Defined input does
not imply observed hidden RGB; accepted estimated-source limits remain.

Accounting: ONE new native4×4 optical proposal, ONE native8 diagnostic, THREE
candidate HQ crop renders, ONE accepted d-HQ comparison; original full baseline
native arrays and two accepted HQ crops reused. Six small-crop control calls
(two identity comparison,four constant/scale). No optimizer/iterative calibration,
failed render, restored partial attempt, new source or accepted pass. All one family.

Files: first-proposal/{recipe.json,measurement.json,material.npy,alpha.npy,
complete.npy,complete-preview.png}; fresh-evidence/{native8,upper,d,underside,
source-verification.json}; invariants.json; reused-baseline-manifest.json;
code/toolbar_response.py SHA4dc32bbd3131b7249f88a85402a909b525923e713f77da6211941641bb7c316e.
Own-worktree proposed API toolbar_response.response(c,gamma), render(source,case,
p,samples=4,scale=1,atlas=None,checkpoint=None), recipe intensity_response.gamma.
Common offsets are stored directly in existing material coefficients. Current
private renderer imports unchanged geometry_signature from the private scattering
module; snapshot includes dependencies. No public/shared edits/commit/push.

Existing Docker reproduction, OPENBLAS_NUM_THREADS=1,
PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps:
python3 /evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/control-and-first.py
--tests for controls; without --tests for the frozen first proposal; evidence.py
for completed-array-reusing diagnostics. Primary independent replay should use
its own verifier, not relabel these agent checks independent. No further fitting
until primary accepts/rejects. Continue authorized30samplingprecision audit while
awaiting, with reciprocal monitoring; explicit Ana pause always overrides.
