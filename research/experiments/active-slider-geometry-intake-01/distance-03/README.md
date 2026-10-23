# One fixed background-distance observation

D=0.5L changes the modeled boundary correspondence substantially, but does not reproduce the reference. White source regions become visible above and below the track, while the track remains too broad and the return placement is wrong. SSIM regresses on both frames. This is an informative geometric observation, not an accepted fidelity replacement.

Only background distance changed from 2L to 0.5L. The same surface, full gradient, index, camera, pose, source, masks, AA and incident blur remain fixed. Material is unit neutral; no lighting, shadow, output blur or spectral smear was added. Historical pass09 and the earlier D2 result remain separate and unchanged.

## Clock and cumulative accounting

The declared clock is 20:15:56–20:35:56 UTC on 23 October 2026. The geometry checkpoint finished at 20:16:58, before its five-minute cap. Both native images completed at 20:18:15. The existing refraction deadline remains 21:10:40.688. Packaging consumes this subpass; unused time is not a new setting allowance.

| Work | This setting | Cumulative |
| --- | ---: | ---: |
| Fixture/comparator rays | 580 | 8,182 |
| Native grid rays | 3,736,800 | 7,473,600 |
| Full native optical images | 2 | 4 |
| Fits | 0 | 0 |

The 580 rays comprise 324 geometry comparison rays, including D2, and 256 small renderer parity rays. The old baseline's failed integration and repeated 1,947,000 clear RGB queries remain disclosed in its original packet. No old native grid was rerendered and no additional distance was evaluated.

## Geometry, source and unchanged stages

The unchanged back has maximum height 0.109091L, leaving at least 0.390909L clearance. Both checkpoint grids have complete regular paths. Intersections, exit normals and directions match the D2 controls exactly; propagation consistency differs by at most 2.22e-16. Shared code remains pinned to commit 6fd37ddee6e418beb0694760d565a6ca8aeebdc6.

The [source proof](source-proof-FIRST.json) passed for both complete grids before RGB. All whole-body and original required guard subrays include their complete incident kernel and four known bilinear texels. Straight misses are included. Defined confidence is one; observed confidence is zero. This is availability of a modeled source, not photographic validation.

Incident sigma is 4.25/4.00 native pixels, finite radius 13/12, before refraction. Clear exterior is unfiltered. Four small parity patches match the shared renderer exactly. All original masks, coverage and clear premultiplied contributions are bit-exact to D2. Raw clipping counts are zero. The integrator uses the already validated bounded chunks; there was no new integration failure.

## Original native guards

| Quantity | A D2 | A D0.5 | B D2 | B D0.5 |
| --- | ---: | ---: | ---: | ---: |
| E | 68.28656 | 52.73025 | 36.21505 | 29.43050 |
| Glass RMSE | 65.85044 | 53.91900 | 36.18733 | 30.85691 |
| Rim RMSE | 73.65817 | 49.84636 | 36.27964 | 25.79730 |
| Held RMSE | 66.10971 | 55.95577 | 36.53278 | 30.37911 |
| Interior RMSE | 62.32781 | 55.51971 | 36.14923 | 32.71440 |
| Exterior RMSE | 12.61556 | 10.64618 | 7.67968 | 7.00849 |
| SSIM | 0.864096 | 0.842075 | 0.935160 | 0.922523 |

Every original historical error guard fails, and SSIM also fails the historical baseline in both cases. Relative to the unfitted D2 diagnostic, error metrics improve but SSIM worsens. There is no tolerance waiver or accepted count change. [Exact results](result.json) retain the original scored masks and numerical values.

## Fixed correspondence sections

The same six sections per case and exact target landmarks from correspondence-02 are retained. Source classification uses the same fixed anchors and finite footprints. Bright target ridges remain image landmarks; their incident source identity and reflection/transmission role are not established.

| Central vertical footprints | A D2 | A D0.5 | B D2 | B D0.5 |
| --- | ---: | ---: | ---: | ---: |
| Entirely modeled track | 100% | 65.30% | 100% | 68.85% |
| Entirely background | 0% | 20.55% | 0% | 16.32% |
| Mixed | 0% | 14.16% | 0% | 14.83% |

At D0.5 the central source y-range expands to 344.81–730.23 for A and 358.89–714.89 for B. The top horizontal track-only fraction changes from 91.30% to 77.87% and from 83.83% to 75.70%. Bottom fractions change from 97.00% to 81.49% and from 87.36% to 79.09%. Thus distance changes source-region selection, not just RGB grading.

The strongest simulated upper central decrease is at 383–384 for A and 388–389 for B. The retained target lists include upper decreases at 421–422 and 435–436. These landmarks are separated, but are not certified correspondences of the same incident feature. Lower target gradients are dominated by the rim, preventing a unique lower-boundary assignment.

White returns now appear, yet the upper boundary remains too high and the lower boundary too low in the viewed comparisons. The reference's pronounced inner turn and rim remain missing. Illumination, modeled source and transition-state uncertainty prevent identifying Apple geometry from this one change. [Section comparison](section-comparison.json) preserves the complete evidence.

## Local crops and regressions

The [A crop sheet](a-fixed-crops.png) and [B crop sheet](b-fixed-crops.png) use the exact historical normalized/native rectangles. Each column is Apple, D2 or D0.5. Widths are twice the source crop, 298–494 pixels per image, within the declared presentation rule. These are enlargements of saved arrays, not additional optical images.

A upper-left luma RMSE worsens from 30.4121 to 31.5959 despite slightly lower RGB error. Both center crops are unchanged; B right-rim is unchanged. Other listed crops improve numerically but still lack the reference rim and return shape. [RGB, luma, chroma and signed RGB measurements](crop-diagnostics.json) remain advisory; masks and gates do not change.

## Retained paths and reproduction

Each case retains entry and exit positions, their outward normals, internal and exit directions, path length, discriminant, boundary status, source coordinates, membership and support. Positions use original-L units relative to the original case center, with front z=0 and background z=−0.5. Clear misses have NaN interface positions/normals because no physical interface was crossed.

The [saved-path audit](saved-path-audit.json) checks the retained exit plus propagation against source coordinates, background plane, normalized directions and normals. Maximum coordinate discrepancy is 6.67e-16L. No tracing or RGB sampling is needed for that audit. Raw pre-response RGB, lens/clear contributions, coverage, pre-foreground and complete arrays are also retained.

The private scripts are checkpoint.py, run.py, correspondence.py and package.py. All enforce the declared clock; run.py refuses a repeated native start. Inputs are restored through the parent packet's hash-checked command. No independent replay, second distance or material calibration is authorized here. The result is ready for primary review, with all historical evidence preserved.
