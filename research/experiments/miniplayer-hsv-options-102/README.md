# Five HSV outline options

Status: complete; awaiting visual choice. One fixed comparison produces five saturation choices for review. The selected model is unchanged. Geometry is finalized under the [feedback specification](../../feedback/miniplayer-hsv-options.md); scores cannot trigger shape retuning.

## Frozen state

The [family snapshot](frozen-family.json) and [height profile](frozen-profile.json) preserve study101 pass two. Source samples, incident sigma 6.6825, actual optical paths, power, shadow, artwork and angular gaps remain fixed. No new ray, source lookup, incident filter or fit is required.

## Response

The body keeps its encoded bias and low-luminance lift. Its gain changes only enough to place grading-stage white at the requested value. Optical transmission and the existing reflected contribution are applied afterward.

$$
V_* = \frac{253}{255},\qquad
g_{\mathrm{new}}=V_*-b,\qquad
b=0.39083683534488656.
$$

For blurred preimage color, the maximum outline endpoint preserves hue, multiplies HSV saturation by the selected fraction, and sets HSV value to the same fixed endpoint.

$$
(H_{\mathrm{out}},S_{\mathrm{out}},V_{\mathrm{out}})
= (H_{\mathrm{in}},kS_{\mathrm{in}},V_*),
\qquad k\in\{0.6,0.7,0.8,0.9,1.0\}.
$$

The peak plateau becomes one native pixel. The existing two-pixel inward fade and angular modulation remain. Full-pixel coverage blends the endpoint with the completed body; partial and faded pixels need not reach value 253.

## Verification and limits

Four cached baseline identities must reproduce exactly before changed compositions. Independent scalar HSV controls verify endpoint hue, saturation and value. A separate OpenCV HSV conversion checks all active candidate pixels. Every original mask and partial cohort remains scored.

Fresh outline-area integration uses the unchanged contour at orders 16 and 32. Their difference is a convergence diagnostic, not a certified error bound. It changes no optical paths or source support.

The declared display-clipping policy retains preclip body samples and reports clipped channels. White-patch records distinguish blurred preimage, target, old output, new body and overlay weight. A grading-stage endpoint is not a guaranteed final radiometric white.

See [protocol](protocol.json), [driver](run.py) and [response](response.py). [All five options and native wipe comparisons](../../../guide/miniplayer-hsv-options.md) are ready. [Scores](results.json), [verification](verification.json), [white-band samples](white-band.json) and [cumulative accounting](cumulative-ledger.json) retain the results.

## Observed result

All twenty option images were inspected. Higher saturation produces a stronger yellow expanded edge and stronger blue/cyan compact edges. The neutral expanded B reference changes little across saturation options. No option is automatically selected; every original guard and geometry mismatch remains visible.

The compact white stripe is brighter, but still too dark after optical attenuation. Fixed preimages near 248–253 produce body output near 240–243; the corresponding targets are 252–253. The grading endpoint passes its exact-white control, but this does not solve final rendered white.

| Reference | Body channels clipped before display |
| --- | ---: |
| Expanded A | 4,530 |
| Expanded B | 37,002 |
| Compact A | 811 |
| Compact B | 905 |

Clipping occurs after the brighter grade combines with retained optical power and the existing reflected-light hypothesis. These are four shared body calculations, not five independently fitted materials. Their preclip arrays remain available; no clipping is hidden as fidelity acceptance.

## Checks and retained interruption

The first independent OpenCV float32 HSV comparison differed by about 0.00036 of an eight-bit channel level. It stopped before scoring or publishing the first option. Its driver, failure and ledger remain unchanged.

The continuation used independent scalar double-precision HSV conversion with the same original tolerance. Maximum completed-pixel discrepancy across the twenty outputs is below one float32 step. No filter definition, shape or saturation setting changed.

Both original cached controls were reconstructed for each reference during recovery. Their additional work is charged. The first unscored S60 composite was repeated and counted. Completed outline integration was reused; the original deadline remained unchanged.

The expanded and compact order differences are below 0.000001 in integrated strength. Every tested opposing gap contributes exactly zero overlay. Exact-white blurred-input cohorts were empty, so the separate fixed white-band samples are not mislabeled as pure-white observations.

[Recovery scope](resume-plan.json), [original failure](failure.json), [numerical diagnosis](diagnostic.json) and [continuation](resume.py) distinguish the records. [Storage preparation](storage.json) removed only remote-verified duplicate LFS cache copies, preserving scientific working files.

## Scope closure

There were no new lens rays, source queries, optical filters, fits or geometry settings. Five requested display options are complete, with unchanged source-support prerequisites. The finalized projected shape is bound in the [shape decision](../../decisions/miniplayer-shape-finalized.json).

The experiment awaits a visual choice. The selected shared family and reconstruction images remain unchanged. No full-fidelity, physical-color identification or new accepted-model count is claimed.
