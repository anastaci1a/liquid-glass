# Spectral-surface hypothesis (tested, not adopted)

The visible cyan/yellow fringes are poorly reproduced by the incumbent. A color-channel displacement proportional to the existing empirical map gave less than the required gain. This separate hypothesis changes the index of the SAME physical height surface by wavelength; it does not paint a rainbow along its outline.

- Three representative wavelengths: R650, G550, B450nm. RGB channels are broad sensor/display responses, so treating them as monochromatic bands is an explicit approximation, not spectral radiometry.
- n(lambda)=n550+delta*(lambda^-2-550^-2)/(450^-2-550^-2). This is a two-term Cauchy family centered on n550=1.5; delta in[0,.03] is a bounded proposed blue/green index difference, not an Apple measurement or a recovered glass composition.
- Recompute Snell exit and background intersection independently for each band using one shared height/gradient. R/G/B indices at the upper proposed delta are1.48274556/1.5/1.53. Check the subcritical slope against each index; never clip invalid rays into range.
- Ordinary source/output Gaussian blur remains distinct from dispersion. The previously accepted directional shifted-ray mixture is retained as a separately labeled empirical effect. Its R/B branches use their corresponding band index, rather than silently reverting to monochromatic rays.
- Zero delta takes the identical monochromatic code path. Initial field checks are bit-exact at zero, unchanged lighting basis, ordered indices, finite valid band rays. These do not establish visual accuracy, global source support or a physical model for the inherited reflection/material layers.
- Model and tests: switch_cauchy_surface.py, check-switch-cauchy-surface.py; cauchy-invariants.json. An initial method-name collision with Study.indices was caught before output, corrected to band_indices; no scored result depended on the failing version.
- Six exact-native steps completed. Delta settled at0.00584130517; E14.37681488/15.66926202, still1.5854%/1.4294% worse than revision5. No pass, public recipe or count changed. Final evidence: cauchy-native-settlement.json.
- Frozen-material operator isolation (color-operator-review.json) worsens both sampled objectives when either ordinary Gaussian or the directional mixture is removed. This shows dependence of this fitted comparator on those operators; it does not prove Apple uses them. The5000point/16tap objective differs from native scoring.
- Local saved-form analysis finds dispersion partly independent of material coefficients, but insufficient for acceptance; relaxing the exterior constraint diagnostically offers only a tiny predicted gain. Larger-gap tests preserving first-order optical power also show negligible change. Stop further index/gap sweeps here.

## Sources and limits

[PBRT4, Specular Reflection and Transmission](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission) describes wavelength-dependent index and resulting dispersed directions. [SCHOTT TIE29](https://media.schott.com/api/public/content/8afd09ccdf4243e890df9f875b1b5579?v=ce5367ec) uses wavelength-dependent optical-glass measurements and the Sellmeier equation. Our reduced two-term curve is a declared low-dimensional experimental approximation, not that manufacturer's measured model. Neither reference establishes Apple's implementation.
