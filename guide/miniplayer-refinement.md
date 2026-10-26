# Miniplayer: smooth shape, shadow and color-aware rim

Latest: [inward joins, broad shadow and color-filter comparisons](miniplayer-feedback-review.md). The complete experimental pair remains unaccepted; original boundary and foreground failures are preserved.

The complete refinement sequence is finished and independently replayed by the primary researcher. The combined proposal makes the compact rim clearer and keeps edge color, but expanded A becomes too bright. **No proposal passes every original family guard.** The selected model remains unchanged.

Drag the divider to compare identical native coordinates. Touch, keyboard arrows, side-by-side mode and fullscreen are available. The first comparisons show the final experimental combination; every separate stage and tested setting follows.

[Full report and verification](../research/experiments/miniplayer-complete-refinement-94/README.md) · [Previous five outline passes](outline-review.md) · [Selected reconstructions](reconstruction.md)

## Combined development result

The shared contour has smooth curvature and slightly convex long sides. The exterior-only shadow uses strength 0.1. The color-aware inner fade uses width 2.6 pixels and a bounded lift with gentle desaturation. Compact and expanded differ only in major length.

| Reference | Starting E | Combined E | Frozen boundary RMSE: start → combined |
| --- | ---: | ---: | ---: |
| Expanded A | 7.8835 | 11.8101 | 40.3268 → 62.3036 |
| Expanded B | 6.1494 | 5.0034 | 26.0804 → 35.2868 |
| Compact A | 20.5319 | 14.7042 | 23.8132 → 21.9686 |
| Compact B | 19.6819 | 15.6437 | 21.0766 → 22.8641 |

Lower errors are better. Improvements in one reference do not waive another reference’s failure.

### Expanded A

![expanded A: reference versus combined result](assets/refinement94-expanded-a-combined-reference.png)

### Expanded B

![expanded B: reference versus combined result](assets/refinement94-expanded-b-combined-reference.png)

### Compact A

![compact A: reference versus combined result](assets/refinement94-compact-a-combined-reference.png)

### Compact B

![compact B: reference versus combined result](assets/refinement94-compact-b-combined-reference.png)

<details id="starting-comparison">
<summary>Starting model versus combined result</summary>

**Expanded A.**

![expanded A: starting versus combined result](assets/refinement94-expanded-a-combined-starting.png)

**Expanded B.**

![expanded B: starting versus combined result](assets/refinement94-expanded-b-combined-starting.png)

**Compact A.**

![compact A: starting versus combined result](assets/refinement94-compact-a-combined-starting.png)

**Compact B.**

![compact B: starting versus combined result](assets/refinement94-compact-b-combined-starting.png)

</details>

## Separate stages and every setting

Each group includes the Apple reference and the starting-model comparison. Shadow and highlight proposals use the new smooth geometry, so they are not isolated changes to the old body. Their separate component-relative guards are retained in the linked reports.

<details data-stage="geometry" id="stage-geometry">
<summary>Smooth geometry only</summary>

[Method, limits and original guards](../research/experiments/miniplayer-complete-refinement-94/geometry-run-02/README.md)

<details id="setting-geometry">
<summary>Setting geometry: all four references</summary>

**Expanded A.** E: 7.9566. Failed original guards: glass, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A geometry: reference comparison](assets/refinement94-expanded-a-geometry-reference.png)

![expanded A geometry: starting comparison](assets/refinement94-expanded-a-geometry-starting.png)

**Expanded B.** E: 5.9386. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B geometry: reference comparison](assets/refinement94-expanded-b-geometry-reference.png)

![expanded B geometry: starting comparison](assets/refinement94-expanded-b-geometry-starting.png)

**Compact A.** E: 20.2544. Failed original guards: interior, partial, title.svg, play.svg.

![compact A geometry: reference comparison](assets/refinement94-compact-a-geometry-reference.png)

![compact A geometry: starting comparison](assets/refinement94-compact-a-geometry-starting.png)

**Compact B.** E: 19.5653. Failed original guards: interior, SSIM, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B geometry: reference comparison](assets/refinement94-compact-b-geometry-reference.png)

