# Fixed saved Search rim profiles

All 24 predeclared profiles are complete: two references, three saved fields and four cardinal directions. Each retains all 17 offsets, requested positions, nearest existing pixels, actual radial offsets, RGB, encoded luminance, finite status and duplicates. These are descriptive image landmarks, not physical alpha, unique reflection or incident-source correspondences.

## Clock and frozen plan

The task started at 10:05:04.529 UTC on 24 October 2026. Its hard deadline is 10:15:04.529, including publication. Headers, hashes, geometry and the fixed plan passed before decoding and within the three-minute checkpoint. Selected Search, transfer34, partial guards and every earlier negative remain unchanged.

The accepted center is (1511.2043368857017, 672.8753258356955) native pixels and radius is 88.75191176648384. The original normalization is L89. The receipt is sealed Search29 source text; no height or geometry function was executed. The raw case center/radius were not substituted for the corrected pose.

Nominal radial offsets are every integer from -8 through +8 pixels, with negative values inward. Directions are upper, lower, left and right. Each requested location is rounded independently by floor(coordinate + 0.5), treating integer positions as native pixel centers. No alignment, interpolation, smoothing, amplitude normalization or threshold search occurred.

Target bytes are expressed in unit encoded RGB by the fixed division by 255, solely to match the saved float-cache units. No profile-dependent rescaling or baseline subtraction is applied. Luminance is the encoded weighted sum, not decoded linear radiance:

$$
Y_{\rm encoded}=0.2126R+0.7152G+0.0722B.
$$

## Header and decode accounting

Before any decode, PNG IHDR dimensions, bit depth and color type were checked. Only the `complete.npy` member was selected from each NPZ. Its NPY shape, dtype, order, header length and exact uncompressed payload size were verified. Other members, source PNGs and optical path arrays were not decoded.

| Input | Count | Shape per input | Payload bytes total |
| --- | ---: | --- | ---: |
| Original target PNG | 2 | 1080 by 1920 by 3, uint8 RGB | 12,441,600 |
| Selected and transfer34 complete NPZ members | 4 | 235 by 240 by 3, float32 | 2,707,200 |
| Total | 6 | 4,372,800 spatial pixels | 15,148,800 |

The complete target PNG decodes are included, even though profiles use only crop locations. Channel entries total 13,118,400 and are disclosed separately from spatial pixel cells. The limits are five million spatial pixels and 64 MiB payload. Exactly 408 selected pixel observations were made; all are finite. There are no within-profile duplicate positions.

## Pixel phase

Nearest-pixel phases differ by direction even at nominal offset zero. All requested and actual positions remain in the machine records; no corrective alignment is applied.

| Direction | Selected native pixel at nominal zero | Actual radial offset, pixels |
| --- | --- | ---: |
| Upper | (1511, 584) | +0.12364896853436846 |
| Lower | (1511, 762) | +0.3729966399560283 |
| Left | (1422, 673) | +0.45251224300683646 |
| Right | (1600, 673) | +0.04383887258227048 |

## Observed spatial structure

The following are sampled global maximum offsets within the fixed window. A maximum at an endpoint is not a located interior peak. Exterior letters and fields can dominate the maximum, so this table does not label every maximum as rim light.

| Reference/direction | Target maximum offset | Selected maximum offset | Transfer34 maximum offset |
| --- | --- | --- | --- |
| A upper | 0 | -8, window edge | -1 |
| A lower | +7 | +6 | +6 |
| A left | -4 | +7 | +7 |
| A right | +1 | -8, window edge | -8, window edge |
| B upper | +7 and +8 | +1 through +8 | +1 through +8 |
| B lower | -2 | -1 | -1 |
| B left | -3 | -8, window edge | -1 |
| B right | +1 | -8, window edge | -1 |

A upper target luminance is 0.9700 at -1, 0.9856 at zero and 0.6797 at +1. Transfer34 is 0.7596, 0.6334 and 0.4970 at the same offsets. The reference's near-white edge-adjacent structure is not reproduced by that dimmer inset maximum. These three samples do not determine an optical width or point-spread function.

Both right-side references peak at +1: A reaches 0.9986 and B reaches 0.9513. That requested offset selects an actual radial offset of approximately +1.04384 pixels. Transfer34 lacks a corresponding bright outer maximum; A falls across the window and B has a smaller inset local maximum at -1, followed by a steep fall.

Reference left-side interior maxima are at -4 on A and -3 on B. Transfer34 has a local A maximum at -3 and a B maximum at -1. The much brighter exterior A maximum at +7 is separate backdrop structure. A uniform outward relocation of every peak is therefore not inferred from these measurements.

B lower target reaches 0.9584 at -2, versus transfer34 0.6889. At -1 the target is 0.9074 and transfer34 is 0.7104. Selected Search peaks at -1 with 0.8271. The missing strong lower reference return remains explicit; these values do not identify whether its energy is transmitted, reflected or illuminated.

A lower is strongly confounded by bright outside content: its overall maximum occurs at +7, while an inward local maximum occurs at -1. B upper rises into a bright outer field rather than isolating a narrow line. Neither global maximum may be treated as an independently identified reflection or source boundary.

## Extrema, differences and foreground limits

`profiles.json` retains every adjacent RGB and luminance difference and every interior luminance extremum. `descriptive-summary.json` adds all channel extrema, global sampled extrema and the largest positive/negative adjacent differences. Exact plateaus are recorded as both non-strict maxima and minima; their tiny fluctuations are not interpreted as separate optical rings. Endpoint extrema require unavailable outside neighbors and are not inferred.

All profile positions lie outside the declared original foreground boxes. That metadata check does not establish actual target glyph coverage beyond those boxes or remove foreground/backing uncertainty elsewhere. Bright background letters and white fields remain confounds. No source image was read to assign their identity; no masks or scoring cohorts were changed.

## Implication for the next physical question

A future front-curvature hypothesis should be judged against these fixed reference-specific locations and transitions, including the strong outer right peaks and different inset left/lower peaks. These measurements do not identify a unique surface, curvature sign, amplitude or radiance scene. No physical setting, fit, displaced normal, uniform ring shift or new renderer is proposed here.

The thin bright reference structure and model inset/broad transitions are now anchored to literal sampled positions. Native one-pixel spacing and phase remain a resolution limit; no subpixel width is claimed. Existing 38-pixel guards, source-confidence limits, historical fingerprint/order disclosures and selected Search stay intact. No image, plot, export, optical event or candidate was generated.
