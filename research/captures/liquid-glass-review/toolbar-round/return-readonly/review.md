# Toolbar pending29 — bounded read-only return

This memo follows the latest requested review baseline **bb1ee80131d39e7661c3d55174767c4d15182e05/count2**, epoch `d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d`. No fit, native render/replay, material-only ablation, source adoption, glyph change or new epoch. Historical later pass03 acceptance files/02a054e2 and source-stage studies are preserved; their existence is flagged rather than silently rewriting history or counting29 again. Primary owns the requested decision.

## Existing numerical evidence — do not repeat

29: shared gamma1.0456395525912732 before affine material, common rim gain+.006, RGB bias+.003, common core gain+.006. Existing geometry/crown/pose/map/source/ordinary filtering/shadow/SVGs unchanged. This is empirical material/intensity response; gamma is highly confounded with source photometry and existing material basis (99.8615% tangent energy in its span), not uniquely identified optics or a new dispersion law.

| Original guard | bb1ee801 |29 |
| --- | ---: | ---: |
| E |6.870490597950|6.790203130095|
| Glass |5.843130588531|5.796156406403|
| Rim |8.813648223877|8.677568435669|
| Fixed exterior |11.469442017232|11.466962522841|
| Archive box |13.242044387462|13.142080481293|
| Plus box |3.667139623528|3.304110822041|

Primary native replay **already exact**, material/complete differences0 and coverage exact: `/evidence/extended/toolbar-response-primary-review/verification.json`. Primary material-only ablation already worsens E7.072459251978449; no duplicate ablation. That early verifier has accepted=false pending its then-visual review; later `accepted-verification.json` has final gate.accepted=true/source/visual/replay true. This memo does not override either stage or the latest decision request.

## Visual/crop limits and existing arrays

Upper crown continuity, d-stroke geometric easing, underside soft reflections and dispersion remain unresolved. Gamma/common material changes contrast; it does not repair transport/shape. **Underside local conditional RMSE worsens5.073945→5.483195 (~8.07%)**, full-visible5.06231→5.47054. Existing fresh HQ views preserve that worsening, not hide it in global improvement. Native8 E6.785228789193 is advisory and never replaces native4×4 scoring.

Ana-requested existing reframed native rectangles:

- Upper rim **[650,369,1270,468]**, extends original66px height downward by33px.
- Adjacent d/letter crop **[960,468,1120,550]**, top equals upper's bottom468, no gap/overlap.
- Historical original upper[650,369,1270,435], d[960,450,1120,550] and underside[650,650,1270,726] stay separate, not mixed into reframed metrics.

Exact existing reframed diagnostics are public `docs/liquid-glass/experiments/reconstruction/studies/archive-plus/review-round/pass-03-crops-reframed.json`: upper glass7.402929→7.302526/full10.888852→10.802674, adjacent d glass3.367798→3.095663/full3.616755→3.437049. Saved evidence only; no new crop/render/metric was produced here. Full masks unchanged.

Existing arrays/comparisons:

- Canonical bb1ee801 package `liquid-glass-review/toolbar-round/evidence-package/`: `recipe.json`, `inputs/`, `native-replay/{render.png,comparison.png,scores.json}` (the original29 driver reused native float arrays at `/tmp/agent-toolbar-inner-settlement/{material.npy,alpha.npy}`; no baseline rerender), primary scores/proof and manifest.
- 29 packet `liquid-glass-review/toolbar-round/revision2-response-trials/first-proposal/{recipe.json,measurement.json,material.npy,alpha.npy,complete.npy,complete-preview.png}`; mirrored large root `/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/`.
- Same packet `fresh-evidence/{upper,d,underside}/comparison.png` and `candidate-hq-material.npy`, `hq-alpha.npy`; original upper/underside baseline arrays reused from immutable queue9, hashes in `reused-baseline-manifest.json`.
- Primary replay arrays `/evidence/extended/toolbar-response-primary-review/{material.npy,complete.npy,alpha.npy}`, `native-review.png`, `public-replay.png`, full `hq/{comparison.png,render.png,scores.json}`.

## Frozen source and canonical vector provenance

Original source SHA256 `6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b`; target `5bb59714854d0bd019d689b3e8c444dd82b057d6abdc9275ca88a8295692bbf8`. The source combines registered known donor ink with estimated paper/hidden gaps; finite in-image source/kernel support is not observed hidden RGB. Original 139,059,200 emitted HQ coordinate proof transfers because29 leaves map/kernel/source unchanged; finite source Gaussian radius44+bilinear1 still applies. B714 is incomplete/inactive; no new paired epoch.

Frozen SVGs in `evidence-package/inputs/`, independently rasterized vector coverage with constant color:

- `archivebox.svg` SHA `0a585750c7ef62d1a337bd4465deb1da651128450183bec9451adff649763cd6`: symmetric three-component SVG path/rect geometry with uniform rounded stroke. **Clean independently reconstructed archive outline**, not an exact Apple/font outline; available original filled font glyph mismatched. No screenshot matte, texture or target-pixel glyph.
- `plus.svg` SHA `846f23109fbb184ad823c1f53029617bcee88f85750e17a97235fe0496762c6e`: original SF `plus.tag.color.large` variable-weight outline, uniform size/placement, one weight and constant color. No copied colored source glyph or per-pixel correction. Original font evidence remains private under `/evidence/extended/icon-source/`.

Public pass02 foreground_layers fix these hashes/placements/colors and both full foreground-box guards. Canonical means frozen procedural vector for this protocol, not proof of exact proprietary symbol geometry/PSF. Source23 font/paper alternative is independently supported as an improved **estimate**, not hidden-text truth; SHA1b64… remains separate/unadopted. Its matched old-incumbent E6.981210 worsens versus6.870491; improved outside-glass text controls do not authorize an epoch reset. See saved `source-adoption-decision/review.md` and `/evidence/extended/toolbar-source-primary-review/review.md`.

Next action is primary's29 visual/source/crop decision, specifically retaining underside worsening and canonical/source uncertainty. No toolbar fitting or source/glyph/epoch change is authorized before that decision. Request next bounded task before finishing this intake; no broad speculative queue.
