# Exact-boundary contract: saved first-fixture diagnosis

**The stopped checkpoint remains failed.** Its first assertion compares two different legacy meanings of `inside`. Saved path outputs agree on boundary status and completeness. This is an API-comparison failure, not evidence of a different physical path in the inspected configuration.

| Evidence | Record |
| --- | --- |
| Original read-only scope | [Protocol](protocol.json) |
| Saved-array diagnosis | [Result](result.json) |
| Exact retained first configuration | [Arrays](config-00-preserved.npz) |
| As-run saved-output loader | [Audit](audit_saved.py) |
| Loader naming failure before array reads | [Startup record](startup-failure.json) |

## What the existing fields mean

The flat-front tracer returns the height adapter's inclusive footprint membership. The closed tracer returns strict front-interior membership. Both separately mark the exact front/back crease as unresolved.

| Saved cohort | Count | Flat `inside` | Closed `inside` | Both `complete` |
| --- | ---: | --- | --- | --- |
| Regular interior | 25 | True | True | True |
| Exact tangent poles | 4 | True | False | False |
| Clear misses | 4 | False | False | True |

Every boundary source coordinate is NaN in both outputs. Every clear-miss source coordinate equals its original coordinate exactly. No boundary ray becomes a transmitted sample merely because the inclusive membership flag is true.

The regular coordinates, normals and exit directions agree exactly. Exit heights differ by at most 1.912e-12 original length units, consistent with the retained intersection brackets. These statements concern only the saved radius 0.9972124917582454 and index-one fixture.

Five configurations remain unexecuted. No selected-index parity, complete six-configuration pass or new geometric acceptance follows this inspection. The original 66 attempted rays remain the only optical work in that checkpoint.

## Proposed explicit contract

Do not silently redefine legacy membership or rewrite frozen evidence. Add two explicit semantic fields to both drivers for future interoperability:

| Proposed field | Meaning |
| --- | --- |
| `projected_inside` | Inclusive projected footprint, including an unresolved exact boundary |
| `regular_entry` | Geometrically regular entry membership, excluding the unresolved projected boundary |

For the inspected circular case:

$$
\begin{aligned}
\mathcal{P}&=\mathcal{I}_{\mathrm{closed}}\cup\mathcal{B}
             =\mathcal{I}_{\mathrm{flat}},\\
\mathcal{E}&=\mathcal{I}_{\mathrm{closed}}\setminus\mathcal{B}
             =\mathcal{I}_{\mathrm{flat}}\setminus\mathcal{B}.
\end{aligned}
$$

Here the boundary set remains unresolved. Neither proposed field overrides `complete`, validates an unavailable source sample or selects a one-sided crease normal. Downstream code must keep those distinctions.

This is a proposal pending contract review, not an implemented repair. Legacy `inside`, image integration and selected models remain unchanged. A future test must compare declared equivalent fields rather than waive the original failure or relabel its result.

## Scope and accounting

This forensic block inspected 33 saved records containing 1,518 scalar array elements. It ran zero rays, heights, source queries, filters, composites, images or fits. The source NPZ hash matched before and after; the preserved copy is byte-identical.

The first loader filename shadowed Python's standard `inspect` module during NumPy import. It failed before loading arrays. Renaming the same loader bytes resolved startup without changing calculations, budgets or deadline.

The exact as-run loader reads the immutable helper checkpoint through a read-only `/helper` mount. The retained local NPZ supplies identical numerical evidence independently of that original checkout. No tracer or remaining configuration is executed by this diagnosis.
