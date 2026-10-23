# True-distance back surface

Private geometric comparator after the low-order polynomial surface failed its native image comparison. No adopted rendering change or qualifying pass.

- Fixed orthographic camera, flat front z=0, back z=−h, background z=−G, n1.5. Same Snell equations and sufficient no-reentry slope bound as the earlier flat-front comparator.
- Let d be actual inward Euclidean distance to the SAME crowned outline; n_b its unit outward normal. This differs from the archived radial boundary coordinate r(1−sqrt(T)). The latter has a nonunit gradient and cannot be substituted for Euclidean distance.
- h=r[t0+bx(x/r)²+by(y/r)²]+w integral_0^(d/w) a(s)ds, with w=.75r and a a cubic spline with the existing knot sequence and final three zero coefficients. Clamp integral at1: rim gradient is zero beyond w. Then grad(h)=(2bx x/r,2by y/r)−a(d/w)n_b. A single height owns its normal; no separately painted displacement or curvature.
- Initial n1.5,t0.8,G10.8r; bx/by in±.08 and seven spline coefficients in±.35. The partition-of-unity bound M≤2 hypot(|bx|hx/r,|by|hy/r)+max|a_i| bounds slope. Positive height/gap checked at actual rays; conservative termwise height bounds can be used before adoption. Parameters describe a geometric family, not recovered Apple values.
- Nearest points use a global16384-boundary-point seed and a constrained normal-projection Newton solve. Require boundary/stationarity residuals and distance no worse than the seed. The .75r support lies below sampled minimum curvature radius≈.9773 (normalized native coordinates). This is numerical geometry evidence, not a formal global reach bound. Samples in the deep core bypass projection only when the proven Lipschitz bound of the old coordinate places actual distance beyond support.
- Initial finite-difference gradient errors≈2.3e−9. Curl errors decrease about quadratically from6.1e−6 at step1e−5r to2.45e−7 at2e−6r; the derivative-step convergence is retained separately. Do not relax tests silently or claim exact numerical zero.
- Reuses the helper's independently checked CrownGeometry derivative equations; true-distance seeding and height model are new private additions. No helper file was edited. Full per-ray support/unique-projection/HQ checks remain necessary if an image candidate qualifies.
- Map projection is only initialization. Uniform source regions do not constrain unique ray addresses, so failure to match an archived map is not proof that a physical family cannot match the observed images. Native image guards remain authoritative; only a final verified≥.5% per-reference improvement can count.

## Native calibration and bound review

- Map-space initializer: RMSE .08404 normalized units; native E19.1048/16.8464. Direct photometric joint geometry/material proposals then reached native E15.2768/16.6057 after10 bounded steps, still7.94%/7.49% worse than accepted revision5. No pass.
- Proposal error continued improving at the10-step boundary; first rim coefficient hit+.35 and the second approached it. A separate continuation permits±.5 for the rim coefficients, retaining±.08 core bounds, fixed source and geometry family. This is an explicit bracket expansion, not an acceptance change.
- Its conservative slope upper bound at the two fixed poses remains below1/sqrt(1.5²−1); height lower bound t0−.08[(hx/r)²+(hy/r)²]−.5*.75 remains positive, and G remains beyond the maximum. The actual per-ray checks continue. The extension is justified by physical validity and bound activity, not a first threshold crossing; both stages are ONE family if eventually accepted.

## Longitudinal height coupling proposal

After20 joint calibration steps, native E14.6782/15.8653 remains worse than revision5. The compact uniform rim cannot vary its cap/body optical strength independently. Test a geometric height extension, not an image stretch: add k(m/a)²[A(d)−A(w)], where A is the integrated rim profile and m/a is the major-axis coordinate. Its derivative includes BOTH the normal factor and tangential term2km[A(d)−A(w)]/a². Dropping the latter would destroy the stated height model. It vanishes with its gradient in the deep core and recovers the previous height exactly at k0. k∈[−.25,.25]; dynamically require conservative slopeM≤.87 and normalized height lower bound≥.02 during proposal formation. This remains the same physical-surface investigation; no prior candidate qualifies.

## Exact-native settlement and cost check

The30-step quadrature proposal ended at E14.5708636610/15.6754090932, still worse than revision5. Six joint steps using the actual native sampling/filtering/compositing and glass/exterior constraints are now testing whether the proposal approximation contributed to that gap. Individual intermediate steps remain unaccepted and may trade error between references while both exceed incumbent thresholds. Publication still requires every reference to improve.

A separate cost-only subclass skips the unused lighting basis on secondary directional rays. Every emitted native field sample matches bit-for-bit for both observations (fast-field-verification.json). One interleaved run showed roughly4% lower field time under concurrent load; this is not a stable benchmark or a change to the running fit. The private prototype duplicates the ray equation solely for this check; consolidate it before any public adoption.
