# Boundary metadata contract peer review

**Recommend the additive fields, with explicit scope and field-validity rules.** They distinguish projected geometry from a regular entry without redefining legacy `inside`. They do not establish completed transmission, source availability or reflected-scene support. The stopped parity checkpoint remains failed; no remaining configuration was run.

| Evidence | Record |
| --- | --- |
| Scope, clock and zero-work limits | [Protocol](protocol.json) |
| Immutable source and report hashes | [First hashes](first-hashes.json) |
| Original strict membership failure | [Stopped result](../agent-circle-radius-parity-11/result.json) |
| Frozen shared definitions | [Optics source](../../../reconstruction/geometric_optics.py) |
| Existing source-support separation | [Renderer](../../../reconstruction/geometric_render.py) |

The root forensic record is pinned to commit `2a78e0fab81a3b27baaee2e651784bbbb8c66d7c`, folder `research/experiments/circular-boundary-contract-02`. Its report and result were read through Git objects. No moving main was merged. This review cites its saved measurements without opening, remapping or reducing numerical arrays.

## Recommended semantics

| Field | Contract |
| --- | --- |
| `inside` | Preserve the driver-specific legacy bytes and definition. |
| `projected_inside` | Inclusive membership in the certified view-ray projection of the solid's footprint. |
| `regular_entry` | Entry-domain membership with unresolved launch boundaries and degenerate zero-thickness launches excluded. |
| `boundary_unresolved` | Preserve existing unresolved launch classification; never infer a usable crease normal. |
| `complete` | Preserve primary background-path status, including complete straight misses. |

For the current supported circular adapters, let the legacy membership and unresolved launch sets be the following:

$$
\begin{aligned}
\mathcal{I}&=\{\text{legacy inside}\},\\
\mathcal{B}&=\{\text{boundary unresolved}\},\\
\mathcal{P}&=\mathcal{I}\cup\mathcal{B},\\
\mathcal{E}&=\mathcal{I}\setminus\mathcal{B}.
\end{aligned}
$$

These formulas implement the proposed fields for the certified fixtures. The inference requires unresolved projected-boundary flags to denote points in the inclusive footprint, and the adapter's legacy membership to cover every other projected interior point. It is not a substitute for the adapter's geometric contract.

## Why the definitions match the geometry

The flat tracer takes inclusive membership from `height_gradient` at line 165. It adds zero-thickness launches to unresolved status at lines 167–168. The closed tracer takes strict front membership at line 234; the circular wrapper uses a strict radial inequality at line 318 and exact radial boundary classification at line 320.

At a regular circular interior point, both proposed fields are true. At an exact crease, only projected membership is true. At a clear miss, both are false, even though the unmodified `complete` flag is true and the source coordinates preserve the straight ray.

| Geometric event | `projected_inside` | `regular_entry` | Completion implication |
| --- | --- | --- | --- |
| Regular primary entry | True | True | None; exit must still be checked. |
| Exact projected crease | True | False | Incomplete, unresolved source coordinates. |
| Clear miss | False | False | Straight primary path may be complete. |
| Regular entry followed by unavailable exit | True | True | Incomplete exit remains incomplete. |

The closed driver's entry selection occurs at line 238. Exit-event regularity, refraction and downward-background reachability are evaluated later at lines 245–253. Thus a regular entry can precede an unresolved secondary intersection, total internal reflection or a non-downward exit. Neither proposed membership field changes those outcomes.

## Cases where the shortcut is not sufficient

The flat primary API allows nonnegative height more generally than the positive circular fixture. An interior zero-height point is already included in its footprint but added to `boundary_unresolved`. Therefore that existing field cannot universally be described as only a projected silhouette boundary. The proposed `regular_entry` definition must also exclude such degenerate launches.

An adapter using a widened numerical boundary band outside the true footprint would make the union formula overstate inclusive membership. An adapter returning only successful exits as legacy `inside` would omit projected points after a failed path. Neither behavior is the reviewed circular contract. Future adapters require explicit projection and launch semantics, not blind reuse of the shortcut.

A nonconvex or disconnected view-ray occupancy may need multiple entry intervals. Two booleans do not certify those branches. The selected nonconcave expanded spline remains outside `CircularHeightSolid`; this metadata proposal does not authorize a convex intersector for it.

## Field validity remains a separate contract

Additive metadata alone does not make every legacy array or NaN pattern interchangeable. The flat tracer returns its computed `exit_direction` for misses and unresolved launches at line 186. The closed tracer initializes outgoing directions to NaN at line 236 and fills only selected interior events. Preserve those bytes; their off-path meanings are not physical exit directions.

A future parity protocol should compare regular physical back positions, normals and outgoing directions only on their explicitly valid event cohort. For completed transmitting primaries, that cohort requires both regular entry and completion. Source-coordinate comparison separately includes complete straight misses and unresolved NaNs. This is a prospective validity contract, not a waiver of the failed original assertion.

For an incomplete secondary exit, membership describes entry geometry only. It does not authorize using any finite placeholder direction, assigning a crease normal, or declaring environment support. Availability of normals at a particular resolved event must remain distinct from availability of a complete background path.

The renderer already checks primary completion before sampling and performs independent finite source-support checks. Neither new field should automatically replace its legacy integration membership or alter coverage, scoring masks, source filtering or compositing. Any future consumer migration needs its own explicit review.

## Evidence scope and verdict

Root reports matching boundary/completion flags and NaN tangent coordinates for the saved first fixture. It reports exact regular coordinates, normals and directions, with maximum exit-position difference `1.9118734373435586e-12` original length units. Clear misses are exact identity. These are attributed forensic findings, not independently recomputed values in this peer review.

They support the interpretation that the first failure concerns strict versus inclusive API membership. They do not retroactively pass the original test, establish selected-index parity or execute the other five configurations. The original 66 attempted rays and all failure records remain unchanged.

Before another execution, pin the root-owned additive implementation and its contract. Specify unchanged legacy fields, exact projection/entry definitions, zero-thickness treatment and per-field validity cohorts. Then declare a fresh bounded parity budget and expected statuses. No implementation, rerun, source audit or reflected image is authorized by this review.

Search geometry, tone, sources, masks, foreground, images and counts are untouched. Mathematical membership does not establish hidden photographic content, source texel support, observed environment radiance or fidelity. All prior provenance and ordering limitations remain.
