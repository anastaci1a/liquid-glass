# Queue30: tiny image sensitivity, substantial small-probe derivative instability

NO optical gain or sampler/epoch adoption. Frozen accepted rev2/source6c68,
target5bb5/masksda7d, exact original float32 ray coordinates and all existing
operators retained. One explicit full-fraction bilinear protocol comparison.
Candidate29 remains frozen pending primary acceptance; not refit in this audit.

Original E6.870490597950, full-fraction comparator E6.870457210018, difference
-.000033387932. This is a numerical-protocol effect, NOT optical improvement.
Full glass material change .00316869/255 RMS(max.0380132), observed-source proxy
.00378741, estimated .00001764, mixed .00382408. Plus guard slightly worsens
3.667139624→3.667554320. Coverage exact. Private comparator epoch
e724a4a9cc51aea9acbe75a3bf103122833943180a24d05f2da2b517e799cccf
is NOT adopted; progress_gate correctly REFUSES original/new protocol comparison.
No mask change, source resampling, coordinate shift, optical fit or accepted pass.

Installed OpenCV5.0.0 has INTER_BITS5/table32. Full-fraction affine-ramp error
1.67e-16 at SAMEfloat32 coordinates versus table ramp max.00076717 normalized
RGB; cv2.convertMaps table-coordinate emulation matches to1.11e-16. Integer,
half-integer, endpoint/partial/outside constant-zero-border controls exact. Constant
interior preserved exactly; partial outside footprints correctly taper to0, not
claimed globally constant. Gaussian's existing reflected-image border is distinct
and unchanged. Native sample coordinates are far from either border.

4096 deterministic observed-kernel-proxy inside rays, no target-selected subset:
full-fraction analytic gradients versus finite differences inside the SAMEbilinear
cell agree within4.21e-11 RGBlevels/nativepx across dyadic h.25..1/4096. Current
OpenCV table derivatives increasingly plateau/jump:

|h nativepx|table gradient RMS error,RGBlevels/px|zero derivative fraction despite analytic signal|
|---|---|---|
|.25|.000578|0%|
|.0625|.000593|0%|
|.015625|.04720|0%|
|.00390625|2.82415|57.495%|
|.0009765625|6.22414|87.793%|
|.000244140625|11.72570|96.704%|

Full-fraction bilinear gradients are piecewise, not a smooth ground-truth source.
Integer-cell crossings/exact-integer ambiguities are explicitly counted and only
excluded from the derivative-error diagnostic, NEVER output score masks. Probes
are diagnostic differences, not applied/fitted per-reference image shifts. Same
float32 coordinates used for both samplers; original double→float32 rounding is
separately reported in derivative-stability.json. Do not infer zero physical
sensitivity or global convergence from very small quantized-remap parameter probes.
Earlier rejected-family logs remain unchanged; no completed experiment repeated.

Limits: the coordinate derivative holds the original clear/blur blend weight fixed;
it is the source-sampling derivative, not a complete optical-parameter Jacobian.
The small image change shows current table precision is not a major baseline
residual explanation here. No permission to switch scoring or refit under a more
convenient differentiable sampler. Ordinary blur/dispersion remain separate.

Recovery accounting: first run stopped BEFOREnative rendering because the test
fixture assigned row/column ramp axes backwards. Implementation unchanged; failed
script/partial control record retained. Border control result reused; corrected
ramp fixture passed. ONE completed native protocol comparator, zero failed native
renders, six completed derivative probe sizes, zero optical trials/counts.

Private proposed primitive toolbar_sampling_precision.bilinear(image,x,y,
gradient=False) handles identical zero borders and explicit float64 weights.
quantized_coordinates() uses installed convertMaps, not guessed tie rounding.
No shared/public edits/commits/pushes. Reproduction existingDocker originalPYTHONPATH:
python3 /evidence/extended/helper-toolbar-work/agent-toolbar-sampling-precision/audit.py.
Completed controls/nativearrays/derivative rows reused; before-ramp-fix file is
historical evidence only. Primary source link/operator protocol in model.md.
Continue31 existing silhouette evidence audit; request nexttask before starting.
