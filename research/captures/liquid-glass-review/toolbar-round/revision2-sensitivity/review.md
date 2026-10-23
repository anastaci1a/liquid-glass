Queue10 — saved native direction sensitivity

No renders or optical fits in this review. Existing outer0–3 native central differences(h=.002), accepted rev1→rev2 inner4–6 material secant, rejected revision2 tangent secant and rejected ordinary-blur secant are compared under the frozen weighted E geometry. All fixed glass/rim pixels remain scored; source/shape/material/glyphs/epoch unchanged. Outer derivatives are local sampled-raster derivatives; the other three are aggregate historical/failed image secants, not independent parameter Jacobians or blind validation. Recipe fields outside inner4–6 were checked identical for the inner secant.

Seven unit image directions have singular values1.345,1.118,1.045,.956,.954,.838,.569: rank7, condition~2.36. This set has NO severe global degeneracy. Within outer directions c2/c3 cosine=.544 globally, .699upper, .889underside: localized profile compensation is much stronger than full-mask compensation. Tangent/blur global cosine−.0177, inner/tangent+.00325, inner/blur+.08297. Leave-one-out explained direction energy: outer c0/c1/c2/c3=.114/.280/.452/.351; inner=.0139, tangent=.0641, blur=.00974. These quantify this saved direction set only, not the full model or physical identifiability.

| Direction/crop diagnostic | Upper | d | Underside |
|---|---:|---:|---:|
| Outer c2 cosine to desired correction |−.0559|zero field|+.1652|
| Outer c3 cosine to desired correction |−.0074|zero field|+.2566|
| Inner historical secant cosine |+.0041|−.2624|−.0183|
| Tangent secant RMS(0–255) |.686|4.63e−7|1.243|
| Blur secant cosine |+.0864|−.0125|−.3770|

Zero-energy cosine placeholders in JSON are not orthogonality evidence. In d, all four outer derivatives are exactly zero; the tangent difference is numerically negligible and its normalized cosine/rank contribution has no useful interpretation. Inner and blur have meaningful RMS3.046/.971 there, with cosine+.0309: they are nearly independent. The historical inner direction is already unfavorable if extrapolated from current rev2; another inner sweep is not justified merely by old improvement.

Actual outer family supports this spatial tradeoff: best full-mask guard-feasibleE6.855726743(−.21489%) fails milestone, upper conditional9.20072→9.21880 worsens, d unchanged3.11043, underside5.07395→5.02994 improves. Both native starts had predeclared8-step budgets, not a convergence certificate. Blur's best similarly worsens d/underside and fails foreground guards. Broad repeated parameter sweeps are not supported by these results.

Source confidence matters more than a single global condition number. Outer c3 desired-correction cosine is−.0744 in observed-content kernels versus+.2976 in estimated-content kernels. Blur is+.1640 observed versus−.0193 estimated. All.75–8px pixels are mixed-support; underside has0complete observed-content output kernels. The paper-field transfer also models absolute RGB in all cohorts. A source repair would be a separate provenance/baseline reevaluation, never an optical gain. Source-confidence subsets are advisory and cannot hide bad score pixels.

Queue11 is supported as a LIMITED empirical cap/body test, not as a solution for d. A uniform depth-only profile has opposing upper/underside responses and localized normal-direction overlap; deterministic boundary curvature adds an angular geometric input not present in those four global depth coefficients. This evidence does not prove the new direction identifiable; one declared bounded family is appropriate. It does not contradict the authorized conditional11. Fixed w=.2*r follows the outer c3 B-spline support(.2normalized radius), chosen before any new fit. It cannot reach the deep d crop; no d-stretch success will be claimed from it.

Exact normalized proposal in current geometry units (L=min shape half):
    u=clip(d/w,0,1); B(u)=64*u^3*(1-u)^3 inside0<u<1, zero outside
    delta_a/L=lambda*B(u)*(L*kappa(s_star)-2*pi*L/P)
    F_lambda=F_0-delta_a*n, inside unchanged footprint; outside F_0

Here d is the accepted renderer's boundary coordinate r-b, NOT an assumed Euclidean distance. s_star is the deterministic TRUE closest point on the actual implicit footprint; curvature is evaluated there. P is that continuous footprint's perimeter. Baseline total edge refraction F_0 remains nonzero; only this addition vanishes at support boundaries. No target-colored rim, per-crop coefficient or proprietary surface assertion. One lambda, one fixed dimensionless width, unchanged source/material/glyphs.

Before any fit: exact lambda0 recovery; analytic curvature/closest-point residual checks; perimeter/total-turn convergence; true-circle constant-curvature zero limit (equal axes in a softened crown are not automatically a circle); mirror/90degree rotation/uniform scale; uniform-input rendering; C2 support boundary continuity; actual ray domain. Initial lambda bounds derive from a declared maximum added displacement.12L and target-independent curvature extrema, with a numerical margin. Then original full-native guards during proposal formation and nonlinear validation, convergence/bounds review, never a first-threshold stop. Implement mathematical primitive only in agent worktree; no shared edits or new public API without lead integration.

Separate next residual-supported direction after this cap/body experiment: a shared potential core strain can address the d crop that outer/tangent fields do not reach. In normalized coordinates Psi=(lambda/2)*x^2*S(clip(d/w_core,0,1)), S=u^3*(10−15u+6u^2), delta_F=−grad(Psi). Deep core gives(−lambda*x,0); boundary perturbation and its first derivative vanish. It preserves mirror/scale/zero/uniform-source invariants and the added term is integrable; inherited total map remains empirical. This is a PROPOSAL for a later assignment, not implemented or fitted here. No independent d/crop/reference coefficient.

Artifacts: evidence.json contains all Gram/cosine/singular/projection/cohort evidence and exact source-array hashes; review-evidence.py makes no renderer calls. Model review, no pass. Accepted toolbar remains bb1ee801/count2; lead owns independent acceptance/commits/pushes. Request5 was sent before10. Continue assigned11/12 and request the next task before12; explicit Ana pause overrides.
