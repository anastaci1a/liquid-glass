# ARCHIVE/PLUS geometry audit — read-only proposal

Authority: Ana’s GEOMETRY-FIRST-DIRECTIVE.md. This supersedes the historical queues and pass quotas. This audit makes **zero image renders, ray evaluations, fits or implementation edits**. Viewing retained images is not a new render. The old Close result is closed as a one-pass partial result, with its accepted baseline, rejected evidence and worktrees preserved.

## Reference, defects and frozen evidence

The reference is WWDC219/710; the registered text donor is219/720. Native target1920×1080, center(960,542), half-extents(392,170), L=170px, major/minor ratio392/170. Original full crop[475,285,1445,845]. The accepted crowned footprint has softness0.1. Keep source/masks/registration and glyphs unchanged; its implicit coordinate is NOT Euclidean signed distance.

Ana’s observations, before any experiment:

- Top/middle and cap/body: a minute continuous crown; no abrupt straight-tube/circular-cap curvature seam. Pass03/README identifies the old capsule’s second-derivative jump and distinguishes XY silhouette from depth crown.
- Final `d` of “around”: its right stroke should bend progressively through more of its height, with increasing horizontal stretch toward upper/lower regions and a smoother transition into the inverted stroke. This is not a request merely for a larger displacement coefficient.
- Underside: inverted/compressed text should retain faint visibility with softer boundaries. Calling this a “reflection” describes the observation; whether it is a transmitted fold, an internally reflected branch or another effect is not established.
- The historical image is a close visual control. Do not replace it casually or conceal geometry with ordinary blur. Dispersion is separate from ordinary blur; neither is identified by the present source.

Use exact existing native crops: upper[650,369,1270,468], adjoining d-stroke[960,468,1120,550], underside[650,650,1270,726]. Preserve older crops separately. Historical revision3 underside glass RMSE worsened5.062311→5.470541; it remains unresolved. Existing assets toolbar-d-stroke-current.png and toolbar-underside-current.png were inspected, not regenerated.

Frozen accepted recipe: docs/liquid-glass/experiments/reconstruction/studies/archive-plus/review-round/pass-03.json at fetched main05fccdfee194098018856b18f2843bd19f1201b6. Accepted epoch d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d. Historical E6.790203130095, glass5.796156406403, rim8.677568435669, exterior11.466962522841, archive13.142080481293, plus3.304110822041; these are retained results, NOT new geometric-model scores. No old .5% threshold or microscopic pass quota carries into this directive.

SourceSHA256 6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b; target5bb59714854d0bd019d689b3e8c444dd82b057d6abdc9275ca88a8295692bbf8; masksda7d9dec1b557f91321e9ed5aaef5a4416371cbd5657b83e2ff6fccb86b0aa53. Use original epoch files, NOT source23/4k. Source construction combines registered uncovered text and estimated paper after erasing the source lens/shadow rectangle. It assumes blank hidden content:92009/188771 glass pixels lie in estimated source. Registration and text PSF/codec error remain; these are not observed hidden RGB or exact typography. Existing source37 study shows that source-width/PSF disagreement can exceed tiny proposed d-width changes; this is not a bound proving all stronger geometric changes unidentifiable.

Archive SVG is an approved symmetric solid geometric trace, not an exact original Apple glyph (SHA0a585750c7ef62d1a337bd4465deb1da651128450183bec9451adff649763cd6). Plus is an original SF plus outline (SHA846f23109fbb184ad823c1f53029617bcee88f85750e17a97235fe0496762c6e), with UI weight/placement still uncertain. Freeze both poses/colors; no glyph correction in this audit.

Historical source sigma=11nativepx, post sigma=1.25nativepx, source-clear transition and empirical encoded-RGB power/affine lighting remain HISTORICAL. The first new geometric comparison must explicitly set optical source/output blur to ZERO. The unchanged source PNG still contains capture/interpolation PSF; zero added blur is not deconvolution. AA remains finite pixel integration. Source/input bytes are not changed by making a separately labeled unfiltered geometric diagnostic. No inherited distance-band lighting, intensity response or copied context should masquerade as geometric evidence.

The historical139059200-address source proof certifies only the old empirical map/grid/filter. It does NOT transfer to a new physical surface or camera. Before a future image evaluation, certify every whole-footprint AND original-scored subray (including clear misses/outside the predicted outline), branch reaching the background, bilinear footprint, and any explicitly active finite filtering. Preserve the original masks and source domain; reject undefined paths/samples rather than clamp, drop mask pixels or extend input.

## Existing implementations: what transfers and what does not

