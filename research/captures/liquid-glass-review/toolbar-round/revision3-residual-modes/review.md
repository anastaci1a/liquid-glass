# Queue36: remaining modes and d-stroke geometry/source ambiguity

Accepted revision3/count3 and original source/target/masks/epoch fixed. ZERO new image renders/fits, source registrations, font fits or optical operators. Reused33/35 original-native normal derivatives, accepted material/complete images and fixed confidence cohorts/crops. Original23font-opacity is an UNADOPTED independent source-model comparator; no source promotion. Geometry analysis evaluates analytic map Jacobians/Hessians, not image sampling or optical gain.

|fixed region|native conditional residual RMSE diagnostic|chromatic residual energy|normal7local span energy|
|---|---:|---:|---:|
|full glass|5.79616|.3787%|.3567%|
|rim|8.67757|.2563%|.3386%|
|observed kernel proxy|4.25594|1.0843%|1.0073%|
|estimated kernel proxy|3.78405|.0578%|41.0434%|
|mixed/uncertain|8.05233|.2534%|1.1131%|
|upper|9.13472|.2905%|3.7970%|
|d|2.89472|2.5717%|19.5576%|
|underside|5.48319|.1398%|41.2688%|

Neutral/chroma use orthonormal encodedRGB components, not physical luminance or a dispersion model. Most remaining error is neutral. Neither low chroma energy nor a hue residual proves/excludes dispersion: sourceRGB/video processing/material remain alternatives. Normal span projections are unbounded local diagnostic spans, never corrected images or a lower bound on nonlinear image fit. Overall original weighted glass/rim objective projection is only.24346%of residual ENERGY (.112251local squared-error reduction); estimate-cohort projection rises to2.5064%under that subset weighting, highlighting source/content dependence. Confidence subsets remain advisory; all original pixels still score.

Normal/tangential placement, ordinary blur and scalar material are separated as DIAGNOSTIC proxies: output normal/tangent image-gradient vectors, output Laplacian curvature and a neutral offset. They include already-rendered material/source/PSF effects and are NOT exact operator derivatives or new fits. Whole-glass desired-correction cosines are−.08293,−.02282,−.03009,−.19447; in d−.10470,+.14501,+.15099,−.56197; underside−.14723,−.00048,+.31779,−.44321. Estimated-source width-curvature proxy+.67357 versus observed−.00080 demonstrates that an apparent width signal can be primarily source/photometry uncertainty. Do NOT infer a supported ordinary-blur refit from these output-Laplacian proxies; completed blur6/26 families remain rejected and their earlier material-baseline secants do not automatically become current derivatives. Constant-offset projection describes scalar residual bias only, not an identified material correction.

Protected roles remain separate: complete exterior/archive/plus RMSE11.46696/13.14208/3.30411. Their current normal7local spans explain only.31381%,.01143%,1.30411%of residual energy respectively. Shadow, independently reconstructed archive-vector geometry, source paper/RGB and icon color/pose remain confounded; no foreground/shadow/source correction is implemented. Glyph/source uncertainty cannot be relabeled as optical gain.

## d horizontal magnification and curvature

Fixed d crop[960,450,1120,550], accepted map has Jxx=.9987738154–.9988422979, while Jyy=.62809575–1.06710952. Vertical source-stem width factor1/Jxx=1.001159044–1.001227690: peak-to-peak only.0000686461 (about.00686% width variation). In registered right-stem output band[1100,445,1116,526] intersected with the fixed crop, peak-to-peak is.0000434827. Thus the current map has substantial vertical variation but essentially uniform horizontal strain there; it does NOT already predict a sizable smooth horizontal d-width curvature.

Two distinct metrics are reported:1/Jxx crosses an intrinsically vertical source edge on a horizontal output scan; Jyy/det is inverse-map horizontal response at fixed sourceY. Their values nearly agree here because cross terms are tiny, not because those definitions are generally interchangeable. Intrinsic source glyph contours need not be vertical everywhere.

