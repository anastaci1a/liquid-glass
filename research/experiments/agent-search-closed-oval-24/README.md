# Search closed grazing-rim oval: incomplete primary transport

**The smooth closed rim supplies grazing normals, but the transmitted-first implementation cannot produce a complete comparison.** Of 98,989 regular native launches, 549 undergo strict total internal reflection at the next interface. Every blocked launch remains required. No source RGB, material field, image, replacement pixel or new selected state is produced.

## Fixed question and geometry

The original upper-rim and lower-return crops contain thin bright boundaries missing from the selected Search reconstruction. This single discriminator asks whether an actual smooth closed rim supplies the corresponding grazing geometry. It does not fit a rim, tune an emitter or infer that the reference light is uniquely reflected.

| Frozen defect rectangle | Original-frame bounds |
| --- | --- |
| Upper rim | `[1440,576,1580,620]` |
| Left cap | `[1418,630,1455,718]` |
| Lower return | `[1440,728,1580,764]` |
| Glyph | `[1467,626,1563,722]` |

The [protocol](protocol.json) fixes the shared `ClosedCircularOval` with zero kappa. Only its analytic radius adapter is element-specific. Shared `trace_closed_orthographic` and `next_convex_boundary` compute actual intersections and normals; neither is copied or modified.

$$
\begin{aligned}
F(x,y,z)&=\frac{x^2+y^2}{R^2}+\frac{(z+d)^2}{d^2}-1,\\
R&=0.9972124917582454,&d&=\frac{0.10909090909090907}{2},\\
\boldsymbol c&=(0,0,-d),&\boldsymbol e&=(R,R,d).
\end{aligned}
$$

The front center is zero, the projected rim lies at negative depth, and the central total thickness equals the original H1 maximum height. Background distance remains two original units below zero, beyond the complete solid. Original L is 89 native pixels, with the same corrected center and reference footprint convention.

## Convexity and one-surface consistency

The solid is a positive-definite ellipsoid. Its Hessian is constant and strictly positive definite, and its gradient cannot vanish on the boundary. Therefore occupancy is convex and the regular implicit boundary is smooth. No concavity assumption about a separate height graph is used.

$$
\begin{aligned}
\nabla F&=\left(\frac{2x}{R^2},\frac{2y}{R^2},\frac{2(z+d)}{d^2}\right),\\
\nabla^2 F&=\operatorname{diag}\!\left(\frac{2}{R^2},\frac{2}{R^2},\frac{2}{d^2}\right)\succ0,\\
F(x,0,z)&=\frac{x^2}{R^2}+\frac{(z+d)^2}{d^2}-1.
\end{aligned}
$$

The last equation is the same solid's central section. The adapter evaluates the shared primitive at radius-scaled coordinates and divides its horizontal gradient components by the same radius. Vertical coordinates and height units are unchanged. Shared front roots, implicit gradients, normals and sections describe one surface.

$$
\begin{aligned}
z_f(x,y)&=d\left(\sqrt{1-\frac{x^2+y^2}{R^2}}-1\right),\\
\nabla F_R&=\left(\frac{F_{0,x}}{R},\frac{F_{0,y}}{R},F_{0,z}\right).
\end{aligned}
$$

At the exact projected poles, orthographic entry is tangent and remains unresolved even though the physical implicit normal exists. No epsilon band, replacement normal or adjusted membership is introduced. Actual native normal tilt reaches 85.00165 degrees, establishing the intended grazing mechanism on this lattice without establishing visible fidelity.

## Clocks and controls

The task started at 05:58:11.523 UTC. Its deadline is 06:18:11.523 UTC, with checkpoint by 06:03:11.523 UTC. [Input identities](input-identity-FIRST.json) verify all frozen Search bytes before controls. The [checkpoint](checkpoint.json) passed at 06:01:02.759 UTC.

There are 56 new fixture rays: unit-index straight coordinates, mirrored index-1.5 paths, exact projected poles and clear misses. Existing primitive controls are reused. The one 225,600-ray native grid is reserved before evaluation and reused for both references. Level queries increment before the shared primitive body.

The declared reservation is 70 level batches per launch. One prose label in the protocol says 67 while its listed worst-case terms sum to 68; the actual reservation remains 70 throughout. This arithmetic-label discrepancy neither lowers the reservation nor resets a counter.

