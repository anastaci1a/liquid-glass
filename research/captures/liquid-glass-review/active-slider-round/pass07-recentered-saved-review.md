# Slider recentered saved model: half-step numerical candidate

READY for primary independent native/source/visual/precision review; accepted newround count stays1/3. Accepted baseline is public pass07, primary record extended/active-slider-primary-pass01/verification.json; recipe strength-postblur-joint/candidate-native.json and its selected trial1 material arrays. No stale revision6 baseline scores used for recentering.

|Ref|Accepted pass07 E|Candidate E|Accepted glass|Candidate glass|Accepted fixed exterior|Candidate exterior|
|---|---:|---:|---:|---:|---:|---:|
|A|14.075936323890298|14.075935303899977|11.155611038208008|11.155485153198242|6.534408092498779|6.534388542175293|
|B|15.317346124726264|15.317325222306266|13.64134407043457|13.64134407043457|4.462714672088623|4.462663173675537|

All original paired E/glass/fixed exterior guards pass strictly. B native glass ties; SAME-array advisory double glass residual decreases. A E gain is tiny, B E gain exceeds the native quantization-derived meaningfulness floor. No epsilon regression allowance or fabricated tie pass. Original foreground/glyph set is empty; no geometry/vector changes.

|Ref|Advisory glass deltaMSE|Advisory rim deltaMSE|Advisory weightedloss delta|Native rim accepted/candidate|
|---|---:|---:|---:|---|
|A|-0.002806035209099367|0.006435162135512276|-0.0000336760057158738|19.236997604370117 / 19.237165451049805|
|B|-0.000013970480401819577|-0.0021008790389600023|-0.0006400430479692744|18.651247024536133 / 18.65118980407715|

A standalone rim worsens as an advisory metric, transparently retained (not a separate original guard). Float64 direct residual uses mean(2*baseline_error*delta+delta²) on SAME saved native float32 images/target/masks, not a new score epoch. Both weightedloss changes decrease.

ONE two-coordinate saved-response model recentered on accepted pass07 residuals. Saved secants were from nearby revision6 strength +/- .002 and ordinarypostblur +/- .05; their columns rescaled by1/2 to radius.001strength/.025reference-nativepxpost. They are explicitly SURROGATES, not exact accepted-state derivatives. No repeated probes, fresh solver phases or optical basis changes. One deterministic constrained quadratic proposal; solver success=true, model minconstraint -2.4866069905383663e-16 never used as native acceptance.

Actual halfstep increments strength -0.0004144186271376695 and post_sigma 0.00018576516488255602 reference-nativepx. Final strength 0.38356702407186094, final outputpost_sigma 2.1642183469081204. Directional angle/length/fade fixed. The tiny ordinary Gaussian change is separate from fixed-direction RGB contribution strength. All sourceGaussian, material/gamma/ambient/grazingreflection, shape/spline/core/tangent, generatedshadow/source/inputs/masks/epoch unchanged.

Fullstep strict FAIL A E +.0000016416895665, advisoryweightedloss +.0000201699353809; saved, no waiver. Halfstep actualnative+advisory strictpass; STOP first qualifier after2nativepairs (out of4budget). Exact-completed-recipe registry checked prior width/post/strength/joint records; neither proposed pair matched, so neither repeats completed probes. No remaining backtracks or fallback spent. Authorized fresh smaller strength secant +/- .0005 was NOT activated because savedmodel found a qualifier.

Source proof freshly checked for candidate activeweights: whole/ALLscored original2x2 base/RGB rays including A50/B27 scored subrays outside corrected outline; reflection actualnativeoutput whole/scored and materialcontext nativefootprint. All definedminimum1/zero undefined. Basewhole A974432/B847118 and ALLscored961824/835876; active red/blue eachwhole363258/316395 andscored359088/312602. Original modeledhiddeninputallowance retained with observed0, not recovered RGB. Transmission source3sigma radii13/12, reflection5. Discrete native/finite3sigma source check only; no continuous/infinitekernel or ordinaryoutput-scattering confidence claim. No new source/shape/mask/epoch.

Packet /evidence/extended/helper-toolbar-work/active-slider-round/pass07-recentered-saved/: candidate-native.json (actualparameters/material/scores), candidate-public-native.json (nativeunitpublic-compatibleparameters; legacy explanatory method/provenance text inherited and should be replaced for publication), result.json/trials.json,proposal.json/forms.json,selected trial1-ref0-material.npy/trial1-ref1-material.npy (NOT fullstep trial0), ref0/1-complete.npy/alpha.npy, fresh-source-proof.json and emptyundefined-ray arrays. Native825x590 and785x570 target/baseline/candidate preview PNGs, originalwidths exceed720cap therefore no enlargement/no4x. Both candidates inspected, no obvious new artifact; inherited darkrim/softness/chromatic mismatch still unresolved. Primary independentvisual judgment required.

Completed command, driver refuses repeats:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/active-slider-round/pass07-recentered-saved.py

Sharedflag READY_FOR_PRIMARY/count1, nativequeued999b2b9e-036a-4ace-8552-74c27a9e2e1e; queueaccepted does not prove consumed/accepted. No nextpass/family or publicedit. Request next bounded work after independentdecision; leadExpanded/publication untouched.
