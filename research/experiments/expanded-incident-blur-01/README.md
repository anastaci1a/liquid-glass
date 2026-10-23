# Expanded playback: incident softness refinement

Status: retain incident width 6.75 native pixels. The blur stage was evaluated, not skipped; neither new width is accepted.

## Isolated test

The selected H1 surface, rays, source, neutral response, AA2, foreground and masks stay frozen. The rejected inferred-profile candidate is not used as a weaker baseline.

Two fixed incident widths, 4.5 and 9 pixels, bracket the historical seed. There is no output material blur or location-dependent edge correction.

## Result

| Completed-image E | A | B |
| --- | ---: | ---: |
| Baseline 6.75 | 45.423695 | 18.219819 |
| Width 4.5 | 48.406075 | 20.203359 |
| Width 9 | 42.582142 | 16.747466 |

Width 4.5 worsens original body and foreground guards. Width 9 improves all body metrics, but both artwork guards regress. These are strict rejections, without a precision allowance.

The fixed neutral-text diagnostic also favors retaining the seed:

| Detail ratio | Value |
| --- | ---: |
| Reference | 0.139211 |
| Baseline 6.75 | 0.122079 |
| Width 4.5 | 0.232552 |
| Width 9 | 0.096455 |

The lower width is too sharp; the larger width erases more detail. A smaller aggregate error at width 9 does not justify hiding geometric mismatch with extra softness.

[All guards](result.json) and [detail measurements](detail-review.json) retain the original cohorts. The analysis filters measure texture; they are not additional rendering blur or a uniquely identified physical roughness.

## Correctness

The [source preflight](source-preflight.json) passes the full radius-27 incident kernel and four bilinear texels for both original domains. Smaller support follows by inclusion. No unknown source is filled.

Cached response, AA and foreground replay are pixel-exact at the seed. Four new native observations use 3,563,392 lens-source queries, zero new rays and zero fits.

[Protocol](protocol.json) retains the actual block, budgets and stop conditions. Geometry and feature-position defects remain open; colour is the next isolated stage.
