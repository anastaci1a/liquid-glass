# Miniplayer refinement observations

Status: active specification for [four complete passes](../experiments/miniplayer-four-pass-100/README.md).

| Region | Observation or requested starting hypothesis |
| --- | --- |
| Expanded left tip | Approximately two visible native pixel blocks too far inward. |
| Expanded right tip | Approximately one pixel block too far inward. |
| Diagonal cap shoulders | Approximately two pixel blocks too far outward on both ends. |
| Outline | Saturated peak plateau about 2–3 pixels, followed by a further 2–3-pixel smooth inward fade. |
| Artwork | Start near 94% centered scale, slightly upward; preserve and modestly increase absolute corner rounding. |
| Peripheral transport | Slightly stronger refraction at far caps. |
| Shadow | Same row below the body: center approximately #DDDDDD, beneath apexes #F6F6F6, crop edges #FCFCFC. |

Pixel estimates refer to visible blocks in native-detail comparisons. Treat them as approximate native measurements, normalize by body height and bracket uncertainty. They are not independently registered silhouette measurements.

Retain blur in the pre-grade refracted guide used by the outline. Brighten while preserving strong color, with a short maximum-strength plateau and a smooth fade. A white input remains white.

Apply the revision to expanded and compact together. Only major length differs in the glass model. Artwork and original foreground metrics remain separate from glass error.

Four full passes share ten hours. Dispersion is excluded. Overall visual and category-score improvement may be promoted with explicit local-regression disclosure; physical and source-validity requirements remain mandatory.

## Four-pass disposition

The complete third pass is selected. [All comparisons and failures](../../guide/miniplayer-four-pass.md) remain public. Raw notes stay local and untracked.

| Feedback | Outcome |
| --- | --- |
| Tips outward, diagonal shoulders inward | Shared smooth support shape separates those changes; exact silhouette remains uncertain. |
| Slightly stronger far refraction | Actual front/back heights increase two percent; normals are not independently adjusted. |
| Slightly less blur | Incident sigma is `6.37875`, below the old working `6.75`; filtering remains before refraction. |
| Saturated colored edge and plateau | Blurred pre-grade guide, soft per-channel response and two-pixel plateau; wider final trial is held. |
| Smaller, higher artwork | Shared `0.95` scale, three-pixel upward shift, eighteen-pixel corner radius. |
| Localized downward shadow | Exterior-only anisotropic field; fixed outward samples retain conditional-background limitations. |
| Four complete passes, no dispersion | Completed and independently verified; all four full results remain available. |
