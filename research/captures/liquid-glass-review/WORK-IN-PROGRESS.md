# Current work — October 19, 2026

Private working checkpoint. Review notes live with each pass; this file records unfinished processing so an interruption does not lose context.

## Current delivery

- **Pass 06 is ready in `pass-06/`: chosen4.5/gain1 optics, proportional1.6px lens blur, a highlight/icon-blur grid, dark-weighted saturation and two motion clips.** Earlier review images remain unchanged.
- Pass 03 contains optional geometry diagnostics and provisional shape preferences. Image 02: third toolbar variant plus a very slight central bulge. Image 03: third slider shape, crown 0.6, primarily for outline.
- Compare Apple / previous slider reconstruction / new shape at identical scale. Measure the line's nearly unchanged interior thickness/position and smooth, strong **near-edge** onset. Do not assume rounder geometry is optically better.
- Playback outer-rim reversal must be investigated separately from lighting/contact artifacts. User sees no matching mirrored strip in Apple. Toolbar inversion remains required where observed.
- Toolbar `d` crop is correct; it needs more blur and a more progressive horizontal-magnification change across its vertical span.
- Playback icon: preserve white silhouette with ~1–2px feather; calculate color from background. User requests very faint additional orange/reddish saturation in darker regions.
- Slider exterior: compute separate contact shadow and broad source-colored halo rather than retaining reference context. Edge-merging of blue into rim still needs work.

## Source and branch

- Worktree: `/mnt/user/live/projects/localica/localica-docs-publish`, branch `docs/glass-presets-222`, PR414 / issue222.
- Pushed HEAD is now **`e42fc48`** (proportional filter units / monotone highlight reduction), after **`610a589`** (radial-tail/icon-response equations), after math **`2c955cb`** and source-input correction **`99d182b`**. Core closed-body/curvature geometry, source construction, independent controls and model.md are committed. Remaining replay/audit/refinement/documentation changes are uncommitted; preserve them. No main/app/Pages deployment for this refinement pass.
- Docker `localica-dark-lab-check` runs with repo `/workspace` and private research `/evidence`. Python dependencies: `PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps`, `OPENBLAS_NUM_THREADS=1`.
- Private scripts/results: `../localica-feedback/dark-glass-lab/apple-matches/`; canonical pre-pass04 fit set `curvature-contour/`; new results `pass04-candidates/`.

## New experiments after the earlier handoff

- `playback-review.py` → `review-pass-02/`; the public-to-Ana copies are in pass-02. Fitted white-mask response improves training/withheld icon RGB RMSE from 22.33/20.88 white or 8.15/7.72 constant cream to 3.47/3.38. Model is encoded-RGB nuisance response, not identified Apple shader.
- `icon-color-review.py` → `review-pass-04/` in research evidence only, **not yet the formal review pass**. Independent channel exponents improve RMSE to 2.97/2.87. Dark-weighted saturation alone gives little independent improvement. Needs inclusion with complete next pass and honest complexity limits.
- `geometry-review.py` → `review-pass-03/`. New C2 integrated-smoothstep cap join reduces sampled normal-derivative jump ~1e4×, max silhouette shift 0.1975px at 392×170. Same sampled straight-section stretch. Unreliable slider ray trials retained in research evidence, excluded from review options.
- `slider-sections-review.py` → pass-03 shape-only image. Preferred crown 0.6 body has no sampled positive height-Hessian eigenvalues in 4,737 interior samples (not a global convexity proof).
- `toolbar-profile-review.py` completed two starts (3301/3302): tangent ≈0.1993, band≈0.4035, source sigma11 vs old8, canonical loss≈0.0016523 vs old≈0.0018478. Fixed normal profile; refitted shared material. Need compose/inspect full and `d` crop.
- `playback-monotone-review.py` completed two no-reversal controls. Positive-derivative PCHIP radial map fits worse: RMSE≈10.67, rim14.52 vs old smooth-front ≈8.66/11.77. It is an image map, not a body; global nonreversal may be too restrictive. Original smooth-front map has TWO radial derivative sign changes: inverted band ~4–19px inward, outer return in last~4px. User may mean unwanted outer return rather than every inverted ray. Diagnose via source mapping and uniform-field lighting.
- `playback-solid-review.py` completed convex rotational closed-body candidate3501. RMSE10.29/rim13.14; residual energy~1e−7, no unknown background. Height0.699, gap0.0708, shoulder12(bound), index1.0345. More coherent transport but poorer fit; do not call it an improvement merely because physical.
- `slider-solid-review.py` tests preferred crown0.6 with shape fixed (m1,beta.5,k1,rear1), effective height/gap/index fitted. Session52034; check log/output before restarting. Needs line-height/onset plot and old/new comparison.
- `slider-shadow-review.py` fits exterior contact + source-chroma halo to recovered background. Session29278; check log/output. Intended reusable approximation, not recovered Apple shadow physics.

## Tests / public docs

- `verify.py` and `verify-solid.py` passed after C2 join implementation. Portable fixture error1.42e−14.
- Public `curvature.py` now has `capsule_offset` (integrated cubic smoothstep), optional `cap_join` in height footprint, independent/cross-coupled crowns. Existing zero-join defaults preserved.
- `model.md` now documents closed-body ray equations and C2 joins. New `solid.py`, `solid_material.py`, `verify-solid.py` still untracked; preserve.
- `reproduce.py` now samples every native parity, supports polynomial oval, RGB environment/dispersion and closed-body controls; `audit.py` standardizes material fits. Existing final results/figures are still from previous published study. Do not silently claim they reflect new parameters.
- `site.cjs` still needs exports for solid.py/solid_material.py/verify-solid.py before linked public Pages math docs can build coherently.
- Remaining: common final scoring/replay, updated public figures/tables/evidence/limitations, docs/link checks, coherent commits pushed under Ana identity. Preserve the same five Apple measured scenes.