![compact B geometry: starting comparison](assets/refinement94-compact-b-geometry-starting.png)

</details>

</details>

<details data-stage="shadow" id="stage-shadow">
<summary>Exterior-only shadow</summary>

[Method, limits and original guards](../research/experiments/miniplayer-complete-refinement-94/shadow/README.md)

<details id="setting-s0.025">
<summary>Setting s0.025: all four references</summary>

**Expanded A.** E: 7.9408. Failed original guards: glass, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A s0.025: reference comparison](assets/refinement94-expanded-a-s0.025-reference.png)

![expanded A s0.025: starting comparison](assets/refinement94-expanded-a-s0.025-starting.png)

**Expanded B.** E: 5.9310. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B s0.025: reference comparison](assets/refinement94-expanded-b-s0.025-reference.png)

![expanded B s0.025: starting comparison](assets/refinement94-expanded-b-s0.025-starting.png)

**Compact A.** E: 20.2547. Failed original guards: interior, partial, title.svg, play.svg.

![compact A s0.025: reference comparison](assets/refinement94-compact-a-s0.025-reference.png)

![compact A s0.025: starting comparison](assets/refinement94-compact-a-s0.025-starting.png)

**Compact B.** E: 19.5656. Failed original guards: interior, SSIM, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B s0.025: reference comparison](assets/refinement94-compact-b-s0.025-reference.png)

![compact B s0.025: starting comparison](assets/refinement94-compact-b-s0.025-starting.png)

</details>

<details id="setting-s0.05">
<summary>Setting s0.05: all four references</summary>

**Expanded A.** E: 7.9265. Failed original guards: glass, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A s0.05: reference comparison](assets/refinement94-expanded-a-s0.05-reference.png)

![expanded A s0.05: starting comparison](assets/refinement94-expanded-a-s0.05-starting.png)

**Expanded B.** E: 5.9261. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B s0.05: reference comparison](assets/refinement94-expanded-b-s0.05-reference.png)

![expanded B s0.05: starting comparison](assets/refinement94-expanded-b-s0.05-starting.png)

**Compact A.** E: 20.2550. Failed original guards: interior, partial, title.svg, play.svg.

![compact A s0.05: reference comparison](assets/refinement94-compact-a-s0.05-reference.png)

![compact A s0.05: starting comparison](assets/refinement94-compact-a-s0.05-starting.png)

**Compact B.** E: 19.5659. Failed original guards: interior, SSIM, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B s0.05: reference comparison](assets/refinement94-compact-b-s0.05-reference.png)

![compact B s0.05: starting comparison](assets/refinement94-compact-b-s0.05-starting.png)

</details>

<details id="setting-s0.1">
<summary>Setting s0.1: all four references</summary>

**Expanded A.** E: 7.9030. Failed original guards: glass, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A s0.1: reference comparison](assets/refinement94-expanded-a-s0.1-reference.png)

![expanded A s0.1: starting comparison](assets/refinement94-expanded-a-s0.1-starting.png)

**Expanded B.** E: 5.9243. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B s0.1: reference comparison](assets/refinement94-expanded-b-s0.1-reference.png)

![expanded B s0.1: starting comparison](assets/refinement94-expanded-b-s0.1-starting.png)

**Compact A.** E: 20.2558. Failed original guards: interior, partial, title.svg, play.svg.

![compact A s0.1: reference comparison](assets/refinement94-compact-a-s0.1-reference.png)

![compact A s0.1: starting comparison](assets/refinement94-compact-a-s0.1-starting.png)

**Compact B.** E: 19.5665. Failed original guards: interior, SSIM, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B s0.1: reference comparison](assets/refinement94-compact-b-s0.1-reference.png)

![compact B s0.1: starting comparison](assets/refinement94-compact-b-s0.1-starting.png)

</details>

</details>

<details data-stage="highlight" id="stage-highlight">
<summary>Color-aware highlight</summary>

[Method, limits and original guards](../research/experiments/miniplayer-complete-refinement-94/highlight/README.md)

<details id="setting-h0">
<summary>Setting h0: all four references</summary>

