# Analytic crossings of retained exit rays

Shorter distance is locally insufficient for the selected central upper/lower rays. Their same-side modeled track crossings require invalid negative background distances. Valid crossings exist at the opposite track edge at much larger distances. Neither branch can be assigned uniquely to Apple's bright regions, whose incident identity remains unknown.

The declared clock is 20:24:49–20:34:49 UTC, within the unchanged 21:10:40.688 refraction deadline. This analysis uses 72 unique saved subrays, represented twice in intersecting horizontal/vertical section records. There are zero new rays, RGB queries, images, fits or distance-grid evaluations. Cumulative budgets remain 7,473,600 native rays, 8,182 fixture/comparator rays and four native images.

## Exact physical-plane dependence

For saved exit position e and downward unit direction u, intersect the plane z=−D. In original-L units:

$$
\lambda(D)=\frac{-D-e_z}{u_z},\qquad
p_{xy}(D)=e_{xy}+(D+e_z)\frac{u_{xy}}{-u_z}.
$$

The complete background plane must satisfy D greater than the maximum back depth, 0.1090909091L. The outward path and its direction remain the saved physical ray. Relative to the frozen track center, write the line as a+bD, where b is the actual exit-direction ratio. Changing D cannot reverse b or change the exit normal.

The source construction declares a capsule: a horizontal segment of half-length c, swept by a circle of radius r. Both are read directly from the frozen case. Top/bottom crossings solve a linear equation. Cap crossings solve the following quadratic, retaining both real roots and the appropriate half-circle domain:

$$
\lVert a+bD-(\pm c,0)\rVert^2=r^2.
$$

No iterative solver, source-boundary fit or RGB lookup is used. Negative or shallow-plane roots are retained and marked invalid. Nearly stationary central rays retain their very large algebraic roots; these are not proposed image settings. Seam classification uses a declared 1e-12 numerical allowance, without changing any rendering guard.

## Same sections, multiple roots

The same six sections from correspondence-02/03 are used. Three fixed positions per section select the central and ±0.6 offsets; all four original AA subrays are retained. Shared positions appear twice as section records. [All roots and finite bands](crossings.json) remain available; no preferred root is selected by image error.

| Central-column point | Same-side crossing D/L | Opposite-edge crossing D/L |
| --- | ---: | ---: |
| A upper, y408 | −1.708 to −1.642 | 28.275 to 28.485 |
| A lower, y667 | −2.468 to −2.395 | 27.555 to 27.758 |
| B upper, y417 | −2.307 to −2.231 | 28.962 to 29.196 |
| B lower, y657 | −3.234 to −3.149 | 27.984 to 28.208 |

The upper rays enter through the top modeled boundary at an invalid plane and eventually leave through the bottom at a valid algebraic distance. Lower rays show the converse. Thus weaker inward transport cannot expose the same-side boundary at these selected central points. Farther propagation permits opposite-edge sampling, but that is not evidence Apple uses this branch.

Cap behavior differs. Representative A upper-right and B upper-left subrays have valid entering roots at approximately 0.244L and 0.882L. These explain why shorter propagation can reveal cap-adjacent background while the central return remains misplaced. There is no global statement that all rays need the same mechanism.

## Finite kernel and source limits

Conservative capsule offsets use radius r plus/minus rho, with rho equal to sqrt(2) times (kernel radius+1.5) divided by L. This encloses the finite square incident kernel, bilinear texels and original source-pixel coverage. The resulting intervals bound mixed footprints; they are not exact raster thresholds or alternate-distance source proofs.

A upper central footprints may remain mixed near the smallest valid planes, up to roughly D=0.389L in this enclosure. Their point crossing still remains invalid. The other three central groups' same-side mixed enclosures end below the valid-plane domain. Opposite-edge mixed intervals broadly span approximately 25.5–31.3L. All individual roots are retained rather than replacing these bands with sharp boundaries.

The analytic boundaries describe the declared modeled capsule, not recovered hidden photography. Distant copied source content, full-image support at other planes, transition state and optical brightness remain unvalidated. No full alternate map is created. Bright target ridges are neither assumed source boundaries nor physical coverage; reflection and illumination remain plausible contributors.

## One geometric hypothesis for review

A genuine concave-front sign-contrast hypothesis is justified as a discriminator: retain the frozen footprint and back, and test whether a smooth recessed front can produce outward net transport at the problematic upper/lower locations while preserving positive thickness. Its front height, intersections and normals must come from one explicit surface, with complete ordered paths certified before any sampling.

This is not proof that a curved front is necessary. Changing an actual back curvature profile could also change net transport; the present evidence cannot identify which surface Apple uses. The proposed curved-front comparison isolates a genuinely different refracting interface, rather than another distance sweep or independent normal adjustment. No new surface or shared API is implemented here.

Such a front may invalidate the current convex-path certificate, so the shared-core owner must review the solid and ordered-intersection requirements first. If that control is not justified, close refraction with the two negative diagnostics. Later blur or colour stages must remain separate and cannot be claimed as a refraction rescue.
