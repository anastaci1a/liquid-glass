# Subpixel outline composition does not resolve the edge failures

The third outline test preserves clear subrays exactly but fails all four original partial-edge guards. A matched AA2 control isolates composition order: sample composition helps compact partial errors slightly and worsens both expanded partial errors. Neither qualifies. The separate outline remains outside all refraction calculations.

## One composition change

The width stays 0.65 native pixel, peak opacity one and color white. The outer maximum stays on the original contour, as in [overlay88](../miniplayer-overlay-outline-88/README.md). Both lengths share the same profile. No placement, shape, source, blur, material or light parameter changes.

Retained working20 source samples, primary powers and direct-front directions reproduce all four pre-foreground and completed images exactly. The outline then blends over those post-refraction sample colors before the original AA2 average. Every original foreground box has exactly unchanged backing, so the fixed foreground chain does not change the outline's visible ordering here.

This commutation is specific to these nonoverlapping regions. An outline intersecting artwork would require an explicit composition-order decision; this test does not establish a general interchange rule.

The control first averages the same four opacity samples, then blends over the already completed pixel. This avoids confusing composition order with the positive area quadrature used in overlay88. AA2 is not an area-convergence certificate for either new output.

## Why the two operators differ

Let the four retained encoded sample colors and opacities be weighted equally. White is the unit RGB vector:

$$
\begin{aligned}
\langle X\rangle&=\frac{1}{4}\sum_{i=1}^{4}X_i,\\
\boldsymbol{C}_{\mathrm{sample}}&=\left\langle(1-\alpha)\boldsymbol{C}+\alpha\boldsymbol{1}\right\rangle,\\
\boldsymbol{C}_{\mathrm{pixel}}&=(1-\langle\alpha\rangle)\langle\boldsymbol{C}\rangle+\langle\alpha\rangle\boldsymbol{1},\\
\boldsymbol{C}_{\mathrm{sample}}-\boldsymbol{C}_{\mathrm{pixel}}
&=\langle\alpha\rangle\langle\boldsymbol{C}\rangle-\langle\alpha\boldsymbol{C}\rangle.
\end{aligned}
$$

Composition order therefore has no universal brightness-error advantage. The sampled backing and opacity interact. These formulas describe arithmetic before the retained float32 conversion and unchanged foreground chain; the saved exact arrays determine native comparisons.

## Original guard results

| Reference | Working E | Sample E | Working partial RMSE | Matched pixel partial | Sample partial |
| --- | ---: | ---: | ---: | ---: | ---: |
| Expanded A | 7.88349 | 7.96951 | 40.32683 | 78.48479 | 83.37568 |
| Expanded B | 6.14943 | 6.15269 | 26.08043 | 19.96709 | 27.59171 |
| Compact A | 20.53188 | 20.50771 | 23.81317 | 41.27345 | 39.25388 |
| Compact B | 19.68186 | 19.67120 | 21.07663 | 46.15160 | 44.29837 |

Both expanded samples fail glass, rim, held, aggregate and partial guards. Both compact samples improve aggregate, glass and rim but fail held and partial guards. All four SSIM, interior, foreground and exterior guards pass. All 16 expanded and 22 compact partial pixels per reference remain scored.

All four full comparison sheets were inspected. Both composition orders produce a single thin line, with only small visible differences at this scale. They do not repair cap brightness, body tone or misplaced source returns. Compact B still lacks the reference's structured bright rim and upper return.

| Reference | Reference / matched pixel control / sample overlay | Fixed crops at 2× |
| --- | --- | --- |
| Expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) |
| Expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) |
| Compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) |
| Compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) |

Crop rows retain the original declared crop order. Short labels identify the three panels; coordinates and named crop scores remain in each metrics record.

## Three-proposal review

| Proposal | Useful observation | Unresolved failure |
| --- | --- | --- |
| Original-contour pixel overlay88 | Single thin contour; small compact aggregate improvements | Three partial cohorts regress; expanded A body errors worsen. |
| Outward placement89 | Smaller failed partial errors; expanded B passes | Compact exterior worsens substantially; family fails. |
| Sample composition90 | Clear subrays remain exact; matched compact partial errors improve slightly | All original partial cohorts fail; expanded matched errors worsen. |

The [partial-pixel diagnosis](../agent-overlay-boundary-52/README.md) correctly identified composition as a question, not a proven cure. This matched experiment rejects that explanation as a sufficient fix. Neither composition order, outward placement nor constant white opacity is identified as the reference implementation.

No fourth width, opacity or placement is tried. The gallery retains overlay88 as the held visible test, with this comparison linked. Working20 and all accepted counts remain unchanged. Future work must distinguish outline strength from existing backing errors, preserving the same compact/expanded family and every original boundary pixel.

## Controls and accounting

The [protocol](protocol.json) began at 20:58:26.443 UTC, with checkpoint due at 21:03:26.443 and sealing due at 21:18:26.443. The exact four-image replay checkpoint passed at 20:58:59.189. [Results](result.json) record scientific completion. The parent outline deadline remains 21:33:02.674; no unused time transfers.

The checkpoint's profile-control label refers to the unchanged controls from overlay88, reused rather than numerically repeated. Native signed-distance membership subsequently matches every retained inside flag. Clear samples and unavailable pixels remain exact. Original input/mask identities and [first](first-hashes.json)/[last](last-hashes.json) scientific hashes agree.

| Work | Actual |
| --- | ---: |
| Cached material samples | 2,974,170 |
| Cached angular-environment evaluations | 1,487,085 |
| Native opacity coordinates | 2,243,200 |
| Exact identities | 4 |
| Candidate/control composites | 8 |
| Study mask points | 1,121,600 |
| Scores / metric Gaussians / erosions | 8 / 40 / 8 |
| Numerical payload bytes | 243,555,200 |
| Study target/source bitmap pixels | 16,588,800 |
| Comparison / crop sheets | 4 / 4 |

No new rays, heights, normals, Fresnel events, source queries, optical filters or fits ran. Study loads its original source bitmap as an input dependency, without sampling it. Earlier path/source proofs transfer only because original paths, kernel and inputs remain unchanged. Hypothetical scene and unassigned later power remain inherited limitations of the frozen body.
