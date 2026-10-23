# Finite-gap toolbar surface audit (queue17)

The accepted empirical map does not pass the derived exact single-back-surface compatibility test at many well-resolved interior points. This is specific to the declared flat-front orthographic comparator, not a claim about Apple or every close approximation. A recovered surface, best-approximation error, image improvement or pass is NOT established. Accepted source/shape/material/masks/epoch and revision2/count2 unchanged; no target-image fits or new optical renders.

## Geometry and evidence

Full independent derivation, branch checks and boundary protocol: model.md. Front z=0, glassn>1, back z=-h, source z=-G; normal entry. For v=F-x,s=G-h,R=sqrt(|v|²+s²),D=nR-s: grad(h)=v/D. h is unknown; s is NOT an independent pixel gap. Surface compatibility requires D*curl(v)-(n/R)*K=0, K=v_y*(v·partial_xv)-v_x*(v·partial_yv). Reject nontransmitted exit branch s<=|v|/sqrt(n²-1), TIR/critical, nonpositive height/gap/descent.

Equation checks pass: known transmitting quadratic inverse gradient error2.78e-17, integrated height error2.86e-14L, two-path difference1.34e-15L. Its map curl is nonzero1.69e-5 while compatibility residual<1.71e-13. Therefore raw map curl by itself is not used as rejection. Identity/flat surface exact; invalid lateral inverse branch rejected. Closed-form clearance inversion independently recovers656known-surface points within3.49e-7L. Earlier checks reused, not repeated.

The protocol fixes centerh0=.5L and centerclearanceg{.5,2,8}L, n{1.33,1.5,1.8}. G=h0+g. Only the center height is anchored; no invented constant boundary height. Both paths remain inside the coordinate-convex frozen crowned footprint. All configurations, invalid sets and numerical fields retained.

| n | g/L | two-path height RMS/L | invalid inverse points xy/yx | forward map vector RMS px xy/yx | forward TIR stencil points xy/yx |
|---|---:|---:|---:|---:|---:|
| 1.33 | 0.5 | 0.03986862 | 460/344 | 5.008/5.301 | 0/628 |
| 1.33 | 2 | 0.03869593 | 0/0 | 8.796/24.389 | 0/280 |
| 1.33 | 8 | 0.01224695 | 0/0 | 8.375/41.377 | 0/0 |
| 1.5 | 0.5 | 0.03635632 | 338/278 | 6.637/5.986 | 0/660 |
| 1.5 | 2 | 0.02706976 | 0/0 | 8.671/31.264 | 0/208 |
| 1.5 | 8 | 0.00813388 | 0/0 | 8.369/40.486 | 0/0 |
| 1.8 | 0.5 | 0.03002810 | 120/80 | 8.973/8.346 | 0/688 |
| 1.8 | 2 | 0.01775458 | 0/0 | 8.584/38.692 | 0/144 |
| 1.8 | 8 | 0.00510732 | 0/0 | 8.365/39.887 | 0/0 |

These are .04L coarse-grid diagnostics, not native image scores. Forward errors exclude invalid rays ONLY with their counts reported; full invalid fields are retained. At n1.5,g2: two-path RMS .02706976L atRK.02, .02706949L atRK.01, .02713905L atspatial.02/RK.01. Integration-step error is much smaller than path mismatch. Forward errors change8.671/31.264px→11.002/31.262px at finer spatial grid: not spatially converged and NOT a best-approximation/lower bound. Large-gap path-height mismatch decreases partly through scaling; forward map mismatch remains, so no automatic physical success.

## Stronger necessary condition, unknown height retained

On the physical transmitted branch, rho=K/c (c=curl(v)!=0) must satisfy rho>|v|², independent of n>1. This follows from monotonic D*R/n=M+s²-s*sqrt(M+s²)/n on s>sqrt(M/(n²-1)). Where possible, the positive analytic root s_req in model.md is NECESSARY and must ALSO satisfy -grad(s_req)=v/D. It is not promoted to an adjustable gap or recovered surface. Near-zero curl remains unresolved.

Direct derivatives1e-4/5e-5L, finite-step noise margin and curl floors1e-5/1e-4/1e-3 are reported. At grid.02L,9248/20755footprint points (44.558%) violate the necessary branch condition at the1e-5floor;7668/20755 (36.945%) at1e-3. Corresponding .04grid fractions44.824%/37.056% are similar. The6boundary-crossing nodes all fail robustness; their large central-derivative outliers are explicitly unresolved, not used in the incompatibility claim. Required-clearance derivative residuals are ill-conditioned at small-c/branch-transition sets and NOT spatially converged; retain them as diagnostics only.

Interior example x1.5L,y.88L, depth.0952921L: c1.516687588, M.364874627, rho.281531090. rho<M by.08334, stable under NEW selected1e-5→1e-6L probes. This mismatch cannot be fixed by choosing a transmitted per-pixel clearance. It does not rule out another approximate surface, camera, front surface, material or source model.

## Next reusable hypothesis

Do not integrate/copy this empirical map and call it an identified surface. Queue18 can test ONE independent low-dimensional biaxial back surface h/L=.5+bMajor*Xmajor²+bMinor*Xminor²+c*T², with actual crowned T gradient, n1.5,G2.5L, bMajor/bMinor±.03,c±.15 declared before any fit. Three shared geometry coefficients, no per-crop/source correction. Analytic height/slope bounds must certify positive height/gap and subcriticality; then a coarse MAP-only projection can propose parameters, followed by a single native comparison if defensible. No source promotion or optical improvement credit follows from geometry.

Source14–15found no newly reliable hidden ink or absolute RGB. That limits interpretation of an image-calibrated map but does not enter this target-free compatibility calculation. A low-dimensional approximate physical family may still be a useful reusable model; the diagnostics above do not quantify its best attainable target score.

Reference verified: [Bösel and Gross1510.01129v2](https://arxiv.org/html/1510.01129), II.2equations4–11, links normal-field integrability and Snell's law and describes its small-angle construction as approximate. Our graph/propagation derivation is explicit in model.md. Lead's private switch model was read only for independent equation conventions. No lead files edited or switch fit imported.

Commands: existing Docker localica-dark-lab-check, OPENBLAS_NUM_THREADS=1 PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps; python3 /tmp/agent-toolbar-surface-diagnostic.py --invariants-only, then --reuse-invariants; python3 /tmp/agent-toolbar-surface-compatibility.py; separate run_grid(.02,.01,[configs[4]],'spatial-02-RK01'); python3 /tmp/agent-toolbar-surface-numerical-review.py. Originals/results are sealed; do not repeat completed diagnostics.