1. curvature.py/solid.py: actual scalar height and analytic normals, Snell/Fresnel branches, event histories and reported residual internal energy are useful. `next_boundary` assumes convex occupancy and fixed box bisection; arbitrary crown/profile parameters are NOT certified convex. Entry assumes an orthographic camera and an explicit top graph. It is not a generic ordered-intersection API for arbitrary finite cameras. The old epsilon and fixed iterations need residual/bracket reporting and independent convergence before reuse.
2. Private toolbar_back_surface.py and sextic extension: physical height and its complete gradient replace the empirical displacement when activated. However h remains positive at T=1; front/back graphs alone do not close the lateral solid. Outside T they return identity maps, not side-surface intersections. Height/slope bounds certify a restricted normal-entry comparator, not an entire object. Earlier native proposal was rejected (E13.374 vs6.870); that single failure is not a lower bound on physical image fit. Retain it; do not rerun.
3. switch_two_surface.py/EuclideanSurfaceStudy: front and back are coupled geometrically, with an iterative back hit and branch/clearance checks. It obtains inherited `d,J` through `super().geometry_field`, rejects side exits, and retains an extra flat-entry restriction. Although its final source coordinates are replaced by physical surface rays, that superclass/shading dependency and graph-only boundary make it unsuitable as the new shared solid interface. Do NOT subclass it for this toolbar.
4. surface_compatibility.py and perspective_back_surface.py: necessary inverse graph-gradient/branch equations, not globally reconstructed solids. Nonzero map curl alone neither proves nor disproves physical realizability. The saved toolbar compatibility study found robust failures for the declared flat-front comparator and unresolved boundaries; it does not rule out an approximate surface, different camera or two-sided object.
5. Lead’s new geometric_optics.py draft: shared unit-vector Snell and `height_gradient`/maximum_height/slope_bound contract are an appropriate first restricted adapter. CircularBevel is certified only for its stated concave height; another class needs its own proof. It currently does not implement finite-camera entry/ordered intersections, general side entry, smooth closed two-sided surfaces, or complete reflected/TIR paths. Its `complete` flag must stay restricted to its certified transmitted case and clear misses.

## Exactly two surface proposals

All equations below use coordinates normalized by L, x right/y down/+z toward viewer. The front reference plane is z=0. Background is z=-D; indices and camera are explicit. Let a=392/170, b=1, epsilon=0.1, and reuse the accepted crowned_footprint.longitudinal/field functions:

T(x,y)=q(x)^2+y^2; q(0)=0, q(a)=1; exact T_x,T_y come from that function. q is nonnegative, even, smooth and convex; q and its derivatives must not be fitted independently. r=sqrt(T) is a gauge, NOT a Euclidean distance. q has no exactly flat body interval.

### A — first: closed flat front with a certified concave back

Choose p=3 fixed initially and physical depth eta>0 (no numeric candidate depth is chosen in this audit):

    K_A = {T<=1, -h(x,y)<=z<=0}
    h = eta*(1-T^(p/2))
    grad(h) = -eta*(p/2)*T^(p/2-1)*grad(T)

Use the continuous center limit (gradient0); h is C2 for p>=3. r is convex: it is the Euclidean norm of nonnegative convex q and |y|. Therefore r^p is convex, h is concave, and K_A is convex/closed. Maximum height eta. Since q' is increasing on[0,a], M=max(1,q'(a)) gives |grad r|<=M and global slope bound eta*p*M. For n>1 choose/certify slope_bound<1/sqrt(n²-1), plus D>eta. The exterior indices remain explicit if other than1; the stated bound assumes glass-to-air n.

Front outward normal(0,0,1); back outward normal normalize(-h_x,-h_y,-1). At T=1 front and back meet with a real rim crease: do NOT call this a globally smooth shoulder or invent a normal there. Tag the degenerate edge explicitly. This is the honest flat-front/convex-back CONTROL, not a promise it explains Apple. Cap/body continuity within XY and the back comes from the same smooth q.

For normal orthographic entry the internal ray is vertical and hits(x,y,-h) exactly. Surface Snell yields the exit; a transmitted outward ray cannot reenter the convex body. This fits the lead’s restricted `height_gradient`/bounds adapter after certificate agreement. For circle T=x²+y² it is EXACTLY CircularBevel(core0,depth eta,power3,edge0): shared physics/shape logic can transfer without a per-control warp.

Limitation: this ties long-axis depth curvature to the very shallow accepted q. It may fail to produce sufficient d-stroke horizontal stretch in the body. Do not free normal/tangent coefficients or alter the silhouette to hide that failure. Stronger normal tilt can also cause folds or TIR; do not confuse a fold with a reflected branch or silently replace TIR by a pixel.

### B — conditional geometric alternative: smooth closed biaxial two-sided solid

If the flat-front limitation is visible, propose a genuinely different closed surface, not a displacement patch. Let u=(z+eta)/eta and X=x/a:

    F_B = T(x,y) + (1+kappa*X²)*u² - 1
    K_B = {F_B<=0}, eta>0, 0<=kappa<=1/3
    grad(F_B) = (T_x+2*kappa*X*u²/a, T_y,
                 2*(1+kappa*X²)*u/eta)

