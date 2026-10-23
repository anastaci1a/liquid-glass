# Slider first numerical candidate: saved strength/post-blur half-step

READY for independent primary native/source/visual/precision review; new round accepted count stays0/3. Stop first numerical qualifier after TWO actual joint native pairs, no next pass/family. Baseline currentmain a1b8b1b5 active-switch revision6; original masks/source epoch60004319569df35f2dcdea7e9418685a27de61728813c3b9a68091337853835c unchanged.

|Ref|Baseline E|Candidate E|Baseline glass|Candidate glass|Baseline fixed exterior|Candidate exterior|
|---|---:|---:|---:|---:|---:|---:|
|A|14.075942720072991|14.075936323890298|11.155917167663574|11.155611038208008|6.534458637237549|6.534408092498779|
|B|15.317415659821096|15.317346124726264|13.641358375549316|13.64134407043457|4.46285343170166|4.462714672088623|

All original paired E/glass/fixed exterior guards strict, no epsilon. Original cases have ZERO foreground/glyph layers; no geometry or icon/vector fit. A standalone rim RMSE worsens; it is retained below and is NOT a separate original acceptance guard. No claim that every diagnostic improves.

|Ref|Baseline rim|Candidate rim|Advisory glass deltaMSE|Advisory rim deltaMSE|Advisory weightedloss delta|
|---|---:|---:|---:|---:|---:|
|A|19.23659896850586|19.236997604370117|-0.006815965912592794|0.015418328706528017|-0.00014567752685655088|
|B|18.651412963867188|18.651247024536133|-0.000411301813893362|-0.006233428572474227|-0.0021579398414676215|

Advisory float64 direct residual changes use SAME saved native float32 pixels/target/masks (mean(2*baseline_error*delta+delta²)), not a changed score epoch. Both weightedloss changes are negative; native B gain is measurable beyond known quantization. A progress is tiny, no visual parity claim.

Candidate: strength change -.001, final 0.3839814426989986, ordinarypost_sigma change +0.0004946601132829589 reference-nativepx, final 2.1640325817432378. Existing directional length.08, angle1.3571487177940904, fadecenter-.395271178284122/fadewidth.3577136899555915 fixed. Material, ordinarySOURCEGaussian, gamma, shape, optical spline/core/tangent, source-derived response, grazingreflection, shadow, inputs/masks unchanged. Fixed spectral/channel-split contribution strength is separate from ordinary outputGaussian; no wavelength-law or new opticaloperator introduced.

Reuse audit: prior revision6-spectral-mixture had combined trial metadata only, no retained PUREstrength pixelarrays/derivativeforms. Its implementation computed transient derivatives but discarded them; those unavailable intermediate values cannot be reused or claimed saved. Only this explicitly authorized +/- .002 purestrength pair was evaluated and saved. Both fail with opposing A/B E tradeoff:

- strength -0.002: E 14.075842460485267/15.317730440697257, strict failure.
- strength 0.002: E 14.076085567038286/15.317104056063696, strict failure.

Conditional joint used ONLY those saved strength arrays plus the already-saved +/- .05postblur arrays, one two-dimensional quadratic proposal. No repeated completed probes or fresh derivative renders. Normalized bounds strength.002/postblur.05reference-nativepx. Solver success=true, but model A constraint -3.6159742218102155e-18 is numerical model output, never native acceptance. Full proposed step fails A native E +.0000006025865247 and advisorydouble A weightedloss +.000041114812616, retained strict failure. Half actualstep passes all original guards and both advisory residuals, stop. No epsilon/tie pass. Historical rev6 spectral-mixture/kernel/curvature rejections remain historical, not retrospectively promoted.

Fresh candidate source check: each whole and ALLscored base/RGB transmission including A50/B27 scored subrays outside corrected outline, reflection actualnativeoutputwhole/scored grid and materialcontext footprint. All DEFINEDminimum1/zero undefined. Original allow_estimated_background=true retained: OBSERVEDfraction/minimum0 across sampled active cohorts; hidden-track/sourcecontext RGB is a previously adopted estimate, NOT recovered photographic truth. A basewhole974432/allscored961824; B847118/835876; active R/B eachwhole363258/316395 andscored359088/312602. Reflection3sigma5px, sourceGaussian3sigma13/12px. This discrete source proof is not continuous/infinitekernel or outputscatteringconfidence theorem. Source maps fixed; strengthweight active support freshly checked. No new sourceadoption/mask/sourcekernel/epoch.

Packet /evidence/extended/helper-toolbar-work/active-slider-round/strength-postblur-joint/: candidate-native.json (authoritative actualparameters/material/scores), candidate-public-native.json (native-unit public-compatibleparameters; retains legacy revision6 explanatory metadata, primary should replace method/provenance for publication), result.json/trials.json/proposal.json/forms.json, selected trial1-ref0/1-material.npy, ref0/1-complete.npy and alpha.npy, fresh-source-proof.json and emptyundefined-ray arrays. Rejected fullstep is trial0, not candidate. Native825x590 A and785x570 B target/baseline/candidate previews respect cap720 rule (originalwider staysnative, no enlargement/no4x). Both candidate previews inspected; inherited darkoutline/softness/colorfringe mismatch persists, no obvious new artifact from this tiny update; independent primary visual review still required.

Exact command already completed; driver refuses reruns:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/active-slider-round/strength-postblur-joint.py

Pureprobe command same directory/strength-first.py, also complete. No newsource/shape/operator/public edits or leadExpanded overlap. Sharedflag READY_FOR_PRIMARY and nativequeue f5a4e531-e9c5-4b7b-8021-dad6b5175aa9. Queueaccepted is not proof consumed or primaryaccepted. Conditional negative three-family/crop review was NOT activated because a numerical qualifier was found; no lengthy diagnostics/nextpass started while waiting. Request next useful bounded task after primary decision.
