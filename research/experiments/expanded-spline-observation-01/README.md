# Expanded playback: paired spline-height observation

Status: substantial body improvement, held by original foreground guards. No accepted full-model pass or baseline replacement.

## Fixed comparison

Observe the [retained positive spline height](../expanded-spline-height-01/README.md) once on both original references. Footprint, pose, source, masks, vectors and artwork stay frozen. The source is blurred before refraction at 6.75 native pixels. AA remains two-by-two; colour is the same common neutral response, with no generated shadow or output material blur.

| Original native metric | H1 A | Spline A | H1 B | Spline B |
| --- | ---: | ---: | ---: | ---: |
| E | 45.423695 | 25.288500 | 18.219819 | 11.044592 |
| Glass RMSE | 38.077415 | 23.725889 | 15.106259 | 9.662211 |
| Rim RMSE | 59.115406 | 28.604530 | 23.959862 | 13.739502 |
| SSIM | 0.871073 | 0.966668 | 0.922811 | 0.970751 |

All original body metrics improve in both references. Exterior error and coverage remain exact. No lens channels clip.

Foreground failures remain explicit: A artwork and title; B artwork, play and forward. [Complete results](result.json) preserve all guards without an epsilon. These failures prevent a strict paired acceptance even where the body change is large.

## Visible result

Both [A](a-comparison.png) and [B](b-comparison.png) were inspected. The coloured return and text/card structure are closer than the H1 prior. Bright contour, cap transitions and some bottom text returns remain wrong. Foreground material/edge errors and source uncertainty are not resolved by the geometric projection.

The [longitudinal](longitudinal-cached-paths.svg) and [transverse](transverse-cached-paths.svg) views use the actual cached back points and primary paths. Background distance is 2.1L in both the renderer and figures. Their axes are independently scaled and labelled.

The earlier lower diagnostic residual was not an image guarantee. This paired observation provides stronger evidence of body progress, while retaining the foreground regressions and unaccepted status.

## Correctness and accounting

[Source preflight](source-preflight.json) passes both original domains before RGB: 890,848 whole-body and 1,076,505 required-union subrays per reference. It covers every original glass/exterior/foreground/artwork guard, radius-21 incident support and all four bilinear texels.

The 10,500 unsupported unscored subrays per reference remain unavailable. No source completion, clamp, registration or mask change occurs. Registered support is not hidden photographic truth or unique Apple optics.

[Runtime accounting](protocol.json) reserves both height-adapter calls per native ray before launch. Actual usage is 1,360,000 new native rays and 2,720,000 height calls, below the declared 2,730,000-height cap. There are two native images and no new fit or setting.

An independent SciPy interpolation check uses 96 cached-coordinate RGB queries. Selected samples differ by at most 2.23e-16; their integrated float32 native pixels are exact. [Verification](sparse-verification.json) records a combined 2,699,096 RGB queries, below the 2,720,000 cap, with zero verification rays or height calls.

[Cached-path consistency](cached-path-consistency.json) checks the actual exit direction, source coordinates and background plane. No separate normal field or decorative lens is introduced. Reflected paths and environmental radiance remain unverified.

The selected H1 state and historical empirical images remain preserved. Further material or foreground work must use a separate declared stage; this observation does not silently relax an original guard or reset a baseline.

## Timing disclosure

Last scientific sampling finished at 21:15:55 UTC, before the 21:29:27 deadline. Final review and recording finished later; [closure](closure.json) reports the administrative overrun explicitly. No rays, height evaluations or RGB queries ran after the deadline. This is not a claim that all packaging finished within the cap.
