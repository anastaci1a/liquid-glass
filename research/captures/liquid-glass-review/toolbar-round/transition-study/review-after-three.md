# Model review: three transition/normal-profile families, no qualifier

Authorized by lead06:14UTC. Baseline is the independently accepted .10 crown/1.25px blur plus generated shadow: E6.998512744608, glass6.044535160065, rim8.832458496094, exterior11.469442019668. Source/registration, material, crown, ordinary blur, shadow and frozen masks remain unchanged. This study does not count a pass, change the incumbent, or modify primary source.

## Numerical results — native4×4, original protocol

| Substantive family | Native E | Glass | Rim | Exterior | E reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| Shared W exponent/band | 6.992219076187 | 6.038764476776 | 8.825050354004 | 11.469438883454 | 0.089929% |
| Joint W plus normal-profile coefficients2,3,4 | 6.967956807821 | 6.015742301941 | 8.797729492188 | 11.469491213375 | 0.436606% |
| Added coupled potential difference | 6.995428678293 | 6.036259651184 | 8.837518692017 | 11.469426403501 | 0.044067% |

All three FAIL. Required next E is at most6.963520180885. Family2 additionally regresses the fixed exterior (about4.92e-5); do not round that away or refit shadow under the fixed-shadow instruction. Retain the original .10/1.25+shadow incumbent. Foreground is unchanged/primary-owned.

## Models and declared freedoms

1. `W(d)=(1-u)^m(1+m*u)`, u=clamp(d/b,0,1), replaces only the tangential profile of the inherited empirical tensor field. Bounds m3–6/b.30–.55; tangent amplitude fixed.
2. Same profile plus additive changes to the existing normal B-spline coefficients2,3,4, each within±.02 normalized displacement. Same fixed shape, material and source; no per-letter/crop residual. Chosen deltas[.01291946,−.00247391,.01432364], m6/b.548419. Current normal/tangent interaction helps but does not reach the new gate in this bounded study.
3. Keep the empirical baseline and add `−grad(.5*x²*(Knew(d)−Kold(d)))`, K=tangent*W. Includes the normal term derived from that same potential and uses the exact derivative of the crowned implicit boundary coordinate. Zero change recovers the baseline. Bounds m4–6/b.30–.55 give at leastC2 added map at inner support; the total inherited field remains empirical/nonintegrable. This is not ray tracing through an identified Apple solid.

`mathematical-checks.json`: added coupled perturbation finite-difference curl max5.75e-9; baseline tensor curl max1.5066, so no false integrability claim. Native zero/base recovery is pixel-exact for BOTH empirical and coupled families before fitting. Source/material/shape/shadow/blur were not reestimated.

## Optimization limits and evidence

Training uses full native-grid positions with1×1 raster samples, same source and ordinary blur, weighted objective .7*glassMSE+.3*rimMSE. It is explicitly an approximation; full4×4 native rendering with all frozen masks owns every table score and gate. Lower-resolution source images or altered masks were NOT used. Rejected training gains cannot qualify a pass.

Each bounded Powell run reached its evaluation budget (91/181/91 objective calls including separately recorded initial evaluation), not a convergence certificate. Every vector/objective is saved in study.json. Family1/2 reach the upper exponent/band neighborhood, so this is NOT evidence of global exhaustion or no possible better model. The honest conclusion is no qualifying improvement in these bounded families; a wider search requires a new justified model review, not a claim that these runs converged.

Native glass and rim improve together in family2, supporting further investigation of the normal/tangential relation, but the improvement is too small and the exterior guard fails. Extra target-specific colors, changing the source, refitting shadow or silently skipping a threshold are not justified by that proximity. Preserve negative evidence rather than forcing a counted checkpoint.

Files: `study.json` all vectors, scores, gates and optimizer limitations; `family-1..3/recipe.json`, `scores.json`, `material.npy`, `alpha.npy`, `clean-preview.png`; `result.json` explicitly any_numerical_qualifier=false/count0; `toolbar_transition.py` snapshot; `checks.py`, `mathematical-checks.json`, `study.py` exact procedures. Existing container scratch `/tmp/agent-toolbar-code`, inputs `/tmp/agent-toolbar-run`, outputs `/tmp/agent-toolbar-transition`; env OPENBLAS_NUM_THREADS=1/PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps.

Next: lead reviews these three families and decides whether a wider normal/tangential model or another observed constraint is justified. Agent has stopped new fits at this review boundary and continues reciprocal monitoring. First accepted revision publication remains primary-owned; no commit/push or next accepted pass by agent.

Model snapshot SHA-256 `d46aeae0ff038d7b15252de342acfd3165786210c10989103ce4224cd15fb45d`.
