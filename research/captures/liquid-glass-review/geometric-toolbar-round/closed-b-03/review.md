Closed surface B is implemented privately and passes its bounded geometry tests. This is mathematical adapter evidence, not visible fidelity or a certified optical path. Lead owns all tracing and public integration. No source, images, fitting or shared edits occurred.

The agreed Closed two-interface extension was read before invariants. The adapter exposes:

```python
ClosedCrownedSurface(half=(392/170, 1.), eta=.15, kappa=0. or 1/3,
                    softness=.1)
surface.level_gradient(points)  # (...,3) -> (F, gradient)
surface.front_height(x,y)       # (z, strict_inside), strict T<1
surface.boundary_mask(x,y)      # exact T==1 projected tangent
surface.half_extents            # (a,1,eta)
surface.center                  # (0,0,-eta)
```

The outward normal is normalized gradient on the boundary, with medium-facing normal selection left to the shared tracer. `front_height` gives the actual finite equator height with strict_inside=False; outside the footprint it returns NaN. It never projects/clamps a miss into the shape. Projected tangencies are distinct from regular entries. This smooth implicit equator is not A's crease.

Private source: `localica-agent-geometric-toolbar/docs/liquid-glass/experiments/reconstruction/closed_crowned_surface.py`, branch `research/geometric-toolbar-222`. Original A/history is preserved. The self-contained private packet is `dark-glass-lab/extended/geometric-toolbar-round/closed-b-03/`.

Exact SHA256 values:

| File | SHA256 |
|---|---|
| closed_crowned_surface.py | ededf4354c68bb87cf53612737c9a59cfe9fa3aee2e3ffe545c71024e1c70ecd |
| unchanged crowned_footprint.py | 2488c958d0749b707d341945ee354726eddc3d66c4c3388b619edb7d9d4532b8 |
| agreed shared interface at test time | ba8a0ad78ffeb892060eb3a991fba650c05c43e8835724f2475a9f12f664ea29 |

One surface and its certificate

Use the exact accepted crowned footprint T=(q(x)^2+y^2)/b^2, a=392/170, b=1. With X=x/a and u=(z+eta)/eta:

`F = T + (1+kappa*X^2)*u^2 - 1`

`grad F = (T_x+2*kappa*x*u^2/a^2, T_y, 2*(1+kappa*X^2)*u/eta)`.

The same F gives front/back roots

`z± = -eta ± eta*sqrt((1-T)/(1+kappa*X^2))`.

There is no independent normal law, displacement map, painted geometry, separate mesh profile, material or source sampler. `section` and the mesh generator call these same sheet roots; their vertices are then checked against actual level_gradient.

The unchanged q is nonnegative, even and convex, with q(0)=0, q(a)=b and q' increasing. Thus T is convex. In coordinates (X,u), G=u^2+kappa*X^2*u^2 has Hessian diagonals 2*kappa*u^2 and 2*(1+kappa*X^2), cross term4*kappa*X*u, and determinant

`4*kappa*u^2*(1-3*kappa*X^2)`.

For 0<=kappa<=1/3 and |X|<=1 these certify positive semidefiniteness. Adding T certifies F convex on that entire enclosing strip. All F<=0 is inside the strip: outside |x|>a, monotonic q implies T>1 while the added term is nonnegative. Therefore the solid is convex. It is closed and compact, contained exactly in the bounding box centered at (0,0,-eta) with half extents(a,b,eta). **F is not claimed convex everywhere in R3**; root's line-convex intersection algorithm must restrict its reasoning to the enclosing box/strip.

The boundary is regular. For u!=0, F_z!=0; for u=0, T=1 and gradT!=0. A quantitative lower bound follows because one of q^2/b^2, y^2/b^2 and (1+kappa*X^2)*u^2 is at least1/3 on F=0. Convex q gives |q'|>=q/a within the strip; its contribution to F_x has the same sign as the kappa term, so no cancellation occurs. Hence

`||gradF|| >= min(2/(3a), 2/(sqrt(3)*b), 2/(sqrt(3)*eta))`

`= .28911564625850344 > 0`.

