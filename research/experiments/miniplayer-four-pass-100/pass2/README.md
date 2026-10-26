# Pass 2: preserved white endpoint and stronger edge color

Status: active. The first pass improves compact but washes out expanded. This pass halves the shoulder correction and tests common tone changes that preserve the previous white endpoint.

Outline width stays at the first pass's two-pixel plateau and two-pixel fade. Chroma varies independently. The response protects a bright peak channel instead of forcing a minimum body luminance, which had neutralized yellow.

Dark guide colors receive a smooth neutral lift. This lift vanishes toward a unit peak, preserving strong bright color. White remains fixed; no channel clipping or target-specific hue adjustment is introduced.

Shadow shape stays fixed while opacity varies. Artwork scale varies around 94%, with its upward shift and absolute corner radius retained. Original masks and partial cohorts stay fixed.

All stages remain required except dispersion. The actual [cycle clock](cycle-clock.json) is earlier than the original latest ceiling; unused first-pass time is not added to this pass.
