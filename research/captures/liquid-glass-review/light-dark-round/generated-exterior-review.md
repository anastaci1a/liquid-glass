# Shared generated exterior candidate — primary review required

One four-parameter fit gives a numerical **exterior-only** qualifier; original optical E ties. No source adoption, public edits, optical renders or counted pass. Shared RGB-gain work remains deferred.

| Frozen supplemental exterior | Zero-generated RMSE | Generated RMSE |
| --- | ---: | ---: |
| Light | 6.082353686184 | 3.805386046630 |
| Dark | 6.752748427481 | 2.120522492242 |

The exact original exterior masks remain `0<sd<.35L`, 49,800 pixels/theme (SHA256 `46e6c6968f940f19905482f1604837770cc309b4a4d5570ed7ef0bc8b07df39b`). Removing the old target-derived presentation context receives no credit. The comparison baseline is the separately frozen source-PNG + true4×4-coverage presentation, with zero generated components.

Before fitting, saved signed-distance profiles support upper brightening in dark and lower darkening in light. Zero opacity reproduces that baseline bit-exactly; black shadow only lowers and white glow only raises it. This supports testing the prescribed empirical family, **not** identifying the gray field as incident background or proving an Apple lighting setup. The previous presentation discrepancy is retained, but its cause is unclassified: localized glow/lighting remains possible. Original dark underbody source0 stays frozen.

The shared law is `B1=B*(1-alphaK); Bout=B1+alphaH*(1-B1)` and `complete=M*coverage+Bout*(1-coverage)`. Each alpha is `opacity*exp(-.5*(max(sd_translated/L,0)/sigma_L)^2)` using the original rounded rectangle. Fixed offsets K=(0,.06)L / H=(0,-.4)L were frozen before the fit; L=106.5 native pixels. Fitted K opacity **.028644737086080185**, sigma **.7L**; H opacity **.0391166614246353**, sigma **.11786013768786802L**. Bounds were opacity[0,.12], sigma[.03,.7]L. K sigma hits its upper bound; no extension/refit was attempted. No theme/channel/pixel coefficients or copied target residual/shadow.

One deterministic L-BFGS-B fit with complete analytic compositing derivatives used **27/120** cheap evaluations. Objective was mean of the two exterior MSEs divided by their respective frozen baseline MSEs; both actual exterior errors independently improve. All evaluated points are retained. Solver convergence is not acceptance.

All original train/held/glass/rim/interior/outer-rim pixels remain bit-exact to the saved legacy native material. A separate scoring-only check uses the original float32 output protocol and verifies **every score dictionary exactly**, including original selection_loss, SSIM, gradient, MAE and chroma. SSIM remains light .999122142791748 / dark .999718964099884. No optical render or original mask/input/recipe change. Original whole/ALL-scored source-domain evidence transfers because map/kernel/material/source are untouched; finite estimated RGB is not observed source truth.

Far bands and previews retain limitations. In light, upper .35–.7L RMSE worsens 1.636898→2.527705, upper .7–1.2L .893942→2.464294, while lower bands improve. In dark, lower .2–.35L worsens 0→.049344 (small glow tail), .35–.7L .032370→.032377. These are advisory, never hidden or promoted into fitting masks. Dark upper .35–.7L improves 8.868358→6.061123, but its broader gray field remains underrepresented. The generated halo follows the translated capsule; it does not recover the full observed exterior pattern. Both per-side720-width comparisons were inspected; primary visual acceptance is still required.

Artifacts are under `/evidence/extended/helper-toolbar-work/light-dark-round/generated-exterior/`: `inspection.json`, `recipe.json`, `trials.json`, `result.json`, `original-metric-verification.json`, per-theme complete/background/alpha arrays, native PNGs and `regular-{light,dark}-comparison.png`. Frozen zero-generated baseline remains untouched in sibling `clean-presentation/`. Driver is `light-dark-round/generated-exterior.py`, copied byte-identically to the large evidence root. Inspection preceded fit; no completed evaluation needs repeating.

Exact original commands (completed; do not rerun fit into existing output):

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/light-dark-round/generated-exterior.py inspect
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/light-dark-round/generated-exterior.py fit
```

Review-ready was native-queued immediately (`f91f4b58-98c1-49f5-ac77-a6ef59608aca`), shared flag raised. Next-task request was sent before final packaging (`1dd249cd-338d-41b5-86aa-631578d07acb`). Await primary independent native/source/visual review before any adoption/count. No additional fit is authorized by this packet.
