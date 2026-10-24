# Linear-light incident filtering does not transfer across the family

At the unchanged blur width, linear-light averaging improves compact aggregate errors but worsens both expanded references. Compact B passes every current guard; compact A still fails SSIM and the artist guard. The shared family does not qualify. No member-specific filter or tone is introduced; working20 remains selected.

| Reference | Working E | Linear-filter E | Protected partial RMSE: working → candidate |
| --- | ---: | ---: | ---: |
| expanded A | 7.883487 | 10.420332 | 40.326828 → 44.307789 |
| expanded B | 6.149430 | 9.081162 | 26.080431 → 26.358114 |
| compact A | 20.531876 | 18.747719 | 23.813168 → 23.810879 |
| compact B | 19.681863 | 18.487713 | 21.076626 → 21.076138 |

Both expanded references fail body, SSIM, boundary and several foreground guards. Compact A improves all four fixed crop RGB errors but still fails its original guards. Compact B also improves the fixed crops. These local gains are retained without selecting a different compact material.

## Exactly one arithmetic change

The Gaussian and exact bilinear interpolation average decoded linear signal, followed by encoding before the unchanged empirical material response:

$$
\overline{\boldsymbol S}_{\mathrm{linear}}(\boldsymbol q)
=\mathcal E\left[
\mathcal B_{\boldsymbol q}\left(G_{\sigma}*\mathcal D(\boldsymbol S)\right)
\right].
$$

The decoder and encoder use the existing sRGB transfer functions. Bilinear interpolation remains exact. The source field retains float32 storage and Gaussian arithmetic; coordinate interpolation retains its existing precision. This is a signal-domain hypothesis, not calibrated reference radiometry or a measured physical PSF.

Sigma is exactly 6.75 native pixels and finite radius is 21. Blur stays before refraction. Geometry, actual primary interface power, direct-front scene, encoded gain/bias, masks, sources, foreground, AA2 and zero shadow remain fixed. The rejected scattering response71 is not used.

All four full comparisons were inspected. Expanded B becomes too light through its central lettering, while compact cap regions improve modestly. Neither operation corrects the thin bright rim or wrong return placement. The existing empirical tone was calibrated in another signal domain; the result does not show that real optical averaging occurs in encoded RGB.

## Inspectable evidence

| Reference | Whole reference / working / candidate | Original-coordinate crops at 2× |
| --- | --- | --- |
| expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) |
| expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) |
| compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) |
| compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) |

[Results](result.json) retain every original/current guard and fixed crop measurement. Pre-foreground, completed and coverage arrays are archived. Changed source fields and full sampled arrays are reproducible from retained inputs, exact coordinates and filter recipe; they are not separately archived.

## Source support, clock and accounting

The [protocol](protocol.json) starts at 15:09:23.225 UTC and ends at 15:29:23.225. The [checkpoint](checkpoint.json) passes at 15:09:32.379. Four baseline pre-foreground/completed identities and all four complete finite-kernel support gates pass before any changed field or RGB query.

Every lens ray audits all four bilinear texels after full 43×43 known-mask erosion. Original scored misses use unchanged clear coordinates and samples, retaining their earlier proof. No undefined source is filled or sampled. Conditional mosaic availability remains distinct from photographic truth.

Usage is 2974170 lens audits and RGB queries, 11896680 known-mask lookups, four incident fields, eight erosions, four identities and four candidates. Four score calls use twenty SSIM Gaussians and four metric erosions. Original mask construction is 1121600 pixels. No new ray, height, clear query or fit runs.

[First](first-hashes.json) and [last](last-hashes.json) input/code bindings match. All clipping counts are zero and clear pixels remain exact. Reused plotting code initially kept incorrect scattering captions; [caption-only correction](caption-correction.json) verifies every noncaption pixel unchanged. Original sheets and the failed caption-bound assertion remain preserved, without any scientific rerun.

## Response-basis review

[Fixed-white encoded contrast65](../miniplayer-white-fixed-colour-65/README.md), [anchor-matched scattering71](../miniplayer-neutral-scattering-71/README.md) and this filter-domain test expose different failures. None supplies a shared replacement. No fourth response setting or automatic optimizer follows. Missing rim illumination and cap-to-body feature correspondence require their own discriminating observation.
