# Thinner hue-preserving outline

The yellow hue correction is removed. Saturation and value retain revision 106's calibrated response, while every outline endpoint preserves its input hue. The enlarged artwork and completed lens body remain unchanged. At full strength, tentative input #EBCE48 now gives approximately #F6E286, preserving its hue while retaining the calibrated saturation and value. White remains #FCFCFC.

The outline plateau and inward fade are both multiplied by 0.8. A second thickness multiplier rises linearly from 4/7 at 43.359684% of the pill width to one at 44.584980%. It stays thinner to the left and thicker to the right. Expanded and compact use the same proportional rule.

[Research and verification](../research/experiments/miniplayer-outline-taper-107/README.md) · [Previous revision](miniplayer-yellow-match.md) · [Selected reconstruction](reconstruction.md)

## Thickness and brightness

| Region | Plateau | Fade scale | Positive value increase |
| --- | ---: | ---: | ---: |
| Left of 43.359684% | 0.685714 px | 0.914286 px | 99% |
| Transition | Linear | Linear | Linear |
| Right of 44.584980% | 1.2 px | 1.6 px | 100% |

The one-percent reduction applies only to the positive HSV value increase, not to the entire color or saturation. Its size is a provisional interpretation of the requested slight brightness change. Endpoint hue and saturation are preserved during this reduction. The original opposing angular gaps remain zero.

Thickness and brightness moments use actual pixel area. Orders 16 and 32 identify pixels needing refinement; those pixels use orders 64 and 96. All pixels remain scored. The original tolerance is unchanged. Original geometry, shadow, optical transport and incident blur remain frozen.

## Image comparisons

| Case | Previous E | Revised E | SSIM | Partial RMSE |
| --- | ---: | ---: | ---: | ---: |
| expanded A | 11.7337 | 10.1653 | 0.97536 | 38.3208 |
| expanded B | 4.8070 | 4.7655 | 0.98210 | 11.3834 |
| compact A | 14.9937 | 16.3208 | 0.96548 | 29.7011 |
| compact B | 15.6359 | 16.5640 | 0.96372 | 25.0957 |

All local and aggregate changes are retained below. All original scoring cohorts remain unchanged. These comparisons are held for review, without a full-family fidelity claim.

### Expanded A

![expanded-a](assets/taper107-expanded-a.png)

<details data-hsv="expanded-a-previous"><summary>Previous revision versus revision</summary>

![expanded-a-previous](assets/taper107-expanded-a-previous.png)

</details>

<details data-hsv="expanded-a-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>

![expanded-a-left-cap](assets/taper107-expanded-a-left-cap.png)

![expanded-a-right-cap](assets/taper107-expanded-a-right-cap.png)

![expanded-a-upper-rim](assets/taper107-expanded-a-upper-rim.png)

![expanded-a-lower-rim](assets/taper107-expanded-a-lower-rim.png)

![expanded-a-upper-right-gap](assets/taper107-expanded-a-upper-right-gap.png)

![expanded-a-lower-left-gap](assets/taper107-expanded-a-lower-left-gap.png)

![expanded-a-upper-transition](assets/taper107-expanded-a-upper-transition.png)

![expanded-a-lower-transition](assets/taper107-expanded-a-lower-transition.png)

![expanded-a-brown-content](assets/taper107-expanded-a-brown-content.png)

![expanded-a-artwork](assets/taper107-expanded-a-artwork.png)

</details>

### Expanded B

![expanded-b](assets/taper107-expanded-b.png)

<details data-hsv="expanded-b-previous"><summary>Previous revision versus revision</summary>

![expanded-b-previous](assets/taper107-expanded-b-previous.png)

</details>

<details data-hsv="expanded-b-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>

![expanded-b-left-cap](assets/taper107-expanded-b-left-cap.png)

![expanded-b-right-cap](assets/taper107-expanded-b-right-cap.png)

![expanded-b-upper-rim](assets/taper107-expanded-b-upper-rim.png)

![expanded-b-lower-rim](assets/taper107-expanded-b-lower-rim.png)

![expanded-b-upper-right-gap](assets/taper107-expanded-b-upper-right-gap.png)

![expanded-b-lower-left-gap](assets/taper107-expanded-b-lower-left-gap.png)

![expanded-b-upper-transition](assets/taper107-expanded-b-upper-transition.png)

![expanded-b-lower-transition](assets/taper107-expanded-b-lower-transition.png)

![expanded-b-brown-content](assets/taper107-expanded-b-brown-content.png)

![expanded-b-artwork](assets/taper107-expanded-b-artwork.png)

</details>

### Compact A

![compact-a](assets/taper107-compact-a.png)

<details data-hsv="compact-a-previous"><summary>Previous revision versus revision</summary>

![compact-a-previous](assets/taper107-compact-a-previous.png)

</details>

<details data-hsv="compact-a-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>

![compact-a-left-cap](assets/taper107-compact-a-left-cap.png)

![compact-a-right-cap](assets/taper107-compact-a-right-cap.png)

![compact-a-upper-rim](assets/taper107-compact-a-upper-rim.png)

![compact-a-lower-rim](assets/taper107-compact-a-lower-rim.png)

![compact-a-upper-right-gap](assets/taper107-compact-a-upper-right-gap.png)

![compact-a-lower-left-gap](assets/taper107-compact-a-lower-left-gap.png)

![compact-a-upper-transition](assets/taper107-compact-a-upper-transition.png)

![compact-a-lower-transition](assets/taper107-compact-a-lower-transition.png)

![compact-a-white-content](assets/taper107-compact-a-white-content.png)

![compact-a-artwork](assets/taper107-compact-a-artwork.png)

</details>

### Compact B

![compact-b](assets/taper107-compact-b.png)

<details data-hsv="compact-b-previous"><summary>Previous revision versus revision</summary>

![compact-b-previous](assets/taper107-compact-b-previous.png)

</details>

<details data-hsv="compact-b-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>

![compact-b-left-cap](assets/taper107-compact-b-left-cap.png)

![compact-b-right-cap](assets/taper107-compact-b-right-cap.png)

![compact-b-upper-rim](assets/taper107-compact-b-upper-rim.png)

![compact-b-lower-rim](assets/taper107-compact-b-lower-rim.png)

![compact-b-upper-right-gap](assets/taper107-compact-b-upper-right-gap.png)

![compact-b-lower-left-gap](assets/taper107-compact-b-lower-left-gap.png)

![compact-b-upper-transition](assets/taper107-compact-b-upper-transition.png)

![compact-b-lower-transition](assets/taper107-compact-b-lower-transition.png)

![compact-b-white-content](assets/taper107-compact-b-white-content.png)

![compact-b-artwork](assets/taper107-compact-b-artwork.png)

</details>

## Verification

The completed body and artwork are pixel-exact to revision 106. Four original baseline identities and four independent color/composition replays pass. All original masks and local guards remain. No clipping, optical rays, source sampling or incident filtering was introduced.
