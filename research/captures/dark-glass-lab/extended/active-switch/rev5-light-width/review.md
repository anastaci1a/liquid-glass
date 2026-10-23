# Lighting-width review after revision5

- Reused exactly the accepted geometry/transmission/filtering, confirmed bit-exact against direct rendering at baseline and two perturbed width pairs on both observations.
- Eight bounded native joint steps varied two existing lighting widths and23shared material coefficients; final E ratios0.9998666884/0.9998597409 (improvements0.0133%/0.0140%), below0.5%. Original glass/exterior guards retained. No pass/public change.
- Initial larger steps slightly worsened the exterior by less than0.001RGB, but were rejected under the frozen guard. No tolerance widening or mask changes. Later smaller feasible steps remained below threshold.
- Earlier width calibration preceded the changed cap profile and source-responsive ambient terms; this was a review of that changed baseline, not a repeat of the same fit.
- Evidence: cache-verification.json, form-01..08.npz, trials.ndjson andsettlement.json. Optimizer steps are not accepted passes or a global-optimum proof.
