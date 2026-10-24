# Dispersion assessment of the selected family

**Dispersion remains unidentified, not absent.** Fixed source/target cohorts do not establish reproducible channel-dependent feature displacement. No spectral model is added.

| Evidence | Record |
| --- | --- |
| Fixed crops, observations and limits | [Protocol](protocol.json) |
| Source color, residuals and original bindings | [Assessment](result.json) |

| Central body cohort | Pixels | Target chroma RMSE | Retained source chroma RMSE | Residual chroma RMSE |
| --- | ---: | ---: | ---: | ---: |
| Expanded A | 9,000 | 47.880 | 91.706 | 6.887 |
| Expanded B | 9,000 | 0 | 0.047 | 0.028 |
| Compact A | 2,300 | 18.888 | 31.621 | 0.884 |
| Compact B | 2,300 | 33.861 | 56.362 | 0.909 |

Chroma removes each RGB mean and reports eight-bit-level RMS; it is not a perceptual color-space distance. The source diagnostic uses actual retained subray samples. It does not assume that target features have known source correspondences.

Expanded B's central target cohort is exactly achromatic. Its signed RGB residual is approximately `[2.524,2.495,2.526]`, predominantly a luminance mismatch. Compact's central residuals are also largely neutral, while its incident source is colored.

These facts do not bound spectral effects everywhere. Refraction geometry, filtering, source reconstruction, response and missing illumination remain confounds. A useful spectral test needs an independently supported feature and repeatable channel displacement distinguishable from channel PSF and registration.

Original glass masks and full coverage define diagnostic cohorts only. No scoring guard changes. These numerical results characterize the selected canonical family, not a transferred verdict for the held two-surface variants.

The stage uses 538,464 saved pixel observations and decodes 144,686,400 array bytes. Rays, heights, source queries, filters, composites and fits are zero. The scalar index remains an approximation; ordinary blur does not prove dispersion absent.
