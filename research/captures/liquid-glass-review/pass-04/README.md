# Pass 04 — current review set

October 19, 2026. This set incorporates the earlier feedback and preserves all previous passes. Images are native crops unless their captions specify enlargement. Apple is on the left.

## Images

| File | Contents |
| --- | --- |
| [01 — toolbar](01-toolbar-current.png) | Refined horizontal-stretch transition and stronger blur. |
| [02 — toolbar rim](02-toolbar-upper-rim.png) | Upper-rim detail from the same new fit. |
| [03 — slider comparison](03-slider-comparison.png) | **Apple / previous optical map / preferred-shape candidate**. Both reconstructions use the corrected input track and the same computed exterior. |
| [04 — playback](04-playback-current.png) | New radial-map control removes the additional outer return; white-mask icon has calculated color. |
| [05 — play icon](05-play-icon-color.png) | Enlarged color comparison. No copied interior icon RGB. |
| [06 — playback rim](06-playback-rim-crops.png) | Three matching crop groups: bottom-left, top-left and both upper-right crossings. |
| [07 — toolbar `d`](07-toolbar-d-crop.png) | The requested stroke-curvature crop with the new stretch/blur fit, enlarged 4×. |
| [08 — slider line height](08-slider-line-height.png) | Measurements of where the line starts expanding toward the left rim. |

## Changes and remaining differences

### Toolbar · 01 / 02 / 07

- Source blur sigma increases from **8 to 11 pixels**. The horizontal-stretch band grows from about **61 to 69 pixels**, with a small increase in its strength. Two independent search starts converge to nearly identical results.
- Whole-glass RGB RMSE improves from about **7.25 to 6.12/255** under the same source/mask. This does not establish perceptual equality.
- The normal displacement profile is retained. These images still use the fitted **tensor image map**, not the new closed-body tracer.
- The extremely shallow central bulge requested for the preferred geometric toolbar variant remains a separate geometry-calibration task. The tensor fit does not prove that shape has been recovered.

### Slider · 03 / 08

- **Baseline correction:** the old input stroke rasterized to 22 pixels; the exposed Apple track is 20 pixels tall, centered at y549.5. The new analytical input reproduces that measured span and center.
- The middle panel holds the previous chromatic optical map fixed and refits its material on the corrected input. It is not a byte-for-byte copy of the older pass 01 image.
- The right panel starts from the preferred **crown 0.6** shape, preserves its measured silhouette and normalized longitudinal section, and fits height/index/background distance plus independent transverse curvature. It traces both curved interfaces. No glass blur is added.
- Both panels now use the same **generated contact shadow and source-colored halo** outside the lens. That exterior is calculated from the reconstructed background and source-derived color, rather than retained reference pixels in this crop. Its color/shape still differs visibly from Apple.
- The older optical map is still the closer overall fit. At 30–60 pixels from the left tip, its measured blue span is **20px**, matching Apple; the new body is **22px**. The new geometry therefore still has unwanted central enlargement. At five pixels from the tip, Apple reaches **44px**, the previous map **41px**, and the new body **38px**.
- This comparison does **not** endorse the new body as a replacement. It exposes the remaining quiet-interior/strong-rim mismatch and separates shape preference from optical accuracy.

### Playback and icon · 04 / 05 / 06

- The earlier mapping changed radial direction twice near the rim. This trial allows one transition and removes the additional outer return that produced a second mirrored strip.
- It remains an **integrable radial image-map approximation**, not a recovered solid. It can still invert detail in the rim; removing the extra outer return is not proof of globally noninverted mapping or of Apple's underlying optics.
- The icon reuses its silhouette and slightly feathered coverage, with all interior colors recalculated from the current underlying reconstruction. Six channel-response parameters reproduce the faint warm shading without a painted positional gradient.
- Icon-interior training/withheld RGB RMSE is approximately **3.02 / 2.91 per 255**. Spatial blocks share the same frame; they are not independent-scene validation.
- Remaining mismatches include dune/rim alignment, reflection/shading, exterior contact treatment and the icon's subtle color gradient. Exterior context in playback and toolbar comparisons is still partly retained/estimated; only the slider exterior is fully generated within its crop.

## Evidence

- [Parameters and scores](diagnostics.json)
- [Blue-span measurements](slider-line-height.json): identical color thresholds on all images; the measured span can include small blue branches.
- [Slider geometry/path checks](slider-path-checks.json): 4,820 sampled height points have no positive Hessian eigenvalue, and 6,265 sampled internal segment points remain inside the body. These finite checks are not a global convexity proof.
- Research checkpoints `99d182b` and `2c955cb` are pushed on PR414. The native application, main branch and deployed lab are unchanged.

[Feedback for this pass](feedback.md)
