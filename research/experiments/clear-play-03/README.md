# Clear play: incident softness convention

Status: source-first model selected; no numerical improvement or outline fix claimed. The bounded review closed early after reusing completed evidence.

## Selection

The primary model now uses incident Gaussian width 1.7 native pixels before the unchanged G05 geometric sampling. Output material filtering is zero; the historical foreground nuisance remains unchanged.

The previous output width is preserved in the [historical comparison](historical-output-comparison.png). This selection follows the operation-order contract, not a waived numerical guard.

| Measurement | Historical output blur | Selected incident blur |
| --- | ---: | ---: |
| Center bandpass RMS | 1.122451 | 1.122313 |
| Glass RMSE | 12.569344 | 12.856474 |
| Rim RMSE | 13.872038 | 14.391801 |
| Outer-rim MAE | 16.897352 | 16.467651 |
| Foreground MSE | 98.166603 | 98.166603 |

Compressed edge texture is sharper. Thin bright rim, crossing placement and lower-left illumination remain wrong. Preserve all [original scores](../clear-play-02/result.json).

The [source proof](../clear-play-02/source-proof.json) and [independent replay](../clear-play-02/verification.json) are reused unchanged. No new ray, source query, optical image or fit was needed.

## Outline limitation

The [saved-path audit](path-audit.json) checks 64 retained starts. Twenty-one still exceed residual-power tolerance; the original audit also found unsupported secondary destinations.

Front reflected illumination is unobserved. Conditional energy fractions cannot determine encoded RGB brightness or justify a target-colored highlight. The outline is blocked, not absent or complete.

A next outline experiment needs scene-supported illumination and complete valid paths from the same optical surface. Independent normal tweaks, residual warps and painted halos remain prohibited.

## Handoff

[Protocol](protocol.json), [selection receipt](selection.json) and the [current sequence](../../method/refinement-sequence.md) retain budgets and scope. Next is expanded Music playback refraction against its own evidence and historical incident softness.
