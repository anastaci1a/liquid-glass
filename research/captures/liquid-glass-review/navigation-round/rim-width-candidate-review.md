# Navigation candidate: shared rim_width −.00025

FIRST trial qualifies numerically; STOPPED. Accepted pass1/native18a09b0 baseline, rim_width .01666772149005208→.01641772149005208. ALL other recipe entries and23 material coefficients unchanged. One native trial pair; no derivative/optimizer, positive-width trial, thin_width study, audit or4x render. Primary independent acceptance pending; count remains1/3.

|Original native metric|A accepted pass1|A candidate|B accepted pass1|B candidate|
|---|---:|---:|---:|---:|
|E|1.978977992926633|1.976554458704428|7.434263434929931|7.430088836808378|
|glass RMSE|1.610706567764282|1.608913302421570|6.044299602508545|6.041206836700439|
|rim RMSE|2.645934581756592|2.642439603805542|9.949000358581543|9.942986488342285|
|exterior RMSE|8.735226423581446|8.735226423581446|9.774154815950626|9.774154815950626|

ALL16 original foreground MSEs are EXACTLY unchanged. E decreases .002423534222205/.004174598121553. Advisory interior RMSE slightly worsens: A .769258856773→.769259691238, B2.855348348618→2.855348587036; retained explicitly, not a hidden added/waived guard. Original whole-glass, exterior, foreground and both E guards all pass strictly.

This is an existing lighting-profile WIDTH change, not source/output ordinary blur, dispersion, an added colored effect or a changed silhouette. Geometry_field source coordinates and source kernel are unchanged; pass1 independently verified center AND emitted-ray source proofs transfer. Source/target/known hashes, masks, canonical SVGs/styles, shape, gamma/material, AA and shadow remain frozen. Prior baseline/native exact-zero controls and primary pixel-exact replay reused; no unnecessary baseline/source rerender.

Inspected1080-width target/baseline/candidate comparisons on both references. Small change with no obvious new artifact; B's existing upper/left dark-rim defect remains. No claim of Apple parity or new physical interpretation. Individual images1080×335, comparison stack1080×1005. Undefined exterior RGB uses nearest-defined source ONLY for presentation on BOTH baseline/candidate; raw material/complete/alpha arrays and native scoring/source remain unchanged, generated shadow retained and no target shadow copied.

Private evidence: /evidence/extended/helper-toolbar-work/navigation-round/rim-width-neighborhood/{started.json,trials.json,result.json,candidate-native.json,candidate-normalized.json,trial0-ref0-material.npy,trial0-ref1-material.npy,ref0-complete.npy,ref1-complete.npy,ref0-alpha.npy,ref1-alpha.npy,ref{0,1}-{target,baseline,candidate}-width1080.png,ref{0,1}-comparison-width1080.png}. Canonical driver navigation-round/lighting-width-neighborhood.py. Accepted pass1 native arrays/input/public-code freeze remain in combined-outer-saved and short-outer-profile packets; no duplication of large input caches.

Exact completed command:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/lighting-width-run.py

Completed guard returns without repeating a study. Because rim qualified, thin_width was NOT started; the conditional negative branch remains inactive. Review flag review-ready.json is READY_FOR_PRIMARY, candidate=true, accepted_count1. Please independently replay/inspect/source-review, then count/commit/push only if accepted. Ask next short task before the queue runs out; no subsequent qualifying fit until primary acceptance. Public worktree untouched; explicit Ana pauses override continuation.
