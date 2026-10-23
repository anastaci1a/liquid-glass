# Bounded physical-surface review

- Height/Snell/scale/mirror/rotation/clearance tests pass for the declared unequal-axis bodies. Material remains empirical, so these are valid ray geometries rather than fully physical renderers.
- Quadratic T back profile: map-projected native E26.655/17.167, worse than accepted14.152/15.448.
- Biaxial plus T² back profile: map-projected21.195/16.308. Eight-step native shared-material fit ends E ratios1.234678/1.009526: still fails both backgrounds. Last step improves a little; this is bounded rejection, not proof of global convergence or family impossibility.
- Curved-front/flat-back tests in neighboring physical-front-surface: simple boundary-height orders1,2,3 also failed map initialization. Direct photometric two-start/300evaluation studies for orders1/2 remained much worse (E34.068/25.745 and36.137/23.325). No accepted pass or public render change.
- A surface can be mathematically valid and a poor match. Low-order polynomial height does not replicate the retained empirical rim profile; do not compensate by changing source pixels or scoring masks.
- Next distinct comparator parameterizes back height by actual Euclidean distance to the crowned boundary, with a compact spline rim and biaxial core. This tests a missed geometric distinction from the older potential study, which used the non-Euclidean boundary coordinate. Its height normal must be differentiated correctly and validated before any image claim.
