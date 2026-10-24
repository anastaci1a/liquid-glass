# Two-height miniplayer peer review

**Pass with limits for fixed split09 primary geometry; held for fidelity.** The two-height solver uses actual height graphs, their gradients and an ordered monotone residual. It does not apply a convex intersector to the nonconcave spline. Light four improves aggregate E and SSIM on all four references, but original guards still fail.

## Scope and provenance

This read-only review started at 05:10:02.461 UTC and ends by 05:20:02.461 UTC. Root checkpoint `8c12a6e2` contains the frozen observations. The numerical solver originated at `3203e4b9`; `358c0b5c` adds the physical height wrapper without changing that function. No root or shared file is edited.

The review reads exactly 128 representative saved path records, 64 per member. Decoded numerical payload totals 435,180,800 bytes, below 512 MiB. It performs no ray, height, source query, Fresnel evaluation, emitter evaluation, composite, filtering, fitting or rescoring. Saved guard values are transcribed, not recomputed.

## Ordered-root certificate

Write the wrapped nonnegative height and its global slope bound as follows. The front multiplier is a physical surface parameter, not a normal correction.

$$
\begin{aligned}
z_{\mathrm{front}}&=s h(x,y),&z_{\mathrm{back}}&=-h(x,y),\\
\|\nabla h\|&\le M,&0&\le h\le H.
\end{aligned}
$$

For the transmitted internal direction, both residual derivatives have strict bounds. The implementation checks their equivalent positive margins at solver lines 47–50.

$$
\begin{aligned}
\frac{d}{dt}\left(z+h\right)&\le v_z+M\|\boldsymbol v_{xy}\|<0,\\
\frac{d}{dt}\left(z-sh\right)&\le v_z+sM\|\boldsymbol v_{xy}\|<0.
\end{aligned}
$$

The first residual starts positive and has a nonpositive upper bracket. Its unique zero is the back intersection. The second becomes negative immediately after front entry. A premature footprint exit would require both positive and negative height-relative signs when both graphs become zero, which is impossible by continuity. No height concavity is required.

The upper bracket reaches at least the lowest possible back height. Bisection retains its bracket; the result must satisfy the explicit back residual and footprint tests. Exact zero-height creases remain unresolved. This reasoning requires the declared continuous boundary-zero height, its global slope bound and a regular positive-height entry.

## Normals, scale and Snell signs

Both outward normals follow the same graph derivatives. The opposing incident normal at exit has the opposite sign to the back outward normal.

$$
\begin{aligned}
\boldsymbol n_f&=\frac{(-s h_x,-s h_y,1)}{\sqrt{1+s^2\|\nabla h\|^2}},\\
\boldsymbol n_b&=\frac{(-h_x,-h_y,-1)}{\sqrt{1+\|\nabla h\|^2}}.
\end{aligned}
$$

The camera propagates downwards. Entry uses air-to-glass with the front outward normal; exit uses glass-to-air with the negative back outward normal. `VerticalScaleBack` scales height, derivatives and both bounds together, preserving the footprint. For 09, half-height wrapping and front multiplier one produce equal shares of the original thickness.

Background distance remains 2.1 original L, below the complete wrapped back. Original L remains 88.5 native pixels. Only major member length differs. Pose translations are applied consistently to the cached source endpoints. No screen-space displacement or independent normal is introduced.

## Additional no-reentry limit

The generic solver's internal margins do not alone prove that its outgoing ray cannot re-enter a nonconcave back. Lines 70–75 require a downward transmitted direction and a valid background-plane time. A separate certificate is necessary before generalizing the solver to arbitrary graphs or parameters.

For fixed split09, a conservative angular derivation supplies that missing sufficient bound. The front and back slope bounds are identical after half-height scaling.

$$
\begin{aligned}
\alpha&=\arctan M,\\
\delta&=\alpha-\arcsin\!\left(\frac{\sin\alpha}{n}\right),\\
\theta_{\max}&=\alpha+\arcsin\!\left(n\sin(\alpha+\delta)\right),\\
- w_z-M\|\boldsymbol w_{xy}\|&\ge\cos\theta_{\max}-M\sin\theta_{\max}>0.
\end{aligned}
$$

The [scalar derivation](analytic-clearance.json) gives slope 0.3361707283, a subcritical Snell argument 0.6314917851 and outgoing clearance 0.2494593100. This is a sufficient worst-angle bound, not a new traced direction. It applies to 09, not automatically to 08 or an arbitrary wrapper scale.

Direct front reflection also escapes the upper graph under the same fixed slope bound: its upward clearance is positive when the expression below is positive. No secondary reflected traversal is claimed.

$$
\cos(2\alpha)-M\sin(2\alpha)>0.
$$

## Saved-path inspection

| Member | Records | Minimum back/front margin | Maximum back residual | Maximum bracket width | Maximum plane residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| Expanded | 64 | 0.9569457264 | 3.647e-12 | 8.044e-12 | 1.696e-17 |
| Compact | 64 | 0.9569487178 | 3.850e-12 | 8.044e-12 | 1.204e-17 |

All inspected records complete. The [saved records](saved-path-review.json) preserve actual points, normals, directions, brackets and scalar residuals without rerunning them. This sample inspection does not replace the root's full-grid source or path checks.

The solver checks coplanarity before multiplying separate s/p transmission factors. This supports its declared two-interface coplanar approximation and fails explicitly if the scalar triple-product residual exceeds tolerance. It does not implement arbitrary three-dimensional polarization-basis transport. Normal-incidence degeneracy does not establish a general curved-surface polarization theorem.

## Source, visible evidence and decision

All four original source-FIRST records pass their changed-map whole-body and original-guard audits before RGB, including the finite radius-21 kernel and four bilinear corners. [Input binding](source-binding-review.json) verifies the original input hashes without repeating those audits. Temporal-mosaic support remains conditional, not recovered hidden photography or front-environment observation.

Saved comparisons show an outer highlight, but not a complete reference match. Expanded B's lower rim remains weak, upper-left structure regresses and cap/text placements remain wrong. Compact B gains a visible outer edge while retaining different cap content and light distribution. No extra image is generated for this review.

| Light-four reference | Original failed guards |
| --- | --- |
| Expanded A | Interior, partial boundary, artwork, artist, play, forward |
| Expanded B | Glass, held, interior, artwork, title, artist |
| Compact A | Interior, title, play |
| Compact B | Interior, artwork, title, play, forward |

Expanded A partial-boundary RMSE worsens from 26.5498047 to 35.4737396. Every original guard and both fixed amplitudes remain in [saved guard review](saved-guard-review.json). The old compact cohort and changed-coverage diagnostics remain distinct. Aggregate improvement is not strict local nonregression.

Direct front reflection needs unobserved incident environment radiance. The directional annular emitter is a hypothetical scene, not an Apple lighting measurement. The sRGB-decoded effective transmission plus reflected contribution is a calibrated-primary hybrid; its empirical bias may already contain illumination. No physical radiometric calibration or complete radiance acceptance follows.

Retain the selected family and hold 09. The actionable shared-system need is explicit outgoing-clearance certification when reusing this solver beyond the fixed proven setting, together with honest polarization scope. No geometry, light or material retuning is requested by this peer review. The next distinct bounded question was requested before packaging.
