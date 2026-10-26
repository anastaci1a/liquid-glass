# Finalized shape and HSV comparison

The current shared pill shape is finalized. Keep its actual surfaces, registration and member lengths unchanged, even where reference alignment or outline scores disagree.

[Shape decision](../decisions/miniplayer-shape-finalized.json) preserves this constraint beyond the current test.

## Requested display changes

| Component | Requirement |
| --- | --- |
| Body grade | Adjust compression slightly so white maps to #FDFDFD at the grading stage. |
| Outline white | Maximum filter response maps white to #FDFDFD. |
| Outline color | Preserve preimage hue; use HSV value 253 out of 255. |
| Saturation choices | 60%, 70%, 80%, 90% and 100% of preimage HSV saturation. |
| Peak plateau | Multiply inward thickness by 1.5: two-thirds pixel becomes one pixel. |
| Other outline settings | Preserve the inward fade and opposing diagonal gaps. |
| Review | One pass; full comparisons and native crops with wipe sliders. No automatic selection. |

Compact A/B white regions are the requested diagnostic. Preimage color retains incident blur and refraction but excludes body grading. Equal brightness here explicitly means equal HSV value, not equal luminance.

Raw wording is retained locally outside Git. [Experiment](../experiments/miniplayer-hsv-options-102/README.md) records execution, white-patch measurements and limitations.
