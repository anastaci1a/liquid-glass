# Detached Music Search: verified neutral tone

**Accept the common encoded-tone component.** Independent cached replay matches both identity controls, graded samples, pre-foreground arrays, completed pixels and every reported score. The body is visibly closer to the reference pastel tone. Missing rim light and incorrect returns remain unresolved.

| Record | Evidence |
| --- | --- |
| Declared primary review | [Protocol](protocol.json) |
| Independent exact replay and float64 checks | [Verification](verification.json) |
| Reproduction code | [Replay](replay.py) |
| Primary decision | [Selection](selection.json) |
| Original candidate and fixed crops | [Color experiment](../agent-music-search-neutral-05/README.md) |

## Result and limits

| Reference | Unit-body E | Selected-tone E | Partial-glass RMSE, before / after |
| --- | ---: | ---: | ---: |
| A | 66.085857 | 27.661699 | 140.474060 / 97.969154 |
| B | 55.939570 | 22.030139 | 108.760757 / 70.071236 |

All original and completed body, SSIM, foreground and exterior guards pass. Both original 38-pixel partial-glass guards pass. All six float64 residual cohorts also improve or tie. Clear samples and exterior remain exact; clipping is zero.

B's lower-return RGB RMSE worsens from 27.966990 to 28.644618, with a chroma regression. Detail contrast falls in both references. The unchanged feature positions, thin bright perimeter and illumination still disagree with the reference.

This component is accepted for visible body-tone improvement. It is not refraction acceptance, a completed pipeline pass or a historical empirical score improvement. The prospective case fingerprints and inherited historical receipt mismatch remain explicit.

## Exact operation

The same gain and bias apply to all three channels and both references. The response acts on retained inside samples before the original two-by-two AA integration. Clear samples and the full frozen foreground chain remain unchanged.

$$
\begin{aligned}
C_{\mathrm{lens}}&=\operatorname{clip}(gS+b,0,1),\\
g&=0.5193880051291454,\\
b&=0.4473611800152188.
\end{aligned}
$$

This is an empirical encoded response, not measured radiance or transmittance. The original incident Gaussian remains 6.75 native pixels with finite radius 21, applied before geometric sampling. Both tested alternative widths remain rejected.

## Geometry and shared-system scope

The selected initialization remains the radius-adapted shared harmonic circular back, flat front, index 1.5 and background distance 2 original length units. The accepted pose, source, masks, vector and style are frozen. No new ray, height, source query, optical filter or fit ran during primary review.

Geometry supplies the actual gradients and refracted paths. Source support remains conditional temporal-mosaic availability, not recovered hidden photography. The magnifier is a clean trace with fitted style, not proven exact original UI geometry.

The response mechanism transfers unchanged between both Search references. Its coefficients are shared within that pair. Different coefficients from expanded playback remain empirical family calibration, not demonstrated physical material identity.

## Review accounting and presentation

The primary replay used two identity composites, two candidates, four unchanged score calls and 112,800 reference-mask points. Scientific input hashes matched before and after. No alternate coefficient was evaluated.

The gallery reformats the saved native panels only. Each side is 480 pixels wide, twice the 240-pixel native crop; the full circle and 64-pixel caption remain. Historical empirical stills and motion remain separately labeled.

Outline scene feasibility is the next stage. No reflected image, environment replacement or new geometric setting is accepted here.

The first browser check used site output generated before the new caption metadata. It failed that metadata assertion. A subsequent media-loading check exposed a registry-key mismatch and an extra historical disclosure layer. The matching section key and explicit historical marker correct this publication issue; no optical evidence was regenerated.

## Replay from a fresh checkout

Fetch Git LFS objects and restore byte-identical indexed inputs with Node 22:

```sh
git lfs pull
node research/experiments/search-neutral-primary-01/restore-inputs.cjs
```

The restore command refuses conflicting existing files. It does not estimate a source or run optics. The exact as-run replay expects the checkout mounted read-only at `/helper` and its shared code at `/repo`; only the new primary-review output directory needs write access. Python dependencies are listed in the reconstruction requirements.

`verification.json` is immutable evidence; its absolute paths describe the isolated review mounts. Running the script again requires a separate output record because it refuses to overwrite that verification.