For a source vertical edge F_x(x(y),y)=constant, q=dx/dy=−Jxy/Jxx; x_second=−(Fxx*q²+2Fxy*q+Fyy)/Jxx; width_factor_derivative=−(Fxx*q+Fxy)/Jxx². Stem-band geometric edge curvature spans−1.55e−7 to+9.51e−7 per nativepx; width-factor derivative−2.993e−6 to+.778e−6 per nativepx. These are geometry predictions on a fixed band, not a newly fitted target edge. Saved grids/Jacobians/Hessians retained.

Numerical caveat: analytic-J spatial Hessian comparisons h=.25,.125,.0625px have nonmonotone global max changes. Largest final difference3.3626e−5 occurs at[1119,542], depth.9974467, small-gradient deep core but NOT flagged undefined. This can be underresolved structure or numerical sensitivity; no globally converged/rigorous Hessian bound is claimed. Actual stem band (y<=525) max Hessian difference is8.03e−11, separately stable.3undefined-normal core grid points remain explicitly labeled, never excluded from scoring. No source-sampler/epoch change.

The tangent band is inactive throughout d (depth>=.4588175>.4036165). Old13potential-core support width.30 is saturated throughout d, so that previously rejected family supplies UNIFORM horizontal strain there, not the missing depth-varying stretch. This distinguishes its coverage, but does NOT justify simply widening support or repeating that family. Actual source d round bowl/stem junction and baseline vertical mapping can themselves alter apparent row width.

## Font/PSF versus apparent width

Existing independently identified SF Pro Text Regular font23 remains conditional on one global intrinsic PSF and the inherited720→A registration. No glass target was used for its selection. Cached accepted-source ink (algebraically recovered from the same fixed paper/source recipe) versus cached unadopted font-opacity gives clean upper stem y445–463 at threshold.5 median widths10.679565 and10.584927nativepx: difference.094638px. Multiplying a≈10.68pxstem by CURRENT stem-band geometric width variation predicts only≈.000464px width variation, about200times smaller. This discrepancy is NOT a formal uncertainty interval or proof either source model is true; it shows why an exact magnification inference is unsupported from the current source assumptions alone.

Threshold.2–.8 and lower source bands are retained. In the bowl/junction y470–510, width medians vary roughly9.76–12.18px in old source and8.74–13.44px in font23, with some font rows explicitly censored by the fixedxband. Those variations include intrinsic contour/PSF and cannot be called optical stretch. Ordinary source sigma11px, intrinsic donor/font PSF≈1px and output sigma1.25px affect grayscale edge widths differently. Contrast/threshold, compressed vertical mapping, color-transfer/source paper and native sampling add ambiguity. No per-crop/channel coefficients or new RGB/spectral law inferred.

No reusable NEW operator is supported distinctly from the rejected families. A deeper support strain could mathematically create width variation, but selecting it from this same ambiguous d residual would repeat a rejected empirical direction without independent identification. Need an unoccluded SAME target-page d/known line at matched native scale, pixel phase, exposure/transfer/paperRGB and known sourcePSF, plus independent stable silhouette/pose uncertainty. Existing720donor and23globalfont/PSF proposal are useful controls but do not establish that exact same-epoch input or recover unknown ink. For physical crown separation, independent contour/alpha/PSF evidence remains needed as31/32documented. No claim local lack of gain proves global unattainability.

Request20 sent BEFORE final packaging, native accepted5e5b5d14. Recommend quantitative conservative source/font/PSF/registration uncertainty propagation from retained23heldout evidence before another optical term; no new source fits, registrations, adoption or native renders. Await primary review/next authoritative queue; preserve explicit future Ana pauses.

Reproduction: docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-code/toolbar_residual_modes_assessment.py . Completed raw arrays/JSON retained under /evidence/extended/helper-toolbar-work/agent-toolbar-revision3-residual-modes. Extra numerical-review and implicit-edge summaries derive only analytic map/saved Hessians, not images. No new pass/count/epoch/public code/commit/push.
