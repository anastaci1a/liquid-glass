# Interface power: fixed response does not transfer unchanged

Applying actual primary transmission power makes all four bodies darker and worsens their original body and foreground guards. The visible front reflection remains, but does not compensate for the attenuation. This is a useful material-role negative, with no adopted replacement or coefficient adjustment.

## Fixed question

The [protocol](protocol.json) runs from 06:38:32.553 to 06:58:32.553 UTC. Four exact identity reconstructions passed at 06:39:33.293 before any changed-power composite. One setting then produced four observations. No second throughput, material fit, light strength or geometry was evaluated.

The [preceding comparison](../miniplayer-inverse-forward-18/README.md) added direct reflection to an effective calibrated primary image. This experiment tests the explicit lossless interface partition instead. The same actual rays supply transmission, direct reflection and the unassigned later branch.

$$
\begin{aligned}
L_{\mathrm{candidate}}&=T_{\mathrm{primary}}\,\mathcal D\!\left(C_{\mathrm{material}}\right)+4R_{\mathrm{front}}E(\boldsymbol\omega_{\mathrm{front}}),\\
T_{\mathrm{primary}}+R_{\mathrm{front}}+W_{\mathrm{later}}&=1.
\end{aligned}
$$

Here the display-response decoder maps the frozen encoded neutral material to an assumed linear incident signal. This interpretation is a model assumption, not measured scene radiance. The annular environment is unchanged and hypothetical. Later branch power remains recorded and unassigned.

## Four-reference result

| Reference | Selected E | Previous hybrid E | Explicit-power E |
| --- | ---: | ---: | ---: |
| Expanded A | 12.90785 | 10.51793 | 12.95030 |
| Expanded B | 8.57587 | 7.35216 | 9.16731 |
| Compact A | 27.32362 | 24.04648 | 28.82035 |
| Compact B | 26.35907 | 23.25206 | 28.18611 |

All four original glass, held, interior and total-error guards fail. Several foreground guards fail because their backing darkens, although original foreground parameters remain unchanged. Expanded A's frozen partial-boundary cohort still fails. Full guard records retain the other outcomes without dropping boundary pixels.

| Reference | Render | Measurements |
| --- | --- | --- |
| Expanded A | [Comparison](expanded-a-comparison.png) | [Metrics](expanded-a-metrics.json) |
| Expanded B | [Comparison](expanded-b-comparison.png) | [Metrics](expanded-b-metrics.json) |
| Compact A | [Comparison](compact-a-comparison.png) | [Metrics](compact-a-metrics.json) |
| Compact B | [Comparison](compact-b-comparison.png) | [Metrics](compact-b-metrics.json) |

## Isolation and accounting

Both lengths retain one shared glass system. Only major half-length varies. Actual source queries, incident blur, original masks, coverage, clear underlay, foreground, artwork and shadow zero remain unchanged. Fresh ray or source-support work is unnecessary because every contributing coordinate and kernel is retained from the preceding certified observation.

| Work | Actual |
| --- | ---: |
| Changed composites | 4 |
| Exact identity composites | 4 |
| Original mask constructor pixels | 1121600 |
| Score calls | 8 |
| Metric Gaussian operations / erosions | 40 / 8 |
| Cached annular-direction evaluations | 1487085 |
| Decoded payload bytes | 895555216 |
| Rays, heights, source queries, filters, Fresnel evaluations and fits | 0 |

The [checkpoint](checkpoint.json), [bindings](bindings.json), [ledger](ledger.json) and [result](result.json) separate cached identity proof from changed material observations. Identity reconstruction includes exact pre-foreground, completed image and scores. No identity rounding, clear contribution or original foreground order is replaced.

## Implication

The previous response is an effective calibration that already absorbs unknown optical and lighting effects. Multiplying it by interface transmission changes its meaning; unchanged coefficients cannot be assumed to transfer. The negative does not invalidate surface geometry or establish that interface attenuation should be omitted.

Keep the previous selected and held states distinct. A later isolated common-material calibration must declare its incident-versus-exit role and preserve all four references and original boundary guards. No per-reference coefficient, screen-space correction or compensating fit is included here.
