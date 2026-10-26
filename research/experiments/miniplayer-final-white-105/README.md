# Final-output white, revised outline and artwork

One candidate targets final body white #E6E6E6 through the existing optical brightness pipeline. The shared gain is calibrated; bias and dark-tone lift remain fixed. The outline yellow saturation/value target becomes #FCF8AD, and its maximum-strength band is 1.5 native pixels. Geometry, blur, shadow, inward fade and diagonal gaps remain unchanged.

[Interactive comparisons and native crops](../../../guide/miniplayer-final-white.md)

## White calibration

The fixed expanded-B cohort uses original glass pixels outside held, rim and foreground regions, with full coverage and every retained incident channel at least 250 out of 255. Its centers are at least 30 native pixels inside the minor extent and cap core. These rules precede evaluation; reference RGB does not select or fit the cohort.

A pure-white probe follows the actual saved primary power and direct reflected light at those 27,311 pixels. One bracketed 48-step gain solve targets mean encoded output 230 after optical lighting. Gain becomes 0.544238219590758; bias remains 0.39083683534488656 and low-luminance lift remains 0.08. No source, optical geometry or illumination parameter is fitted.

The probe spans approximately 229.999967 to 230.000003, with mean 230. Actual retained near-white input is measured separately because it is not exactly white. Grading-stage white is deliberately higher than the final target. The original position-dependent optical behavior remains active elsewhere.

## Outline

The existing hue-preserving response is recalibrated only through its requested anchor values. The revised yellow target is #FCF8AD; preserving input hue gives approximately #FCEFAD. Saturation and value match, while the green residual remains explicit. White stays #FCFCFC, and the other two colored anchors retain their prior targets.

The maximum-strength plateau changes from two to 1.5 native pixels, following the user's correction to the initial 0.6 multiplier request. The two-pixel inward fade and opposing diagonal gaps remain unchanged. Orders 16 and 32 independently integrate the revised width against the fixed actual contour. No new lens ray, incident filter or source query is required.

## Artwork followup

While optical-overlay integration ran, the user requested width and height multiplied by 0.986 and vertical centering, with no horizontal movement. The separately declared foreground followup preserves the preceding four images and their accounting. It scales current artwork rectangles, retains horizontal centers and radius 18, and rounds vertical placement to the nearest native pixel around the actual pill center.

The foreground adjustment uses the original image source, resize method, coverage model and ordered compositor. It verifies zero-change replay, exact pixels outside the artwork union, zero outline contribution throughout that union, and an independent manual artwork-layer replay. Requested fractional sizes and realized raster dimensions are reported separately.

## Evidence

The parent packet retains the color/rim candidate before artwork. The artwork subfolder retains the final candidate, controls and its separate ledger. Both stages preserve original masks, partial cohorts, code/input hashes and selected state. The final comparisons show Apple and the previous revision without alignment changes. No result automatically replaces the selected model.

The scene remains hypothetical, source correspondence is conditional, and four warm anchors do not identify a unique global color response. These limits are separate from arithmetic verification and visual review.

## Outcome

All four color/rim replays and all four artwork-layer replays are pixel-exact. Outline order differences remain below 4.762e-7. There is no clipping. The pure-white control reaches final value 230; actual retained near-white body samples average approximately 228.8 because their input is not pure white.

| Case | Previous revision E | Final E |
| --- | ---: | ---: |
| expanded A | 13.390896 | 11.907829 |
| expanded B | 9.771798 | 4.808293 |
| compact A | 17.579734 | 14.166782 |
| compact B | 18.417607 | 15.230886 |

Aggregate errors improve against revision 104 in all four cases. Artwork pixels are outside the original glass scoring cohort, so resizing changes the separate artwork metric rather than aggregate E. Original guards and local regressions remain in the result records. No full-fidelity or selected-state acceptance is claimed.

| Member | Previous artwork size | Requested size | Raster size | Vertical-center error |
| --- | --- | --- | --- | ---: |
| expanded | 109 by 112 | 107.474 by 110.432 | 107 by 110 | 0.355464 pixels |
| compact | 109 by 111 | 107.474 by 109.446 | 107 by 109 | 0.284555 pixels |

Horizontal centers are unchanged exactly. Radius remains 18 pixels. The original and revised artwork rectangles have zero outline contribution, and every pixel outside their union is exact. One initial import-order failure stopped before numerical work; its source and repair are preserved.
