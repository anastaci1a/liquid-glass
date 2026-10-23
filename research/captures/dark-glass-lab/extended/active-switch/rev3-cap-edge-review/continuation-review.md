# Same-family continuation

- Initial8 native steps: paired E reductions .896%/.969%. Steps9–16 reuse the existing clipped-affine material derivatives; optical derivatives and all acceptance renders remain full native. This derivative path exactly matches public material_local sufficient statistics and agrees with sampled finite differences within .11% relative L2.
- Coefficient1 repeatedly reaches its LOCAL trust-step bound (about +.375 each step), not its absolute range. Continue the same family with its proposal scale raised from .25 to1, while retaining absolute [-3,6], full native backtracking, shared source/masks/material and all original gates. This avoids spending many iterations on an artificial small-step limit. No new pass or threshold stopping.
- Batch01/02 stay immutable; final bounded result goes to bound-settlement.json. Center-only source coverage currently passes, but full emitted-ray/HQ/exterior/visual checks remain outstanding.

## Settled candidate

- Optical continuation finished at24native iterations, all part of ONE proposed pass. Final worst-normalized squared-error gain1.70998e-6; bounded local settlement, not proof of global optimum. All three added coefficients are interior to absolute bounds.
- Initial shadow fit reached sigma/vertical-offset limits. Continuation widened sigma[.09,.12]to[.09,.18]and y[.10,.13]to[.10,.20], retaining x[-.008,.012],opacity[.04,.10], fixed source and one shared profile. It converged in224evaluations to interior sigma.124809,y.159735,x.001437,opacity.058661. Exterior guards pass; distant tails await inspection.
- Initial shadow report was accidentally overwritten by continuation. shadow-initial-summary.json preserves values from captured tool output; full initial optimizer history is not recoverable. Final report preserved as shadow-continuation.json; script output path corrected. No fake rerun or evidence claim.
- Public implementation isolated in /tmp/cap-profile-public-code passes33tests. Fresh independent4x replay/all-emitted-ray checks running; public worktree untouched.
