# Unfitted crowned slider baseline

Status: ready for independent review; no improvement accepted. The two images completed at 20:01:57.623 UTC on 23 October 2026. Scientific execution began at 19:56:01.537, with a 20:16:01.537 subpass cap. The prior intake used 320.849 seconds. Its 57-minute review delay is recorded separately and is not a four-hour turnaround claim.

## Result

| Native metric | A | B |
| --- | ---: | ---: |
| E | 68.28656033 | 36.21504660 |
| Glass RMSE | 65.85044098 | 36.18732834 |
| Rim RMSE | 73.65817261 | 36.27964020 |
| Exterior RMSE | 12.61555576 | 7.67968082 |
| SSIM | 0.86409646 | 0.93515980 |

All historical error guards regress. Only B SSIM improves. Historical pass09, its inputs, masks and accepted counts remain unchanged. [Exact scores](baseline/result.json), [A comparison](baseline/a-comparison.png) and [B comparison](baseline/b-comparison.png) are retained.

The track nearly fills the predicted lens. Apple's broad white upper/lower regions and inner track boundary are missing. B retains a small left-edge transition, but not the reference structure. Neutral material also omits rim illumination and generated shadows. Aggregate RGB error cannot isolate those effects from geometry. This is a useful negative physical prior, not identified Apple optics.

## Frozen construction

The dependency is commit 6fd37ddee6e418beb0694760d565a6ca8aeebdc6. Shared transport, surface and filtering files are unchanged. The actual accepted half tuples, softness 0.08, depth 0.15, crown 0.4, index 1.5 and background distance 2L are fixed.

One scalar height and its full gradient provide transport. The private adapter translates pose only; its optional section method returns base-local coordinates and was not used to generate world-coordinate sections.

The source receives finite incident Gaussian filtering before refraction: sigma 4.25/4.00 native pixels, radius 13/12. Clear misses remain unfiltered. Native AA is 2 by 2; output blur is zero. Gain is one, bias zero. There is no inherited lighting, generated shadow, directional smear or foreground layer.

## Source and numerical evidence

[Preflight](baseline/source-proof-FIRST.json) completed before RGB.

All 3,736,800 native rays are complete and supported. Whole-body counts are 974,432 and 847,118. Required guard subray counts are 1,571,908 and 1,366,252; every ray includes its actual finite kernel and four bilinear texels. Defined confidence is one; observed confidence is zero. This proves availability of the modeled input, not recovered photographic content or a common transition material.

The checkpoint used 7,346 rays; four shared-renderer parity patches used 256 additional rays. Total fixture/comparator usage is 7,602 of 10,000. All four patches match exactly, including partial coverage. Source coordinates, membership, support, masks, sampled RGB, lens/clear contributions, coverage and complete arrays are saved. Raw values have zero clips. Two full native images and zero fits were produced.

## Preserved failures and recovery

An initial runtime dependency mismatch failed before rays. After both native preflights passed, RGB integration exceeded OpenCV's 32,767-column remap limit for a flattened lens row. The failed implementation and logs remain saved. That attempt sampled 1,947,000 clear RGB coordinates but completed zero images.

Integration resumed from immutable coordinate arrays using 16,000-sample chunks. It repeated those clear RGB queries but traced zero additional native rays. The full native budget was not reset. The resulting four parity patches validate the narrow integrator against the shared renderer. No source, masks, optical settings or numerical tolerances were changed.

## Reproduction and limits

The source manifest identifies existing compressed evidence objects. Restore them into baseline/inputs/a and b using their hashes; case JSON comes from frozen-records/paired--a.json and paired--b.json. Run `node restore-inputs.cjs /path/to/canonical/repository` from this packet. It verifies existing files and refuses replacements.

Local input copies are excluded from Git because those exact bytes already exist in the evidence store. Python dependencies remain outside Git.

The executed scripts were checkpoint.py, baseline.py, then baseline.py --resume-cached after the preserved failure. They enforce the original deadlines and restart sentinels intentionally. Do not delete sentinels or rerun this completed experiment. Independent replay requires a separately authorized output directory and clock, while reusing these frozen inputs and code hashes.

## Next proposal only

First inspect the saved map's correspondence with the modeled track boundary and Apple's upper/lower transitions. A possible next geometric question is whether a shorter background distance preserves the inner track boundary instead of filling the lens. This is not an executed trial or a request to restore historical empirical displacement.

Source and transition-state ambiguity may prevent identification even if edge positions improve. No parameter calibration, new ray grid or new image is authorized before primary review.
