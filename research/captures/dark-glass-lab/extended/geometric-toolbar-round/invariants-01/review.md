Geometry-only task complete; proposal A interface agreed. Proposal B is inactive.

The private CrownedBevel uses the accepted crowned_footprint functions and imports lead's unchanged bevel_profile and trace_flat_front_orthographic. No empirical map, independent optical normal, source query, image, material, fit or shared edit was introduced. Implementation started 2026-10-22 03:31:37 UTC; final changed-core checks finished 03:37:53 UTC, within the original 15-minute deadline 03:46:37 UTC. All geometry ray calls, including checks under the previous core, total **12,034 / 50,000**. Only toolbar depths .02 and .04 were tested; n=1.5, D=2, core=0, p=3, edge=0, softness=.1, half=(392/170,1). Transform/rejection controls are labeled fixtures, not extra fitted candidates.

The initial 30 checks passed. The mandatory gradient/circle checkpoint preceded the remaining checks. After lead clarified the boundary contract, the original packet was preserved and a separate boundary-v2 packet pinned the new core before execution. Its 13 checks passed, with a second circle-equivalence checkpoint before toolbar status checks. No circle image or unchanged optical gradient calculation was rerendered.

**Current pinned core SHA256:** `f3a7fef6e9150164479454417079619670a5577c04eb576c28f01db49cba2abd`.

The source for review is `localica-agent-geometric-toolbar/docs/liquid-glass/experiments/reconstruction/crowned_bevel.py`, isolated branch `research/geometric-toolbar-222`, base `05fccdfee194098018856b18f2843bd19f1201b6`. The immutable executable packet is `dark-glass-lab/extended/geometric-toolbar-round/invariants-01/boundary-v2/code/`. The earlier pinned source and reports remain in its parent directory. No commits or pushes were made.

Global certificate and limits

Let a=max(half), b=min(half), e=softness*b, R=hypot(x,e), neck=a-b. The accepted longitudinal q is a positive multiple of softplus((R-neck)/e) minus its value at x=0, normalized so q(a)=b. Thus q>=0, q is even and q(0)=0. With C=b/den and s=sigmoid((R-neck)/e),

`q'' = C * [s*(1-s)*x^2/(e^2*R^2) + s*e/R^3] >= 0`.

`rho = sqrt(q(x)^2+y^2)/b` is convex by convex coordinate composition with a norm on the nonnegative orthant; equivalently use (q(x),abs(y)). It is a level coordinate, **not a homogeneous norm or Euclidean distance**. `T=rho^2` gives a convex continuous footprint, including the tiny nonflat crown. The shared height `h=depth*(1-rho^3)` is decreasing and concave as a function of rho, hence concave in (x,y). Therefore `{T<=1,-h<=z<=0}` is a closed convex solid. At the center, cubing the norm gives a C2 extension with zero gradient and Hessian. The rim T=1 is a crease, not a globally smooth solid.

Since q is monotone for x>=0 and q(a)=b, the footprint implies |x|<=a. Convexity gives |q'(x)|<=q'(a), and

`|grad rho| <= max(1,q'(a))/b`,

`0<=h<=depth`, `|grad h|<=3*depth*max(1,q'(a))/b`.

The certified global slope bounds are .06 and .12, both below `1/sqrt(1.5^2-1)=.8944271909999159`; maximum heights are .02/.04, below D=2. This is an analytic certificate. Finite-grid Hessian/slope observations corroborate it; they are not asserted to prove a global bound. The convex-solid certificate supports the restricted transmitted-primary path without later back reentry, under the shared orthographic assumptions. It does **not** certify Fresnel/radiance completeness, reflected paths, a finite camera, or image fidelity.

Checks and measurements

- Height and analytic derivatives equal the true radial circle fixture bit-exactly; all shared tracer outputs are bit-exact, including the new exact-crease status. A softened equal-half crown was deliberately not used as the circle.
- Gradient finite differences at steps 1e-5 and 5e-6 have maximum error 7.651e-12 across the two depths. Center Hessian estimates decrease linearly to zero. Mirror/quarter-turn errors are zero; scaling all lengths by 2.5 has maximum error 8.882e-16.
- Unit-index paths are identity. Snell tangent residual is at most 3.331e-16; reverse propagation residual at most 2.221e-16. Interior exit paths are unit, downward/outward and reach z=-2; minimum discriminants are .9927676764/.9712035066.
- Section and mesh vertices call the same height function. Cardinal boundary heights close exactly to the front plane. Whole-solid edge normals are undefined, although one-sided face limits can be plotted with that label.
- `boundary_mask` tests actual T==1, or hypot/b==1 for the radial fixture. Exact crease hits return NaN source/back/normal and complete=False. Clear misses retain straight paths. A tolerance used by the section's diagnostic label does not alter rays, inside tests or masks. Shared auxiliary exit_direction/path fields on an unresolved hit are not valid transmitted paths and must never be rendered.
- Unsupported global slope and D<=maximum_height are rejected. Explicit TIR and exactly k==0 grazing return no transmitted direction. No fabricated source coordinate or extra normal was added.
- Changed-core regular toolbar outputs match all saved earlier outputs exactly at 700 strict-interior points per depth. No new source arrays, field samples or optical candidates were introduced.

Execution record

Commands ran in the existing Docker container, not the moving /workspace renderer. Each driver inserts its pinned code directory before imports. The first invocation stops at its checkpoint; `--remaining` loads that checkpoint, without repeating its completed tests.

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/invariants-01/check_geometry.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/invariants-01/check_geometry.py --remaining
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/invariants-01/boundary-v2/check_boundary.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/invariants-01/boundary-v2/check_boundary.py --remaining
```

These are the exact historical commands; the drivers enforce the recorded absolute deadline. A later independent replay requires its own explicitly authorized budget, not a silent extension of this run. Reports, checkpoints, dependency hashes and raw geometry-only NPZ fixtures are retained. No PNG/image output exists in this experiment.

Transfer agreement and next authority requested

All profile evaluations, Snell refraction, back hit, exit direction and background intersection calculations transfer unchanged from circle to toolbar. Only the footprint coordinate and its exact gradient differ; aspect ratio/softness and sag are real surface parameters. Sections use the same surface. The flat front, camera, index and background distance are shared. Proposal B remains conditional and unimplemented.

This establishes mathematical compatibility, **not successful visible refraction**. Lead's three under-refracting circle diagnostics remain honest negatives. Existing source/registration/glyphs and fixed crops remain unchanged and read-only. The old empirical ray-domain proof cannot certify these new physical ray addresses. Before any authorized image, freshly verify whole shape, every scored subray and actual finite contributing filter support. The exact crease must remain unresolved, not covered up.

Mail's smooth source would test tone/placement, not optical transfer. Existing paired Music Navigation text-backed inputs are a candidate textured held-out control only after checking their retained source provenance and supported domain; this task did not inspect/adopt those inputs or claim them as validated. No new source acquisition or third-control study was started.

Requested lead review: accept/reject this private adapter and certificate, then declare a short unblurred fixed-source diagnostic budget and source-domain controls. No image, fit, material change, second surface family or automatic monitoring loop is authorized by this completed task.
