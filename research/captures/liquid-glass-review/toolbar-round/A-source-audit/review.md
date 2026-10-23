# A source-only donor audit (queue14–15)

No clean-source reconstruction is supported by this bounded audit. Accepted revision2 bb1ee801, source, masks, epoch, all measurements and two verified passes remain unchanged. B714 remains inactive. No optical fits, source pixels promoted, input reevaluation or new pass. Because no input proposal is defensible, repeating the incumbent render would not test a new input.

## Native footage and independent geometry

Original Meet Liquid Glass video219, native1920×1080 at30000/1001; SHA256 3d58f9e843f0b8c22e99d76de6b5201ef5b17de5bb4bf5732862ba7dbf9be60e. Existing same-example overview plus known valid724 and unrelated726 bound the interval706–724, with a declared final1s eligibility screen. Reused exact native706/708/712/716/718/722 extractions; newly extracted724.5 (frame21713/PTS724.4904333333334) and725 (21728/724.9909333333334).725 visibly changes example and was rejected BEFORE registration. No repeat registration of720/724, rejected726/728/730 or other element. PNG/RGB hashes and exact native PTS are in frame-provenance.json and late-screen/frame-provenance.json; eligibility-overview was visually inspected.

Fit4DOF similarity only to mutual SIFT ratio.7 features outside BOTH source and target [490,330,1430,820]. Distorted target glass is excluded. RANSAC1px then train-inlier least squares; target128px spatialblocks (bx+3by)%4==0 are held out. ALL heldout correspondence residuals, including wrong repeated-text matches, remain reported. Conditional200spatialblock bootstrap is not a total error bound.

| donor s | train inliers | ALL heldout RMS px | heldout<1.5px | max conditional bootstrap q95 px | registration gate |
|---|---:|---:|---:|---:|---|
| 706 | 24 | 315.397 | 52.2% | 0.821 | fails |
| 708 | 75 | 88.790 | 82.5% | 0.193 | provisional |
| 712 | 143 | 0.745 | 95.8% | 0.105 | provisional |
| 716 | 128 | 105.124 | 86.0% | 0.223 | provisional |
| 718 | 42 | 204.384 | 76.5% | 0.305 | provisional |
| 722 | 14 | 407.251 | 46.7% | 2.751 | fails |
| 724.5 | 14 | 296.389 | 46.7% | 2.204 | fails |

The initial fixed64px patch grid was sparse. A separate predeclared32/96px grid adds NEW controls in the SAME heldout blocks, with no search, transform refit or color correction. All original controls remain.708/712/716/718 pass both registration and combined-patch gates:19/27/23/14 patches in6/7/8/5spatialblocks, median gradientNCC .9799/.9922/.9961/.9724, responsive phase p95 .728/.863/.409/.686px.706 fails its correspondence gate;722 fails correspondence and combinedpatch gate (only3blocks, p95shift2.093px);724.5 has14inliers,46.7% heldout agreement and >2.2px conditional q95, so cannot be promoted. Far exterior patches cannot certify the hidden region under a similarity model; matching/model bias is not captured by bootstrap.

## Content observation versus absolute RGB

Coverage uses unchanged incumbent native4×4 incident-source addresses and original masks AND actual footprint. Confidence requires all4bilinear source corners safe; ordinary source-filter support proxy erodes34source pixels. These SOURCE diagnostics differ from prior center-only cohort proxies and are not revised output masks.

Using identical conservative geometric exclusions, accepted720 nominal source-kernel support is31.2426079% of glass rays and1.9540001% of underside rays. Adding ONLY708/712/716/718 leaves both values EXACTLY unchanged. Even the provisional724.5 scenario reaches only45.9633221%/6.0899050%, is geometrically rejected and is NOT recovered source. Legacy narrower720 erasure yields38.4263999%/3.8769146%; different exclusion policies must not be called improvement. Historical720 registration covariance is unknown.

New observed dark cores (minRGB<.5) in the eroded historically estimated query/filter domain: ZERO across all six initial donors, including unreliable ones; also ZERO for724.5. No new hidden ink was established. Dark cores are only content proxies and can remain shadow attenuated. All coverage masks, query histograms, control points and bootstraps are retained.

Across seven registered donors, far exposed flat-paper RGB residual RMS is0.790–1.401/255; dark-ink residual RMS3.721–27.432/255. Signed/channel values and sample sizes are stored per donor. These are cross-frame exposed-control differences, mixing geometry/codec/photometry, NOT an error bound on hidden absolute RGB. The large far-context exclusion [380,200,1540,1030] provides zero incident-ray coverage here; it does not prove all less distant paper is unusable, but does not certify it shadow-free either. Original720 source normalizes fitted donor-paper ink and applies fitted target paper: absolute under-glass paper remains modeled. No glass-target color fit, raw donor paste, shadow copying or invented RGB.

## Reproduction and limits

Use existing localica-dark-lab-check, python3, OPENBLAS_NUM_THREADS=1, PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps. Scripts target /tmp/agent-toolbar-A-source-audit. In order: register.py (six previously unregistered donors), validate-and-cover.py (cached native query histograms), supplemental-patches.py (new heldout patches only), late-screen.py (two bounded eligibility frames), register-late.py and validate-late.py (724.5 only). Raw registered PNGs are explicitly RAW-NOT-CLEAN and must not enter optical input. Completed tests are immutable; do not rerun for a new success count. Two initial launch attempts used unavailable executable python, failed before scientific execution; python3 runs completed normally.

No lower bound on all possible video-source recovery is claimed. This bounded content-matched evidence fails to establish additional hidden ink or defensible absolute-RGB input. A future source replacement needs better observed hidden-page coverage plus independent registration and photometric controls. Accepted E6.870490597949865, glass5.843130588531494, rim8.813648223876953, exterior11.46944201723165 remain the baseline. Next authorized work is16joint feasibility, then17surface integrability and18model recommendation; source/count unchanged.
