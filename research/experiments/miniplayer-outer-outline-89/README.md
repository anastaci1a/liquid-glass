# Half-pixel outward outline: a boundary tradeoff

One fixed outward placement improves aggregate error against the frozen working body on all four references. It reduces the first overlay's partial-boundary regressions, but increases compact exterior error substantially. The family remains unqualified. No refraction, source, incident blur, foreground or body material is changed.

## Fixed placement question

The [first overlay](../miniplayer-overlay-outline-88/README.md) places its maximum at the frozen optical silhouette. This second observation moves only the display outline's outer contour half a native pixel outward. Width remains 0.65 pixel, peak opacity one and color white. Both lengths use the same parameters.

The parallel rounded rectangle preserves the inner rectangle while changing its display extents:

$$
\begin{aligned}
\delta&=0.5\,\mathrm{px},\\
a_{\mathrm{outline}}&=a_{\mathrm{body}}+\delta,\\
b_{\mathrm{outline}}&=b_{\mathrm{body}}+\delta,\\
R_{\mathrm{outline}}&=R_{\mathrm{body}}+\delta,\\
d_{\mathrm{outline}}(\boldsymbol{x})&=d_{\mathrm{body}}(\boldsymbol{x})-\delta.
\end{aligned}
$$

This does not move the optical footprint or any original mask. It tests the display layer's placement. The [same operator](../../../reconstruction/post_refraction_outline.py) integrates the Gaussian inward fade and composites it over the completed working20 pixel. No optical code runs.

## Results

| Reference | Working E | First overlay E | Outward E | Original partial RMSE: working → outward |
| --- | ---: | ---: | ---: | ---: |
| Expanded A | 7.88349 | 7.96922 | 7.83329 | 40.32683 → 67.72722 |
| Expanded B | 6.14943 | 6.14915 | 6.13893 | 26.08043 → 17.58432 |
| Compact A | 20.53188 | 20.50074 | 20.52487 | 23.81317 → 24.50793 |
| Compact B | 19.68186 | 19.66365 | 19.67857 | 21.07663 → 25.72124 |

Expanded B passes its original guards. Expanded A still fails held and partial. Both compact references fail partial and exterior: exterior RMSE rises from 10.55028 to 14.05207 on A and from 15.07277 to 17.54183 on B. All foreground and interior guards pass. No local failure is waived.

All four full comparisons were inspected. The line remains thin and single, but extending it outside the body creates an exterior tradeoff. Brightness still differs from the reference around the caps. The shifted outline does not correct body tone, source-return placement or earlier geometric defects.

| Reference | Reference / frozen body / outward overlay | Original-coordinate crops at 2× |
| --- | --- | --- |
| Expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) |
| Expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) |
| Compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) |
| Compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) |

## Two-placement review

The first overlay has smaller compact aggregate/exterior errors. The outward placement reduces the three failed partial-cohort errors and improves expanded aggregate scores, while harming compact exterior. Neither setting establishes the correct outline location or an acceptable family replacement. The first stays visible as the held gallery test; this second placement remains linked evidence.

White compositing cannot repair already over-bright channels. Mixed color residuals can also worsen when every channel moves toward white. These failures do not establish a dark outline, direction-dependent opacity or a need to change refraction. No third placement, width or opacity search follows from this record.

The declared convention remains post-completed-pixel composition. Joint integration of an outline with spatially varying subpixel backing is a different model; it would require legitimate retained backing and matched numerical support. Neither alpha recovery nor foreground subtraction is inferred here.

## Controls, accounting and limits

Four exact zero-opacity identities, original input/mask checks and profile/distance controls pass. The checkpoint is 20:48:44.380 UTC. Orders eight and sixteen differ by less than 0.000000002 encoded level on either member. The same negligible-tail bound applies; the analytic profile has no finite inner cutoff.

The [protocol](protocol.json) starts at 20:48:40.870 UTC and ends at 21:08:40.870. Science finishes at 20:49:21.435 UTC. [Results](result.json) retain all original guards and saved first-overlay comparators. Publication remains inside the same subpass cap; the parent outline deadline is 21:33:02.674 UTC.

Actual work is 48,758 quadrature calls, 29,354,880 nodes, four identities, four candidate composites and four scores. Original Study constructors cover 1,121,600 mask pixels; numeric decoding totals 30,451,200 bytes. Repeated profile controls are charged as 277 observations. There are no optical rays, heights, source queries, filters or fits.

[First](first-hashes.json) and [last](last-hashes.json) scientific bindings match. Shared operator bytes are unchanged. [Source reuse](source-reuse.json) records the driver changes. First-overlay comparator metrics are read from their sealed files; their additional commit bindings are recorded during packaging, rather than claimed as part of the original startup hash list.
