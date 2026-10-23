# First toolbar candidate — UNACCEPTED, primary review required

Separate worktree `/mnt/user/live/projects/localica/localica-agent-reconstruction`, branch `research/agent-toolbar-222`, base `288e2adc02da6ffe1dfc8ea25b42687dd8c262df`. Lead changed from docs/reconstruction-review to selector-crown by assignment execution; the observed current HEAD was used. No shared source edited, no commits/pushes, no accepted pass counted. Investigation stops here pending independent primary acceptance.

## Candidate

| Native fixed-mask metric | Incumbent | Candidate |
| --- | ---: | ---: |
| E = sqrt(.7 glass² + .3 rim²) | 7.103742101595 | 7.043770523525 |
| Glass RMSE | 6.123516082764 | 6.079080104828 |
| Rim RMSE | 8.984233856201 | 8.896825790405 |
| Fixed clean-composite exterior RMSE | 19.272913277567 | 19.214948373522 |

E reduction **0.8442%**, required maximum7.068223391087. All numerical guards pass. Local repeat from the new renderer exactly matches saved candidate pixels (max absolute difference0); this is not independent primary acceptance. progress_gate deliberately reports accepted=false while external evidence booleans remain false. Source support tested at frozen glass pixel centers with source3σ+bilinear margin34px: all inside image. This does NOT certify every continuous/subpixel lookup; primary should check that independently.

Recipe `candidate-recipe.json`: existing material/normal profile/tangential parameters/source blur unchanged; add `footprint_softness=.08` using lead's crowned_footprint primitive and ordinary glass-color post_sigma=.5/170 (0.5 native px at L170). No dispersion, per-image color field, material refit, new source content or painted effect. The crown is extremely slight, continuous/convex with unchanged cardinal bounds. Its boundary coordinate is not Euclidean signed distance or identified Apple geometry; using it in the empirical map remains an approximation. Normalize all lengths by L.

Ordinary color filter is `C_blur = Gsigma(C alpha)/max(Gsigma(alpha),epsilon)`, then composite through the ORIGINAL sharp alpha. It prevents exterior zero padding from darkening the edge. The earlier naive postblur experiment is retained as rejected diagnostic evidence; no gains from that boundary artifact are promoted.

## Frozen inputs and limits

- `source.png` SHA2566c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b; `target.png`5bb59714854d0bd019d689b3e8c444dd82b057d6abdc9275ca88a8295692bbf8. Both copied byte-for-byte from public-settled-confirm, not composed comparison images. Incumbent replay matched archived E/glass/rim exactly. Source/registration/masks never changed while testing.
- Current epoch `d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d`; `epoch-input-hashes.json`, `protocol.json`, `frozen-masks.npz`, `incumbent.json` freeze it. The input audit's earlier digest precedes adding an exterior guard to the protocol, before trials; E/glass/rim/source remain identical. This is not a gain or a reset.
- The uncovered/registered source has its original lens/shadow rectangle erased through a smooth paper field. 92,009/188,771 direct footprint pixels fall inside that estimated blank rectangle. Target-free paper estimation plus recovered text is an explicit hidden-background assumption; source-support evidence must not be presented as photographic truth for the blank rectangle. input-audit.json preserves provenance and limitations.
- Baseline had no independent generated exterior-shadow model. The NEW guard freezes the original 0<sd<35 exterior region and evaluates complete clean compositing against Apple, with no reference residual/shadow copied. Both shadow diagnostics are still high; this candidate does not solve exterior shadows. Baseline/candidate use the same clean exterior definition.
- Canonical archive/plus glyphs remain unsolved and unscored; glass-only previews omit them instead of pasting reference symbols. Do not claim a complete foreground reconstruction. No second observed background or motion acceptance; keep the single-stage requirement.
- This first candidate partly softens underside lettering and smooths the footprint. The d-stroke stretch/easing mismatch and remaining underside/exterior differences are not solved by the numerical threshold. Fresh HQ images show those limits.

## Evidence and code

`toolbar_candidate.py` and `test_toolbar_candidate.py` are the ONLY untracked files in the separate worktree's `docs/liquid-glass/experiments/reconstruction/`. Proposed API: `mapping(x,y,recipe)`, `boundary(x,y,recipe)`, `render(source,case,recipe,samples=4,scale=1)` returning conditional glass color plus independent coverage. Uses existing crowned_footprint, settled and render primitives. The original geometry library/shared renderer is untouched. Model SHA2566dd437aa98a244da88a2440eb7d849dd200b583fee71669e46bd9b019e0d79a1.

Private files here:
- `audit-inputs.py`, `input-audit.json`: original source/replay audit.
- `first-experiments.py`, `first-experiments.json`: all three bounded experiment families and every internal evaluation; none accepted.
- `review-after-three.md`: required procedural review, including rejection of zero-padded postblur and the proposed corrected combination.
- `combined-experiment.py`, `combined-experiment.json`: fourth experiment; .25px fails threshold, .5px passes numerical gates; stop at first passing candidate.
- `verify-candidate.py`, `candidate-replay.json`: fresh native repeat, source domain diagnostics and deliberately incomplete gate evidence.
- `d-stroke-4x-comparison.png`, `upper-rim-4x-comparison.png`, `underside-4x-comparison.png`: Apple native detail enlarged at left, independently re-evaluated 4x incumbent center, fresh 4x candidate right. Fixed crop positions: [1040,370,1210,500], [650,369,1270,435], [650,650,1270,726]. No recentering/recoloring. Actual new high-resolution model evaluation, not upsampled optical output. Foreground absent/unscored.
- `candidate-material.npy`, `candidate-clean-exterior.png`, `candidate-recipe.json`, `candidate.json`, paired incumbent files.

Execution used existing container, no service changes or extra container: copy ONLY the separate worktree reconstruction folder to container `/tmp/agent-toolbar-code`, scripts to `/tmp/agent-toolbar-*.py`, outputs `/tmp/agent-toolbar-run`. Python env OPENBLAS_NUM_THREADS=1, PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps. Scripts hardcode these private scratch paths; primary should use a fresh independent path and its own verifier before accepting.

Commands used:
```
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-input-audit.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-first-experiments.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-combined.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-verify.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps:/tmp/agent-toolbar-code localica-dark-lab-check python3 -m unittest test_toolbar_candidate
```
All three meaningful regressions passed: exponent4 reproduces incumbent map, constant glass stays constant at filtered boundaries (no dark edge), crowned map mirror symmetry. Native baseline renderer also matched old settled output bit-for-bit. No model is called identified Apple physics.

Next: primary independently checks frozen inputs/registration, actual4x images, all scoring/subpixel source support and the new exterior guard; accepts/rejects and owns any commit/push/publication. Agent awaits that decision and continues five-minute monitoring; no next qualifying pass is pursued.
