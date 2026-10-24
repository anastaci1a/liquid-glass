# Independent straight-body grazing integration

**PASS WITH LIMITS.** All twelve frozen pixel rows agree with root adaptive values within the predeclared absolute tolerance of 1e-7. This verifies scalar first-front interface power integration, not radiance, RGB integration, selected antialiasing or scoring. The circular two-dimensional pixel problem remains separate.

## Scope and clock

The task began at 08:10:12.489 UTC on 24 October 2026. Its unchanged hard deadline is 08:18:12.489 UTC, including documentation and versioning. Root scientific files are pinned to `af8db46252dd2fe1cadc55b707be96e56fb6a243`. First and last hashes match. No root files were edited.

The phase verification used original case metadata and corrected center placements before quadrature. The original unit is 88.5 native pixels. The minor half-extent is 1.012503164339156; the corner radius is 1.0043663048754772. The axial half-thickness is 0.07090401172809527. The vertical translation does not change the normal.

## Independent derivation

On the straight body, let the inner-rectangle half-height be the minor half-extent minus the corner radius. The actual implicit surface is

$$
F=\rho^2+\left(\frac{z-z_0+\eta}{\eta}\right)^2-1,
\qquad
\rho=\frac{|y|-b+R}{R}.
$$

The same implicit gradient supplies the incident cosine. With the substitution below, the square-root endpoint disappears from the integration measure:

$$
\rho=\sin\beta,
\qquad
|dy_{\rm native}|=LR\cos\beta\,d\beta,
\qquad
c=\frac{\cos\beta}{\sqrt{\cos^2\beta+\left(\frac{\eta}{R}\right)^2\sin^2\beta}}.
$$

The independent implementation uses algebraic air-to-index-1.5 Fresnel power, without importing or executing shared numerical optics:

$$
c_t=\sqrt{1-\frac{1-c^2}{n^2}},\qquad
R_s=\left(\frac{c-nc_t}{c+nc_t}\right)^2,\qquad
R_p=\left(\frac{nc-c_t}{nc+c_t}\right)^2,
\qquad R_f=\frac{R_s+R_p}{2}.
$$

Each unit-width native pixel is clipped to the projected footprint. Exterior power is zero. The exact projected edge supplies the integration endpoint; roundoff-sized endpoint representation is restored to one before arcsine. This is a one-sided measure-zero limit, never a fabricated regular tangent ray or normal.

## Results

| Check | Result |
| --- | --- |
| Fixed quadrature requests | 24: 64 and 128 nodes for each of twelve rows |
| Nonempty intervals | 8 |
| Joint cosine/Fresnel scalar points | 1,536, below 3,000 |
| Maximum 64 versus 128 difference | 1.18e-16 |
| Maximum 128 versus root adaptive difference | 1.64e-13 |
| Root adaptive reruns | 0 |
| Optical rays, source/RGB queries, images | 0 |

Expanded lower row 503 retains root AA2 power 0.33802421721784204 versus continuous power approximately 0.02523092017814. The discrepancy is sampling phase and grazing-band integration evidence. It does not establish a reflected scene, source support, radiometric calibration or an adopted replacement antialiasing protocol.

Every row and discrepancy is retained in `result.json`. The four completely exterior intervals have zero integral and consume no scalar Fresnel points. No node-count search, adaptive refinement, tolerance change, normal modification or geometric setting was introduced.

## Provenance and limits

First/last hashes cover root scientific records, implicit geometry, coordinate implementation, family metadata and corrected phase inputs. Tracked inputs were also compared directly to immutable root Git blobs. Local case metadata hashes are retained separately; source and target RGB were not decoded.

The independent calculation applies only to a straight body where the field is constant longitudinally. It cannot certify circular pixels, cap integration, internal reflections, illumination or a complete image. All previous accepted states, negative studies and original counts remain unchanged.
