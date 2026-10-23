# Saved track correspondence diagnostic

The current map compresses the modeled track into the lens rather than recovering the reference's broad white returns. This is a concrete correspondence failure under the frozen modeled input. It does not establish that Apple's bright regions are transmitted background rather than illumination, reflection or transition behavior.

The declared clock is 20:10:21–20:20:21 UTC on 23 October 2026, within the existing 21:10:40.688 refraction deadline. The [protocol](protocol.json) was written before analysis. [Measurements](measurements.json) and per-pixel [A](a-sections.csv)/[B](b-sections.csv) tables use saved arrays only. No rays, RGB resampling, new images, fitting or parameter trials were performed.

## Fixed sections and region definition

Horizontal sections use corrected-center y plus −0.6, 0 and +0.6 original L. Vertical sections use corrected-center x plus −0.6, 0 and +0.6 corrected horizontal half-extent. Each is rounded once to the nearest original integer pixel. Every existing 2-by-2 subray remains represented. Original glass masks are used unchanged for target statistics.

Source labels distinguish the existing modeled track from background using two fixed source anchors: original case center and pixel (0,0). Nearest-anchor classification is a description of the frozen synthetic field, not a source fit.

Binary finite-footprint tests include radius 13/12 and all four bilinear corners. A footprint touching both classes is mixed; it is never treated as a clean boundary correspondence.

## Measurements

| Section | Track-only subrays A | Track-only subrays B |
| --- | ---: | ---: |
| Top horizontal | 91.30% | 83.83% |
| Central horizontal | 96.08% | 91.00% |
| Bottom horizontal | 97.00% | 87.36% |
| Central vertical | 100% | 100% |

The remaining top/bottom footprints are mixed; none is entirely background. B's central horizontal section has 2.70% background-only footprints near the left edge. This agrees with its small visible white edge but does not reproduce the broad reference return.

| Central vertical quantity, native pixels | A | B |
| --- | ---: | ---: |
| Fixed x | 1040 | 864 |
| Sampled source y range | 404.44–670.62 | 414.00–659.90 |
| Modeled track global y extent | 391–692 | 396–687 |
| Largest upward displacement magnitude | 104.14 | 95.58 |
| Largest downward displacement | 104.29 | 96.58 |
| Target / cached mean luma, encoded levels | 207.27 / 172.57 | 217.65 / 193.50 |

The entire central vertical lens section samples track-only finite footprints. At the top horizontal sections, mapped y moves inward by 18.14–61.61 pixels for A and 16.78–56.87 for B. At the bottom, it moves inward by 18.12–61.46 and 16.81–57.12 pixels. These are measurements of the retained map, not fitted displacements.

## Bright landmarks are not source correspondences

The central target columns reach upper-half maxima at y=404 for A and y=410 for B, both at luma 237. The lower maxima are y=749 and 735, near luma 255. Current central-column material is almost constant at 172.57/193.50. The mismatch is not merely the position of an already-present simulated white return: the retained samples do not contain one.

The stored gradient lists include outer-rim transitions as well as possible inner returns. A's upper 421–422 transition is −7.13 levels; B's 435–436 transition is −5.00. These are image landmarks only. The strongest lower gradients are dominated by the rim, so this procedure does not assign a unique lower incident boundary.

CSV data retain the entire fixed sections without selecting a fit mask.

Missing rim illumination, colored source, ordinary filtering, unknown incident content and the two frames' transition states confound brightness interpretation. Defined support one and observed confidence zero remain distinct. No conclusion about material equality, spectral behavior or physical alpha follows from these luma measurements.

## Shorter-distance test and retention limit

A single shorter physical background distance is a discriminating next hypothesis: it tests whether the current strong inward track compression is controlled mainly by propagation distance. A useful result would move the same frozen source boundaries toward the reference's inner returns on both frames while preserving complete paths and original guards. Better aggregate brightness alone would not establish that result.

However, the native coordinate cache contains source X/Y, membership, support and masks, but neither exit height nor exit direction. The checkpoint cache also omits those path components. The shared tracer returns them, yet this baseline did not retain them. The saved map at one distance cannot determine a unique map at another distance without additional physical path information.

Therefore no quantitative distance extrapolation, alternative D, new geometry evaluation or image is computed here. The next test remains conditional on primary review and a new bounded authority that accounts for any necessary rays. A shorter distance could still fail, and modeled-source or transition-state errors could dominate. Historical accepted inputs, masks, images and counts remain unchanged.
