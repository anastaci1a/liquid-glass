# Shared outline law: pinned static peer review

**The declared pass 1 angular law, bounded endpoints and scalar fit are consistent within their stated conventions.** No family qualifier is established. This review consumes immutable source text from `fbca678ee34fc202034b731b1b32f5394b099df7`, not the subsequently evolving field-reuse driver. No arrays, numerical imports, evaluations or images are used.

Task 55 started at 21:46:56.219 UTC on 25 October 2026 and ends by 21:54:56.219 UTC, including versioning. The archived `driver-source.txt` digest matches the original run_pass.py receipt exactly. Recorded first/last receipts are equal. Own hashes bind every reviewed Git blob.

## Cap convention and rotation

Native y points down. The right-cap angle uses atan2 of negative centered y and horizontal displacement from the right cap center.

Thus minus 45 degrees is lower-right, plus 45 upper-right and plus 90 the upper join. The declared strength decreases smoothly from one at minus 45 to zero at plus 45, stays zero through 60 and recovers smoothly to one at 85.

The left branch subtracts 180 degrees and wraps the result. Under a 180-degree rotation of both centered coordinates, the cap-center displacement and y reverse together, recovering the same local angle. Left recovery is consequently near its lower join, as required by a rotated pattern rather than a left/right mirror.

The coordinate is a cap-center polar angle. For an ordinary rounded rectangle whose minor half exceeds radius, the short core-y offset means this is not exactly the local arc-normal angle. The code does not claim to calculate a three-dimensional optical normal. Keep that distinction explicit if future guidance refers to physical edge-normal angles.

The cubic smoothstep has zero endpoint derivatives. Ordered breakpoints ensure continuous fade, minimum interval and recovery. Straight-body strength is one. Recovery finishes before the joins, avoiding a strength jump at the outer contour joins. Deep-interior switching of the side-region definition is not an optical surface change.

## Inward law, quadrature and tails

The profile is nonnegative, bounded and maximal at the outer silhouette; its inward generalized Gaussian has no analytic inner cutoff. Sigma is in native pixels and exponent exceeds one. Pass1 uses widths 1.95, 2.275 and 2.6, corresponding to three through four times the prior 0.65. These are predeclared hypotheses, not inferred widths.

The existing shared area rule supplies positive full-pixel-normalized weights over the actual footprint. It does not divide by occupied area or choose residual pixels. Fields are checked finite and bounded. Orders 8/16 are compared against the declared 1e-6 opacity threshold before fitting. Positive quadrature and fixed-order agreement are not rigorous all-order error certification.

For valid configurations, the maximum configured tail depth bounds every omitted pixel's alpha because signed distance is 1-Lipschitz and angular weight stays at most one:

$$
D=\max_j\left[\sigma_j(-\log\epsilon)^{\frac{1}{p_j}}\right],
\qquad d_c<-D-\sqrt{\tfrac12}\Longrightarrow\alpha_j<\epsilon.
$$

The omitted per-pixel integral is at most epsilon. Encoded unit-endpoint composition then has per-channel omission at most strength times epsilon. Summed absolute errors require the number of omitted pixels. Quadrature and floating-point errors are separate. This bound assumes valid positive sigma/exponent, ordered finite angles and tail strictly between zero and one.

The integrator does not validate every generic configuration before calculating its active band. The point function validates width/exponent only when nodes are evaluated; tail validation is also a caller prerequisite. This limits generic malformed-input handling, but does not invalidate the pinned positive finite pass 1 recipe. No shared correction or replay is authorized here.

## Bounded color endpoints

White targets the unit RGB endpoint. Encoded lift scales a nonblack encoded RGB vector until its maximum channel reaches one. Linear lift decodes sRGB, scales that linear vector until its maximum reaches one, then re-encodes. Both lifts leave black unchanged because their zero-maximum branch is explicitly zero; white also remains unchanged under the lifts.

Each lift preserves channel ratios in its declared space. Neither should be advertised as preserving every perceptual hue/chroma metric. The linear operation is a display-response hypothesis, not measured scene radiance. Shared response does not mean a separately fitted endpoint per reference.

For finite unit backing and an endpoint within the unit cube, bounded alpha and fitted strength produce a convex combination:

$$
C_{\mathrm{out}}=(1-s\alpha)C+s\alpha E,
\qquad 0\le s\le1,\quad0\le\alpha\le1.
$$

The compositor rejects out-of-range raw output rather than hiding it with clipping. It preserves unaffected unavailable pixels and rejects unavailable affected backing. It assumes the alpha and delta shapes/endpoints come from the validated helpers; it is not an arbitrary-array validation API. All operations remain post-completed encoded effects, outside refraction.

## Scalar fit

For each fixed width, the driver forms its response direction from the frozen completed body and integrated alpha. Training uses original glass minus held, then explicitly checks that no foreground box contributes. Each reference contributes one mean divided by four, so differing cohort sizes do not dominate the shared fit.

$$
N=\frac14\sum_{r=1}^{4}\langle V_r(T_r-C_r)\rangle,
\qquad Q=\frac14\sum_{r=1}^{4}\langle V_r^2\rangle,
\qquad V_r=\alpha_r(E_r-C_r).
$$

$$
s^*=\operatorname{clip}\!\left(\frac NQ,0,1\right),
\qquad L(s)=L(0)-2sN+s^2Q.
$$

This is the correct convex scalar least-squares solution when Q is positive. The zero-denominator fallback selects identity and does not establish global infeasibility. Held and foreground do not enter N or Q. The original partial cohort is not specially optimized or removed; any overlap with ordinary training remains governed by that unchanged mask convention.

The quadratic describes encoded double-precision proposal arithmetic. Actual output storage and nonlinear metrics can differ through casting. Every completed candidate is therefore evaluated with original masks, partial/exterior/body/foreground guards and incumbent guards. A development seed chosen by train loss is explicitly separate from acceptance.

## Preserved outcomes and accounting

Every width fails the family test: expanded A fails glass/rim/held/aggregate/partial; compact A and B fail partial/exterior. Expanded B passes its original guards, which does not make a family qualifier. No visual comparison is independently reviewed here, and no shared color-lift setting is accepted by static algebra.

The parse-only predecessor is preserved. Its disclosure records a malformed numeric literal rejected before module execution and a one-token correction without clock reset. Its prose description of the two literal forms is ambiguous; the preserved syntax-failure source is authoritative. This review neither executes nor repairs it.

The as-run profile-control ledger remains 24. The separate supplement adds twelve previously omitted zero-composite fixture points, yielding 36 conservative controls under the 1000 cap. The supplement is not a new numerical run or a reset. Both records remain bound to the pinned commit.

## Versioning and delivery

Only this own report folder is written. Old scientific records and untracked task 46 remain untouched. Documentation, privacy and immutable-text hashes are checked before own commit/push. The prompt Sessionsation report encountered ADAPTER_BUSY; no Queue fallback is used. Final delivery status is distinct from scientific readiness.
