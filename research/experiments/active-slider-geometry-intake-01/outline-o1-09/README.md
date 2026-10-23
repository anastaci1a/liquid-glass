# H1 closed outline paths: incomplete radiance scene

The private closed H1 wrapper passes its invariants. Thirty-two cached launches complete the declared 32-encounter limit without unresolved numerical geometry. Rendering remains blocked: 235 exits require unobserved upper-environment radiance and 32 downward exits lack original finite source support. No RGB lookup, image, fit, environment color or extra bounce was performed.

This is an incomplete outline stage, not evidence that reflection is absent. The accepted neutral tone remains an isolated transmission component. It does not repair the missing reference returns or supply specular radiance. Historical pass09 and all prior diagnostic states remain unchanged.

## Clock, interface and ownership

The [protocol](protocol.json) began at 21:31:20.613 UTC. O1 ends by 21:46:20.613 UTC. The outline-stage actual cap is 22:31:20.613 UTC, below its original latest deadline of 22:50:40.688 UTC. The total deadline remains 23:50:40.688 UTC. Native-path work finished at 21:35:48.474362 UTC.

The pinned core remains `6fd37ddee6e418beb0694760d565a6ca8aeebdc6`. [surface.py](surface.py) owns only the new element wrapper. The unchanged shared `next_convex_boundary` accepts its certified surface protocol. The separate restricted `CircularHeightSolid` constructor was neither instantiated nor bypassed. Shared refraction, reflection, Fresnel and intersection implementations were not copied or edited.

Only the original H1 back is wrapped. The rejected raised back and shorter background distance are not used. The wrapper preserves the actual posed half-size, softness, height and full gradient. Its enclosing box is centered halfway between the front and maximum back depth.

## One actual solid and convex occupancy

In the original normalized length unit, with the frozen crown level and original harmonic height,

$$
\begin{aligned}
F(x,y,z)&=\max\{z,-z-h(x,y),T(x,y)-1\},\\
K&=\{(x,y,z):T(x,y)\leq1,\ -h(x,y)\leq z\leq0\}.
\end{aligned}
$$

The three active-constraint gradients are

$$
\begin{aligned}
\nabla F_{\mathrm{front}}&=(0,0,1),\\
\nabla F_{\mathrm{back}}&=(-h_x,-h_y,-1),\\
\nabla F_{\mathrm{footprint}}&=(T_x,T_y,0).
\end{aligned}
$$

The original crowned coordinate has a convex nonnegative radius. Its cubic is convex, so the original cubic-back height is concave on the convex footprint. The longitudinal quadratic crown is also nonnegative and concave there. The shared harmonic cap is concave and increasing in both inputs; their combined height is therefore concave.

The solid is the intersection of a convex footprint cylinder, a front half-space and the epigraph of the negative concave height. Hence its occupancy is convex. This certificate concerns the occupied solid; the clamped extension of the max field outside the footprint is not claimed globally convex or a Euclidean signed distance.

The enclosing quantities are

$$
\begin{aligned}
H&=\frac{0.15\cdot0.4}{0.15+0.4}=0.10909090909090907,\\
\mathbf{c}&=(d_x,d_y,-\frac{H}{2}),\\
\mathbf{e}&=(a,b,\frac{H}{2}).
\end{aligned}
$$

Regular interior height is smooth, with the inherited center extension. Front and back meet at a genuine crease. Exact zero-height poles and multiple active zero constraints have no unique normal: the wrapper returns unresolved status and a NaN boundary normal. No origin displacement, normal adjustment or fitted boundary band was added.

## Bracket-based nonsmooth status

For each intersection bracket, the wrapper uses its spatial uncertainty to bound the three constraint values. Front and back Lipschitz bounds are one and the norm of the height-graph gradient bound. The footprint bound uses the monotone longitudinal function over the enclosing box expanded by that same uncertainty.

