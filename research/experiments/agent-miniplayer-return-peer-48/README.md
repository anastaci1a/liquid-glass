# First-return observations 85 and 86: independent peer review

**PASS WITH LIMITS.** Four cached foreground replays and every original metric record match exactly. The inset-band negative is preserved. Ordering, polarization and source-binding scope are consistent for these fixed graphs. No reflected-scene, physical-radiance, whole-image convergence or fidelity acceptance follows.

The review started at 19:44:36.181 UTC on 24 October 2026. Its checkpoint was saved before 19:49:36.181 UTC. Packaging and versioning must finish by 19:59:36.181 UTC. Primary files were read only after matching immutable pin `0e78dea9cefe3fda61ac16b8b0d7b73f1dc56370`. No merge, hydration or primary edit was needed.

## Independent replay

The sealed pre-foreground arrays were reused directly. The original Study constructor, original ordered vector/artwork compositor and original score function were consumed without invoking their optical rendering methods. All four completed arrays match, including unavailable-pixel patterns. Every score dictionary matches exactly, including foreground boxes, fixed crops and completed-image partial/exterior conventions.

| Reference | Replayed error | Replayed SSIM | Frozen partial pixels |
| --- | --- | --- | --- |
| Expanded A | 17.7197663624 | 0.8623149395 | 16 |
| Expanded B | 11.5729253334 | 0.8972504735 | 16 |
| Compact A | 18.0756367651 | 0.7978649139 | 22 |
| Compact B | 18.3620333850 | 0.7716655135 | 22 |

All four aggregate and SSIM comparisons regress against 78. Expanded glass/rim/held/interior fail; compact glass/rim/held fail while interior does not fail. This is not strict family nonregression. The original partial, foreground and exterior metrics tie. Fixed body crops tie. Compact A upper-left RGB improves from 18.55547 to 17.65723; that local exception does not reverse the overall result.

Four saved full comparisons were inspected without exporting images. Both lengths develop a doubled bright interior contour. It is displaced inward from the reference outer highlight; expanded B and compact B make the extra line especially clear. The existing inaccurate source returns and background/foreground limitations remain.

Root's four zero-added-return identities are preserved and bound to the immutable record. They were not rerun: this review independently replays only the four candidate foreground composites. The pre-foreground optical reconstruction, zero controls and complete first-return transport remain sealed root evidence, not newly executed peer controls.

## Ordered first return

Let the actual front be the positive height graph and the actual back be its separately defined negative graph. Both share the same boundary-zero convex projected footprint. With global slope bounds and an upward back-reflected direction, the two strict margins are:

$$
\mu_f=v_z-M_f\lVert\boldsymbol v_{xy}\rVert>0,
\qquad
\mu_b=v_z-M_b\lVert\boldsymbol v_{xy}\rVert>0.
$$

The front residual increases strictly; clearance above the back also increases. Before the front event, leaving the common footprint would require the ray height to be both positive and negative at its zero-height boundary. Hence the next front root is unique. This argument does not require back concavity or solid convexity.

The implementation brackets the original ray, uses forty bounded bisections and retains both bracket endpoints. It neither nudges the origin nor replaces normals. Its front normal is differentiated from that same height. The saved native margins exceed 0.4807 and 0.6472; maximum root residual is approximately 4.15e-12 in model units. These are inspected saved values, not recalculated optical tests.

Correct normal orientation is essential: air-to-glass uses the front outward normal; glass-to-air uses the negative outward normal at the back and returning front. The code supplies those signs. The power-eight front is concave over this unsmoothed convex-distance footprint. A strictly outward emitted ray consequently escapes its supporting tangent plane; the nonconvex back is never sent to a convex-only intersector.

First-front ordering does not certify transmission. Native 85 retains 114446 expanded and 80004 compact blocked front emissions. Their directions remain unavailable and emitted powers zero. The corresponding reflected matrices and remaining powers are retained during evaluation, without low-power deletion. Maximum retained power is approximately 0.041321; means approximately 0.007002 / 0.007238 are launch averages, not radiance or pixel-area averages.

## Polarization and partial scene

The interface rotates the incoming coherency matrix into its actual local transverse basis before splitting. Reflection uses complex Fresnel amplitudes, preserving TIR phase; transmission uses energy-normalized amplitudes. Density propagation has the form:

