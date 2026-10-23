# Queue25: bounded achromatic scattering control

Uses queue24's frozen analytic map/Jacobian atlas, OLD accepted source6c68d31a,
target5bb59714, masksda7d9dec, epochd1d864eb and accepted revision2. Typography23
is a separately verified input alternative, NOT adopted. No source, AA4×4,
lighting/material, shape, ordinary width/transition/postfilter, glyph or shadow
calibration in this study. Empirical geometry-conditioned covariance, not a
physical roughness derivation or dispersion. Exact operation is queue24/model.md.

Predeclared BEFORE native comparison: rho in [0,.02], normalized variance
t=(rho/.02)^2. Gaussian Cartesian orders3,5,7,9 only, same native4×4 AA at every
order. First compare consecutive orders at rho=.02, the maximum declared width.
An order is provisionally usable only when material RGB RMS difference over
frozen glass AND rim <=.01/255, absolute E difference <=.001, and absolute
difference of EACH original glass/rim/exterior/archive/plus score <=.001.
These are numerical convergence controls, NEVER relaxed acceptance guards.
Order is selected by this rule, never by lowest E. If no consecutive pair through
9 passes, terminate this direction as numerically unsupported at this budget;
do not fit an unstable approximation or claim no continuous-model improvement.

Only after convergence: initial variance points t=0,1/16,1/4,1 (rho0,.005,.01,.02),
reuse the completed maximum-width point and saved accepted native baseline.
If there is a feasible/improving bracket, at most8 additional scalar proposals
within the SAME bounds; otherwise document a negative sampled direction. No
global convergence claim. Any numerical qualifier requires a higher-order check,
fresh HQ crop/source evidence and independent primary review before counting.

Implementation API in own worktree only:
toolbar_scattering_renderer.render(..., order, atlas, prepared, checkpoint).
rho0 literally delegates accepted toolbar_candidate.render. Mathematical node
moments, rho0 delegation/exact small crop, constant-source native controls and
scale controls precede the first full native comparison. Source average precedes
the existing affine/clipped material, then original conditional coverage and
normalized postfilter. Each actual render checkpoints raw bands/material/alpha
BEFORE scoring. Completed arrays reused on recovery. No coefficient rounding or
silent replacement of old artifacts. All orders are numerical trials of ONE
family; no artificial optical passes. Review after this third substantive family
(18 biaxial,20 sextic,25 covariance), then proceed26.
