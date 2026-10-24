# Anchor-matched linear scattering is rejected

One shared neutral scattering mixture fails the protected working-family guards on all four references. Expanded A becomes visibly washed out. Matching material white and middle gray does not preserve colored-background response. No alternative mixture, backtrack or target fit runs; working20 remains selected.

| Reference | Working E | Candidate E | Protected partial RMSE: working → candidate |
| --- | ---: | ---: | ---: |
| expanded A | 7.883487 | 17.772709 | 40.326828 → 48.686390 |
| expanded B | 6.149430 | 6.894943 | 26.080431 → 25.974951 |
| compact A | 20.531876 | 20.880758 | 23.813168 → 22.266167 |
| compact B | 19.681863 | 19.776415 | 21.076626 → 23.416597 |

All four aggregate errors worsen. Some partial-boundary and rim measurements improve, but they cannot override the other original body, SSIM and foreground failures. Clear pixels replay exactly and all actual clipping counts are zero. Missing thin rim illumination and wrong feature placement remain separate defects.

## One derived material hypothesis

The [shared response](../../../reconstruction/neutral_scattering.py) mixes normalized incident linear light with assumed neutral white illumination. Its parameters come only from the existing encoded material's white and middle-gray anchors. No target objective is used.

$$
\begin{aligned}
W&=\mathcal D(g_0+b_0),\\
M&=\mathcal D\left(\frac{g_0}{2}+b_0\right),\\
\tau&=\frac{1-\frac{M}{W}}{1-\mathcal D\left(\frac{1}{2}\right)},\\
\boldsymbol L_{\mathrm{material}}
&=W\left[\tau\mathcal D(\boldsymbol S)+(1-\tau)\boldsymbol 1\right].
\end{aligned}
$$

Here the decoder is the existing sRGB transfer function. Derived transmission is 0.6888191624 and linear white level is 0.8818141869. The two material anchors agree within floating arithmetic under multiple primary powers and unchanged additive light signals.

The assumed white-scattered contribution raises dark channels substantially. In expanded A, body RGB RMSE rises from 2.16586 to 17.54278 while signed luminance stays near zero. This is a chromatic response failure, not evidence that geometry, PSF or missing reflection is fixed. It does not disprove scattering generally.

## Frozen stages and claims

Actual18 surface paths, primary Fresnel power, source samples and direct-front light remain unchanged. Incident sigma stays 6.75 native pixels with finite radius 21 before refraction. The existing encoded source-filter domain is preserved; changing material response does not also change filter arithmetic or camera integration.

Compact and expanded share every material and optical value; only major length differs. Original masks, registration, sources, artwork and vectors remain fixed. Unknown later reflected power remains unassigned. The neutral white illumination is an explicit unobserved assumption, not measured radiance or identified microscopic roughness.

## Inspectable evidence

| Reference | Whole reference / working / candidate | Original-coordinate crops at 2× |
| --- | --- | --- |
| expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) |
| expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) |
| compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) |
| compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) |

[Results](result.json) retain original/current guards, fixed crop regressions and exact recipes. Pre-foreground, completed and coverage arrays are retained for all four candidates. All four whole comparisons were inspected; no claim of a separately quantified perceptual study follows.

## Controls, clock and accounting

The [protocol](protocol.json) starts at 15:02:47.315 UTC, with checkpoint due 15:07:47.315 and hard end 15:22:47.315. All four pre-foreground and completed identities pass at 15:04:11.743 before any candidate. Science finishes at the timestamp in [results](result.json); the five-minute checkpoint cap is met.

Usage is fifteen algebraic checks, four identity composites, four candidates, four score calls, twenty SSIM metric Gaussians and four metric erosions. Cached native sample inspection is 4486400, environment lookups 1487085 and original mask construction 1121600 pixels. No new ray, source query, optical field, filter or fit runs.

[First](first-hashes.json) and [last](last-hashes.json) hashes match for retained input arrays, original source/target/known PNGs, cases, assets, masks and implementation dependencies. Source-proof transfer covers unchanged queries and finite kernels only; conditional mosaics are not photographic truth.

This closes one new response-basis experiment after the earlier pass review. It does not reset rejected color65 or reopen its solver. The broader research sequence remains active; the next question must address a distinct material or geometric assumption rather than sweep this failed mixture.
