# Expanded outline: independent partial-audit review

**PASS WITH LIMITS for the saved partial audit.** The clearance argument and first-return polarization accounting are valid within their stated scope. They do not establish a complete reflected scene, an outline image or fidelity acceptance. No invalid convex-solid traversal appears in the audited script.

The review started on 24 October 2026 at 01:13:32.680 UTC. Its hard deadline is 01:23:32.680, including checks and versioning. The existing Search cycle ceiling remains 04:25:20.608. Only this new review folder is written; primary files and all sealed Search records remain unchanged.

See [protocol](protocol.json), [verification](verification.json), [identity review](identity-review.json) and [readiness](review-ready.json). No audit, direction calculation, Fresnel evaluation, height, ray, RGB query, composite or fit was rerun. Numerical counts below are the saved root results, checked for logical scope rather than independently recalculated.

## Frozen implementation and selected surface

The root evidence is `research/experiments/expanded-outline-role-04`. Its `audit.py` uses cached actual spline normals and imports only shared Fresnel and reflection functions. The paths, selected decision and shared optics SHA256 values match its saved result. Every entry in the published spline-observation code snapshot also matches the current files.

The selected eleven height controls and breaks come from `expanded-spline-height-01/inference.json`. Native preflight constructs that exact spline over the recorded rounded footprint with zero cap-join width. The inference and native driver use the same radius. Shared `spline_height_back.py:16–23` supplies nonnegative height, zero boundary height and the derivative-control global slope bound.

The saved bound is 0.6723414566078295. Positivity and bounded slope do not imply concavity. The selected solid must not be passed to `next_convex_boundary`, whose contract requires a separately certified convex solid. The current audit never calls that function or wraps the spline as a convex body.

## Clearance and footprint argument

Let the saved back point be below the flat front, and let its reflected direction point upward. Assume the actual height is nonnegative, boundary-zero and globally Lipschitz over its convex footprint:

$$
\begin{aligned}
\mathbf{p}_0&=(\mathbf{x}_0,-h(\mathbf{x}_0)),\\
\mathbf{p}(t)&=\mathbf{p}_0+t\mathbf{r},\\
|h(\mathbf{x})-h(\mathbf{y})|&\le M\|\mathbf{x}-\mathbf{y}\|,\\
g(t)&=z(t)+h(\mathbf{x}(t)),\\
g(t)&\ge t\left(r_z-M\|\mathbf{r}_{xy}\|\right).
\end{aligned}
$$

Thus the strict cone condition in `audit.py:34–40` prevents another back encounter while the segment remains inside the footprint. This is a sufficient condition; failing it does not prove a back rehit.

Suppose the segment first left the footprint before reaching the front. Boundary height would be zero, while its vertical coordinate remained negative. Clearance would then be negative, contradicting the positive lower bound. The same argument rules out a front-edge crease for a strictly certified launch. It needs boundary-zero height, not back concavity.

The saved numerical classification uses a positive margin of 1e-10. It certifies 800,823 of 890,848 launches under the stated bound and floating-point computations. The remaining 90,025 next events are unresolved. The analytic proof is valid; this margin alone is not a formal interval-arithmetic proof of every machine rounding operation.

## First-front TIR and polarization scope

`audit.py:40` evaluates returning-front Fresnel factors only for the cone-certified subset. Line 82 counts TIR or critical cases only in that array. Therefore the reported 72,808 events do not classify any of the 90,025 unresolved next intersections.

The initial front has normal incidence, so its s and p factors agree. At the back, the incidence plane contains the vertical axis and the horizontal surface-gradient direction. Reflection remains in that plane. The next flat-front normal is vertical, so the next incidence plane is the same. Zero-gradient degeneracy is harmless because both reflectances coincide there.

For each certified launch, the script correctly retains separate polarization powers:

$$
\begin{aligned}
P_{\mathrm{primary}}&=\frac{T_0}{2}\sum_{u\in\{s,p\}}(1-R_{b,u}),\\
P_{\mathrm{front}}&=\frac{T_0}{2}\sum_{u\in\{s,p\}}R_{b,u}(1-R_{f,u}),\\
P_{\mathrm{tail}}&=\frac{T_0}{2}\sum_{u\in\{s,p\}}R_{b,u}R_{f,u},\\
R_0+P_{\mathrm{primary}}+P_{\mathrm{front}}+P_{\mathrm{tail}}&=1.
\end{aligned}
$$

For uncertified launches, all back-reflected power stays in the unresolved tail. Multiplying averaged reflectances would generally be wrong; the script instead averages the s/p products. Its saved maximum partition residual is 2.22e-16. This reasoning applies to the first certified return, not arbitrary later three-dimensional bounces.

The shared Fresnel implementation at `geometric_optics.py:261–276` returns lossless dielectric power reflectances and classifies critical/TIR as one. The audit correctly labels a combined critical-or-TIR count. Later rotating incidence planes require explicit polarization-basis transport or conservative bounds; scalar repeated averages are not licensed by this review.

## Power is not reflected image radiance

The ledger partitions an unpolarized normal incident launch under an incoherent, lossless smooth-interface model. Its four-percent first reflection, primary power and retained tail are not pixel colors or an error bound on the displayed image. A small residual-power tail cannot be assigned an arbitrary RGB value or ignored as a proved image tolerance.

No environment radiance, return-path source support or later ordered intersections are supplied by this audit. Accepted incident blur and encoded tone do not identify a physical scattering law or specular response. The existing unit-throughput transmission renderer is unchanged. Fresnel weights must not simply multiply its encoded output or be added as a painted rim.

## Encoded ceiling and foreground exclusion

With nonnegative common gain and bounded encoded source values, the selected response obeys:

$$
0\le S\le1,\qquad G(S)=gS+b\le g+b=0.9252129976035592.
$$

`audit.py:56–75` compares target values only in the original rim mask at full actual coverage. The Study rim derives from the original glyph-excluded valid mask. Full coverage means all four retained AA2 subrays are inside, not a continuous pixel-area certificate.

This avoids treating clear partial coverage or painted foreground as bounded lens transmission. The saved any-channel exceedance counts are 3,485 for A and 6,005 for B; no recount was performed.

The next representable float32 bound encloses the real scalar ceiling. It is not a universal error certificate for arbitrary filtering or accumulated arithmetic. Here the accepted native record independently reports preclip maxima 0.9205652579960504 and 0.9211134506181065, below that ceiling. No additional sample scan is needed for this limited check.

The maximum target excess of 19.07 coded levels indicates a current response/coverage limitation. It does not prove reflection is the unique missing mechanism. Source estimation, coverage, illumination and camera response remain possible causes. Encoded RGB and physical radiance must remain distinct even where the numerical ceiling is valid.

## Next shared-interface need and decision

The next discriminating shared capability is a certified ordered-next-event contract for the actual potentially nonconvex height graph. It must exclude earlier roots, return a bracket and the same-height normal, and preserve tangent or unresolved outcomes. A convex intersector cannot safely substitute for that contract on the selected spline.

This recommendation authorizes no implementation or fixture. A complete reflected image would additionally require supported scene radiance and appropriate polarization transport. Those are separate prerequisites, not values inferred from bright target pixels. Retain the selected geometry and tone, the unresolved outline and all historical counts. This review is count zero.
