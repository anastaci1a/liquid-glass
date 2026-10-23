# Queue25: negative bounded covariance study

No qualifying candidate. On the OLD accepted input/epoch, baseline E6.870490597950
is best among the declared initial variance points. At selected quadrature order7:

|rho|E|glass|rim|exterior|archive|plus|
|---|---|---|---|---|---|---|
|0 saved accepted|6.870490598|5.843130589|8.813648224|11.469442017|13.242044387|3.667139624|
|.005|6.871758399|5.844397068|8.814983368|11.469453326|13.242034596|3.667168006|
|.01|6.875521458|5.848190308|8.818893433|11.469498490|13.242031220|3.667130316|
|.02|6.890646163|5.863790989|8.834057808|11.469735592|13.242005347|3.667069829|

Every positive sampled width worsens E, glass/rim and exterior; .005 also worsens
plus. Original exact guards remain unchanged. No feasible improving bracket, so
the predeclared initial-point stopping rule applies. No arbitrary bound expansion,
material compensation or additional search. This is a negative sampled direction,
NOT global optimality/infeasibility or a proof against all scattering kernels.

Numerical controls passed before calibration: positive normalized node weights,
zero mean/identity covariance for orders3/5/7/9; rho0 literal delegation and exact
small-crop comparison; native uniform-input errors2.98e-8(scale1),1.49e-7(scale2).
Full accepted native arrays reused, zero new full-baseline renders. All new
full-native coverages equal saved accepted alpha exactly. Atlas/primitive unchanged.

Quadrature was chosen by predeclared CONVERGENCE, not lower image error. Order3
versus5 failed rim-material difference .0142502/255 (> .01). Order5 versus7 passes:
glass .00275613/255, rim .00475815/255; E difference .000019004; all five original
score differences <=.000032425. Hence7 frozen;9 not needed by declared rule.
Maximum-width order3 E6.890117754 and5 E6.890627159 are numerical controls, not
distinct optical passes. Exact comparisons in quadrature-comparison.json.

Accounting: FIVE full native renderer attempts/completed points: rho.02 at3/5/7,
plus .005/.01 at7. THREE positive scalar locations, ONE family. Four additional
small-crop controls (two zero comparison calls, two uniform/scale calls), not
full-native optical evaluations. No failed/partial attempt or completed-test
restart. No optimizer. Zero qualifiers/counts; independent visual/source/HQ checks
not requested for an already rejected proposal. Hidden-source uncertainty remains.

Private implementation only: toolbar_scattering_renderer.py SHA
c196969a85e137140d2f89b685808700c80f713b9f15ca1c6ccb334118ff6dcd.
API render(...,order,atlas,prepared,checkpoint) averages common RGB source offsets
BEFORE current affine/clipped material and preserves clear/blur transition,
conditional4×4coverage, normalized postfilter, generated shadow and solid glyphs.
Empirical geometry-conditioned scattering, not identified physical roughness or
dispersion. No shared code edits, commits or pushes.

Reproduce in EXISTING localica-dark-lab-check container:
OPENBLAS_NUM_THREADS=1 PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps
python3 /evidence/extended/helper-toolbar-work/agent-toolbar-scattering-trials/control.py
--tests; then --order3/5/7 --rho.02 and --order7 --rho.005/.01 as separate commands.
compare-quadrature.py reads persisted arrays only. Completed checkpoint directories
reuse arrays and measurement files; do not rerun sealed tests gratuitously.
Large artifacts remain on disk-backed /evidence/extended/helper-toolbar-work;
copied private evidence/manifest here. Continue authorized26 filter-space audit.
