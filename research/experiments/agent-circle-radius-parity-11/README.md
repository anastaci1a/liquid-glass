# Circle-radius primary-map parity

**Stopped on the first exact-status mismatch.** The first nonunit-radius, index-one configuration disagrees at all four exact tangencies. The flat-front tracer reports inclusive footprint membership; the closed-solid tracer reports strict interior membership. This is an API classification discrepancy, not evidence of a displaced regular ray or image failure.

| Evidence | Record |
| --- | --- |
| Declared fixture, limits and clock limitation | [Protocol](protocol.json) |
| One-shot comparison and entry-count instrumentation | [Driver](check.py) |
| First failure and actual counters | [Result](result.json) |
| Both unchanged tracer outputs | [Saved arrays](config-00.npz) |
| Immediate review notification state | [Readiness](review-ready.json) |
| Shared radius contract | [Root certificate](../circular-solid-radius-01/README.md) |

## Result and stop

The first fixture uses radius `0.9972124917582454`, index `1`, background distance `2` and the approved harmonic back. Its 33 points contain 25 regular grid points, four clear misses and four exact axial tangencies. Both shared tracers ran once. Membership differs at indices 29–32, precisely the four tangencies.

No membership normalization, tolerance waiver or replacement normal was applied. The remaining five configurations were not executed. Later status, NaN and regular-coordinate assertions were not reached. The saved arrays retain every returned field, but this packet does not claim those subsequent checks passed.

The source code explains the discrepancy: flat-front membership comes from the back's inclusive radial test; closed membership comes from its strict front-height test. Both APIs separately expose unresolved boundary status. A future shared contract must distinguish inclusive footprint membership from regular strict-interior membership before raw status parity can pass.

## Independent equivalence argument

Let the supported unit-radius back have height and gradient derived from the same scalar function. The fixed-radius construction is

$$
\begin{aligned}
h_R(x,y)&=h_1\left(\frac{x}{R},\frac{y}{R}\right),\\
\nabla h_R(x,y)&=\frac{1}{R}\nabla h_1\left(\frac{x}{R},\frac{y}{R}\right).
\end{aligned}
$$

The closed occupancy uses this height without changing its physical units:

$$
F_R(x,y,z)=\max\left(z,-z-h_R(x,y),\frac{x^2+y^2}{R^2}-1\right).
$$

At a regular back point, the active outward gradient is

$$
\boldsymbol{g}_{\mathrm{back}}=(-h_{R,x},-h_{R,y},-1).
$$

The flat-front tracer uses its negative as the normal opposing the incident direction. Normal incidence through the flat front leaves the internal direction vertical. Thus both formulations have the same regular back location and Snell direction, subject to numerical intersection error. This analytic equivalence does not erase their different exact-boundary status conventions.

For the approved harmonic circular back, nonnegative concave constituent heights combine through the increasing concave harmonic cap. Positive lateral scaling preserves concavity. The resulting solid is convex; this does not establish convexity for the expanded spline or arbitrary private surfaces.

The global primary certificate still uses the scaled slope bound:

$$
H_R=H_1,\qquad M_R=\frac{M_1}{R},\qquad
(n^2-1)M_R^2<1.
$$

No reflected-path, secondary source-support or radiance claim follows. Index-one straightness was scheduled but its assertion was not reached after the membership failure.

## Accounting and provenance

| Work | Actual | Cap |
| --- | ---: | ---: |
| Attempted primary/comparator rays | 66 | 396 |
| Closed level points | 1,075 | 50,000 |
| Nested height/boundary points | 2,456 | 100,000 |
| Configurations executed | 1 | 6 |
| Source queries, RGB, filters, Fresnel, images and fits | 0 | 0 |

Instrumentation increments counters on function entry before numerical evaluation. Nested delegation is counted, including the radius adapter and base height calls. Closed level points are recorded separately. The root fixture suite was not repeated. The driver stops on the first exception and refuses to overwrite a completed result.

The exact root commit `84a9ed4988a7139e68c5ca07d0c1e0edda72a857` was merged without conflicts as `12e9d931dc8d5c26d3ec562392808980bc85be31`. Its remote tip was verified before tests. The merged ancestry includes published research and gallery records; this task did not author or modify them.

The new shared module SHA is `0a1a75e06d234c7f47d5bd22dcec2b2af767fcba1ac976b02108a1ac50f05a81`. This is an intentional dependency update for this separate task. Sealed Search code pins remain historical rather than being described as current unchanged hashes.

## Clock limitation and next question

The initial setup timestamp was not retained across context compaction. The first retained clock is 02:31:11.987 UTC. Rather than restart the allocation, this task uses the earlier prerequisite commit time, 02:28:19 UTC, as a conservative lower bound and stops by 02:43:19 UTC. It is not presented as an exact receipt time.

The fixture ran from 02:32:43.127438 to 02:32:43.184884 UTC. Setup and documentation consume the same bounded task. Final versioning and remote verification are recorded separately. There is no additional scientific execution after the failure.

The next requested shared question is the intended membership and unavailable-field contract at exact tangencies and clear misses. No implementation or repeated fixture is activated here. Search inputs, images, selected tone, source-confidence limits, historical fingerprint discrepancy and counts remain unchanged.
