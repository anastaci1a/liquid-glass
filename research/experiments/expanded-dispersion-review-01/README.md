# Expanded playback: dispersion identification review

Status: spectral transport is not identified. The stage is assessed, not omitted; no spectral renderer or channel-specific coefficient is added.

## Current residual

Saved selected-model arrays give:

| Original glass | A | B |
| --- | ---: | ---: |
| RGB RMSE | 38.07742 | 15.10626 |
| Neutral residual RMS | 33.53857 | 15.10333 |
| Chromatic residual RMS | 18.02926 | 0.29758 |
| Chromatic squared-error fraction | 22.419% | 0.0388% |

The [fixed text rectangle](result.json) gives the same qualitative split. It is the complete rectangle intersected with original glass, not the smaller eroded diagnostic cohort used in earlier reports.

A has coloured incident content and wrong return geometry. B is predominantly neutral, with weak nonzero chroma retained. Neither observation uniquely measures wavelength-dependent refraction. Missing illumination, source uncertainty, video sampling and camera response remain confounds.

## Decomposition

Neutral and chromatic residuals use an orthogonal RGB decomposition:

$$
\mathbf{e}=\mathbf{C}-\mathbf{T},\qquad
\mathbf{e}_{\mathrm{neutral}}=\frac{e_R+e_G+e_B}{3}\begin{bmatrix}1\\1\\1\end{bmatrix},\qquad
\mathbf{e}_{\mathrm{chroma}}=\mathbf{e}-\mathbf{e}_{\mathrm{neutral}}.
$$

The squared RGB error equals the sum of these squared components. This is a diagnostic decomposition, not a physical spectrum or a claim that all chromatic error is dispersion.

The earlier [target-only observations](../../captures/dark-glass-lab/extended/agent-pipeline-01/dispersion/identification.json) remain useful. Their old material residuals are not substituted for current measurements.

No new rays, RGB queries, filters, images or fits were run. Ordinary incident blur stays neutral and separate from spectral transport. Absence of physical dispersion is not established.
