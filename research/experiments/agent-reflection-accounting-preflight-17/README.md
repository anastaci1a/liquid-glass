# Combined reflected-transport accounting preflight

**All 64 synthetic fixtures pass.** One combined callback counts old geometry delegates and the two proposed reflection/Fresnel delegates through the same guarded ledger. No shared numerical module was imported, no real profiler was installed and no optical or mask-array operation ran. Primary review is required before any actual event.

| Evidence | Record |
| --- | --- |
| Actual clock and synthetic-only limits | [Protocol](protocol.json) |
| Immutable combined callback | [Callback](combined_callback.py) |
| Callback hash and source lineage | [Binding](combined-binding.json) |
| 46 old, 12 primitive and six combined cases | [Synthetic result](synthetic-result.json) |
| Synthetic harness | [Harness](synthetic_check.py) |
| Explicit future reservations | [Budget](future-reservations.json) |
| Complete decode cost versus indexed lookups | [Decode budget](decode-and-mask-budget.json) |
| Prior coherent transport proposal | [Plan 16](../agent-circular-reflection-plan-16/README.md) |

## Combined callback and tests

The callback derives from accepted `e02a4470`, with two added rules. Reflection requires matched one-to-sixteen rows of three-component vectors. Fresnel requires one-to-sixteen cosine rows and finite positive real scalar indices. Original matched-shape restrictions remain; general broadcasting is not supported. Scalar array indices, nonfinite values, zero and negative indices are rejected.

All rules reach the same total, per-launch, global-level and per-launch-level checks before modifying any count. Categories and per-function counts update only afterwards. Unknown shared/generated calls and `fresnel_unpolarized` remain rejected. There is no separate interface-only ledger in this artifact.

The first 46 fixtures reproduce the old regression suite. The next 12 reproduce the new primitive cases. The final six test four invalid scalar indices and a mixed synthetic old-query/new-interface ledger: reflection accepts its last available unit, then Fresnel rejects before mutating that complete ledger.

All rejection fixtures compare the entire ledger with a deep copy, including categories and function counts. These are 64 new instrument fixtures, not optical work. Shared source is parsed and compiled without execution; fake frames and inert owners supply only shape metadata. Existing callback and stopped-driver artifacts remain unchanged.

The original callback defaults are retained for regression compatibility. Future transport must instantiate the explicit new limits: 130,000 global nested units, 25,000 global level points, 8,000 nested units and 1,500 level points per launch. `reserve_config` serves as the prospective per-launch reservation boundary.

## Future wall-time wrapper

The callback does not enforce wall time. A future harness must check its separately authorized deadline before installing profiling, before every selected shared/adapter/generated-constructor entry, before each launch/event, before comparisons and before packaging. The wrapper then invokes this callback, retaining its checks-before-mutation behavior.

Hash and shape validation, cache provenance and complete reservations precede any real profiling. Unknown delegates or unexpected shapes stop execution; no accounting repair occurs during a run. This preflight neither installs that wrapper nor implements a transport driver.

## Explicit future geometry budget

Keep the existing radius-adapted harmonic circle, index 1.5 and background distance two. Preserve incident sigma 6.75/radius 21, selected transmission tone, source, style and masks. Reuse the deterministic cached-launch selection from plan 16, without selecting any launch now.

| Proposed future scope | Bound |
| --- | ---: |
| Unique cached launches | 16 |
| Encounters including cached initial events | 384 |
| Cached initial front/back events | 32 |
| New ordered segments | 352 |
| Accepted static nested bound | 121,158 |
| Accepted static level bound | 23,584 |
| Accepted per-launch nested/level bounds | 7,572 / 1,474 |

Add two explicit initial-cache surface checks per launch, using shared level gradients at the retained front/back points. These validate same-surface residuals and cached normals; they do not replace either normal. The 32 added level points cost 160 nested units including all delegates. No such check is executed here.

The scalar setup allowance is 128, including the six scalar units already present in the old bound. It covers bound-property and constructor checks; geometry queries cannot be hidden inside it. Cached field finiteness, dimensions and identity checks remain separately counted cache analysis, not free height queries.

$$
\begin{aligned}
Q_{\mathrm{new}}&=121158+160+(128-6)=121440,\\
L_{\mathrm{new}}&=23584+32=23616,\\
Q_{\mathrm{launch}}&=7572+10=7582<8000,\\
L_{\mathrm{launch}}&=1474+2=1476<1500.
\end{aligned}
$$

The original bounds are preserved, with the additional initial checks visible. Full reservations also fit:

$$
16(8000)+128=128128<130000,\qquad16(1500)=24000<25000.
$$

Level points are a subset of nested units, never an additional total. These new proposed budgets do not reset earlier ledgers. No further optical execution is authorized by their sufficiency.

## Full decoding is separately charged