Every normal is normalized grad(F_B). Front/back sections solve the SAME equation:

    z_± = -eta ± eta*sqrt((1-T)/(1+kappa*X²)).

They meet regularly at T=1,z=-eta: grad(T) is nonzero there, so there is no graph-normal singularity or cap/body seam in the implicit surface. At the center the front is0 and back-2eta. Orthographic XY projection remains EXACTLY the frozen T<=1 footprint; kappa changes actual longitudinal depth crown independently of that projection. There are no pasted effects or per-crop degrees of freedom.

Sufficient convexity certificate on |X|<=1: for G=u²+kappa*X²*u², Hessian determinant=4*kappa*u²*(1-3*kappa*X²)>=0, diagonals nonnegative. Add convex T; the enclosing XY strip is convex, so K_B is convex. Surface gradient is nonzero on F_B=0: if u!=0 the z component is nonzero, otherwise T=1 has nonzero XY gradient. This is a mathematical proposal, not a numerically verified implementation. kappa=0 gives a smooth shared-gauge body; the circle limit with kappa0 can be tested with unchanged material/camera/indices.

This requires a generic closed-solid intersection/path extension beyond the present height tracer, owned by lead. It may have TIR and upward/environment branches near the edge. They must be traced/reported, not excluded as if they were transmitted backdrop rays. Finite camera changes the projected silhouette, even though orthographic projection is fixed; preserve reference masks and report that discrepancy rather than recenter/re-register/refit the source.

## Shared interface recommendation — agreement requested, no implementation yet

Reuse lead’s `refract(incident, against_incident_normal, n_from, n_to)` with unit vectors and explicit TIR. A surface returns OUTWARD normals; the path layer chooses the opposing normal and medium transition once. Do not mix those conventions in per-control code.

Restricted first adapter: `height_gradient(x,y)->h,hx,hy,inside`, `maximum_height`, `slope_bound`, and a reviewed concavity/footprint certificate. Toolbar A implements only this interface privately after agreement; it does not inherit Study.geometry_field or expose any image displacement function.

Generic extension request (lead-owned): `intersections(origin,direction,t_interval,tolerances)->ordered events`, with t, point, outward_normal, surface_id, entering/exiting/tangent classification, root residual and bracket uncertainty. `sections/mesh` consume the same implicit/height functions and parameter object. Camera/IOR/background plane are scene objects; texture lookup and finite AA are outside tracing. Camera returns unit directions from orthographic or explicit pinhole geometry; never substitute a fitted map.

For convex B, intersect its enclosing box then use convex F(ray(t)) and monotone directional derivative to isolate the interior minimum and bracket the entry/exit roots. Proposed limits for agreement:64 safeguarded bisections per bracket, dimensionless implicit residual1e-10 AND normalized t-bracket width1e-9; tangent/ill-conditioned cases report unresolved status, not success at a fixed iteration. These tolerances are proposals requiring convergence/scale tests, not current guarantees. Plane/back-edge coincidences must be explicit events, not epsilon nudges that change source addresses.

Path results distinguish MISS, TRANSMITTED_TO_BACKGROUND, TIR/reflected branch, ENVIRONMENT_EXIT, ROOT_UNRESOLVED, and SOURCE_UNDEFINED; report events/branch weights/residual energy. A miss may use the ordinary clear ray; an invalid solid path may NOT. Background hit is a physical plane intersection. For pinhole camera(0,0,C), source projection at the plane is defined by the same camera: physical backdrop U maps to registered no-lens source coordinates U/(1+D/C). Old registered PNG coordinates are not silently treated as physical z=-D coordinates.

First geometry diagnostics should be raw texture transmission/valid-path and same-surface ray/section outputs; keep any incomplete reflection/environment term explicitly unresolved. No empirical image-map lighting normal, independent normal scale or fitted foreground response can compensate for failed geometry. A transmitted branch alone is not a complete radiance solution when nonzero reflected energy is omitted.

## Next task / budget request before packaging finishes

Recommend agreeing interface A with lead first, then ONE private geometry-only invariant task before any image fit/render: analytic-gradient consistency; circle/core0 exact equivalence; scale/mirror; explicit unit-index/plane limit; closed boundary and grazing/TIR/missing-path cases; same-parameter section/intersection equality. Ask lead to specify/approve physical eta/n/D/camera test values, wall/evaluation limits and held-out reference before execution. This audit authorizes none of those evaluations. Suitable transfer set: toolbar A and lead’s circular control plus a held-out same-family toolbar such as Mail ONLY if its independent source/shape supports geometric observations. Smooth Mail fields cannot validate text refraction/dispersion; an additional textured held-out observation may be required. No target/control adoption or paired claim here.

Report one recommended result after at most three substantive proposals, including rejects. Keep mathematical correctness, visible agreement, cross-control transfer and device speed separate. No final media during an unpromising geometric study.
