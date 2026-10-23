# Complete squared-RMSE guard forms

Evidence review after initial35packaging added the PSD image-curvature term for ALL original hard guards (glass/exterior/archive/plus), not just objective curvature and conservative guard-gradient envelopes. Saved-image review only, no new native render/fit. Gram matrices retained for both native central and full surrogate; normalization divides each squared-RMSE guard form by twice its original baselineRMSE to match score-gradient envelope units. The model inequality is envelope first-order guard change plus x^T G_guard x/(2RMSE)<=0; no epsilon allowance. This is a LOCAL image quadratic, not actual nonlinear guard verification.

Native all7guarded local loss reduction stays.01174710064045 versus required.459915943833. Strict native axis4witness normalized guard changes are[-.00113618803,−9.97939418e−10,0,0] and pass machine comparison exactly. Numerical all7SLSQP optimum has positive residuals≈1e−20 and is NOT labeled strictly feasible despite solver success. Full surrogate axis4archive quadratic contributes+2.66203949e−23 while native finite fields give0: surrogate witness is correctly labeled strictly infeasible; it is NOT erased by an arbitrary epsilon or by claiming exact geometric disjointness (coefficient4can potentially influence205archive pixels after postfilter). This distinction does not alter the NO native proposal conclusion.

Raw initial35assessment and manifest retained. New complete forms/results: guard-quadratic-review.json; exact saved-evidence driver guard_quadratic.py. Command:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/agent-toolbar-code:/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-code/toolbar_normal_rank_guard_quadratic.py
