Joint inner-normal/tangent study — rejected, one family, zero counted passes

Frozen accepted baseline bb1ee80131d39e7661c3d55174767c4d15182e05, E6.870490597950; epoch d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d. Native4x4 baseline material and foreground recover exactly. No source, mask, pose, silhouette, material, ordinary blur, shadow, foreground or outer normal0–3 changes.

Parameters: inner normal4–6 deltas each[-.08,.08]; tangent amplitude[.10,.30], band[.30,.75], exponent[3,10]. Two distinct starts: [0,0,0,.19928550849212562,.40361651491050377,4] and [.015,.025,-.045,.18,.60,7]. Both Powell coarse fits terminated successfully (331 and473 training evaluations); all six final values interior to initial bounds. Training was1x1 approximate; final measurements4x4 native.

| Result | E | E reduction | glass | rim | exterior | archive FG | plus FG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Accepted rev2 |6.870490598|0%|5.843130589|8.813648224|11.469442017|13.242044387|3.667139624|
| Coarse start1 native |6.844925353|0.37210%|5.823799610|8.777120590|11.468614027|13.242310015|3.666268351|
| Coarse start2 native |6.847577380|0.33350%|5.827270985|8.778639793|11.468739551|13.242302831|3.666138887|
| Best native guard-feasible |6.855243146|0.22193%|5.830674171|8.793297768|11.468900906|13.242023343|3.666710775|

Both coarse optima fail the0.5% threshold AND regress archive FG. No tolerance waives that guard. Authorized native settlement used32 recorded native evaluations and two finite-difference/trust-region iterations; linearized guards generated proposals, final exact guards determined feasibility. Best feasible point is delta[.00375,.00375,-.0003726719273102025], tangent.1842855084921256, band.43486651491050377, exponent4.1875. It improves all measured guards but misses the milestone. Native settlement was budget-limited to two iterations; no claim of global or native convergence. It belongs to this same family, not an additional pass, and was not stopped at a success threshold.

Completed processes were checked after capacity recovery; none restarted. Outputs copied before further work. coarse/study.json contains every training evaluation, optimizer status and native scores; native-settlement/native-evaluations.json and iterations.json contain all probes/steps. Rejected results remain evidence, not a new incumbent. No baseline reset, scoring-epoch change or new renderer primitive.

Commands (already completed; do not rerun merely to resume):
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-revision2-joint-study.py
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-joint-native-settlement.py

Procedural/model review after isolated tangent, potential-coupled, and joint families: extra tangent freedom gives only small improvements within tested ranges; canonical archive FG is an active guard. Fits do not establish an Apple solid, global exhaustion or dispersion model. Existing-map residual diagnostics are in ../revision2-residual-diagnostics/diagnostics.json: compressed upper/underside inverse-map singular values differ substantially, while the d-stroke is near identity. Source and output filters therefore differ, supporting the authorized ordinary blur tradeoff as a distinct next test. Local Jacobian proxies ignore nonlinear kernel integration/folds and do not identify a physical PSF. Fixed-depth residuals use their stated pixel selection and are not the primary published crop scores.

Next: queue6 ordinary source/output blur begins from accepted rev2 only; no rejected joint parameter is carried forward. Lead alone independently accepts/counts/commits/pushes. Current verified toolbar count remains2.
