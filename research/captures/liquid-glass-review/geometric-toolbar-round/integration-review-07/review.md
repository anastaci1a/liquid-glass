PASS WITH LIMITS for the current code/evidence integration. No blocking regression identified in this read-only review of root worktree localica-geometric-playback, observed HEAD66517150. This is not a fidelity, full-transport, held-out or performance acceptance. No rays, RGB sampling, renders, fits, source edits, shared edits or commits were performed; sealed controls were read, not rerun.

Surface-derived optics and refactor

`experiments/reconstruction/geometric_render.py:9–25` contains the same render_rows function previously in geometric_playback.py. Normalized function text is identical, SHA256 d6f9e3b836d121fc3c4cb9a63579cc71bf6ca89ff42452a7d8a82b96e255bceb. Relative to the sealed unified-control copy, the only file difference is removal of one trailing blank line. All other reviewed core/wrapper/adapter files are byte-identical to that control snapshot. The three helper adapters plus crowned_footprint are byte-identical to the accepted private implementations, including the authorized radial-fixture correction.

`geometric_optics.py:147–179` obtains actual h/hx/hy from the surface, constructs the back normal from those derivatives, calls shared Snell and intersects the declared background plane. No empirical map, independent normal field, target residual or post-trace warp appears in this path. Exact crease hits remain incomplete with NaN source coordinates; the renderer rejects incomplete paths before source sampling at geometric_render.py:15.

`geometric_optics.py:25–40` owns harmonic H and its derivative weights; harmonic_crowned_back.py:32–45 composes actual gradients. CrownedBevel height/gradient and sections use the same function at crowned_bevel.py:66–80/99–110. ClosedCrownedSurface F/gradient, sheet roots and sections agree structurally at closed_crowned_surface.py:46–80. Root's closed tracer at geometric_optics.py:213–257 uses that F/gradient for ordered entry/exit and shared Snell, retaining TIR/tangent/non-downward incomplete statuses. It is a separate geometry path, not secretly selected by render_rows.

The inferred radial surface at geometric_optics.py:116–144 integrates continuous nonnegative curvature twice to obtain one height and exact derivatives. Its forward source coordinates still come from physical tracing; the old diagnostic map is not evaluated in render_rows. This realizes a map physically without independently identifying Apple's geometry.

Units, sampling and frozen stages

At geometric_render.py:11–16, L=min(case.half), the original case center and source pixel coordinates are used consistently. Quarter-pixel grids minus.375 are the same integer-pixel-center4x4 phase as the sealed drivers. At line25, all16 actual lens/miss rays are averaged, so geometry-derived coverage remains coupled to source integration and clear misses remain straight. No scoring/reference-mask shrink or recrop is performed by the shared renderer.

Exact four-texel interpolation is at lines18–20; the alternative historical OpenCV table interpolation is explicit at21. G04/G05 surface records set raw_transmission=True and exact_bilinear=True. There is no source/output optical blur. Optional frozen constant gain/bias at22–24 is opt-in legacy diagnostic behavior, not hidden spatial lighting or a fitted material stage.

`geometric_playback.py:25–31` retains input-byte verification and the existing historical-material-derived icon color/coverage stage. Old material is used for the icon, not replacement lens pixels; target pixels enter comparison/scoring, not refraction. The provenance limits are explicitly labeled at line33. This is not a newly unified physical foreground material. The caller must supply the matching frozen historical material; this review does not claim a new independent full icon validation.

Three32-pixel controls and precision

Read `/evidence/extended/geometric-unified-code-control/result.json` and its check.py, without executing it. Public shared-render-control.json is byte-identical to that saved result. Both circle controls have exact float32 and original-precision equality. The toolbar comparison explicitly casts saved float64 to common float32: equality after cast is0; uncast maximum difference is2.7863171658815133e-8. These three patches cover96pixels/1,536 previously executed ray queries, not full images. The float32 cast is disclosed software-refactor validation, not an epoch change, relaxed guard, score improvement or new optical result. No saved score was changed or recomputed here.

Current reversal wording and claim limits

`geometric-optics.md:69–81` explicitly supersedes the earlier blanket no-reversal/no-fold aim. Reference-specific onset/location/strength/extent/transition is the criterion. G03 is incomplete because primary-only transport cannot fill TIR paths, not because transmitted rays reverse (122–133). G04's crossing mismatch is separated from nonfolding (145–147). G05 retains desired edge reversal as a correspondence question and preserves mixed local results/missing light (169–181). Toolbar-harmonic.json's current interpretation likewise forbids blanket fold rejection. Historical experiment names/measurements remain historical controls, not active no-fold constraints.

`geometric-optics.md:193–197` correctly distinguishes mathematical implementation compatibility from visible transfer, Apple's geometry, full radiance and Android performance. Nav06 remains explicitly **incomplete: no held-out image or score**, before all guard/compositor checks finished. Its earlier predicted-outline equality stop is only a superseded protocol-prerequisite result, not proof of reference unusability. No third-reference visual validation is claimed. Clear/frosted material differences and unfinished scattering are disclosed.

Limits to retain, not requests to widen this task

- The shared renderer's check at geometric_render.py:17 certifies image bounds only. It does not itself load known/confidence masks or certify inverse registration/domain. The separate sealed all-ray/four-texel proofs remain prerequisites for those exact experiments; the three tiny software controls do not replace them or certify a new scene.
- render_rows imports/calls only trace_flat_front_orthographic (lines7/14). Closed B remains geometry/path evidence with unresolved TIR; this integration does not turn it into a rendered complete radiance model.
- Primary unit-throughput transmission is not Fresnel/reflected/environment radiance, a finite camera, frosted scattering or device speed. These limits are explicit in geometric_playback.py:33 and geometric-optics.md:9–13/50–52/193–197. No device performance was measured in this review.
- Passed patch controls are not full-render replays or image-fidelity acceptance. The corrected toolbar float64 history and every prior negative/incomplete record remain authoritative and unchanged.

Exact current file hashes and text/control identity results are in static-read-checks.json and control-code-identity.json. One false byte-identity flag for geometric_render.py is fully explained by its trailing blank-line difference; its function body is identical. No test or optical executable was run. Root owns all edits and final public commits. This review is complete and stopped within its eight-minute cap.
