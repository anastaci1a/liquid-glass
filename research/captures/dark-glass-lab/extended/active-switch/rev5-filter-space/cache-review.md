# Cache and derivative verification

- Original whole-image finite-difference assertion failed at epsilon 0.00005: A relative RMS 0.0153904, above 0.01. No fit ran with that unverified derivative.
- Expanded step-size diagnostic: the cached renderer is bit-exact against direct tiled rendering on both observations. Whole-image derivative error decreases at larger perturbations; clipping crossings, the rounded BT.709 transfer knees and float32 rounding invalidate a global smooth-derivative assumption.
- Excluding only output support affected by analytically identified clipping/knee crossings, all four step sizes pass the original 0.01 relative-error bound. At epsilon 0.001 the errors are 0.00009979 / 0.00011352. Even the smallest step gives 0.001964 / 0.002192. See cache-verification.json for all counts and unmasked errors.
- These exclusions apply ONLY to derivative diagnostics. No scoring pixels, native guards or source pixels are excluded or changed. Native render comparisons decide candidate acceptance. The derivative supplies a local proposal, not a proof of solver convergence across transfer knees.
