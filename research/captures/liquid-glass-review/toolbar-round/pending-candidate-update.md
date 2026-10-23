# Pending first candidate update — bracket, generated shadow, corrected crop

Responds to lead review05:52UTC. Nothing counted or committed by agent; all sources, masks, registration and original E baseline remain frozen. Primary's earlier independent acceptance work on .08/.5 does not automatically verify this updated .10/1.25+shadow version.

## Updated metrics

| Metric | Original frozen incumbent | Updated pending candidate |
| --- | ---: | ---: |
| Conditional-glass E | 7.103742101595 | 6.998512744608 |
| Glass RMSE | 6.123516082764 | 6.044535160065 |
| Rim RMSE | 8.984233856201 | 8.832458496094 |
| Frozen exterior RMSE | 19.272913277567 | 11.469442019668 |

E reduction1.481322879%, one pending substantive optical/material improvement. No shadow-only pass counted. Gate epoch remains `d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d`. `candidate-with-shadow.json`, `candidate-with-shadow-recipe.json`, `shadow-fit.json` are the CURRENT pending proposal; retain earlier candidate.json/recipe as the earlier reviewed variant.

## Completed bounded bracket

`bracket-initial.json` inventories .04/.06/.08/.10 softness × .25/.5/.75/1px blur. `bracket.json` completes .08/.10/.12 × .75/1/1.25/1.5. Best interior result is .10/1.25: both neighboring softness values and both neighboring blur widths have worse E. Normal/tangential/material coefficients and source blur stay unchanged. Detailed procedural review after experiments4–6: `review-after-six.md`; no verification reruns or internal optimizer evaluations count as extra passes.

## Generated neutral shadow

`a(x)=opacity * (G_sigma * shape_coverage)(x-offset)`; composite `glass*alpha + clean_source*(1-a)*(1-alpha)`. Gaussian-convolved shape coverage, no reference residual or inherited source shadow. Neutral black attenuation applies equally to RGB. Sigma and offset normalize by L; output samples honor current footprint. Proposed API `gaussian_coverage_shadow(case,recipe,scale=1,samples=4)` generates the whole footprint plus four-sigma padding before cropping, preventing crop-dependent shadows.

Opacity0.219680649874, sigma0.299999947760L, offset[-0.002930886319,0.007772858575]L. Native L170 means sigma51px/dx−0.498px/dy1.321px. Width reaches the explicit .3L bound; DO NOT imply uniquely identified geometry/lighting or a fully calibrated shadow tail. Three bounded starts converge consistently. The mask was not expanded to improve scores: additional35–55/55–80px bands are advisory only, improving21.6271→15.7654 and21.4535→18.2716 respectively.

Frozen-mask conditional glass remains the historical scoring protocol. New footprint coverage is partial at some original glass-mask boundary pixels (minimumalpha .625), disclosed in shadow-fit.json. Actual complete-composite glass/rim errors also improve to5.972587/8.680297, so compositing does not hide regression; those better advisory numbers MUST NOT silently replace the conditional-glass score protocol.

## Corrected diagnostic and verification

- `d-stroke-corrected-4x-comparison.png`, crop[960,450,1120,550], now shows the refracted around text/d near470–530. Previous crop remains in the archive. Some reference plus pixels overlap at lower-right; glyph is explicitly unscored and omitted from material panels pending lead's canonical vectors. No scoring masks or reference colors changed.
- `upper-rim-updated-4x-comparison.png`, `underside-updated-4x-comparison.png`: fresh4x model evaluations with generated shadow. Source/reference information quality remains native. Full native clean preview: `candidate-with-shadow-clean.png` (no pasted glyphs).
- Native shadow repeat through padded crop-independent API agrees with optimizer output to8.3e-8 RMSE. Five meaningful unit checks pass: incumbent map recovery; no zero-boundary darkening on uniform glass; mirror symmetry; shadow crop independence; zero-opacity identity.
- Latest code in separate worktree ONLY: toolbar_candidate.py and test_toolbar_candidate.py. Identical frozen snapshots are in `code/`; hashes below. Do not modify primary's copied crowned_tensor.py from this agent. Primary can independently integrate the new shadow helper alongside its existing glyph work.
- Reproduction: existing `/tmp/agent-toolbar-code` snapshot in current container, env OPENBLAS_NUM_THREADS=1, PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps. Private scripts `bracket-and-shadow.py`, `bracket-completion-shadow.py`, `finalize-shadow.py`, `updated-hq.py` preserve exact procedures. First shadow attempt hit OpenCV1D map size; final reporting hit float64 Sobel; both were corrected without changing any fit/source evidence. Not extra experiments/passes. See review-after-six.md for details.

Primary must independently replay this updated recipe and fresh shadow, inspect HQ/contour evidence, check all emitted subpixel source-domain support and decide whether the .3L shadow width bound needs further work. Foreground canonical glyphs remain primary-owned. Source blank-region estimate, lack of second photographic background, and d-stroke/stretch mismatch remain limits. No commits, pushes, publication, new accepted pass or next qualifying pass by agent. Waiting for primary acceptance/next instruction while monitoring.

## Snapshot SHA-256

- `code/toolbar_candidate.py`: `256ee8e084139ec1c81d07cd1e423d8962a665bfc44d4ab9d48744fae1b746f3`.
- `code/test_toolbar_candidate.py`: `af6da609d95207cfd09ffcc574da06deea8853128815d3a4a1567b70233d1e5c`.
