# Shared membership metadata without legacy changes

**Additive contract verified.** Both geometric drivers now return `projected_inside` and `regular_entry`. Every existing output remains exact against the pinned implementation, including different legacy direction diagnostics at misses and unresolved launches. No geometry, selected image, source or tolerance changes.

| Evidence | Record |
| --- | --- |
| Declared scope and limits | [Protocol](protocol.json) |
| Old/new controls | [Check](check.py) |
| Exact legacy comparison and source hashes | [Result](result.json) |
| Conservative wrapper accounting | [Accounting](accounting-review.json) |
| Preserved earlier failure | [Boundary diagnosis](../circular-boundary-contract-02/README.md) |

## Membership has distinct roles

| Field | Meaning |
| --- | --- |
| Legacy `inside` | Preserved adapter/driver convention; not standardized retroactively |
| `projected_inside` | Inclusive projected footprint for the certified adapter |
| `regular_entry` | Geometrically regular launch membership, excluding unresolved launches |
| `boundary_unresolved` | Existing unresolved launch flag, including interior zero thickness in the flat driver |
| `complete` | Existing complete background-path status, including straight clear misses |

For the supported certified adapters, the added fields derive from already evaluated states:

$$
\begin{aligned}
\mathcal{P}&=\mathcal{I}\cup\mathcal{U},\\
\mathcal{E}&=\mathcal{I}\setminus\mathcal{U}.
\end{aligned}
$$

These set relations rely on the adapter's existing membership and unresolved-boundary contract. They do not infer arbitrary silhouettes from an unavailable branch. An interior zero-thickness launch remains projected inside but is neither regular nor complete.

Regular entry does not certify a transmitted exit, background reachability or source support. Neither added field overrides incomplete status, supplies a crease normal or authorizes sampling unknown pixels.

## Prospective field-validity cohorts

For primary interface-field comparisons, use the common completed regular cohort:

$$
\mathcal{V}=\mathcal{E}\cap\mathcal{C}.
$$

Here the completion set describes geometry and paths, not photographic source confidence. Source support remains a separate requirement.

| Cohort | Prospective comparison |
| --- | --- |
| Completed regular entry | Actual interface positions, normals, directions and background coordinates |
| Completed clear miss | Straight identity background coordinates; no interface event is asserted |
| Unresolved launch | Incomplete status and NaN background coordinates; preserve other legacy diagnostics |
| Incomplete exit after regular entry | Retain available event information; do not claim a complete background path |

This comparison cohort is conservative. An incomplete path may still have valid intersection geometry. A more detailed event contract could expose that information separately; these fields do not erase it.

The flat tracer retains finite analytical direction diagnostics at misses and unresolved launches. The closed tracer retains NaNs there. Those raw legacy arrays must not be forced equal or interpreted as equivalent physical interface exits.

## Controls and accounting

The controls cover the fixed Search radius at indices one and 1.5, the unit radius at index 1.5, and a separate interior zero-height flat launch. Each old and new implementation runs only the declared small fixture; no original failed checkpoint resumes.

| Work | Result |
| --- | ---: |
| Fixture configurations | 4 |
| Attempted comparator rays | 50 of 64 |
| Closed level points | 516 of 10,000 |
| Measured delegated height/boundary query points | 580 |
| Conservative nested-interface upper count | 1,232 of 20,000 |
| Source queries, images, fits | Zero |

The measured query counter omits some wrapper methods. The separate accounting record encloses those calls conservatively without rewriting the as-run ledger or repeating controls. The fixed fixtures and solver iteration limit give a separate reconstructed structural bound below the original cap. This supplement is not an as-run nested counter.

All legacy fields match exactly, including NaN placement. Both new fields match their prospective meaning. The interior zero-height fixture confirms that unresolved launch status is not merely a silhouette label.

## Scope of acceptance

This accepts an API clarification, not a physical or visual improvement. The earlier 66-ray checkpoint remains failed under its original incompatible membership assertion, with five configurations unexecuted.

A later primary-map parity task needs this immutable contract and a fresh declared budget. It must compare equivalent fields and physical cohorts, retain raw legacy differences and stop on unexpected path discrepancies. No reflected scene, environment, image or new surface is authorized here.
