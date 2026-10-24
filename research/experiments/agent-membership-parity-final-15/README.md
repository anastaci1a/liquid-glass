# Final primary parity under additive membership

**All six fixed configurations pass the agreed primary geometry and metadata contract.** Both shared tracers agree on projected membership, regular entry, unresolved launches and completion. Their regular physical outputs satisfy the unchanged absolute tolerances. This establishes interoperability for the declared fixtures; it does not establish source support, reflected-scene completeness or image fidelity.

| Evidence | Record |
| --- | --- |
| Actual clock, frozen fixtures and caps | [Protocol](protocol.json) |
| Startup code and callback bindings | [Start](started.json) |
| First configuration, reported immediately | [Checkpoint](checkpoint.json) |
| All configurations, errors and counters | [Result](result.json) |
| One-shot harness with deadline wrapper | [Harness](run.py) |
| Exact reviewed accounting dependency | [Callback](../agent-parity-accounting-preflight-14/callback.py) |
| Input and historical record hashes | [First hashes](first-hashes.json) |
| Final readiness | [Ready flag](review-ready.json) |

## Fixed comparison

The shared back is `HarmonicCircularBack(.15,.4)` with index one or 1.5 and background distance two in original length units. Radius scales lateral coordinates and gradients only; height retains its original units. The flat comparator delegates to that same shared back through the approved chain rule.

Each configuration has exactly 25 Cartesian points from the five declared offsets, four axial misses at 1.1 times the radius and four exact poles. Both shared tracers receive all 33 points. No additional fixture, zero-height test, native grid or reflected branch is evaluated.

| Radius | Index | Nested units | Level subset | Status |
| --- | ---: | ---: | ---: | --- |
| 0.9972124917582454 | 1 | 6,551 | 1,075 | Pass |
| 0.9972124917582454 | 1.5 | 6,551 | 1,075 | Pass |
| 1 | 1 | 6,551 | 1,075 | Pass |
| 1 | 1.5 | 6,551 | 1,075 | Pass |
| 2 | 1 | 6,676 | 1,100 | Pass |
| 2 | 1.5 | 6,676 | 1,100 | Pass |

The ordered solver uses tolerance `1e-11` and at most 64 bisections. Comparisons use absolute tolerance `1e-9` original length units for positions and source coordinates, `1e-9` for unit vectors, and zero relative tolerance. No tolerance, radius, index, background distance or surface parameter changed during execution.

## Status and physical-field results

All four agreed boolean fields match exactly over all points. Projected membership includes the 25 regular points and four poles. Regular entry includes only the 25 regular points. Poles are unresolved and incomplete; regular paths and straight misses complete. No incomplete regular path was waived.

Raw legacy `inside` differs exactly at indices 29–32 in every configuration. Flat membership is inclusive and closed membership is strict there. These expected differences are retained in the saved arrays. No legacy array is masked, rewritten or normalized to manufacture equality.

Both source-coordinate NaN patterns match globally. Every clear miss preserves its input coordinates exactly. All pole source coordinates are NaN. These statements concern geometric background coordinates; no source image or confidence mask is queried.

The physical interface comparison cohort is

$$
\mathcal{V}=\mathcal{E}_{\mathrm{flat}}\cap\mathcal{E}_{\mathrm{closed}}
\cap\mathcal{C}_{\mathrm{flat}}\cap\mathcal{C}_{\mathrm{closed}}.
$$

Here entry and completion remain independent fields. Physical back positions, outward normals and outgoing directions are compared only on this common completed regular cohort. Front entries are also checked against the analytical flat front. Raw finite flat direction diagnostics and closed NaNs at misses or unresolved launches are retained without comparison as physical events.

| Completed regular measurement | Maximum difference |
| --- | ---: |
| Background X or Y | 6.217248937900877e-14 original length units |
| Back position | 2.018940570280847e-12 original length units |
| Outward normal | 0, exact |
| Exit direction | 0, exact |

All index-one regular paths are straight within the declared tolerance. No source availability, radiance or reflected-path assertion follows from a complete primary. The nonconcave expanded spline remains outside this convex wrapper.

## Exact retained raw outputs

| Configuration | Raw arrays |
| --- | --- |
| Nonunit radius, index one | [Configuration 00](config-00.npz) |
| Nonunit radius, index 1.5 | [Configuration 01](config-01.npz) |
| Unit radius, index one | [Configuration 02](config-02.npz) |
| Unit radius, index 1.5 | [Configuration 03](config-03.npz) |
| Radius two, index one | [Configuration 04](config-04.npz) |
| Radius two, index 1.5 | [Configuration 05](config-05.npz) |

Every archive retains original point coordinates and all returned fields from both drivers. Saving occurs before comparisons. The harness would retain any returned partial outputs on failure; this execution completed both drivers for every configuration. No older numerical array was opened or recomputed.

## Accounting and deadline enforcement

| Budget | Actual | Cap |
| --- | ---: | ---: |
| Reserved and entered launches | 396 | 396 |
| Flat launches | 198 | Included above |
| Closed launches | 198 | Included above |
| Nested total | 39,556 | 100,000 |
| Closed-level subset | 6,500 | 50,000 |
| Source, RGB, filters, Fresnel, images and fits | 0 | 0 |

The 6,500 level points are already included in the 39,556 total. Categories are 114 scalar-bound operations, 1,044 interface-vector rows, 28,532 point queries, 6,500 closed-level points and 3,366 metadata rows. These budget units are not device-performance measurements.

All configurations reserve 15,000 nested units, 2,000 level points and 66 launches before constructor or tracing work. The exact accepted callback counts generated constructors, bound properties, bevel and harmonic delegates, radius wrappers, interface work and metadata. Persistent global counters are never reset; per-configuration offsets delimit the approved reservation.

The callback SHA is `fc444f33e5422d8f75f7956962516c0fa3e697a32a5a8754d62b39a1f4b93313`. The harness imports that reviewed artifact directly, without copying or editing it. A surrounding profile hook checks wall time before every selected shared, adapter or generated-constructor entry, then invokes its pre-mutation accounting.

Startup verifies pinned shared, callback and old-driver hashes before optical work. All six coordinate arrays and complete future reservations are validated before profiling is installed. Deadlines are checked before each configuration, comparison and packaging step. No optical setup probe, repeated attempt or new setting is used.

The first configuration is saved and printed immediately. A host coordinator sends its structured checkpoint through Sessionsation asynchronously while the same process continues the other five. The checkpoint receipt is native-accepted. There is no blocking stdin or permission wait and no clock reset.

## Preservation and interpretation

The shared numerical pin remains `54681b1128ee345687469e5ab767a6dedd528d87`, SHA `bab1ed8681db4086f394998f12b563a41cc42af3b4fa2afd175191c24a43b428`. No merge or shared edit was needed for this task. The old driver hash is bound independently and remains unchanged.

The stopped parity-11 assertion remains failed, with its original 66 attempted rays and five unexecuted configurations. Parity 13 remains an accounting-prerequisite failure with 66 reserved attempts, 33 entered launches, 117 measured units and conservative 150. These records are not resumed or relabeled by the new six-configuration task.

Search inputs, geometry selection, material, incident blur, foreground, masks, images and historical counts are unchanged. Conditional source mosaics and missing environment radiance remain separate limits. The present result certifies only primary geometry and the agreed metadata interoperability within the six fixed configurations.

The task began at 03:09:21.424 UTC on 24 October 2026 and closes by 03:24:21.424 UTC, including setup, documentation and versioning. Numerical start, checkpoint and finish times are retained exactly in machine records. Primary review determines the next bounded shared question; no scene, target or calibration follows automatically.
