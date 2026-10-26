# Miniplayer feedback: inward joins, edge color and broad shadow

Latest: [intermediate joins, colored plateau and downward shadow](miniplayer-middle-ground.md). Incident blur is retained. All settings and original failures are published; no family adoption is claimed.

The new shared shape moves top joins down and bottom joins up, while keeping the outer tips fixed. Near-tip refraction becomes stronger. The final combination remains experimental: boundary, foreground and other local failures prevent family acceptance. The selected reconstruction is unchanged.

Drag each divider across identical native coordinates. Fullscreen, keyboard, touch and side-by-side views are available. The first group shows the complete proposal; isolated tests and native edge close-ups follow.

[Full report](../research/experiments/miniplayer-stronger-joins-98/README.md) · [Previous refinement](miniplayer-refinement.md) · [Selected models](reconstruction.md)

## Complete experimental result

The common model uses stronger inward join smoothing, ten-percent less incident blur, a broad exterior-only shadow and a finite color filter. Black reaches light gray at maximum filter strength; nonwhite inputs remain below white. Compact and expanded still differ only by major length.

| Reference | Original E | Final E | Original boundary RMSE → final |
| --- | ---: | ---: | ---: |
| Expanded A | 7.8835 | 11.1280 | 40.3268 → 78.4099 |
| Expanded B | 6.1494 | 5.6279 | 26.0804 → 50.9031 |
| Compact A | 20.5319 | 16.0236 | 23.8132 → 40.2864 |
| Compact B | 19.6819 | 16.7582 | 21.0766 → 39.8497 |

All four original partial-boundary guards fail. Aggregate improvements do not override those failures. The final images retain incorrect returned-feature placement and compact tone differences.

### Expanded A

![expanded-a-final](assets/feedback98-expanded-a-final.png)

### Expanded B

![expanded-b-final](assets/feedback98-expanded-b-final.png)

### Compact A

![compact-a-final](assets/feedback98-compact-a-final.png)

### Compact B

![compact-b-final](assets/feedback98-compact-b-final.png)

<details id="starting-comparison">
<summary>Previous published refinement versus this result</summary>

![expanded-a-previous](assets/feedback98-expanded-a-previous.png)

![expanded-b-previous](assets/feedback98-expanded-b-previous.png)

![compact-a-previous](assets/feedback98-compact-a-previous.png)

![compact-b-previous](assets/feedback98-compact-b-previous.png)

</details>

## Native edge close-ups

These crops preserve native pixels without smoothing. Use fullscreen to inspect the cap joins and upper colored edge. The filter preserves yellow rather than replacing it with white, but the correct strength and source-feature placement remain unresolved.

![expanded-a-left-detail](assets/feedback98-expanded-a-left-detail.png)

![expanded-a-right-detail](assets/feedback98-expanded-a-right-detail.png)

![expanded-b-left-detail](assets/feedback98-expanded-b-left-detail.png)

![expanded-b-right-detail](assets/feedback98-expanded-b-right-detail.png)

![compact-a-left-detail](assets/feedback98-compact-a-left-detail.png)

![compact-a-right-detail](assets/feedback98-compact-a-right-detail.png)

![compact-b-left-detail](assets/feedback98-compact-b-left-detail.png)

![compact-b-right-detail](assets/feedback98-compact-b-right-detail.png)

## Shadow measurements

Fixed source/reference patches show darkening extending tens of pixels beyond the pill. Top-center residuals approach the measured far-background level around 45–55 pixels, rather than the previous four-pixel shadow width. The conditional mosaic is not a pristine before-image; these measurements do not uniquely identify a physical shadow.

| Reference | Darkening at 4 px | 16 px | 32 px | 64 px |
| --- | ---: | ---: | ---: | ---: |
| Expanded A | 15.55 | 8.92 | 4.07 | 0.07 |
| Expanded B | 19.06 | 12.06 | 6.71 | -0.07 |
| Compact A | 7.65 | 5.80 | 3.57 | -0.57 |
| Compact B | 21.57 | 15.00 | 10.00 | 1.00 |

Values are encoded luminance levels on a 255-level scale. Negative values and far-field confounds remain in the [measurement record](../research/experiments/miniplayer-feedback-diagnostics-95/README.md). Bottom profiles can cross unrelated interface content; they are not evidence of a growing shadow.

## Separate tests

Less blur sharpens texture but worsens aggregate error on all four fixed-geometry references. The stronger joins are a single geometric hypothesis, not a fitted silhouette. The compact interior is approximately 12–14 luminance levels too dark in the preceding model, while expanded means are nearly correct. A global exposure increase cannot resolve that discrepancy safely.

<details data-stage="geometry">
<summary>Stronger joins and less blur, before new edge/shadow</summary>

![expanded-a-geometry](assets/feedback98-expanded-a-geometry.png)

![expanded-b-geometry](assets/feedback98-expanded-b-geometry.png)

![compact-a-geometry](assets/feedback98-compact-a-geometry.png)

![compact-b-geometry](assets/feedback98-compact-b-geometry.png)

</details>

<details data-stage="blur">
<summary>Less blur on the previous geometry</summary>

![expanded-a-blur](assets/feedback98-expanded-a-blur.png)

![expanded-b-blur](assets/feedback98-expanded-b-blur.png)

![compact-a-blur](assets/feedback98-compact-a-blur.png)

![compact-b-blur](assets/feedback98-compact-b-blur.png)

</details>

<details data-stage="filter">
<summary>Light-gray edge response with broad shadow</summary>

![expanded-a-filter](assets/feedback98-expanded-a-filter.png)

![expanded-b-filter](assets/feedback98-expanded-b-filter.png)

![compact-a-filter](assets/feedback98-compact-a-filter.png)

![compact-b-filter](assets/feedback98-compact-b-filter.png)

</details>

<details data-stage="combination">
<summary>Previous geometry with all new material stages</summary>

![expanded-a-combination](assets/feedback98-expanded-a-combination.png)

![expanded-b-combination](assets/feedback98-expanded-b-combination.png)

![compact-a-combination](assets/feedback98-compact-a-combination.png)

![compact-b-combination](assets/feedback98-compact-b-combination.png)

</details>

[Finite filter and broad-shadow trials](../research/experiments/miniplayer-edge-filter-96/README.md) · [Blur and revised filter evidence](../research/experiments/miniplayer-subtle-blur-97/README.md)
