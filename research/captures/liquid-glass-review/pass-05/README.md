# Pass 05 — playback lens and play icon

Playback-only review following [pass 04 feedback](../pass-04/feedback.md). Earlier image sets are unchanged. Slider and toolbar work remains separate.

## Start here

- [06 — complete button comparison](06-playback-combined.png): Apple, pass 04, the combined 1.5×-tail candidate, and a 2×-tail control.
- [09 — moving lens](09-playback-motion.mp4): six seconds over the fixed dune source image.
- [10 — motion comparison](10-playback-motion-comparison.mp4): pass 04 left, updated candidate right, on the same path.

The videos are offline renders, 30fps, H.264. They demonstrate changing background sampling; their playback rate does **not** measure rendering speed on Android. Future element reviews will also include a short motion clip, as requested.

## Independent comparisons

| File | What changes |
| --- | --- |
| [01 — lens transition grid](01-lens-transition-grid.png) | Columns: 1×, 1.5×, 2×, 2.5×, 3×, 3.5×, 4× inner-tail width. Rows: 0.75×, 1×, 1.25× inner-shoulder displacement. Apple repeats at the left. Same outer refraction, material, source blur and old icon response. Full lenses are reduced to half scale to fit the grid. |
| [02 — rim-detail grid](02-lens-rim-detail-grid.png) | Same grid, fixed bottom-left detail at 2× nearest-neighbor enlargement. |
| [03 — dune blur options](03-dune-blur-options.png) | Pass-04 geometry held fixed; added post-refraction Gaussian sigma from 0 to 3.5px in 0.25px steps, then 4, 4.5 and 5px. Apple repeats at the left. Dune detail is enlarged 4× without display smoothing. |
| [04 — icon color options](04-icon-color-options.png) | Apple, pass-04 response, white-plateau response, plateau plus chroma, ordered response, and shared monotone curve. Same glass and silhouette throughout. |
| [05 — icon diagonal detail](05-icon-diagonal-detail.png) | Same icon alternatives, upper-right diagonal/highlight detail at 4×. |
| [07 — combined rim crops](07-playback-combined-rim.png) | Bottom-left, top-left and both upper-right dune crossings: Apple, pass 04, combined candidate and 2×-tail control. |
| [11 — motion frames](11-motion-contact-sheet.png) | Four matching frames from the two motion variants, before left / after right. |

Full native renders are in [renders](renders/).

## Findings and limits

- **Lens transition:** the earlier exponent was only about 2.10. Its second derivative tends to zero very slowly immediately before the inner join, despite mathematical C2 continuity. The new inner endpoint uses exponent 4, with a C2 entry and C3 exit. The strongest outermost refraction remains unchanged. The two grid axes are **inverse-map controls**, not recovered surface-curvature values. Details: [model notes](model-notes.md).
- The 1.5× tail with shoulder gain 1 has the lowest training selection loss in this 21-option grid. Whole-glass RGB RMSE changes only slightly, approximately **8.64 → 8.64/255**. That is not evidence of a substantial perceptual improvement; the crop review matters. Wider nominal tail support does not create proportionally wider visible deformation when entry derivatives are held fixed.
- **Blur:** the tiny-dune diagnostic favors an additional **2px sigma after refraction** among the tested values. The source already has 0.5px sigma before refraction. These stages are not generally equivalent. Compression, source registration and material differences confound the estimate; it does not identify Apple's actual blur stage or radius. The original source and sample frame remain unchanged.
- **Icon:** the new responses reach a white plateau instead of merely approaching white. Independent channel fits improve the original-pose error but can turn pink over other dunes; the motion preview exposed this failure. They remain visible as experimental alternatives, not a generally safe shader.
- The combined candidate and videos use the **shared monotone color curve**, which preserves neutral grays and the order of RGB components for any input. This prevents a warm background becoming a pink icon. It trades some single-pose fitting accuracy for that guarantee. The near-white region remains wider than Apple's; exact color/area matching is unfinished.
- Extra 1–8px averaging of the background used for icon color did **not** improve the fitting objective, so the combined candidate uses none. The icon coverage/feathering is unchanged and remains sharp; its interior colors are calculated, not copied from Apple.
- Still-image exterior context retains pass-04 estimated/retained reference treatment. Motion uses the uncovered source background directly and omits the exterior shadow; it does not leave the original lens painted beneath the moving one. Lighting/color fits remain calibrated on one pose, and translation is an extrapolation. No morph/deformation is included in these clips.

## Evidence

- [Parameters and image scores](diagnostics.json), including every grid cell, blur option and color model.
- [Numerical checks](verification.json): exact original-profile recovery, outer-map preservation, splice derivatives, scale/rotation behavior, symmetric map Jacobian, supported-profile fold counts, neutral/ordered icon colors and white endpoint.
- [Video metadata and limitations](motion-diagnostics.json): both clips fully decoded without reported errors; 180 frames each.
- [File hashes](files.sha256).
- Reproduction scripts are retained in [scripts](scripts/); their inputs remain in the sibling private research directory. Nothing in this folder is Git-tracked.
- General model equations are pushed as `610a589` on research PR414. Native app, main and the deployed lab are unchanged.

[Feedback for this pass](feedback.md) · [All passes](../README.md)
