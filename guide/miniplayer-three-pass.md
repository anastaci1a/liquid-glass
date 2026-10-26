# Miniplayer: three complete refinement passes

Expanded references lead outline decisions; compact receives the identical model. The overlay reaches zero around the right upper-right and left lower-left diagonal cap regions. Earlier results retain their disclosed half-pixel registration error.

This review follows the shared compact and expanded model through contour, refraction, incident blur, color, outline, exterior shadow and artwork. Dispersion is excluded. Each completed pass retains its original failures and local tradeoffs.

Drag the mask to compare identical native coordinates. Fullscreen, keyboard, touch and side-by-side controls are available. Native detail crops preserve source pixels without smoothing or alignment changes.

[Research plan](../research/experiments/miniplayer-three-pass-101/README.md) · [Feedback](../research/feedback/miniplayer-three-pass.md) · [Previous four passes](miniplayer-four-pass.md) · [Current models](reconstruction.md)

Completed and independently replayed: **1 of three passes**. Numerical ranking and visual selection are separate; the original strict local guards remain reported.

## Pass 1

The narrower plateau and gentler contour improve both expanded aggregate errors, while compact errors worsen against the previous selection. Stronger uniform edge exposure over-brightens neutral regions; the expanded rim ranking retains the baseline endpoint. All fixed endpoint contrasts remain available below.

Independent arithmetic agrees within one float32 step. Pre-foreground arrays, aggregate error and original guard decisions agree; some detailed metrics differ in their last bits. Source-coordinate checks and zero overlay in both diagonal gaps pass. The improved shadow and artwork settings remain unchanged.

| Reference | E | SSIM | Original partial RMSE | Normalized combined score |
| --- | ---: | ---: | ---: | ---: |
| expanded A | 10.4927 | 0.97461 | 43.3327 | 0.9425 |
| expanded B | 5.3039 | 0.98244 | 13.9233 | 0.8842 |
| compact A | 14.4979 | 0.96716 | 21.8595 | 0.7991 |
| compact B | 14.2202 | 0.96596 | 21.5530 | 0.8260 |

Combined score equally weights baseline-normalized glass, rim, exterior and artwork errors across references. Lower than one improves this numerical ranking. It is not a physical-material identification or a replacement for visual review.

### Expanded A

![p1-expanded-a](assets/three101-p1-expanded-a.png)

### Expanded B

![p1-expanded-b](assets/three101-p1-expanded-b.png)

### Compact A

![p1-compact-a](assets/three101-p1-compact-a.png)

### Compact B

![p1-compact-b](assets/three101-p1-compact-b.png)

<details id="pass1-previous" data-stage="pass1-previous">
<summary>Previous result versus pass 1</summary>

![p1-expanded-a-previous](assets/three101-p1-expanded-a-previous.png)

![p1-expanded-b-previous](assets/three101-p1-expanded-b-previous.png)

![p1-compact-a-previous](assets/three101-p1-compact-a-previous.png)

![p1-compact-b-previous](assets/three101-p1-compact-b-previous.png)

</details>

<details data-stage="pass1-details">
<summary>Native cap, rim and artwork details</summary>

![p1-expanded-a-left](assets/three101-p1-expanded-a-left.png)

![p1-expanded-a-right](assets/three101-p1-expanded-a-right.png)

![p1-expanded-b-left](assets/three101-p1-expanded-b-left.png)

![p1-expanded-b-right](assets/three101-p1-expanded-b-right.png)

![p1-compact-a-left](assets/three101-p1-compact-a-left.png)

![p1-compact-a-right](assets/three101-p1-compact-a-right.png)

![p1-compact-b-left](assets/three101-p1-compact-b-left.png)

![p1-compact-b-right](assets/three101-p1-compact-b-right.png)

![p1-expanded-a-yellow](assets/three101-p1-expanded-a-yellow.png)

![p1-expanded-b-yellow](assets/three101-p1-expanded-b-yellow.png)

</details>

<details data-stage="pass1-endpoints">
<summary>Three fixed outline brightness/color contrasts</summary>

![p1-expanded-a-outline0](assets/three101-p1-expanded-a-outline0.png)

![p1-expanded-b-outline0](assets/three101-p1-expanded-b-outline0.png)

![p1-compact-a-outline0](assets/three101-p1-compact-a-outline0.png)

![p1-compact-b-outline0](assets/three101-p1-compact-b-outline0.png)

![p1-expanded-a-outline1](assets/three101-p1-expanded-a-outline1.png)

![p1-expanded-b-outline1](assets/three101-p1-expanded-b-outline1.png)

![p1-compact-a-outline1](assets/three101-p1-compact-a-outline1.png)

![p1-compact-b-outline1](assets/three101-p1-compact-b-outline1.png)

![p1-expanded-a-outline2](assets/three101-p1-expanded-a-outline2.png)

![p1-expanded-b-outline2](assets/three101-p1-expanded-b-outline2.png)

![p1-compact-a-outline2](assets/three101-p1-compact-a-outline2.png)

![p1-compact-b-outline2](assets/three101-p1-compact-b-outline2.png)

</details>

Recipe: incident sigma `6.6825`; rim plateau `0.6666666666666666` pixels and fade `2.0` pixels; artwork scale `0.95`. [Exact results and stage choices](../research/experiments/miniplayer-three-pass-101/pass1/README.md).

## Interpretation

Artwork uses the original asset with a shared centered scale, upward offset and absolute corner radius. Its score includes the exposed backing in the unchanged original guard box. It does not improve the glass score by changing that mask.

The outline uses incident-blurred refraction before the body grade. Chroma and peak strength remain distinct. Shadow darkens only uncovered contributions; it is excluded from lens transport. Shared optical parameters still differ only by member length.

All source mosaics are conditional evidence. Reflected scene assumptions and unassigned later power remain unresolved. A better appearance does not uniquely identify the original renderer.
