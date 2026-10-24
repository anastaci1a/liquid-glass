# Dispersion remains unidentified

The current shallow42 saved samples do not establish reproducible channel-dependent feature displacement. Colored source content, geometry, missing illumination, response and incident blur remain confounds. No spectral model is added; this is not a finding that dispersion is absent.

The [protocol](protocol.json) freezes four original crops per reference. [Assessment](result.json) retains actual source chroma, target chroma and signed residual RGB. Full-coverage original glass cohorts are diagnostic only; no guard changes. Shadow50 leaves these pixels exact, so that underlay component does not alter this assessment.

| Central body | Target chroma | Source chroma | Residual chroma |
| --- | ---: | ---: | ---: |
| expanded A | 47.880 | 91.706 | 1.718 |
| expanded B | 0.000 | 0.047 | 0.025 |
| compact A | 18.888 | 31.621 | 2.091 |
| compact B | 33.861 | 56.362 | 3.704 |

Chroma is RGB minus its channel mean, reported as eight-bit RMS. It is not a measured channel displacement or perceptual color distance. A useful spectral experiment requires an independently supported feature and repeatable channel offsets distinguishable from registration and channel PSF.

The assessment uses 538464 saved pixel observations and 144686400 decoded array bytes. No ray, height, source query, filter, composite or fit runs. Thin-boundary integration remains unresolved; the central diagnostic cannot certify edge behavior.
