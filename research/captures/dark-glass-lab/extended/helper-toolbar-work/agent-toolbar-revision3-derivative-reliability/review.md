# Queue33: full normal-profile derivative reliability

Completed on accepted revision3, commit02a054e23fb0fb8f9d1a1e1ee3bb53a36ed12d45, E6.790203130095051, gamma1.0456395525912732 and accepted common material offsets. Source/target/masks/epoch unchanged.43 native diagnostic evaluations (zero plus seven coefficients × three symmetric step scales); zero optimizations, zero qualifying optical passes. All70strips checkpointed; no interrupted evaluations or duplicate runs. Native zero material is EXACT (maximum difference0) against frozen accepted29/revision3, all original scores reproduce.14 representative original-map comparisons (4096rays each, both signs, each coefficient at largest step) are float32-coordinate exact. This does not prove every perturbed ray is bitwise identical under alternate floating-point reassociation.

Complete chain: exact normal coefficient map derivative, clear/blur source gradient mixture, current shared power response and material gain, clipping indicator, conditional native4×4 AA, normalized fixed-coverage postfilter, then fixed coverage/shadow/glyph transmission for complete guards. The full-fraction source-gradient chain is a SURROGATE, not the derivative of discontinuous OpenCV quantization. Actual direction images/scores use original quantized cv2.remap, original source and masks; surrogate scores NEVER accept a pass. Native guard finite differences inherit original float32 glass/rim reduction and can be unreliable for very tiny changes; no higher-precision scoring epoch silently substituted.

At h=.002, whole-glass image direction cosine / relativeRMSerror / actualE derivative:

|coefficient|cosine|relative RMS error|native dE/dc|
|---|---:|---:|---:|
|0|.997329|.073070|+.067056|
|1|.999129|.041770|+.074863|
|2|.999890|.015133|−.264678|
|3|.999885|.015420|−.242753|
|4|.999961|.009074|−.666053|
|5|.999957|.009346|−.979075|
|6|.999961|.008838|−.530507|

At h=.000125, coefficient0 cosine falls to.791643/relativeerror.617188;4–6 errors are.093077,.120511,.159958. At.002,4–6 observed-source proxy direction cosines are.999959,.999951,.999968 and RMS errors.009372,.009918,.007968; forward/backward asymmetry remains3.0–3.6%, so even these local directions are not globally linear. Source cohorts are earlier fixed support PROXIES, not recovered hidden text.0/1 observed-source glass derivatives are exactly zero;2's observed signal is tiny (.00647RGB/255 per coefficient) and cosine.8798, so outer direction agreement mainly comes from other/uncertain support. No source identifiability claim.

32768 deterministic inside rays, no target selection. At h=.002, active-ray table-cell crossing fractions span.671827–.739156; integer crossings.068111–.095921. Observed largest displacement is.339788px (coefficient0), inner4–6 maxima.239820,.218156,.210945px. At h=.000125, table crossing fractions are only.1690–.2012, explaining table plateaus/noisy small finite differences. Full distributions/denominators are in coordinate-steps.json; outside diagnostic support is NEVER excluded from scoring masks.

The five guards matter: at.002, increasing4 lowers glass/rim, leaves foreground scores unchanged and changes exterior by about−1e−9absolute. Increasing5 or6 lowers E/glass but WORSENS rim and plus (native plus derivatives+.089918,+2.107510). Thus an E-only descent direction is insufficient. Increasing2 also worsens exterior;3's exterior slope is positive and tiny/sign-sensitive across steps. Outer0/1 lack source-supported observed signal. No coefficient sweep is counted as progress.

Large raw native/derivative arrays and32768-ray diagnostics are retained in dark-glass-lab/extended/helper-toolbar-work/agent-toolbar-revision3-derivative-reliability (same folder inside Docker /evidence/extended/helper-toolbar-work). JSON/protocol/code copied here. Full native outputs are raw AA colors with fixed postfilter defined in audit.py; postfiltered surrogate.npy retained. No source/AA/material/shape/shadow/glyph edits, no public edits, commits or pushes. Source-only Gaussian blur remains ordinary blur, no spectral/dispersion operator added.

Exact command (Docker already running):

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-code/toolbar_derivative_reliability.py --root /evidence/extended/helper-toolbar-work/agent-toolbar-revision3-derivative-reliability --recipe /tmp/agent-toolbar-code/accepted-toolbar-revision3.json

Completed driver is idempotent: signature-checked completed results exit without native reevaluation. No new native refit is authorized by this report;34 prepares/rejects a protocol, primary reviews.
