# One next toolbar hypothesis — rejected bounded study

Authorized by lead06:04UTC. Experiment7 adds one normalized analytic phase tail to the fixed pending .10/1.25 recipe. The pending first candidate, its source, material, shape, ordinary blur, generated shadow, registration and masks remain unchanged. No accepted pass counted; no commits or shared-code edits.

All12 nonzero proposals fail the frozen numerical gates. The best nonzero result, strength−.005/band1.0, is WORSE than the pending baseline:

| Metric | Pending first candidate | Best nonzero phase-tail trial |
| --- | ---: | ---: |
| E | 6.998512744608 | 7.051264928016 |
| Glass RMSE | 6.044535160065 | 6.109173774719 |
| Rim RMSE | 8.832458496094 | 8.868471145630 |
| Fixed exterior RMSE | 11.469442019668 | 11.469444072748 |

Required next E maximum is6.963520180885. Reject the trial; retain the original pending first candidate, not the best nonzero trial. Do not round away its small exterior regression or count an experiment as a success.

## Mathematical scope

`model-notes.txt` gives the full field. Added potential `Psi=.5*k*x²*H(d/b)` uses `H=64u³(1-u)³` within0<u<1 and zero elsewhere. The inverse-map perturbation is `−grad(Psi)`, including the normal term required by the same scalar. The exact gradient of the crowned implicit boundary coordinate is used; it is not assumed to equal the negative unit normal. No word/caption detection, positional residual painting or target color enters the field.

Phase isC2 and the added map isC1 at its support endpoints; no stronger endpoint regularity is claimed. The ADDED map has a symmetric Jacobian (finite-difference curl max2.85e-10); the inherited tensor field remains empirical and is NOT made globally integrable by this addition. There is no recovered physical solid or Apple-model claim.

Zero strength exactly reproduces the frozen pending material pixels (max absolute difference0), so the observed regressions come from the tested field, not a source/renderer reset. Bands.65/.8/1.0 and strengths±.005/±.01 were bounded global normalized proposals. `study.json` preserves every row; `checks.json`, `best-score.json` and `result.json` record evidence and rejection. `best-*` means best within rejected nonzero trials, NOT a new incumbent or accepted state.

The fixed-material compact-potential tail alone does not explain the desired d-stroke stretching without worsening the rest of the glass. Normal coupling required by the chosen phase changes other features too. This rules out the tested neighborhood, not every tangential/geometric model. No further hypothesis or freedom is silently added after this rejection.

## Evidence and handoff

- Separate worktree adds only `toolbar_phase_tail.py` alongside earlier untracked toolbar module/tests. Frozen snapshot of this new module is also in this directory. It imports the pending frozen model, overriding only analytic mapping while repeating the same raster/material/filter pipeline.
- `rejected-d-stroke-4x.png`: Apple native detail enlarged, pending baseline fresh4x, rejected trial fresh4x. Corrected crop[960,450,1120,550] is wholly inside the current footprint; foreground overlap is labeled unscored, no reference glyph is pasted into glass panels. Crop remains advisory.
- `study.py`, `crop.py` reproduce the bounded native and4x evidence. Container scripts `/tmp/agent-toolbar-tangent-study.py` and `/tmp/agent-toolbar-phase-crop.py`; existing env OPENBLAS_NUM_THREADS=1, PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps. Code snapshot `/tmp/agent-toolbar-code`; inputs read-only from `/tmp/agent-toolbar-run`; outputs separate `/tmp/agent-toolbar-tangent`.
- Still no independent second photographic background, no primary acceptance of this experiment, no next qualifying pass, no public changes by agent. Await primary's review of the pending first candidate and next instruction. Reciprocal monitoring continues; explicit Ana pause overrides future work.

Module SHA-256 `54d8ec65624d0bbdffae8fafe2a0dc2e99bc3414fe07f2930c82ae0dad09790b`.
