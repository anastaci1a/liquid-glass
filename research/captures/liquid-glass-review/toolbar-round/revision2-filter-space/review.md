# Queue26 negative; queue27 conditional fit not activated

Six predeclared discrete ordinary-filter comparisons, zero optical qualifiers.
OLD accepted E6.870490597950 remains best. All inputs/widths/geometry/material,
native AA4×4, coverage, generated shadow and vector foregrounds stay fixed.

|Convention|source only E|output only E|both E|
|---|---|---|---|
|sRGB|11.185951289|6.874198209|11.194086071|
|inverse BT709 OETF|10.424424685|6.873461101|10.431581284|

Every comparator fails glass/rim and BOTH foreground guards; exterior modestly
improves, which does not override failed optical/foreground gates. Full scores,
progress_gate reports and cohort diagnostics are in each measurement.json.
Observed-source-kernel proxy63571pixels: source-only change has desired residual
cosine -.36010(sRGB)/-.35835(BT709), output-only -.02651/-.02640. Observed-cohort
RMSE worsens from4.49449 to12.8111/11.5447(source) or4.49504/4.49494(output).
The larger changes are not supported improvements on independently supported
content. These masks remain advisory, not replacements for native scoring masks.

Controls: new raw encoded raster plus original postfilter recovers accepted full
native material BIT EXACTLY, as does coverage and baseline E. Earlier queue6 did
not persist its unfiltered raster, so one necessary raw reconstruction enables
output-only evaluation; no independent completed test was restarted. THREE raw
native rasters (encoded,sRGB,BT709) generate SIX operator results; no optimizer
or material fits. All arrays persist before scoring. Encoded small-crop delegation
is exact; four uniform native controls across two conventions/two scales pass
within1.50e-7. Gaussian source11px/output1.25px widths unchanged/proportional.

Explicit knees: sRGB max roundtrip2.96e-8, BT709 .0002479329 in normalizedRGB due
rounded published coefficients. BT knee decode drops from approximately.018 to
.01794502 at.081; encode jumps at.018 to.081247944. These tiny inconsistencies
are retained and documented, not silently smoothed into a new transfer curve.
No claim of strict identity at the rounded knee. Baseline remains encoded.

Operator order and primary links in model.md. Default Core Image light-linear
filtering motivates the comparison, not proof of Liquid Glass internals; footage
tags do not identify UI space. The result concerns the current bounded operators
with current affine material; it does NOT rule out all radiometric renderers or
calibrated physical materials. Ordinary transfer-dependent filtering is separate
from dispersion21 and empirical covariance25. Source23 remains UNADOPTED.

Queue27 review: no useful filter convention is supported by the measured native
or observed-cohort direction. Its conditional shared-material fit is therefore
NOT activated; compensating a selected losing operator with an arbitrary sweep
would not resolve the working-space evidence. This is a conditional decision,
not a fabricated fitted family or global impossibility claim. Next-task request13
sent BEFORE this decision (nativeaccepted d7003cd8-62af-4f9c-a1d8-f0144a5fec64).
Continue28 intensity-response audit using these saved residuals and fixed source.

Reproduction in existing Docker, OPENBLAS_NUM_THREADS=1 and original PYTHONPATH:
python3 /evidence/extended/helper-toolbar-work/agent-toolbar-filter-space/study.py
--tests (controls); same command without --tests for the six comparisons. Reuse
completed raw-raster artifacts; do not gratuitously repeat completed controls.
No shared edits/commit/push or new accepted pass. Native original scoring epoch
d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d.
