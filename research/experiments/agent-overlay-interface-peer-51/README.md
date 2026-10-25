# Separate outline interface: static peer review

**Pass for the declared valid geometry and sigma 0.65, with API and evidence limits.** The operator implements an outer-anchored white display overlay with a smooth inward fade. It does not change refraction. Saved experiment 88 has no all-family guard qualifier. No numerical function, image, replay, sample or fit ran in this review.

Task 51 started at 20:36:42.849 UTC on 25 October 2026 and must finish by 20:44:42.849 UTC, including versioning. Shared module SHA256 is `e7ae1b111b077c14b9faf3ab7ff5b8305d4987594cca203f8db9d3c168595543`. Primary files were read only. First/last hashes bind the module, quadrature and available 88 scientific records.

## Profile and sign

The rounded-rectangle formula is the standard Euclidean signed distance for valid positive extents and corner radius: negative inside, zero on the silhouette. Distances, sigma and pixel centers use native pixel units. The analytic profile is:

$$
\alpha(d)=\begin{cases}\exp[-(\frac{d}{\sigma})^2],&d\le0,\\0,&d>0.\end{cases}
$$

Its unique maximum is at the outer boundary. It decreases monotonically moving inward and approaches zero without an analytic inner cutoff. Its inward derivative tends to zero at the rim. The outside silhouette discontinuity is intentional support clipping; pixel integration antialiases it. This is not a smooth two-sided halo or a second inner contour.

## Positive full-pixel integration

The shared rule clips each pixel against the actual footprint and uses positive Gauss weights normalized to the full unit pixel area. The outline integral does not divide by occupied area, select target-error masks or paint a residual correction. Exterior nodes contribute zero. The active band is determined solely by geometric distance and the declared tail tolerance.

The sixty tensor-piece reservation is conservative for the unsmoothed rounded-rectangle rule. Its partition includes pixel center, core joins and crossings of internal y partitions. The code charges actual generated nodes and rejects nonfinite or out-of-range alpha. No integrator, area control or reservation was numerically rerun here.

Positive weights establish an area-integral construction, not convergence by themselves. Saved 88 reports order 8-to-16 maximum alpha differences of approximately 1.42e-13 expanded and 6.70e-12 compact. These are attributed fixed-order comparisons, not rigorous quadrature error bounds or new peer reductions.

## Negligible-tail scope

Signed distance is 1-Lipschitz. Every point in a unit pixel lies within its center's half-diagonal. If a center is deeper than the declared band, every point has opacity below the requested bound:

$$
D=\sigma\sqrt{-\log\epsilon},\qquad
 d_c<-D-\sqrt{\frac12}\ \Longrightarrow\ \alpha(d)<\epsilon.
$$

The omitted pixel integral is therefore at most epsilon because pixel area is one. For finite unit encoded backing and color, its per-channel composite error is at most strength times epsilon. Summing absolute pixel errors adds a factor equal to omitted-pixel count. This is a truncation bound only; quadrature and floating-point error are separate.

The numerical implementation sets deep-interior alpha to zero. Its reported no-inner-cutoff flag describes the analytic profile, not bitwise infinite support. No visible hard cutoff is claimed to be resolved from epsilon alone. Finite crop coverage and the actual surface convention remain prerequisites.

## Composition order and unavailable pixels

`composite_outline` operates on the already completed encoded image, including foreground. It changes only positive-alpha pixels at nonzero strength; zero-strength identity returns a copy without accessing unavailable backing. Positive-alpha backing must be finite. Unaffected unavailable pixels are preserved, without target fill or source query.

$$
C_{\mathrm{new}}=(1-s\bar\alpha)C_{\mathrm{complete}}+s\bar\alpha C_{\mathrm{outline}}.
$$

This is the declared post-completed-image model. It is not per-ray radiometry, a Fresnel term, incident blur or source reconstruction. Pixel-averaged alpha is intentionally composed with the existing completed pixel; it is not claimed equivalent to jointly subpixel-integrating varying backing and alpha. Foreground overlap would be overpainted under this order and must remain guarded.

## Generic API caveats

The public pixel integration function uses sigma in tail-depth arithmetic before `inward_opacity` validates it. If an invalid sigma produces no active pixels, that validation can be skipped. The fixed positive finite sigma 0.65 does not exercise this issue. Future generic callers should validate finite positive sigma at entry; no shared edit or rerun is requested during this frozen review.

The low-level distance helper also assumes valid rounded-rectangle dimensions, while the rule validates geometry only when called. Crop integers, floating completed-image dtype and unit encoded backing are declared input assumptions rather than fully enforced universal contracts. Integer image arrays could quantize composition. These limitations do not establish a failure of the frozen 88 recipe.

The exterior zero cutoff and negligible deep-interior truncation have different roles. Neither authorizes changing original masks or dropping partial pixels. An overlay can affect an exterior guard pixel if the geometric footprint covers part of that pixel; this is a scored consequence, not automatic source-proof failure.

## Saved 88 guard review

No image was viewed and no visible-improvement verdict is independently established. The available scalar records show all four SSIM values improve, and aggregate error improves except expanded A. None passes every original guard. The visual claim must remain primary-reviewed evidence, separate from this interface review.

| Reference | Saved failed guards |
| --- | --- |
| Expanded A | Glass, rim, held, aggregate error and 16-pixel partial |
| Expanded B | Held |
| Compact A | 22-pixel partial and exterior |
| Compact B | Held, 22-pixel partial and exterior |

ExpandedA partial RMSE rises from 40.32683 to 82.50563. CompactA rises from 23.81317 to 36.65421; compact B from 21.07663 to 41.35635. Foreground and interior guards tie. Exterior regressions for compact remain strict failures regardless of their small magnitude. No epsilon waiver or model adoption follows.

The frozen body is working 20, not the rejected first-return 85 image. The operator acts after its foreground chain and makes no optical call. Consequently it can test a separate rim effect without retroactively accepting old inset-band geometry or assigning missing reflected radiance.

## Checks and delivery

The prompt report attempted fresh Sessionsation steer-target three times; all timed out before sending. No Queue fallback was used. This delivery limitation is retained. The final handoff is attempted only through the required Steer or immediate Submit path. No transport payload or session dump is included in evidence.

Documentation, privacy, first/last hashes and preservation of old records are checked before own-folder versioning. Only this report folder is staged. No numerical replay, images, shared/root/guide edits or successor task is authorized by the review.
