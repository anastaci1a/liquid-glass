# Convergence continuation of the same joint experiment

- Initial eight-update artifact is immutable. It ended with E ratios0.9952020202/0.9907238880 (not qualified) and worst normalized squared-loss improvement0.00028570 at its last step. This is not yet evidence of numerical stationarity.
- Continue from that exact final point for at most eight additional native updates. Retain ALL original parameter bounds, reference baseline, masks, source, optical/material degrees of freedom and native guards. No area term, widened gamma bound or new shape coefficients.
- Stop early only after two consecutive worst normalized squared-loss improvements below1e-5 or the existing trust-region termination. Do not stop at first threshold crossing. This remains ONE experiment and can at most supply ONE new verified pass after independent checks; intermediate solver states are not passes.
- Keep source-first eight-step report and this continuation separately, with exact hashes. Native replay against the saved starting scores precedes optimization.
