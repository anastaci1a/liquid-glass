# Pass 02 — focused crops and white-icon trials

October 19, 2026. Derived from the [pass 01 feedback](../pass-01/feedback.md). These files do not change the pass 01 images.

## Images

| Image | Contents |
| --- | --- |
| [01 — playback rim crops](01-playback-rim-crops.png) | Three rows: bottom-left, top-left and upper-right. Apple on the left, the same pass 01 reconstruction on the right. The upper-right group includes both dune-boundary crossings. Enlarged 2× with nearest-neighbor sampling to preserve the underlying pixel evidence. |
| [02 — uncovered video frame](02-playback-uncovered-frame.png) | Baseline record; no preference requested. Native 1920 × 1080 Apple frame at 180 seconds, before the lens example. This is the recovered photographic input, not an independently obtained original photograph. |
| [03 — registered background](03-playback-registered-background.png) | Alignment record; no preference requested. The uncovered frame is enlarged approximately **3.63%**, translated about **−34.88 px horizontally / −19.61 px vertically**, and rotated about **0.0021°** to align it with the target at 190 seconds. No glass or play icon added. |
| [04 — background comparison](04-playback-background-comparison.png) | Apple lens scene beside its registered uncovered input. |
| [05 — white-icon shading trials](05-white-icon-shading-trials.png) | Apple; uniform white; constant cream; two background-dependent color fits. The replacement icons reuse only the reference silhouette/edge coverage, not its interior RGB colors. |
| [06 — icon opacity mask](06-white-icon-mask.png) | The extracted silhouette and antialiased coverage, with a slight opacity feather confined to roughly 1–2 native pixels. White represents opaque coverage; black represents transparency. |
| [07 — toolbar `d` crop](07-toolbar-d-crop.png) | Apple and the same pass 01 tensor fit, enlarged 4×. Isolates the stroke/curvature transition near the final `d` in “around.” This is a diagnostic crop, not a newly refined fit. |

## White-icon experiment

The icon starts from a white mask. Its color is calculated from the background using:

```text
C = 1 − strengthRGB × (1 − GaussianBlur(B, sigma))^exponent
```

- `B` is either the registered uncovered photograph or the reconstructed glass beneath the icon.
- The three strengths and shared exponent are fitted; blur is tested at 0, 3, 12, 24 and 48 native pixels.
- The silhouette/edge coverage comes from the reference, with an additional 0.35-pixel Gaussian opacity feather. No reference interior colors are pasted into the trial's shading.
- Fits use the icon interior, excluding a three-pixel boundary. Spatial 32-pixel blocks are withheld from fitting. Selection uses training error only.

| Candidate | Training RGB RMSE | Withheld RGB RMSE |
| --- | ---: | ---: |
| Uniform white | 22.33 | 20.88 |
| Constant cream | 8.15 | 7.72 |
| Background-dependent color, reconstructed glass, no added blur | 3.47 | 3.38 |
| Same family, 3-pixel blur | 3.63 | 3.60 |

Errors use encoded RGB on a 0–255 scale. Parameters and all twelve trials: [icon-trials.json](icon-trials.json).

**Interpretation:** the tested background-dependent response fits this icon better than a uniform fill. Within this family, little/no added blur better preserves the sharp lower dune transition. The remaining vertical color-gradient mismatch is visible. This does not identify Apple's shader, prove a literal diffusion model, or establish transfer to another scene. The withheld blocks share the same frame, and the underlying reconstructed glass has its own errors.

## What remains unchanged

- Lens curvature has not been refitted for these crop sheets.
- The slider's general exterior-shadow/blue-halo model remains unfinished.
- Pass 01 still contains the original six images and all feedback received so far, including the subsequent geometry/join feedback.

## Ana's review: image 01

- The playback reconstruction appears to contain an **unnecessary inverted/mirrored strip at the very outer edge**.
- The lighter sand eases into the circular rim, then **sharply mirrors at its outermost edge**. Ana does not see this mirroring in Apple's version of this sample.
- Ana expects removing that reversal to resolve much of the mismatch.
- The transition between the rounded rim and flatter front should also be **even smoother**.
- This feedback concerns the playback control; it does not retract the toolbar's observed inverted text.
- Next check: distinguish source-map reversal from reflection/highlight or contact-compositing artifacts before changing the model. This is an observed appearance constraint, not yet a diagnosis.

## Ana's observation: images 02–03

- Image 03 looks slightly more zoomed-in than 02. This is correct: registration changes the input framing by the measured scale above.
- These are source/alignment records, not competing lens variants. They require no choice or visual-preference review.

## Ana's review: image 05

- The **last two background-dependent icon shading trials are very close** to Apple.
- Apple's darker icon regions appear **slightly more saturated**.
- There is a little more **orange immediately above the sharp lower bright line**.
- The color grades toward **almost reddish orange at the darkest point near the top**.
- This is a **very faint effect**; retain that subtlety rather than introducing a strong colored wash.
- Next check: compare brightness-dependent saturation and channel-response curves against the existing fits. Derive changes from the sampled background; do not paint a fixed top-to-bottom color gradient into this particular icon.

## Ana's review: image 07

- The crop is **exactly the region Ana intended** and makes the width-stretching discrepancy clearer.
- Across the height of the cropped `d` stroke, there should already be a **slightly greater, more continuous change in horizontal stretching**.
- The stroke should progressively bend over more of that vertical span, instead of remaining relatively straight and changing curvature more abruptly.
- This is a working mathematical interpretation of the observation, not a user-specified equation: inspect local horizontal magnification as a function of vertical position, and the continuity of its rate of change. Do not assume that simply increasing maximum stretch will solve it.
- **There is also insufficient blur** in the reconstruction. This reinforces the earlier request for a small toolbar blur increase.
- Compare blur and stretch-profile changes separately so optical shape errors are not hidden by smoothing.
