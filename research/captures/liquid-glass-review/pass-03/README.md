# Pass 03 — cap joins and curvature variants

Prepared from [Ana's geometry feedback](../pass-01/feedback.md#0506--geometry-experiments). Passes 01–02 remain unchanged.

| Image | Purpose |
| --- | --- |
| [01 — cap join comparison](01-cap-join-comparison.png) | Original straight/circular join on the left, gradual-curvature join on the right. Same height, crown, refractive index, background and lighting. |
| [02 — toolbar curvature options](02-toolbar-curvature-options.png) | Three cross-coupled crown strengths: 0, 0.15 and 0.30. All use the gradual cap join. Intended to inspect the effect of subtler toolbar curvature; these are not new Apple fits. |
| [03 — slider shape options](03-slider-shape-options.png) | Shape-only sections for crown strengths 0.2, 0.4 and 0.6. Top: longitudinal XZ section; bottom: XY sections at several depths. These use the measured slider outline and a continuously rounded front. No cap/tube subdivision. |

## Join diagnosis

- The original capsule uses `q=max(abs(x)−a,0)` and footprint `T=(q²+y²)/r²`. Its surface has matching slopes across the tube/cap join, but the second X derivative changes abruptly. Refraction can reveal that curvature change.
- The trial replaces the positive-part function across a narrow interval with the integral of cubic smoothstep:

```text
u = clamp((s/w + 1)/2, 0, 1)
q = 0                    when s ≤ −w
q = w(2u³ − u⁴)         when −w < s < w
q = s                    when s ≥ w
```

- Value, slope and second derivative agree at both transition endpoints. This is an actual change in the surface geometry and its analytic normal; it is not a screen-space stretch or a painted seam repair.
- At the tested 392 × 170-pixel lens size, with `w=0.30r`, the maximum sampled vertical silhouette change is **0.1975 pixel**. The shape is very close to, but not exactly, the original capsule.
- At two join probes, the jump in the X derivative of the unit normal falls from about **0.0091 / 0.0123 per pixel** to **0.00000049 / 0.00000056 per pixel**.
- At two upper straight-section probes, horizontal magnification remains about **1.072× / 1.070×** before and after smoothing. These probes do not establish identical behavior everywhere.

## Toolbar curvature versus stretching

| Cross-coupled crown strength | Horizontal magnification at two control points |
| --- | --- |
| 0 | 1.000× / 1.000× |
| 0.15 | 1.026× / 1.026× |
| 0.30 | 1.053× / 1.052× |

Reducing crown strength reduces geometric horizontal stretching in this model. The cap-join smoothing itself did not change stretching at those probes. The current close-fitting toolbar image map remains preserved in pass 01; these geometric trials do not replace it.

## Limits

- 01–02 trace rays through two curved surfaces with Snell/Fresnel interfaces, four subpixel samples and up to 32 internal reflections. No added blur, adaptive contrast or painted outline is applied. The background itself has smooth color transitions.
- The remaining untraced internal energy is small on average for those toolbar trials, but reaches about 1.7–2.0% at isolated samples. [Full diagnostics](geometry-diagnostics.json) record this limitation.
- Some slider optical trials had unresolved rim artifacts and significant untraced energy at isolated samples. They are retained with the private experiment evidence, not offered here as rendering choices. Image 03 therefore compares shapes only; it does not demonstrate corrected slider optics.
- Arbitrary geometry parameters are not certified convex. Surface continuity and tested ray correctness do not establish Apple fidelity or validate every setting combination.
- The measured slider silhouette and new shape options remain hypotheses about its three-dimensional form. A provisional visual preference does not identify Apple's private geometry.

## Ana's review: image 02

- The **third toolbar variant** appears closest to the intended result.
- Apple appears to have an **extremely slight outward bulge in the center of the middle section**; these variants look exactly straight there.
- Apart from that difference, Ana likes these models a lot.
- Retain the third variant as the reference and test a very shallow central crown independently of its stronger rim curvature.
- Working interpretation: curvature of the three-dimensional center surface. The observation alone does not uniquely identify whether silhouette curvature or depth curvature is responsible; keep those parameters distinct during investigation rather than silently equating them.

## Ana's review: image 03

- The **third slider shape (`crown 0.6`)** is the closest of these options, primarily on the strength of its **outline shape**.
- Ana is willing to try that geometry.
- This remains a **provisional shape preference**, not acceptance of an optical rendering or proof that it is Apple's geometry. Test ray behavior and rendering artifacts separately.
- **Request:** compare the previous slider reconstruction and this new third-shape candidate side by side for refraction differences; include Apple as the common baseline.
- **Specific concern:** the new rounder geometry may make the blue slider line **expand vertically too early**, farther from the edge than in Apple.
- Compare the **onset and progression of line-height expansion** toward the left rim, as well as its maximum height. Preserve the relatively unchanged middle section; overall silhouette similarity alone is insufficient.
- **Further clarification:** Apple's line looks essentially normal/unrefracted through the interior **until it is quite close to the edge**, where it eases into very strong refraction. The desired profile has a quiet interior and a smooth but rapid near-rim onset, not weak distortion accumulating across the whole lens.
