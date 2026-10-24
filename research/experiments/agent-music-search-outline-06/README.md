# Music Search outline: scene and interface remain incomplete

**INCOMPLETE, not absent or accepted.** The frozen input supplies a scrolling background plane, not observed upward environment radiance. The shared closed-circle wrapper also rejects the exact Search radius adapter. These are independent prerequisites. No reflected image, branch classification or illumination proposal was evaluated.

The stage began on 24 October 2026 at 01:48:19.863 UTC. Its deadline is 01:58:19.863, including checks and versioning. The Search ceiling remains 04:25:20.608. See the [protocol](protocol.json), [diagnostic](ceiling.json) and [startup disclosure](startup-failure.json).

## Frozen evidence and material roles

The primary-reviewed [neutral component](../agent-music-search-neutral-05/README.md) has common gain 0.5193880051291454 and bias 0.4473611800152188. H1 geometry, background D2, incident sigma 6.75/radius 21, AA2, original vectors/styles, masks and shadow zero remain fixed. The accepted tone is not a full optical model or historical replacement.

The [source preflight](../agent-music-search-baseline-01/source-preflight.json) certifies the original transmission coordinates and finite incident kernels. Each reference has 98,989 body subrays and 139,337 required subrays. All 59,616 original scored subrays, including 52 outside the predicted circle, are retained. Each reference has 38 partial-glass pixels.

Those counts are historical evidence, not work repeated here. They provide no support for a changed reflected endpoint. The two cases contain source, target, known mask and magnifier vector inputs. They contain no angular environment map, camera-side scene plane, light geometry, radiometric calibration or measured specular roughness.

The source is a registered temporal mosaic. Its known mask provides conditional availability, not recovered hidden photographic truth or a directional light field. Neither the scrolling backdrop nor the target's bright rim can be relabeled as observed front-environment radiance. Historical fingerprint mismatch and the baseline masks-after-fixtures disclosure remain unchanged.

Incident frosted transmission uses its approved source-plane Gaussian before refraction. Reflection requires its own scene and material interpretation. Applying that Gaussian or the accepted encoded gain/bias to specular radiance is not justified. Unit-throughput encoded transmission also cannot receive a pasted Fresnel-weighted white border while being called energy conserving.

## Exact closed-solid interface mismatch

The pinned `geometric_optics.py:291–317` defines `CircularHeightSolid`. Its constructor accepts only `RadialCurvatureBack`, `CircularBevel` and `HarmonicCircularBack`. Search's `RadiusBack` is none of these. This is established by reading the definitions; no constructor, height function or optical fixture ran.

Removing that restriction alone would be incorrect. The wrapper hardcodes horizontal half-extents one, side level at unit radius, strict front membership at unit radius and a unit-radius nonsmooth test. Search's accepted radius in original L units is:

$$
R=\frac{88.75191176648384}{89}=0.9972124917582454.
$$

The actual frozen height is the base circular height evaluated at radius-scaled coordinates. Height units do not scale with that adapter. Its existing chain-rule gradient divides the base gradient by R. Using the unadapted back would silently alter the accepted geometry; subclass tricks or a permissive wrapper are not an acceptable repair.

### Analytic convexity scope

Within the accepted disk, the two actual constituent heights are:

$$
\begin{aligned}
r&=\frac{\sqrt{x^2+y^2}}{R},\\
h_1&=0.15(1-r^3),\\
h_2&=0.4(1-r^2),\\
h&=\frac{h_1h_2}{h_1+h_2}.
\end{aligned}
$$

Both constituents are nonnegative and concave on the disk. The shared harmonic combination is increasing and concave on its nonnegative domain. Therefore the interior height is concave. The zero boundary extends continuously. XY scaling preserves concavity; this argument applies to the original harmonic H1, not an arbitrary spline or raised annular back.

The occupancy between the flat front and this back is consequently convex:

