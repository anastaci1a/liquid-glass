# Pass 2: preserved white endpoint and stronger edge color

Status: active. The first pass improves compact but washes out expanded. This pass halves the shoulder correction and tests common tone changes that preserve the previous white endpoint.

Outline width stays at the first pass's two-pixel plateau and two-pixel fade. Chroma varies independently. The response protects a bright peak channel instead of forcing a minimum body luminance, which had neutralized yellow.

Dark guide colors receive a smooth neutral lift. This lift vanishes toward a unit peak, preserving strong bright color. White remains fixed; no channel clipping or target-specific hue adjustment is introduced.

Shadow shape stays fixed while opacity varies. Artwork scale varies around 94%, with its upward shift and absolute corner radius retained. Original masks and partial cohorts stay fixed.

All stages remain required except dispersion. The actual [cycle clock](cycle-clock.json) is earlier than the original latest ceiling; unused first-pass time is not added to this pass.

## Completed outcome

The complete candidate is rejected. Combined normalized score is 1.03739 against the previous proposal's 1.0. E is 15.87278 / 6.28478 for expanded and 17.09305 / 20.58498 for compact. All four full panels were inspected.

The peak-only response oversaturates the guide. At expanded A's fixed upper sample, the reference is RGB 255,238,119; the result is approximately 251,211,15. Compact develops an incorrect colored contour. No response from this pass is adopted.

Both geometry/source gates, four original identities, rim integration and all four independent final replays pass. Complete and pre-foreground arrays, scores and original guard decisions are exact. No optical or source operation was repeated by verification.

The color choice preserves the original white endpoint. The rim trial varies its exponent with width fixed; all three remain negative. Shadow opacity 0.23 and artwork scale 0.95 rank best among their fixed proposals. All local outcomes remain recorded.

A [training-mask audit](../selection-audit.json) reproduces every pass-two choice without held pixels. The original procedure still inspected full-mask scores and is exploratory, not held-out validation. Subsequent ranking uses training masks explicitly. The first pass's color choice differs under normalized training-only ranking; that record remains unchanged.

The next response should lift intermediate channels rather than multiplying source ratios alone. A bounded neutral lift can prevent a dark colored line while retaining brighter yellow. The underlying source hue remains a confound, not an identified physical material.