## Concrete branch limitation

| Native primary status | Launches |
| --- | ---: |
| Regular entries | 98989 |
| Complete transmitted branches | 98440 |
| Strict TIR at next interface | 549 |
| Exactly critical discriminant | 0 |
| Other incomplete regular paths | 0 |
| Exact projected tangent hits | 0 |

The shared blocked flag uses a nonpositive Snell discriminant. Saved inspection shows all 549 cases are strictly negative, ranging from approximately -0.990244 to -0.001327. Their launch radii lie between 0.997266 and 0.999989 times the frozen radius. This is a real near-rim reflected branch, not a geometric invalidity or proof that the ellipsoid cannot match the reference.

[Saved path review](saved-path-review.json) locates 98 blocked subrays in each original glass/rim cohort and 15 in the held cohort. All 549 are required by the whole-body union in both references. No partial-glass pixel or source requirement is removed. Complete-path source certification therefore stops before RGB.

The largest retained intersection bracket is 5.135e-12 original L; the largest exit level residual is 9.377e-11. Full native points, normals, internal and outgoing directions, discriminants, brackets and statuses remain in the indexed path record. Blocked outgoing coordinates remain NaN, with their launch records preserved.

A transmitted-first tracer does not follow the internally reflected continuation or quantify its power. No complete reflected-scene ledger is implied. Source support is not certified for the 98,440 completed primary branches merely because their geometry completes.

## Direct-front scene roles

Exactly 98,989 optional direct-front reflection directions are computed from actual saved entry normals. No Fresnel or emitter evaluation is added. Convexity excludes solid reentry for these outward reflected branches, but their next scene object depends on direction.

| Direct-front direction | Count | Scene role |
| --- | ---: | --- |
| Upward | 98682 | Unobserved upper scene; no radiance evaluated |
| Downward | 307 | Meets the modeled background plane before infinite environment |
| Lateral | 0 | None in this lattice |

The downward endpoint follows its actual ray and background-plane intersection. It is never assigned annular black or white as though the plane were absent.

$$
\begin{aligned}
t_{\mathrm{bg}}&=\frac{-D-z_f}{v_z}>0,\\
\boldsymbol p_{\mathrm{bg}}&=\boldsymbol p_f+t_{\mathrm{bg}}\boldsymbol v.
\end{aligned}
$$

| Raw downward support | A | B |
| --- | ---: | ---: |
| Endpoints | 307 | 307 |
| Out of bounds | 155 | 155 |
| Four known bilinear corners | 109 | 116 |
| Unsupported, including bounds failures | 198 | 191 |

These are unweighted direction counts, not power fractions or radiance measurements. Only original known-mask corner lookups are performed. No background color, environment color, Gaussian filter, encoded transmission grade or replacement radiance is applied. The [role review](direct-front-role-review.json) retains every unsupported endpoint category.

## Source and visible scope

Original sources, known masks, vectors, styles, all scoring masks, native AA2, accepted tone, incident sigma 6.75/radius 21 and shadow zero remain frozen. Conditional temporal-mosaic availability remains distinct from photographic or environment truth. Historical fingerprint and original protocol-order disclosures remain unchanged.

There is no changed image and no changed score. Therefore this implementation cannot answer whether the grazing rim reproduces the original upper-rim or lower-return features. It answers the narrower physical question: grazing normals exist, but required TIR continuations and incomplete downward scene support prevent a complete conditional comparison. Reference bright bands are not assumed incident correspondences.

## Usage and decision

| Work | Actual | Cap |
| --- | ---: | ---: |
| New fixture rays | 56 | 64 |
| Native rays | 225600 | 225600 |
| Implicit level points | 4258591 | 20000000 |
| Direct-front direction entries | 98989 | 100000 |
| Known-mask corner lookups | 1216 | 4000000 |
| Fresnel or emitter evaluations | 0 | Not used |
| Incident fields and RGB queries | 0 | No gate passed |
| Conditional comparisons | 0 | 2 |

No second depth, source search, fallback setting, retint, field warp, normal tweak or source repair runs. The original selected Search state and every historical count remain unchanged. The next bounded question was requested before packaging; further branch tracing, scene completion or geometry requires separate authority.
