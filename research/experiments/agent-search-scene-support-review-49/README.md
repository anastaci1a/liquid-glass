# Search continuation support gaps: missing frame versus unknown content

**The largest unsupported downward share is off-frame data, not an environment miss.** For the same 549 TIR launches, unknown in-frame corners remain a separate substantial gap. The fixed background plane has no inferred physical edge. No radiance, source completion, rendering or selected-state change follows.

Task 49 started at 20:07:16.015 UTC on 24 October 2026 and ends by 20:19:16.015 UTC, including versioning. Its checkpoint passed at 20:09:24.208 UTC. All consumed snapshot bytes match immutable commit `5538fdd082d2c0ff1eebbbdd7241085f31eee5ae`. No dependency merge was needed. Task 46 and every older record remain untouched.

## Fixed cohort and retained data

The original 549 launch IDs match the partition archive exactly. The inventory includes the initial front-reflected branch and every available later transmission through event 16. The cached second event is TIR, with no available air exit. Blocked placeholders are retained in accounting; no available zero-weight branch is dropped.

There are 2489 available air exits: 1288 downward, 1201 upward and zero lateral. These include 549 initial branches and 1940 later transmissions. The review decoded 8235 retained row records, including unavailable placeholders. No whole-circle fraction or result from 31 is mixed into this denominator.

Exact selected NPY headers, dtypes and payload counts were checked before decoding. Original known-mask metadata establishes a 1920 by 1080 frame. Saved native coordinates are original integer-centered source-index pixels. The original length unit is 89 native pixels and the corrected center is retained. Only ordinary unit conversion cross-checks saved normalized and native endpoint positions; no plane hit is recomputed.

## Deterministic categories

Center membership is explicitly defined in the original data-index domain, with width and height from sealed metadata:

$$
0\le x<W,\quad0\le y<H,\qquad (W,H)=(1920,1080).
$$

The required four-corner footprint uses the unchanged integer floor convention:

$$
i=\lfloor x\rfloor,\quad j=\lfloor y\rfloor,\qquad
0\le i,\quad0\le j,\quad i+1<W,\quad j+1<H.
$$

This is a declared indexing convention, not a statement that the physical background ends at an image boundary. It does not reinterpret half-pixel cell edges as a different sampled scene. Endpoints outside this index domain remain downward background roles with unavailable data.

Every downward record belongs to exactly one category: saved raw support; center outside the data domain; center inside but required bilinear corners crossing the frame; or all corners within the frame but saved raw-known support false. Saved incident-compatible flags are separate and are checked to imply raw support.

## Power inventory

Values below are sums of separate s/p powers divided by the unchanged 549-launch count. They are interface-power inventory values, not measured radiance or whole-image energy fractions. Endpoint counts can exceed launch counts because a launch may emit at several encounters.

| Raw endpoint category | A records | A mean power | B records | B mean power |
| --- | --- | --- | --- | --- |
| Supported raw | 658 | 0.293479016953 | 691 | 0.309887550353 |
| Center outside data domain | 462 | 0.172260894486 | 462 | 0.172260894486 |
| Border-crossing bilinear footprint | 1 | 0.000004606314 | 1 | 0.000004606314 |
| Unknown raw corners wholly in-frame | 167 | 0.062446634155 | 134 | 0.046038100755 |

Off-frame and border contributions are identical because the geometry and frame bounds are shared. A/B differ through their already-saved known-content flags. No mask is decoded, indexed or reconstructed to obtain this distinction.

| Separate role | A mean power | B mean power |
| --- | --- | --- |
| Incident-compatible supported downward | 0.274972699864 | 0.299947311707 |
| Additional compatibility failures among raw-supported exits | 0.018506317089 | 0.009940238647 |
| Total incident-compatible unsupported downward | 0.253218452043 | 0.228243840201 |
| Unknown upward/lateral environment | 0.454493355681 | 0.454493355681 |
| Geometrically unresolved events | 0 | 0 |
| Event-16 internal tail | 0.017315492411 | 0.017315492411 |

Incident compatibility is the saved finite 43-by-43-kernel diagnostic, not adoption of a reflection PSF. It supplies neither observed scene radiance nor permission to apply transmission tone or frosting to reflected light.

## Closure and retention

The raw supported and three unsupported subdivisions reproduce the original per-launch s/p downward partitions. The incident-compatible categories reproduce their original partitions independently. Environment, unresolved and tail arrays also match. Maximum category/closure discrepancy is 1.1102230246251565e-16, below the declared 3.411e-13 guard.

$$
P_{\mathrm{supported}}+P_{\mathrm{offframe}}+P_{\mathrm{border}}
+P_{\mathrm{unknown\ content}}+P_{\mathrm{environment}}
+P_{\mathrm{unresolved}}+P_{\mathrm{tail}}=1.
$$

Each launch starts with one half in each polarization. Component checks preserve that partition without renormalization. `summary.json` retains separate s and p sums, and `classification-details.json` retains event/category launch IDs. Original event archives remain the immutable source of every individual endpoint and polarization record.

The tail is not small for every launch: the saved maximum is 0.833627470128, although the cohort mean is 0.017315492411. No later branch was continued here. Unknown environmental power remains separate even if future path transport reduces that tail.

## What is missing

Off-frame endpoints need additional source evidence covering those background-plane coordinates. In-frame failures need legitimate evidence for missing raw corners. The one border footprint needs its complete four-corner support. These are data gaps, not black pixels, white pixels, environment misses or evidence for a finite physical backdrop.

Upward/lateral roles need independently observed or explicitly hypothetical environmental radiance. The internal tail needs bounded continued transport before a complete-scene claim. Conditional mosaic support is not photographic truth, and existing path geometry does not identify Apple's illumination.

One possible next rendering question is whether the fixed background-connected reflected component can explain the rim once its actual endpoint radiance is independently supplied. Prerequisites are complete raw source support and an explicit treatment of environment and retained power. This is a proposal only: no source construction, rendering or new scene is activated.

## Accounting and controls

| Review work | Actual |
| --- | --- |
| Decoded numerical payload | 703269 bytes |
| Retained endpoint rows charged | 8235 |
| Conservative scalar classification/reduction entries | 2529792 |
| NPY headers read | 14336 bytes |
| Machine-record text consumed by classification process | 12971 bytes |
| New optical, mask-query, source/RGB or image operations | 0 |

The text cap is 16 MiB; metadata and packaging records are additionally bounded in validation. Numerical payload is below 128 MiB. No shared numerical module is imported. No masks, source/target RGB, fields or image buffers are decoded. The reported scalar units are a conservative work reservation, not device performance.

The first harness invocation failed parsing because a dictionary keyword used a colon instead of equals. Python therefore executed no module body in that invocation. Its original source is preserved in `startup-unparsed.py.txt`; one syntax-only correction precedes the sole classification execution. No scientific failure, clock reset or hidden numerical repeat is claimed.

First/last hashes and privacy/documentation checks are recorded. Only this folder is staged. Readiness and the next-question request were delivered through Sessionsation before packaging. Old results, counters, sources, masks, selected Search and historical failures remain unchanged.