Sealed metadata records 2,073,600 cells per original known mask, 225,600 native subrays and 56,400 crop pixels. Generator text establishes boolean known/support masks and float64 coverage. Numerical NPZ members and image pixels were not opened here.

| Each support container member | Cells per case | Expected dtype |
| --- | ---: | --- |
| `known` | 2,073,600 | Boolean |
| `incident_known` | 2,073,600 | Boolean |
| `support` | 225,600 | Boolean |
| `required_pixels` | 56,400 | Boolean |
| `required_subrays` | 225,600 | Boolean |
| `coverage` | 56,400 | Float64 |

Full decoding of both mask containers totals 9,422,400 cells and 10,212,000 array-payload bytes. Their sealed compressed sizes sum to 47,748 bytes. Lazy decoding only known, incident-known and support would still read 8,745,600 cells/bytes. None of this work may be mislabeled as merely 5,920 corner queries.

Reserve 4,096 NPY-header bytes per allowed member, or 49,152 for the twelve mask members. Validate exact container hash, member allowlist, declared shape, dtype and expanded byte length before allocation. A mismatch stops rather than widening decode limits. Allocator overhead is distinct from array payload and is not a device-memory measurement.

The original path-cache generator additionally implies a full payload bound of 36,998,448 bytes: twenty full float64 components, four boolean fields and six constant float64 components. Its eighteen members receive a separate 73,728-byte header allowance. The combined cache-and-mask payload bound is 47,210,448 bytes, before runtime overhead. No cache is decoded now.

## Indexed support and material roles

Keep 5,920 actual indexed mask lookups as a separate cap: 5,888 raw/incident-compatible bilinear corners for both mosaics, plus 32 optional cached-primary proof bits. Zero new erosions, source filters or RGB queries are proposed. Hash and header reads do not supply scene radiance.

Initial primary proof reuse requires exact retained subray indices, pixel/source coordinates, geometry/index/distance, source/known hashes and support semantics. It never certifies a new secondary endpoint. Every secondary downward endpoint is audited separately against both original known mosaics, with bounds and all four corners.

The unfiltered role describes conditional specular-backdrop availability. The incident-compatible role requires the complete radius-21 finite footprint via the exact retained erosion. It is a separate compatibility flag, not adoption of blur or encoded transmission tone for specular radiance. Missing or incompatible retained masks stop before future transport; no new erosion or source construction follows.

## Prospective numerical checks

Retain the fixed launch meridional basis from plan 16. At each actual event, measure position, direction and normal residuals against that plane. Proposed limits are `1e-9` original length units for position and `1e-9` dimensionless for unit vectors. Report actual residuals; never project, rotate or renormalize fields to make them pass.

Use actual shared transmission status and discriminant for critical/TIR classification. A returned reflectance of one alone does not prove TIR: a transmitting grazing case can round to that value. Record that distinction. Blocked transmission requires unavailable transmitted direction and consistent total-reflection component weights; disagreement retains incoming power as unknown and stops the path.

A nonblocked result requires a finite regular outgoing direction and the shared positive transmission discriminant. Finite component weights must lie in their physical interval. No replacement normal, epsilon branch, coordinate clamp or coefficient clipping is added. The shared implementation's own arithmetic remains pinned.

For each polarization component, conserve the initial half-unit across supported and unsupported downward exits, unknown environment, unresolved events and remaining continuation/tail. Report closure error before any correction:

$$
\epsilon_j=\frac12-\left(\sum_k W_{j,k}+W_{j,\mathrm{tail}}\right),\qquad j\in\{s,p\}.
$$

A proposed diagnostic roundoff guard per launch is

$$
|\epsilon_j|\le1536\,\epsilon_{\mathrm{mach}},\qquad\epsilon_{\mathrm{mach}}=2^{-52}.
$$

This deliberately encloses the fixed event bookkeeping; it is not an optical score tolerance. Preserve any excess as a numerical limitation and stop the affected path, without renormalization. An unresolved interface keeps its incoming power unknown. No low-weight deletion or small-tail assumption is allowed.

Retain every geometrically available external endpoint, including unsupported and zero-weight rounded cases. Blocked transmission has no fabricated endpoint. The 24-event cap retains its full reflected continuation. Initial front reflection and upward/lateral branches still lack observed environmental radiance.

## Review gate and preservation

The combined callback hash is recorded in the binding and final manifest. It is not yet an authorized transport implementation. Primary review must approve the combined instrumentation, exact decode semantics, extra initial checks and a new timed execution budget before any ray event.

All Search, parity and reflection-plan records remain immutable. Root shared code and the expanded nonconvex work are untouched. This block begins at 03:32:44.368 UTC on 24 October 2026 and ends by 03:42:44.368 UTC, including checks, commit, push and remote verification. No target, reflected image or material calibration follows automatically.
