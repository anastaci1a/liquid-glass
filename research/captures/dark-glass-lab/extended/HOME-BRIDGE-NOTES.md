# Private Home correction candidate

- `music-home-vector/ambient-optics-slack/report.json` best is native feasible: A loss40.344559562/glass5.870895 vs protected40.344658450/5.888642; B103.328859341/9.226412 vs old114.298282992/9.730605. All direct/defined/3sigma source support1. No public acceptance yet.
- Shared radial geometry and23 material coefficients plus THREE source-brightness response values. Unrefracted source RGB mean over native-center footprint; encodedY=dot(mean,[.2126,.7152,.0722]); effective neutral thin/e/f material coefficients6/9/12 +=(Y−.5)*response. Common lighting bases, no independent per-background materials. Best response[-4,-.3761051322,.2206780773], sourceY A.4025882441/B.4480587199. Empirical sparse-context law, not Apple optics. Only this Y range calibrated; no outside generality claim.
- Exact candidate record preservesoptics/material/provenance. EPS1e-4 joint trial checkpointstopped (plateau); normalizedkernels/EPS.001 trial checkpointstopped after extractingbest. Both checkpoint-stop.json preserve reason; not converged/completedpass counts.
- Fixedgeometry quadraticmaterial solve nearly metA (over3.5e-6), then small common negativeAgradient step yields strictlyfeasiblecandidate. Full native independentlyverified inprivate script; publicimplementation/native/HQ/moving/parity/Jacobian checks stillrequired. No gate/mask changes.

## Implementation after current switch movies finish

DO NOT edit sharedrenderer until50880 A/B captures done. FinishPR425/merge/Pages first, then separate Home branch.

- Refactor existing `material_context.py` mean into a shared target-independent helper. Add affine context `(T,b)`; existingchroma contractionT unchanged, ambientoffsetb only6/9/12. Wrappermatrix() for compatibility; effective=T@co+b. Mean computed once when either optional contextenabled; absent/zeroambient exactidentity.
- Study.render applies effective for either context. Cached savesT/b, renderco=T@co+b. `material_local.statistics` usesT@co+b forclipping but Jacobian remainsT (offsetindependentco).
- Prepared currently cachesbaseillumination J@co. Forambient only, retain three neutral basisplanes J[...,0/3/6] (small Home exports) and add those dot(co_effective[6/9/12]−originalco[6/9/12]) dynamically per backdrop shift; matrixneverchangesneutralcoefficients, so this is exact. Recomputeeffective atsource shift as existingadaptivecontextdoes. Default cachememory unchanged exceptNone bookkeeping.
- Verify strictbaseline with publiccode; zero/defaultidentity; Cached+Prepared native/scale2/HQ+sourceXYtranslation; materialJacobian with contextoffset; sourceguards. Math source-derivedencodedluma andnormalizedradialbasis, not objectshape change/physicalinverseclaim.
- Preserve original publicinvalidpairedreceipts in an explicitlynamed archivalsubfolder (cases,passes,accepted,verification), not deletion/silentreset. Publicstillcorrectlyflagsoldboundary. Start a NEW corrected paired chain from new shared feasible baseline A<=retainedsingle, B<=oldpublishedB; redo20 meaningfulpaired refinements. Record bridgeevidence/provenance. Original singleA/cases/masks stayfrozen. Do not count invalidoldbaseline chain as validacceptance.
