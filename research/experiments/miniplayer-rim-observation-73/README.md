# The missing rim contains different local defects

Fixed image-plane sections localize large reference brightness excesses, but some excesses are ordinary backing transitions rather than isolated rim peaks. A uniform outline correction would conflate those cases. No pose, surface, response, light, mask or source is fitted or changed.

| Location | Native position | Maximum reference excess in rim band | Reference peak above both side means |
| --- | --- | ---: | ---: |
| expanded A, upper-left corner | 347.83, 349.57 | 70.75 levels | 66.55 levels |
| expanded A, top center | 961.21, 323.54 | 25.31 | 29.73 |
| expanded B, top center | 961.21, 323.54 | 17.72 | 27.25 |
| compact A, lower-right corner | 1368.01, 736.29 | 77.19 | 62.95 |
| compact B, upper-left corner | 551.61, 609.14 | 88.43 | 6.94 |
| compact B, top center | 959.81, 583.11 | 53.11 | −0.01 |

Compact B's top-center excess is large, yet its rim-window maximum does not exceed the outer bright backing. Compact A has a distinct peak at the same shared contour location. This contrast warns against treating every missing bright pixel as the same reflected-light defect.

## Fixed observations

Each reference uses twelve sections: three straight top positions, three bottom positions, two axial tips and four diagonal corners. Positions come from the unchanged projected rounded rectangle. These two-dimensional silhouette normals are diagnostic directions, not substituted three-dimensional optical normals.

Signed distance spans −6 to +6 native pixels at quarter-pixel intervals. Negative distance points inward. Exact bilinear image sampling compares the frozen reference and working20 completion; it is not a new optical source query or a resampled candidate model.

The restricted rim window spans −1.5 to +1.5 pixels. Each side mean uses the outer three pixels of its half-section. Peaks at the restricted window boundary do not identify a true ridge location or width. Registration, source content, blur and geometry remain possible explanations.

$$
\begin{aligned}
\boldsymbol p(d)&=\boldsymbol p_0+d\boldsymbol n_{\mathrm{outline}},\\
\Delta Y(d)&=Y_{\mathrm{reference}}(d)-Y_{\mathrm{working}}(d),\\
P&=\max_{|d|\leq1.5}Y_{\mathrm{reference}}(d)
-\max\left(\overline Y_{[-6,-3]},\overline Y_{[3,6]}\right).
\end{aligned}
$$

Luminance uses the existing fixed RGB weights. These are eight-bit signal levels, not calibrated radiance. Positive prominence alone has no statistical significance threshold. None of the sampled bilinear footprints intersects the original foreground boxes; no guard or exclusion is edited.

## Inspect the sections

Black is the reference; orange is the current working reconstruction. All panels share a 0–255 vertical scale. The vertical guide marks the frozen projected outline. Horizontal distance is in native pixels.

| Reference | Twelve brightness sections |
| --- | --- |
| expanded A | [Profiles](expanded-a-profiles.png) |
| expanded B | [Profiles](expanded-b-profiles.png) |
| compact A | [Profiles](compact-a-profiles.png) |
| compact B | [Profiles](compact-b-profiles.png) |

[Complete sampled RGB, luminance and saved coverage](profiles.json) retain every location. [Results](result.json) give peak and residual summaries. Saved AA2 coverage is a numerical field, not measured physical alpha. Neither brightness peaks nor these sections establish incident-source correspondence or reflection/transmission identity.

## Clock and retention

The [protocol](protocol.json) starts at 15:21:08.964 UTC, with first checkpoint due 15:24:08.964 and hard end 15:31:08.964. The first reference checkpoint passes at 15:21:10.732. All forty-eight panels were inspected without changing or rerunning any model.

Usage is 2352 profile positions, 18816 RGB corner lookups and 9408 saved-coverage lookups. Four target images decode 8294400 pixels; retained numerical fields decode 22432000 bytes. These image-plane observations are separate from optical queries. Rays, heights, source queries, filters, model composites and fits are zero.

[First](first-hashes.json) and [last](last-hashes.json) hashes agree for all four cases, targets and working arrays. The section diagrams derive from those exact samples. Full-model guards and selection remain unchanged.

## Next discriminating bound

A constant white environment capped at the existing scene radiance would bound the direct-front signal attainable by any angular light distribution under that cap. This could distinguish inadequate direct-front reflectance from a poorly placed emitter. It would not bound unknown later paths or identify the reference environment.

Such an experiment needs its own declared clock and four-reference controls. No inferred per-pixel light, outline mask, target-derived halo or new geometric setting is introduced by this observation record.