## Latest findings and handoff

- Corrected the slider source baseline: old21px OpenCV stroke actually produced22px span. New analytical capsule gives **20px** at x595/605/625, centered at549.5, exactly matching the exposed reference threshold. Source regression tests pass for blue and gray. The hidden blue endpoint remains estimated. Do not silently compare old22px-source scores with new20px-source scores.
- `slider-corrected-source.png/json` and all final pass04 candidate outputs are in `apple-matches/pass04-candidates/`.
- `slider-solid-review.py --transverse --corrected` completed3662; source20, crown.6 fixed, transverse power1.5883, height1.9526, gap.7044, index1.0277. RMSE11.50: still worse overall than the older image map. Interior track22px vsApple20; first near-edge peak38vs44. Preferred outline alone does not solve optics.
- New `cross_section_power` geometry preserves silhouette and normalized longitudinal section; changes transverse meridian. Analytic normals verified. Final candidate:4,820 interior samples have max Hessian eigenvalue−1.56e−5;6,265 internal segment samples allinside. Finite checks, not global proof.
- Old chromatic map rerendered/refit on source20 as `slider-original-map-corrected.png/json`: central span20matchesApple;10px fromlefttip40matchesApple40. Much of the previously apparent early expansion came from input stroke inflation.
- `slider-shadow-review.py` now reads corrected20px source and computes exterior rather than retaining reference pixels. Color/shape mismatch remains visible; no recovered Apple shadow-physics claim.
- `playback-singlefold-review.py`3461/3462: radial phase-map with one orzero derivative sign changes, removes OUTER return rather than all rim inversion. RMSE8.64/rim11.83, canonicalloss.003114. Used in pass04 to test the unwanted extra mirrored strip. It is an image-map approximation, not closed-body geometry.
- `playback-solid-review.py --broad`3561: closed convex rotational bodym29.77,index1.119,H.529,gap.224; RMSE8.635/rim11.405,loss.002959; residual~1e−6, no unknown background. Retained as a physical comparator, not the pass04 primary.
- `assemble-pass04.py` generated `review-pass04-complete/`; copied to user review pass-04. It clears the entire old icon neighborhood and uses white-mask channel-response shading, no copied interior icon RGB. Final icon RMSE3.02/2.91.
- Formal pass04 README explicitly notes weaker new slider optics, still-pending toolbar central-bulge calibration, image-map vsphysical-tracer distinction and retained exterior context on playback/toolbar.
- All latest fitting jobs are complete; no pending long-running job is required for the prepared review set. Docker remains running as an existing workspace tool.
- Source99d and math2c exact-index tests passed;200 local Pages links checked. Android performance remains unbenchmarked. Current repo has RuntimeShader GPU adapter on modernAndroid; user was given feasibility assessment with8.3ms total-frame120Hz budget, not a performance guarantee.
- Public issue222 updated through source checkpoint comment6282138158; add math/review readiness evidence after delivering pass04. No native app edits/main merge/release.

Keep private feedback outside Git. Use umask0002 and workspace fix-permissions.sh on created/modified paths, including Docker outputs, for SMB.

## Current result and next action

- **Playback calibration settled by Ana:** width4.5/gain1; glass blur1.5px, dark saturation0.2, taper0.5, icon-color blur3px, at490px reference diameter. Both sigmas scale with the shorter lens dimension. Icon blur is last color operation before sharp coverage. Original pass04 channel response retained; no global color-order guarantee.
- Final full-HD media in pass-06/settled/: playback-final.mp4 (1920x1080,6s,30fps,927562bytes); playback-final.gif (same dimensions,6s,15fps,128colors,7960291bytes <10000000). Both fully decoded/checked; source/background unchanged. Offline motion, no deformation/exterior shadow, no Android fps claim.
- Source playback-settled.py reuses playback-pass06.py with explicit settled parameters. Tests independently verify final color blur at native/half output size. Preset, still, frame captures, metrics and scripts preserved in settled folder; no generation jobs remain.
- **Progression requested:** earlier PR commits7a8061b andb1636bb, then passes01–06 andsettled, all frozen PNGs re-scored on identical native reference/masks. GlassRMSE10.18 ->8.08; SSIM.9577 ->.9724 (nonmonotonic). Pass05 has best8.06/.9738. Icon02~3.50,04~3.08,settled~3.24. First symbols copied/unrelated redraw, so no independent icon scores. Earlier unmeasured lab/preset/physics commits listed honestly as unscored. Full table/provenance in settled/progression.md/json. Floating-point fit scores differ slightly from common PNG re-scores.
- Ana is exhausted by fine tuning. **Own routine comparison work; bring one recommended result and only meaningful alternatives.** Standing request: motion clips with later element reviews. Do not reopen settled playback for tiny metric improvements without a concrete defect.
- Public math calibration checkpoint **bc40089** on PR414; native app/main/Pages unchanged. Existing8 replay/audit/refinement files still uncommitted; preserve them. Public comparison figures/scores remain older, not current private accepted presets.
- Next research element remains slider (measured achromatic narrow shadow, wider correctly colored blue halo, late/abrupt line expansion); toolbar follows (blur-stage comparison, small curvature adjustment only if worthwhile). Current turn finishes the requested final media and score history; next element should begin when Ana steers it.
