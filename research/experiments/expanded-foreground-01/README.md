# Expanded playback: transport-symbol material

Status: no strict paired qualifier. Original opacity, vector paths, placement and inline ink colours remain unchanged.

## Isolated proposal

One common opacity applies to the existing play and forward vectors across both references. Artist, title and artwork retain their separate material roles. Geometry, source blur, cached body and all original masks stay fixed.

One closed-form fit uses opaque SVG cores and alternating fixed 8-pixel blocks. The other blocks are advisory held cores. There is no bitmap matte, font search, weight adjustment or body fit.

The proposed common opacity is 0.9984231811. Full and one predetermined half-step were evaluated. The full step worsens both transport-symbol guards in both references. The half-step passes A but worsens B forward. Neither is accepted.

[Results](result.json) retain all original guards, held-core errors and complete native arrays. Zero-response foreground replay is pixel-exact. There are no new rays or source queries.

This tests material opacity only. Shape/weight correspondence remains uncertain; this negative does not establish that the original symbol shapes are exact. A future shape proposal needs independent original-vector evidence rather than a fitted target matte.
