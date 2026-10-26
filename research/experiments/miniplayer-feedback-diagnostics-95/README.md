# Miniplayer feedback: measured discrepancies

The latest feedback is supported in several specific regions. Exterior darkening extends tens of pixels, substantially beyond the previous four-pixel trial. Compact interiors are about twelve to fourteen encoded luminance levels too dark. Several cap joins remain one to two pixels too far outward. The upper yellow outline is excessively desaturated at particular samples.

The corrections are separate: top joins move down, bottom joins move up, and far caps should refract more. No global translation or far-edge silhouette retraction is inferred.

## Broad shadow measurements

Each fixed section compares original reference and temporally reconstructed source patches at identical native coordinates. Distances extend to 160 pixels, beyond the reconstruction crops. Every raw sample, validity flag and signed difference is retained. Smooth-source selection excludes unknown or strongly textured patches; it does not remove inconvenient negative differences.

| Top-center distance outward | Expanded A | Expanded B | Compact A | Compact B |
| --- | ---: | ---: | ---: | ---: |
| 4 px | 15.55 | 19.06 | 7.65 | 21.57 |
| 16 px | 8.92 | 12.06 | 5.80 | 15.00 |
| 32 px | 4.07 | 6.71 | 3.57 | 10.00 |
| 64 px | 0.07 | -0.07 | -0.57 | 1.00 |
| 128 px | 0.00 | -0.28 | 1.07 | 0.00 |

Values are source-minus-reference encoded luminance levels on an eight-bit scale. These sections support a broad, subtle falloff, roughly approaching the local noise floor around 64–96 pixels. They do not support interpreting the reconstruction crop boundary as the shadow boundary.

Bottom profiles encounter other interface content. For example, their deficits can rise again near 128 pixels; that is not evidence of a growing shadow. Aggregate profiles also change their eligible patch population with distance. Use individual sections and retained flags, not a pooled curve as a physical fit.

The source is a temporal mosaic, not a matched pristine photograph. Its construction excludes lens-covered strips but does not explicitly exclude broad shadows. Source lighting, registration and other interface elements remain confounds. A precise physical shadow radius cannot be uniquely recovered from these differences.

## Join smoothing and far-cap refraction

The current smooth shape moves the old join inward only about 0.66–0.68 pixel. Several compact lower joins retain one-to-two-pixel inward target-gradient offsets. Compact B also shows approximately two pixels at both upper joins. Expanded gradient offsets conflict across content, so intensity transitions are not treated as exact silhouette measurements.

Three fixed shared geometry diagnostics preserve the four axis extrema. Reducing the dilation radius increases the inner ellipse axes, producing stronger inward join rounding. The actual front and back use the same normalized radial law and its correct derivative chain rule.

| Dilation reduction | Expanded join inset | Compact join inset | Far-right source displacement, 1 px inward |
| --- | ---: | ---: | ---: |
| 0 px | 0.680 px | 0.665 px | -74.665 px |
| 1 px | 1.562 px | 1.511 px | -75.722 px |
| 2 px | 2.407 px | 2.308 px | -76.814 px |

The signed displacement is inward source transport at the far-right cap. Its magnitude increases near the outer edge, without retracting the silhouette. At sixteen pixels inward the trend differs; this is a coupled real-surface change, not an independent displacement adjustment. All 240 sparse paths complete; no native source certificate or image-fidelity claim follows.

The first changed-radius constructor rejected an unscaled Hermite endpoint before any changed-radius ray. Forty baseline rays were retained and reused. The explicit continuation rescales radial nodes and derivatives consistently, preserves physical heights and retains the original clock and cumulative ledger. No rejected source or failure was overwritten.

## Yellow edge and lens tone

At expanded A coordinate `(1400, 325)`, the reference is approximately `(248, 224, 116)` while the prior combined model is `(243, 229, 176)`. The excessive blue channel makes the yellow much less saturated. The native strip and full profiles expose this without aligning or smoothing either image.

The old edge operator also explicitly kept black fixed. That contradicts the clarified requirement that black lift to light gray. The next filter therefore needs a finite black lift and bounded color-preserving brightness response, rather than a white endpoint or a black-preserving peak normalization.

| Deep original interior | Mean model-minus-reference luminance |
| --- | ---: |
| Expanded A | -0.94 |
| Expanded B | -0.07 |
| Compact A | -11.83 |
| Compact B | -14.03 |

These are the latest combined model's original glyph-excluded interior pixels. A compact-only exposure would violate the shared-family requirement. A uniform lift would also disturb the nearly balanced expanded interiors. Investigate the shared nonlinear response and input/feature differences before changing a global coefficient.

The earlier [blur study](../miniplayer-working-blur-64/README.md) tested a much larger 25-percent reduction. Its rejection does not answer the present request for a slight reduction on the new smooth geometry. A separate smaller incident-width test is appropriate; ordinary blur still precedes refraction.

## Evidence

[Shadow patches](shadow-points.json), [section profiles](shadow-profiles.json), [join profiles](join-profiles.json), [yellow-rim RGB](yellow-rim.json), [body-tone statistics](body-tone.json) and [sparse geometry](geometry-discriminator.json) retain the literal measurements. No target fit, image warp, source completion or selected-model change occurred.

After subtracting each top section's observed far-distance offset, the half-darkening crossings lie around 21–29 pixels. Ten-percent crossings lie around 45–55 pixels. These are interpolations between fixed measured brackets, not fitted Gaussian radii. [Crossing brackets and offsets](shadow-falloff-summary.json) preserve the calculation.