$$
\begin{aligned}
L_{\mathrm{front}}&=1,\\
L_{\mathrm{back}}&=\sqrt{1+M^2},\\
L_T(u)&=\frac{2\sqrt{[q(a+u)q'(a+u)]^2+(b+u)^2}}{b^2}.
\end{aligned}
$$

Two constraints whose zero sets remain possible within the bracket are conservatively marked nonsmooth. The uncertainty contracts with the solver bracket; it is not a fitted image-space band. Exact zero-thickness status remains unresolved even at zero uncertainty. All geometry-derived normals come from the same height and level used by intersections.

## Invariants before paths

[Fixture results](fixture-result.json) passed before any path continuation. They cover finite differences at regular front/back points, outward winding, midpoint occupancy, mirrors, pose, uniform length scaling, exact pole statuses and bracket-derived crease uncertainty. Numerical controls supplement the convexity derivation rather than replacing it.

| Case | Maximum regular gradient error | Height bound | Slope bound |
| --- | ---: | ---: | ---: |
| A | 1.003e-10 | 0.1090909091 | 0.5321837552 |
| B | 1.121e-10 | 0.1090909091 | 0.5237430737 |

The actual normalized centers are approximately 0.0011679654 and 0.0047550857 in both references. Their major half-extents remain 1.5032401726 and 1.5274665006; the minor half-extent remains 1.0112242531. Scaling controls change every length coherently. They do not renormalize the actual height gradient.

## Paths and scoped accounting

Four nearest regular cached subrays were selected around each upper, lower, left and right anchor in each reference. This gives 32 launches, not a full native grid. The earlier D0.5 record supplies exits and normals because its H1 exit geometry and directions were already verified unchanged by background distance. All endpoint propagation here uses D2.

Initial internal incidence is vertical. The unchanged shared intersector uses tolerance 1e-11 and at most 64 iterations. Initial front and back encounters count toward each launch's 32-event cap. The saved records contain 992 back/later events plus 32 separately recorded initial-front events, totaling 1,024 encounters.

[The final result](result.json) and [complete paths](paths.json) preserve all actual points, normals, reflected directions, brackets and endpoint roles. Maximum final bracket width is 6.668e-12; maximum absolute level residual is 3.261e-12. There were 549 later TIR or critical events. No incomplete numerical intersection was replaced with a fabricated ray.

| Budget | Actual | Cap |
| --- | ---: | ---: |
| Fixture surface API points | 280 | 2,048 |
| Cached launches | 32 | 128 |
| Encounters per launch | 32 | 32 |
| Total interface encounters | 1,024 | 4,096 |
| Conservatively charged graph evaluations | 833,608 | 3,000,000 |
| New full native grids | 0 | 0 |
| RGB queries / images / fits | 0 / 0 / 0 | 0 / 0 / 0 |

One persistent counter charges before geometry evaluation. Each main geometry batch reserves twenty graph-point evaluations, covering the level, actual height, nested base/footprint/profile calls and arithmetic. Additional longitudinal bracket-bound batches charge separately before execution. Fixture and path phases share this counter without resetting it. These are conservative charges, not a claim that every reserved operation executed.

## Power intervals, not invented radiance

At normal entry, front reflection is exactly four percent for the declared index. The initially transmitted light remains unpolarized, so the first back split uses the exact unpolarized average. Later three-dimensional incidence planes can rotate polarization. Later weights therefore use conservative s/p intervals rather than repeated exact scalar averages.

$$
\begin{aligned}
P'_{\mathrm{reflected}}&\in[P_{\min}R_{\min},P_{\max}R_{\max}],\\
P'_{\mathrm{transmitted}}&\in[P_{\min}(1-R_{\max}),P_{\max}(1-R_{\min})].
\end{aligned}
$$

Every launch retains a capped residual interval. The largest upper endpoint is 9.773e-13; the smallest lower endpoint is 1.346e-31. These tails were not assigned a replacement color. Small residuals do not remove already emitted unsupported or unobserved radiance contributions.

## Endpoint source audit and material roles

Downward positive-power exits were propagated to the D2 plane and checked against each original finite incident kernel and all four bilinear texels. Stored float64 and prospective float32 endpoint positions were both checked. No source RGB was read. Upward/lateral exits were classified as environment roles rather than mapped onto a mirrored UI source.

| Case | Modeled supported background | Unsupported background | Unobserved upper environment |
| --- | ---: | ---: | ---: |
| A | 104 | 16 | 117 |
| B | 104 | 16 | 118 |
| Total | 208 | 32 | 235 |

The [saved power review](power-review.json) retains every unsupported endpoint and its power interval. Unsupported downward exits occur at encounters 16 through 22. Their largest upper powers are 0.000341811 in A and 0.000352166 in B. No threshold discards them. All upper-environment exits remain unobserved, including the initial four-percent front reflection on every launch.

Summed environment bounds over sixteen launches are approximately 1.219–1.243 in each case. These sums are diagnostic interval totals, not simultaneous polarization-exact values. They establish a missing radiance role even though the final internal tail is small. Modeled downward source support still has observed confidence zero and is not photographic validation.

The transmission tone and source PSF were calibrated as empirical encoded-image components. They do not identify environmental radiance, its color space or a specular roughness operator. They were not applied to reflected light. No white/HDR environment, target halo, extra blur, shadow or source extension was invented.

## Disposition and preserved limits

O1 closes as scene-incomplete. A reflected image is not supported by the current source and environment evidence. The permitted [saved review](saved-review-protocol.json) used only the existing path/power records, with no new geometry, RGB, images or fits. There is no automatic repair, restart or additional surface proposal.

The accepted neutral tone and original incident widths remain the experimental transmission state. This wrapper does not alter its saved native pixels. Later stage work requires its own bounded direction; missing reflection input is not evidence that the outline is satisfactory or absent. Shared implementation and final integration remain primary-owned.