$$
\mathcal{K}=\left\{(x,y,z):x^2+y^2\le R^2,\quad -h(x,y)\le z\le0\right\}.
$$

This is a mathematical occupancy argument, not a completed intersection test. At the zero-height circular crease, front and back meet without a unique interface normal. Exact tangency and numerical crease uncertainty must remain unresolved. No normal is invented, boundary moved or origin nudged.

## One proposed shared-interface requirement

Request one root-owned certified radius-aware extension of the strict circular-height solid. It must retain the exact base height and chain-rule derivative, and use the actual radius consistently for occupancy, enclosing bounds, front membership, exact boundary and nonsmooth classification. Heights remain in original L units. No helper implementation or type bypass is proposed.

For such an extension, the geometric contract would be:

$$
\begin{aligned}
F(x,y,z)&=\max\left(z,-z-h(x,y),\frac{x^2+y^2}{R^2}-1\right),\\
\mathbf{e}&=\left(R,R,\frac{H_{\max}}{2}\right),\\
\mathbf{c}&=\left(0,0,-\frac{H_{\max}}{2}\right).
\end{aligned}
$$

The active constraint must supply the same actual surface derivative. The existing shared ordered convex-boundary solver may become applicable only after that exact contract is independently certified. This proposal does not authorize its implementation, fixtures or paths. Missing environment radiance remains a separate blocker even if the interface is supplied.

## Ordered events and power are not yet available

The retained paths contain primary front/back transmission, not a multiple-reflection ledger. Shared `next_convex_boundary` requires an actual on-boundary inward ray and separately certified convex occupancy. Its bracket and crease rules must classify every future event before assigning an exit to a scene surface. None of those reflected events were computed here.

There are no Search-specific counts of reflected front exits, TIR, residual power or supported secondary background endpoints. Expanded-bar or other-circle counts cannot be transferred. Future upward exits require camera-side radiance; future downward exits require a new finite source-support audit. A small power tail would not make unknown radiance known.

The circular symmetry and centered orthographic convention can support a meridional polarization treatment for regular paths. They do not establish any actual path sequence. Shared s/p coefficients are interface power fractions, not image radiance. No coefficients, directions, normals or power partitions were recomputed during this audit.

## Conditional coded ceiling

For bounded retained incident samples and nonnegative common tone, fully covered transmitted pixels have this real-arithmetic ceiling:

$$
C_{\mathrm{transmitted}}\le g+b=0.9667491851443641.
$$

Eight binary64 epsilons enclose the bounded multiply/add and four-sample mean; an additional binary32 successor encloses the stored result. The resulting conservative coded ceiling is 0.9667492508888245. This is not a physical-radiance bound, reflection estimate or source-identification test.

The optional A count stopped after reading its 56,400 target pixels: the loader requested `alpha`, while the saved array is named `coverage`. The failed script is preserved. A was not reread. The remaining 56,400-pixel allowance was used for B alone with the documented key; no optical code was imported.

B has 8,326 fully covered original rim pixels. Of these, 750 have any target channel above the enclosure, and four have all channels above it. The 38 partial-glass pixels are excluded only from this supplemental full-coverage statement, not from any original score or guard. A's optional count remains incomplete.

These counts identify a limitation of the bounded encoded transmission component. They do not uniquely identify reflection. Missing illumination, conditional source content, feature correspondence, geometry, exposure and camera response remain possible explanations. No threshold sweep, new scoring mask or white-edge fit follows.

## Closure and next bounded question

The audit performs zero rays, heights, normal/direction/Fresnel calculations, source queries, fields, filters, composites or fits. Target-plane work is exactly 112,800 pixels, including the failed A read. Original baseline, blur, tone and source records remain immutable. No new model, source, input epoch or historical count is adopted.

Outline closes as an incomplete radiance scene with a precise shared-interface prerequisite. It is not skipped or declared absent. After sealing, request the existing bounded shadow-stage authority. Do not activate a shadow, environment, geometry extension or dependent fit from this report.