The interior center gradient is zero, appropriately: the lower bound applies to the boundary, not to all space. At T=1,u=0, the implicit surface remains regular while the graph derivative can diverge and the orthographic projected ray is tangent. That ray is not a regular entry; boundary_mask must be respected by root's tracer.

Checks and retained geometry

The mandatory gradient/circle checkpoint preceded remaining tests. All24 checks passed: analytic/finite-difference gradients, exact independent oblate-ellipsoid fixture, front-height/strict/boundary statuses, reflection about each center plane, rigid coordinate-frame covariance, all-length scale2.5, analytic convexity/Hessian corroboration, boundary chord corroboration, positive global regularity bound, closed mesh topology, actual sections/equator. A frame rotation is not a claim that an elongated crown is rotationally symmetric.

Maximum finite-difference gradient error was 1.135e-9 at steps1e-6/5e-7. The true radial T=x^2+y^2,kappa0 fixture matches independent ellipsoid F and gradient exactly. This is **not** a softened equal-half crown. Root owns its actual circle adapter; equality to that implementation remains a separate shared-code test, not a claimed completed replay.

Each κ has 1,986 mesh vertices and 3,968 triangles. Every undirected edge belongs to exactly two faces, no triangle is degenerate, and orientation follows the actual outward gradient. Maximum level residual across mesh/sections is 6.662e-16. Sampled minimum gradient norm is1.99370, above the analytic global bound. Sampled Hessian eigenvalues and chord tests corroborate, rather than establish, the global proof. A piecewise planar mesh is an approximation between its exact surface vertices.

Artifacts, with no image output:

- `surface-0.obj`, `surface-one-third.obj`: closed geometry meshes.
- `geometry-0.npz`, `geometry-one-third.npz`: vertices, faces, actual outward gradients and sections.
- `sections-0.csv`, `sections-one-third.csv`: x-front/x-back/y-front/y-back actual geometry.
- `checkpoint.json`, `report.json`, `code-hashes.json`: execution and provenance.

Only eta=.15, κ=0/1/3 were actual toolbar sets. The true-circle and all-length-scale controls are declared invariants, not additional fitted shapes. The driver records18,701 level-point evaluations and **zero geometry rays of30,000 allowed**: there is no intersection/tracing implementation here. There are zero images, fits and source operations. Both commands below completed inside the original15-minute wall budget; the absolute deadline is enforced without reset:

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/closed-b-03/check_geometry.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/closed-b-03/check_geometry.py --remaining
```

The second command loads the checkpoint instead of repeating its tests. These are historical run recipes; a later independent run needs its own explicit budget. No native images, source/kernel/domain proof or previous optical checks were repeated.

What this shape may address, and what remains unproven

The smooth front/back join removes A's rim crease while retaining the exact orthographic XY crown footprint. κ changes actual longitudinal thickness/crown without changing that projection. At the center,

`front_xx = -eta*kappa/a^2`, `back_xx = +eta*kappa/a^2`.

At κ=1/3 this is ±.009403633902540608/L, so the shape has a genuine central longitudinal curvature absent from A. At κ=0 the zero longitudinal second curvature persists; this control does not magically solve the d-stroke defect. Physical two-interface entry/exit may now generate different horizontal stretch, shoulder behavior and underside compression, but none is established without the shared tracer and visible tests.

The front is curved and total center thickness is2eta=.3L; this is not the same thickness as earlier A depths. Eta was authorized, not fitted or measured from the screenshot. TIR, exact tangencies, near-critical branches, root tolerances, complete ordered intersections, background reachability, Fresnel/radiance, finite camera and new source addresses remain unverified here. No old source proof can transfer. Estimated hidden-source uncertainty and glyph/PSF limits remain historical, not newly inspected or changed.

Immediate readiness and the next-task request were sent to lead before packaging; native queue acceptance is confirmed, consumption unknown. Next review should accept/reject the adapter certificate and let root integrate it with root's ordered two-interface tracer, then declare one bounded intersection/Snell/reciprocity/branch test budget. No B image, material fit, finite camera, extra family or helper tracing was started. This task is stopped after sealing the packet.
