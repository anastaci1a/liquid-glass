# Pass3 complete cycle

Own arithmetic replay and source-coordinate spot checks pass. Original masks and partial cohorts remain fixed. This is a working comparison, not a full-fidelity acceptance. Dispersion is excluded.

| Stage | Recorded decision |
| --- | --- |
| Geometry / registration | native-pass3-corrected; corrected common center and independent position arrays |
| blur | blur6.6825; original failures retained |
| color | color0; original failures retained |
| outline | outline0; original failures retained |
| shadow | shadow1; original failures retained |
| artwork | artwork0; original failures retained |
| Own verification | Four completed composites, metrics, source-coordinate parity and exact angular-gap contribution |

| Reference | E | SSIM | Partial RMSE | Failed starting100 guards |
| --- | ---: | ---: | ---: | --- |
| expanded A | 10.33814 | 0.975356 | 40.55716 | interior, jupiter.jpg, title.svg |
| expanded B | 5.16582 | 0.982541 | 13.56488 | interior, jupiter.jpg, play.svg |
| compact A | 14.65728 | 0.967018 | 21.82698 | glass, rim, held, E, exterior, title.svg, forward.svg |
| compact B | 14.34145 | 0.965804 | 21.38666 | glass, rim, held, interior, E, forward.svg |

Fixed expanded upper/lower peak training selects the outline; these training pixels exclude held samples. Compact uses identical settings. All other stage rankings use equal-reference training cohorts, excluding held pixels. Original guards remain evaluation evidence.

[Recipe](final-recipe.json), [all stage scores](all-metrics.json), [source gates](blur-source-FIRST.json), [integration](integration.json), [own verification](verification.json), [fixed diagnostics](fixed-diagnostics.json) and [ledger](ledger.json) retain the detailed evidence.

Outline integration reports a successive-order difference, not a certified global error bound. Exterior shadow affects clear subrays only. The source mosaic and annular scene remain conditional; later reflected power is unassigned.
