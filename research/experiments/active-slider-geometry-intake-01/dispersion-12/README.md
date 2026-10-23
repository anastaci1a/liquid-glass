# Dispersion identification remains limited

The saved evidence does not identify a shared physical index-dispersion direction. This does not establish that dispersion is absent. No spectral rays, image resampling, filters, composites or fits were executed.

## Fixed observations

The original upper-left, lower-left, right-rim and center rectangles remain fixed. Statistics use their intersection with the unchanged glass mask. The full measurements retain RGB, signed channel differences, luminance, chroma and adjacent spatial differences.

| Case and cohort | Target luminance gradient RMS | Current luminance gradient RMS | Target chroma gradient RMS | Current chroma gradient RMS |
| --- | ---: | ---: | ---: | ---: |
| A upper-left | 5.197 | 0.128 | 3.362 | 0.063 |
| A lower-left | 4.025 | 0.000 | 2.865 | 0.000 |
| A right-rim | 3.953 | 0.310 | 2.225 | 0.190 |
| B upper-left | 3.135 | 0.429 | 0.473 | 0.034 |
| B lower-left | 2.229 | 0.345 | 0.761 | 0.027 |
| B right-rim | 2.863 | 0.000 | 0.825 | 0.000 |

Values use encoded 0–255 levels and native adjacent differences. They describe image variation, not a point-spread function or a channel displacement. The right-rim rectangle contains the cyan-interest region; it is not a newly fitted cyan mask.

## Interpretation

A's retained lower-left incident samples are essentially constant green, with mean RGB near 121, 192, 132. Its current image therefore lacks both reference luminance structure and chromatic structure. Missing reference returns remain a geometric and illumination ambiguity before channel offsets can be assigned a source identity.

B has weaker chromatic variation, but it is not an otherwise identical neutral-source control. Its pose, size and transition state differ. The hidden source is modeled, with observed confidence zero. Unknown camera encoding and illumination also prevent treating its smaller chroma residual as an isolated dispersion measurement.

The foreground manifests are empty, so glyph antialiasing is not an explanation for these cohorts. Native antialiasing remains separate from the incident Gaussian. Ordinary blur changes intensity transitions without selecting independent channel paths; these saved gradients do not distinguish that broadening from uncertain incident edge structure.

The accepted common tone changes all channels equally. It cannot establish the cause of localized chromatic rims. Neither a colorful target edge nor a reduced RGB error identifies a wavelength-dependent refractive index.

## Decision and next evidence

Keep the accepted tone and original incident widths. Do not add a spectral operator or arbitrary channel coefficients. Dispersion is assessed but remains unidentified, rather than skipped or verified absent.

A discriminating observation needs independently supported incident texture with identifiable neutral edges under a matched material and transition state. A specified illumination and spectral-background model could also constrain the question. These are evidence requirements, not authority for a new source search.

See the [declared protocol](protocol.json), [saved measurements](result.json) and [analysis script](analyze.py). No new optical or material hypothesis was executed.
