# Common neutral grading: first local qualifier, pending primary

Actual cap08:05:56–08:25:56UTC. One two-parameter encoded-RGB affine family C=g*S+b, ALL channels tied and same g/b across both observations. ONE constrained least-squares proposal uses original glass TRAIN only, original rim/glass weighting and equal observations; no held/foreground fit. No iterative optimizer, RGB/crop/image coefficients, source/pose/map/mask change or new ray/source query. Body response acts BEFORE fixed sigma6.75 coverage-normalized output filter; actualcoverage+clear and canonical foreground remain exact.

The fit's nativefloat32 cached integrated-material basis is explicitly a numerical proposal surrogate: constant affine/filter commutation holds mathematically, but actual shade-before-filter/native compositor alone scores. Constrained polygon bounds g[.25,1],b[0,.6],sum[.75,1] keep the response bounded and neutral. This is empirical encoded grading, not recovered physical radiance, transmission or environment.

| Actual pair | g | b | A E | B E | All guards |
| --- | ---: | ---: | ---: | ---: | --- |
| Prior physical+blur |1|0|70.948751|31.981697|baseline|
| Full LS |.4039616552|.4484643400|37.367982|17.580270|FAIL B artwork + artist|
| Halfstep |.7019808276|.2242321700|49.127160|19.818510|PASS both E/glass/rim/held/interior/SSIM/exterior+all10FG/artwork|

Stop at the halfstep: quarterstep was NOT evaluated. Full LS rejection remains immutable; no epsilon waiver. All actual covered pre-/postfilter and native clipping counts0. Clear exterior remains exact unchanged and source/finite-output support proof transfers. The Gaussian is ordinary neutral blur; no spectral change or independent normal/light basis.

Visually halfstep reduces excess color contrast and white-body mismatch but still lacks the bright rounded rim, and background feature positions/light distribution remain wrong. Historical full pass03 E5.388045/3.116864 is still vastly better; no accepted optical gain/public adoption/count is claimed. This is a conditional component candidate in a new physical pipeline, not a replacement of the polished historical baseline.

New comparison sheets use the ACTUAL saved historical accepted PNG panel, extracted at native1360x250 from the original2722x332 comparison (82px old caption,2px gutter). Its Apple panel matches the frozen target crop PIXEL EXACT, so no rescaling/source registration is inferred. It is8-bit presentation only, never scored; inherited historical unscored completion is not active source. This supersedes material-only historical panels for later visual comparisons, without rerendering any old optical field. Provenance is historical-presentation-provenance.json. Earlier material-only sheets remain labeled/preserved.

Evidence: analytic-proposal.json, ledger.json, result.json, a/b-step0.5-{material,complete,lens}.npy and a/b-comparison.png; fixed native crop sheets preserve rejected full LS. No source, geometry, SVG, artwork or shared code edits. Root owns independent final verification and publication.
