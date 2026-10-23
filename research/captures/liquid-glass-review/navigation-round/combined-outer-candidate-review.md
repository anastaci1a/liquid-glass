# Navigation candidate: combined existing outer-normal step

FIRST numeric candidate from the latest approved combined-step task; primary acceptance PENDING. Stopped after ONE native proposal; no backtracking, further material/shadow family, optical count, commit or public edit. Earlier eight negative proposals remain rejected and unchanged.

Paired/pass24 baseline, two original observations. Delta(c0,c1,c2)=(-.0008796622505031546,-.0007882308784403789,+.0003321068710566408). Each is within ±.002. No other parameter changed. Sources, target/known masks, original scoring masks, shape, glyphs/styles, material/gamma, shadow, ordinary blur and AA fixed.

|Original native metric|A baseline|A candidate|B baseline|B candidate|
|---|---:|---:|---:|---:|
|E|1.979013168449246|1.978977992926633|7.434360042278334|7.434263434929931|
|glass RMSE|1.610732555389404|1.610706567764282|6.044371128082275|6.044299602508545|
|rim RMSE|2.645985364913940|2.645934581756592|9.949139595031738|9.949000358581543|
|exterior RMSE|8.735226423581446|8.735226423581446|9.774154815950626|9.774154815950626|

All eight original foreground MSEs in EACH reference are EXACTLY unchanged (full names/values in result.json). Interior RMSEs unchanged. E decreases .000035175522613 for A and .000096607348403 for B, roughly .00178%/.00130%; no percentage minimum invoked. Both prior native baseline/cache zero controls had maximum material difference0 and E difference0. Candidate alters13460/12102 scored glass pixels, with glass delta-image RMS .001689/.017490 RGB0–255; this is a real native image change, not a changed scoring reduction or a solver success label. Final meaningfulness and visual acceptance remain primary decisions.

Source report freshly evaluated for the changed candidate map: defined, observed, Gaussian3sigma-defined and Gaussian3sigma-observed fractions are1.0 on both original valid masks; source Gaussian radius21nativepx. Unchanged source provenance/confidence caveats remain, including temporal recovery and compression. Coverage shape is unchanged. No unknown hidden ink, exact Apple optical model or exact Apple glyph/font configuration is newly established.

One small predictive SLSQP calculation used the SAVED SIX scalar native score responses (the six full response images had not been retained). It did not rerender derivatives or fabricate full arrays. Model uses normalized steps delta_c/.002, saved central slopes and nonnegative diagonal scalar curvature; mixed terms omitted. Tiny model constraint residuals are recorded without claiming strict feasibility from optimizer status. Actual ORIGINAL Study.render, s.scores, fixed nonlinear SVG compositor and generated exterior check independently pass all numeric guards; those alone selected the candidate. No surrogate sampler or precision epoch substituted.

720p preview order is target / baseline / candidate, stacked vertically, both774×720. Inspected both: no obvious new artifact at this preview scale; improvement is subtle and existing B upper-rim dark streak remains. Original source/unknown-context edge markings remain visible outside the scored lens; they are not synthesized effects or a new glass correction. No4x render was run. These previews are advisory and do not prove perceptual improvement; lead must independently inspect before accepting.

Frozen input/public-code digests and baseline arrays: /evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/{freeze.json,baseline-public.json,baseline.json,zero-controls.json,code/,a/,b/}. New immutable packet: /evidence/extended/helper-toolbar-work/navigation-round/combined-outer-saved/{proposal.json,trials.json,result.json,candidate-native.json,candidate-normalized.json,native-change-summary.json,trial0-ref0-material.npy,trial0-ref1-material.npy,ref0-complete.npy,ref1-complete.npy,ref0-target-baseline-candidate-720.png,ref1-target-baseline-candidate-720.png}. Normalized recipe sigma/post_sigma retain the public113.5px parameter basis; native recipe carries physical-pixel widths.

Exact completed command (completed guard prevents accidental repeat):

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/combined-run.py

Primary replay: instantiate public Study on each frozen a/b input folder, use candidate-native.json parameters/material with original Study.render, compare material arrays and all original native metrics/foreground/exterior guards. No baseline replay is needed solely for logs; existing exact matched baseline outputs are saved. Public normalized candidate is supplied for final lead recipe construction after acceptance. Agent has not altered the public paired history/accepted state or applied pass labels.

Next: primary independent replay,720 visual/source review, then commit/push ONLY if accepted. Await acceptance before counting or pursuing another qualifying pass. Please supply one subsequent bounded task before the queue runs out; no new speculative audits. Navigation count remains0/3 until independent acceptance.

## Superseding preview rule

Ana's subsequent WIDTH rule replaces the720p-frame sizing above. New target/baseline/candidate files are EACH1080×335, preserving the original navigation crop without enlargement. Optional vertical comparison stacks are1080×1005 (three individual1080×335 images), so height is not capped at720. Files ref{0,1}-{target,baseline,candidate}-width1080.png and ref{0,1}-target-baseline-candidate-width1080.png are saved in the same evidence packet; preview-width-rule.json records dimensions. Old720 previews remain separately preserved. No optical render or score recomputation occurred: target and candidate arrays were reused and baseline presentation recomposited from the saved material/source and unchanged shadow. Native scoring/source epochs and candidate metrics are unchanged; no automatic4x render. Independent lead visual acceptance should use the new1080-width images. Count still0/3 pending primary review.