**Expanded A.** E: 11.4354. Failed original guards: glass, rim, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A h0: reference comparison](assets/refinement94-expanded-a-h0-reference.png)

![expanded A h0: starting comparison](assets/refinement94-expanded-a-h0-starting.png)

**Expanded B.** E: 5.0223. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B h0: reference comparison](assets/refinement94-expanded-b-h0-reference.png)

![expanded B h0: starting comparison](assets/refinement94-expanded-b-h0-starting.png)

**Compact A.** E: 15.1614. Failed original guards: interior, partial, title.svg, play.svg.

![compact A h0: reference comparison](assets/refinement94-compact-a-h0-reference.png)

![compact A h0: starting comparison](assets/refinement94-compact-a-h0-starting.png)

**Compact B.** E: 16.3739. Failed original guards: interior, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B h0: reference comparison](assets/refinement94-compact-b-h0-reference.png)

![compact B h0: starting comparison](assets/refinement94-compact-b-h0-starting.png)

</details>

<details id="setting-h1">
<summary>Setting h1: all four references</summary>

**Expanded A.** E: 11.5481. Failed original guards: glass, rim, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A h1: reference comparison](assets/refinement94-expanded-a-h1-reference.png)

![expanded A h1: starting comparison](assets/refinement94-expanded-a-h1-starting.png)

**Expanded B.** E: 5.0225. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B h1: reference comparison](assets/refinement94-expanded-b-h1-reference.png)

![expanded B h1: starting comparison](assets/refinement94-expanded-b-h1-starting.png)

**Compact A.** E: 14.9580. Failed original guards: interior, title.svg, play.svg.

![compact A h1: reference comparison](assets/refinement94-compact-a-h1-reference.png)

![compact A h1: starting comparison](assets/refinement94-compact-a-h1-starting.png)

**Compact B.** E: 16.0486. Failed original guards: interior, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B h1: reference comparison](assets/refinement94-compact-b-h1-reference.png)

![compact B h1: starting comparison](assets/refinement94-compact-b-h1-starting.png)

</details>

<details id="setting-h2">
<summary>Setting h2: all four references</summary>

**Expanded A.** E: 11.8537. Failed original guards: glass, rim, held, interior, E, SSIM, partial, jupiter.jpg, title.svg, artist.svg, play.svg, forward.svg.

![expanded A h2: reference comparison](assets/refinement94-expanded-a-h2-reference.png)

![expanded A h2: starting comparison](assets/refinement94-expanded-a-h2-starting.png)

**Expanded B.** E: 5.0227. Failed original guards: interior, partial, jupiter.jpg, title.svg, artist.svg, play.svg.

![expanded B h2: reference comparison](assets/refinement94-expanded-b-h2-reference.png)

![expanded B h2: starting comparison](assets/refinement94-expanded-b-h2-starting.png)

**Compact A.** E: 14.7034. Failed original guards: interior, title.svg, play.svg.

![compact A h2: reference comparison](assets/refinement94-compact-a-h2-reference.png)

![compact A h2: starting comparison](assets/refinement94-compact-a-h2-starting.png)

**Compact B.** E: 15.6431. Failed original guards: interior, partial, jupiter.jpg, title.svg, play.svg, forward.svg.

![compact B h2: reference comparison](assets/refinement94-compact-b-h2-reference.png)

![compact B h2: starting comparison](assets/refinement94-compact-b-h2-starting.png)

</details>

</details>

## What remains wrong

Expanded A’s left and lower edge becomes too bright. Compact returns, especially the left cap and upper lettering, remain misplaced. The new outline does not repair those source-feature errors. Its nominal width and angular fade remain hypotheses, not measured shader parameters.

The shadow improves separation from bright exterior backgrounds, but neither the shadow alone nor the full combination passes every original guard. The contour keeps the measured extrema; it is not an accepted pose or size correction.

All four baseline images reproduce exactly. Twenty-eight material candidates replay within one float32 rounding step, and every stored score and guard reproduces exactly. Positive-area checks and two-order outline integration pass. These checks establish implementation consistency, not Apple fidelity or a uniquely identified material.
