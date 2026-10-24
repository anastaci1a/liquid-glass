# Thin reflection sampling is not converged

The six fixed tiles reproduce cached AA2 subrays exactly, but increasing sampling changes the reflected component materially. Some AA4-to-AA8 differences remain large. The thin contour's brightness is therefore not numerically converged. No optical improvement, full-image convergence or score-epoch change is claimed.

| Member and tile | Maximum AA2–AA8 difference | Maximum AA4–AA8 difference |
| --- | ---: | ---: |
| Expanded upper | 0.00019341 | 0.00007370 |
| Expanded lower | 0.04303850 | 0.00054069 |
| Expanded right cap | 0.03970122 | 0.02126757 |
| Compact upper | 0.02133438 | 0.02139187 |
| Compact lower | 0.02141846 | 0.02132203 |
| Compact right cap | 0.03968349 | 0.02137650 |

Values are linear direct-reflected signal, not encoded RGB levels or full reconstruction error. The same actual front, normals, Fresnel power and finite panel at z1770 generate every sample. Optical blur, surface coefficients and illumination remain unchanged. This is camera pixel integration only.

The [protocol](protocol.json) starts at 12:14:48.054 UTC and ends at 12:29:48.054. Science finishes at 12:14:58.650. All six AA2 subray identities are exact; no unresolved boundary sample occurs. [Result](result.json), [checkpoint](checkpoint.json), [profiles](profiles.json) and [ledger](ledger.json) retain all three levels.

There are 290304 camera-front evaluations, 5806080 conservative adapter units and 146611 reflected/Fresnel/panel paths. Cached identity checks cover 13824 subrays. No target/source RGB, full composite, score or fit is evaluated.

The original AA2 model scores and images remain immutable. Uniform samples can miss fractional boundary coverage; fixed AA8 alone does not certify continuous pixel integration. A future geometry-aware integration rule should split pixels at the actual projected footprint, use positive area weights, and refine every eligible boundary pixel independently of target masks or error.

This is a numerical correctness limitation, not proof that a geometric light hypothesis is physically impossible. It blocks treating the held thin-rim previews as converged fidelity evidence. Later stage assessments must retain that limitation rather than silently bypass it.

Publication exceeded the declared deadline. Science finished before the cap; no additional numerical work ran. The [administrative record](publication-overrun.json) preserves the delay without restarting the clock.