$$
C_{\mathrm{local}}=Q C Q^{\mathsf T},\qquad
C_r=D_r C_{\mathrm{local}}D_r^{\dagger},\qquad
C_t=D_t C_{\mathrm{local}}D_t^{\dagger}.
$$

The real orthonormal basis rotation justifies the transpose. At exact normal incidence the retained transverse basis supplies a gauge, without changing any surface normal or direction. The reflected p-basis orientation and amplitude sign are consistent. Blocked transmission has zero matrix and unavailable direction/basis. This is not repeated multiplication of scalar unpolarized averages.

The calculation retains coherence within each ray and adds separate geometric-path intensities incoherently. The saved partition is:

$$
R_{\mathrm{front}}+T_{\mathrm{primary}}+P_{\mathrm{return}}+P_{\mathrm{tail}}=1.
$$

Saved maximum closure errors are approximately 1.56e-15 / 1.45e-15. Native matrices were computed but not archived individually; reproducing them would require a separately authorized optical execution. This peer inspected implementation and sealed summaries only. The remaining tail is explicitly unassigned, not assigned black, white or a guessed environment.

## Source-proof transfer

The original whole-body/all-guard finite 43-by-43 kernel and four-corner proof binds unchanged primary coordinates and input bytes. Every dependency in 85's receipt matches current bytes. The archived as-run 78 driver matches its original 78 receipt; the maintained-driver digest matches the explicit snapshot mapping. No source proof or source grid was rerun.

A reviewer metadata check initially compared the archive against 85's maintained-driver digest. That false comparison is retained separately and corrected against the original 78 receipt. This changes no input, numerical result or replay. The documented as-run/maintained distinction is explicit rather than silently aliased.

All valid new first-return emissions are upward, so85 introduces no additional backdrop endpoint. That does not establish observed environmental radiance. The annular white scene is hypothetical; empirical encoded transmission tone and incident frosting are not applied to reflected light. This remains a calibrated-primary, finite-path partial-scene image with conditional mosaic availability.

The external full input-receipt audit finished after the cached replay. Study enforced its per-case source hashes before bitmap decoding; scientific files and cache headers had already been bound. The later full audit found no mismatch. This prerequisite-ordering limitation is disclosed rather than claimed as perfect protocol compliance; no replay was repeated.

## Convergence 86

The selection is sixteen pixels per length: four highest model-return means in each of four fixed geometric cohorts, with stable row-major ties and membership in both original rim masks. It uses no target RGB. Orders 4, 8 and 16 are fixed. This deliberately selected 32-pixel cohort tests the inset-band peaks, not silhouette transitions or the whole image.

$$
I^{(n)}=\sum_jw_j^{(n)}c_j^{(n)},\qquad
\delta_{8,16}=255\lVert I^{(16)}-I^{(8)}\rVert_{\infty}.
$$

The saved maximum 8-to-16 change is 0.000208688 of an 8-bit level, below the predeclared 0.1-level criterion. Native AA2-to-16 differences reach approximately 0.108804. Positive full-pixel weights and fresh source support apply only to the selected nodes. This peer did not repeat quadrature, optical transport, source sampling or convergence reductions.

The narrow conclusion is that integration error at these selected peaks is too small to explain the visible inset band. Whole-image convergence, physical camera response and complete radiance remain unestablished. Original AA2 scores are neither replaced nor improved by publication of 86.

## Accounting and limitations

| Peer work | Actual or reserved bound |
| --- | --- |
| Study constructors / original mask points | 4 /1121600 |
| Cached foreground composites / score calls | 4 /4 |
| SSIM Gaussians / metric erosions | 20 /4 |
| Vector coverage visits / box reservations | 32 /617616 |
| Numeric payload decoded | 43910400 bytes |
| Study bitmap/buffer reservation | 362959616 bytes |
| New optical functions/source queries/filters/fits | 0 |

Numeric NPY headers were inspected before replay bodies and payload decoding. Bitmap bounds conservatively include decoded source, target, artwork and vector buffers; saved comparison decoding is recorded separately. The combined bound remains below 512 MiB. This is work accounting, not a device-memory or performance measurement.

Historical 75/78 accounting violations remain separate. Native 85 explicitly charges its baseline angular lookups and new return events; publication does not repair old ledgers. Recovery 47 and untracked task 46 remain untouched. The current working family, sources, masks, styles and accepted counts do not change.

Readiness and the request for the next actual scientific question were sent through Sessionsation before packaging. No successor task, target, geometry, light or material setting is activated by this review.
