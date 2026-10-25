# A separate thin outline over the frozen body

One white overlay produces a single thin perimeter without a detached inner line. It remains a held test: expanded A and several original boundary guards worsen. Compact and expanded use identical outline parameters; only the existing control length differs. No refraction, incident blur, optical normal, source coordinate or material coefficient changes.

## Composition convention

The outline is a display effect applied after the completed working20 image, including its original foreground. It does not participate in ray tracing. The previous first-return experiment remains a negative physical-reflection study; its doubled contour is not the backing for this test.

The shared [operator](../../../reconstruction/post_refraction_outline.py) uses distance to the unchanged projected rounded rectangle. Width is 0.65 native pixel; peak opacity is one and color is white. These are fixed initialization values, not estimated physical alpha or a fitted optimum. Constant all-around opacity remains a hypothesis.

For signed distance negative inside, the single outer maximum fades smoothly inward:

$$
\begin{aligned}
a(d)&=\begin{cases}
\exp\!\left[-\left(\frac{d}{\sigma}\right)^2\right],&d\leq0,\\
0,&d>0,
\end{cases}\\
\sigma&=0.65\,\mathrm{px},\\
\overline a_P&=\frac{1}{|P|}\int_P a\!\left(d(\boldsymbol{x})\right)\,\mathrm{d}\boldsymbol{x},\\
\boldsymbol C_{\mathrm{out},P}&=(1-\overline a_P)\boldsymbol C_{\mathrm{working},P}+\overline a_P\boldsymbol{1}.
\end{aligned}
$$

This is encoded pixel composition over the retained image, not a claim about radiometric subray integration. Optical AA remains the original two-by-two protocol. The new overlay has its own positive pixel-area integral; it neither filters the body nor changes refraction sampling.

## Results

| Reference | Working E | Overlay E | Original partial RMSE: working → overlay |
| --- | ---: | ---: | ---: |
| Expanded A | 7.88349 | 7.96922 | 40.32683 → 82.50563 |
| Expanded B | 6.14943 | 6.14915 | 26.08043 → 18.70746 |
| Compact A | 20.53188 | 20.50074 | 23.81317 → 36.65421 |
| Compact B | 19.68186 | 19.66365 | 21.07663 → 41.35635 |

All four SSIM comparisons improve, and every original foreground guard passes. Expanded A fails glass, rim, held, aggregate and partial guards. Expanded B fails held. Both compact partial and exterior guards fail; compact B also fails held. No guard is waived and no family replacement or accepted count follows.

Both compact images show a more distinct, single thin boundary. Its brightness still falls short locally, and the body retains incorrect source-return extent and tone. Expanded A already has over-bright regions; a white overlay cannot darken them. All four full comparisons were inspected. A lower aggregate error does not establish correct rim placement or strength.

| Reference | Reference / frozen body / overlay | Original-coordinate crops at 2× | Exact scores |
| --- | --- | --- | --- |
| Expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) | [Metrics](expanded-a-metrics.json) |
| Expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) | [Metrics](expanded-b-metrics.json) |
| Compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) | [Metrics](compact-a-metrics.json) |
| Compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) | [Metrics](compact-b-metrics.json) |

## Numerical controls and retained support

Four zero-opacity identities are pixel-exact, including unavailable pixels. Analytic profile, circle-distance, mirror and physical-scale controls pass. Original source/case hashes and masks are checked before integration. The original 16-pixel expanded and 22-pixel compact partial cohorts remain intact.

Orders eight and sixteen integrate the same profile using full-pixel positive weights, without occupied-area renormalization. Maximum encoded-level differences are below 0.000000002 on both members. [Results](result.json) retain exact values. This agreement concerns the new overlay alone, not whole optical-image convergence.

The analytic fade has no finite inner cutoff. A one-Lipschitz distance bound excludes only pixels whose opacity is everywhere below the declared numerical tolerance:

$$
\begin{aligned}
\epsilon&=10^{-15},\\
t&=\sigma\sqrt{-\ln\epsilon},\\
d(\boldsymbol{x}_P)+\frac{\sqrt{2}}{2}&<-t
\quad\Longrightarrow\quad
\sup_{\boldsymbol{x}\in P}a(d(\boldsymbol{x}))<\epsilon.
\end{aligned}
$$

The omitted encoded-channel contribution is bounded by the same tolerance on the unit signal range. This deep-interior numerical omission cannot create the visible sharp inner cutoff described in the feedback. Exterior support follows the projected silhouette; antialiasing can affect pixels crossed by that boundary.

No new source lookup is needed: composition uses the exact saved backing, with unavailable pixels preserved. Original source support transfers only for that unchanged backing. The outline makes no claim about reflected scene radiance or a uniquely identified Apple implementation.

## Clock and work

The [protocol](protocol.json) starts at 20:33:02.674 UTC, with an eight-minute checkpoint and 21:03:02.674 deadline. The checkpoint passes at 20:35:54.821 UTC. [Results](result.json) preserve scientific completion; publication remains part of the same cap.

Actual work is 50,934 quadrature calls and 29,325,440 nodes, four identity composites, four candidate composites and four score calls. Metric work includes twenty Gaussians and four erosions. Four original Study constructors cover 1,121,600 mask pixels. Numeric payload decoding totals 30,451,200 bytes. Rays, height calls, optical source queries, incident filters and fits are zero.

[First](first-hashes.json) and [last](last-hashes.json) input/code hashes match. Complete outputs, both alpha integration orders, profiles, original masks through their bindings and exact recipes remain retained. [Gallery exports](publication-assets.json) copy saved reference/candidate panels without resizing or rerendering.

The next question is whether the remaining mismatch comes from boundary registration, overlay strength/profile or the frozen body. No second width, angular opacity tuning or dark overlay is tested here.
