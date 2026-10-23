# Independent slider tone review

Status: isolated encoded-tone component accepted for the experimental H1 state. Historical pass09 and full-pipeline counts remain unchanged.

The candidate uses one common response on both references:

$$
\mathbf{C}=\operatorname{clip}(g\mathbf{S}+b\mathbf{1},0,1),\qquad
g=0.7670740463511121,\qquad b=0.2313859317868898.
$$

Independent replay from retained raw samples reproduces both complete native images, sampled colours, clear samples and every reported original score exactly. All original H1 guards and both predeclared center checks pass. Two cached composite controls use zero rays, source queries, filters or fits.

| Metric | A | B |
| --- | ---: | ---: |
| Candidate E | 51.541176 | 26.858637 |
| Center RGB RMSE, baseline | 21.289447 | 12.158391 |
| Center RGB RMSE, candidate | 4.994948 | 5.083740 |

Both full triptychs and fixed crops were inspected. Green/gray centers are visibly closer without the full proposal's excessive whitening. Missing white returns and reflective contours remain; the lens is still too uniform.

[Verification](verification.json) retains exact hashes, scores and guard results. The peer worktree was read-only. Source coordinates, incident kernels, geometry, masks and coverage did not change.

This is empirical encoded grading, not recovered radiance, refraction repair or successful full-material transfer. Hidden source confidence remains modeled, with observed confidence zero. The next outline audit must use the same surface and independent supported illumination; no painted halo is authorized.
