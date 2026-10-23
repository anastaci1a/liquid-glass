# One geometry-conditioned scattering covariance proxy (queue24)

Empirical geometry-conditioned scattering, NOT derived physical roughness. The
positional inverse-map Jacobian is not a microfacet-normal angular response.
Accepted toolbar rev2/source6c68d31a/epochd1d864eb remain fixed pending independent
review of23's separate typography input proposal. No crop/reference coefficients.

Let J=DF0 be the accepted map's lens-INTERIOR Jacobian, H=J-I,
A=H/sqrt(1+||H||_F²), M=A*A^T. Proposed single normalized scalar rho>=0 adds
source covariance rho²*L²*M to the fixed ordinary Gaussian source branch:

    Sigma_blurred = L²*(sigma0²*I + rho²*M).

The existing clear/source-blurred transition w(d) is retained. Precisely, at an
original4×4native ray x, use the same extra scattering offsets for BOTH branches:

    E_u[(1-w)*S(F0(x)+rho*L*A(x)*u)
        + w*(G_sigma0*S)(F0(x)+rho*L*A(x)*u)],  u~N(0,I).

Then apply existing material/lighting at x, sharp coverage, coverage-normalized
postfilter, independent generated shadow and original vector glyphs in unchanged
order. RGB channels share every offset/weight. This is not dispersion. sigma0,
transition, postfilter and all photometric coefficients stay fixed. The clear
branch's ordinary covariance is zero, not sigma0²; the baseline transition is
not silently removed. At rho0 delegate the accepted renderer exactly.

PSD and bounds: v^T*M*v=||A^T*v||²>=0. tr(M)=||H||F²/(1+||H||F²)<1; operatornorm(M)
<=tr(M)<1. Extra source standard deviation in any direction <=rho*L. Fix initial
rho[0,.02] before any image fit, maximum3.4nativepx atL170; compared with fixed
ordinary sigma11px this is a modest bounded spatial covariance, not a new global
sigma sweep. Do not widen from a first threshold/bound hit without review.

Similarity invariants: under x'=kQx and F'=kQF with orthogonal Q, J'=QJQ^T and
A'=QAQ^T, so M'=QMQ^T and Sigma'=k²Q Sigma Q^T. Mirrors/90degree rotations are
exact symmetries of Cartesian symmetric Gaussian quadrature; other rotations
hold in the continuous integral and need numerical convergence assessment.
Uniform source stays uniform. Identity transport J=I has zero added scattering
by this empirical definition, even though a physical rough material need not.

This added scattering is independent of pixel-footprint antialiasing. Native
4×4coverage/transport samples remain fixed; their locally affine source-space
pixel-footprint covariance is (5/64)*J*J^T nativepx². It is already present and
is not replaced/increased to gain score. Added scattering uses (J-I), has a
shape-relative material scale rho*L, and NEVER jitters silhouette coverage,
lighting, vector glyphs or shadows. At high-res evidence, rho*L still uses the
same physical source/native units; AA remains the frozen protocol.

Differentiate the actual crowned r-b coordinate, B-spline and tangential field,
not an assumed Euclidean distance or inferred optical surface. Use the lens-side
boundary derivative, not the distributional jump to identity outside the lens.
Outside footprint J=I/A0. Preserve the inherited near-center numerical normal
branch as an explicit flag. Native4×4rays avoid its exact symmetry singularity;
verify this rather than claiming every arbitrary point is differentiable.

The first nonzero expansion is in s=rho², not rho:

    deltaS = .5*s*L² * M : Hess_source(S)(F0) + higher orders.

There is no leading gradient/centroid shift. Ordinary isotropic blur's generator
uses I:Hess; this proxy uses a fixed, varying anisotropic M. A zero derivative
with respect to rho at0 is not evidence of a dead direction. Geometry/source
confidence and saved ordinary-blur evidence should establish whether M is more
than a redundant constant isotropic operator before any new native calibration.

Finite deterministic Gaussian quadrature has explicit offsets and support.
For maximum chosen node norm Rq, source-offset norm<=rho*L*Rq; include the
existing source-filter and postfilter support separately. Gaussian truth has
unbounded tails, so finite nodes are a numerical approximation, not all-tail
physical certification. Inspect actual emitted nodes, source confidence,
quadrature order and native-score/crop differences. Numerical convergence is
not an optical pass. No new AA, output mask, source input or scoring epoch.
