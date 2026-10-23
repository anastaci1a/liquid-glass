# Spline candidate: bounded material guard check

Status: no strictly feasible evaluated proposal was established. The solver did not converge; this is not a proof of material infeasibility. No candidate image ran and the spline remains held on foreground guards.

## Frozen geometry and one direction family

The improved [spline body](../expanded-spline-observation-01/README.md), incident filter, source, masks and foreground stay fixed. Only one common RGB gain/bias pair may move within 0.01 of the selected response. The original H1 images remain the numerical comparison; no easier baseline is substituted.

Cached source samples and fixed foreground transmission give analytic response columns. Four float64 compositor controls verify them. These are derivative checks, not new optical renders or accepted images.

Each original cohort has a normalized quadratic constraint:

$$
Q_j(\boldsymbol{\delta})=
\boldsymbol{\delta}^{\mathsf T}H_j\boldsymbol{\delta}
+2\mathbf{v}_j^{\mathsf T}\boldsymbol{\delta}+c_j\leq0.
$$

The [forms](forms.json) retain the old residual and proposal reserve. Changing foreground cohorts receive a stricter 0.01 squared-level model reserve; exactly unchanged cohorts receive none. This tightens the proposal, not a waiver of native regression.

One TRAIN objective and one bounded solve produced two evaluated parameter vectors. Neither satisfies every model constraint. The solver reports a positive directional derivative for its line search. No extra start, model solve, native trial or backtrack follows.

The result does not establish a global impossibility or resolve conditioning of the constrained model. A future saved-form assessment requires a new declared task; no solver repair is run after this cap.

## Setup recovery and timing

The first attempt requested an interior-mask archive entry that does not exist. It failed before fitting or any candidate. [Recovery](setup-recovery.json) preserves the original code, derives the canonical glass-minus-rim mask and asserts equality with the original scoring definition. Source bytes and masks do not change.

The retry keeps the original 21:41 UTC deadline. [Result](result.json) finished at 21:38:41 UTC, using one fit, two model evaluations and zero rays, source queries, filters or images. The failed setup did not repeat a completed probe.

Final documentation and publication occurred after the research cap; [closure](closure.json) records that administrative delay. No scientific evaluation ran after the deadline. No completed experiment or acceptance history is rewritten.
