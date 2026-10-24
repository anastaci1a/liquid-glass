# Expanded playback: outline power and response limits

**Useful partial result; no outline image or material adoption.** The selected transmission response cannot reach some observed bright rim pixels. Actual cached normals support a partial power ledger, but the reflected scene remains unknown.

| Record | Evidence |
| --- | --- |
| Predeclared clock and budgets | [Protocol](protocol.json) |
| Actual counts, bounds and input hashes | [Result](result.json) |
| Reproducible calculations | [Audit](audit.py) |
| Selected geometry and tone | [Accepted increment](../expanded-contrast-guard-02/README.md) |

Science finished at 01:09:48 UTC, seven seconds after declaration. The fifteen-minute block ends at 01:24:41.774 UTC. No new intersections, heights, source queries, composites or parameter fits ran.

## Actual geometry and next encounter

The existing global height Lipschitz bound applies to the selected back. The solid lies between that back and the flat front. Its footprint is convex; the back itself need not be concave.

$$
\begin{aligned}
-h(\mathbf{x})&\le z\le 0, & \|\nabla h\|&\le M,\\
g(t)&=z(t)+h(\mathbf{x}(t)), &
\frac{\mathrm{d}g}{\mathrm{d}t}&\ge r_z-M\|\mathbf{r}_{xy}\|.
\end{aligned}
$$

A strictly positive lower bound prevents a reflected segment from hitting the back again before the front. Extend the nonnegative, boundary-zero height by zero outside its footprint. Leaving that footprint below the front would contradict positive clearance.

This certifies the next front encounter for 800,823 of 890,848 cached back reflections. The other 90,025 next intersections remain unresolved. No convex-solid intersector or assumed back concavity was used.

The numerical certificate reserves a positive margin:

$$
r_z-M\|\mathbf{r}_{xy}\|>10^{-10}.
$$

This is a geometric classification margin, not a scoring allowance. The maximum global slope bound is 0.6723414566.

## Power ledger and missing scene

The first front reflection carries four percent under the declared lossless dielectric indices. Back reflection varies from four percent to 7.576 percent. These are optical power fractions, not encoded RGB predictions.

The first front event is normal incidence. The back reflection and next flat-front encounter share their incidence plane. Separate polarization components therefore propagate as follows:

$$
\begin{aligned}
P_{\mathrm{primary}}&=T_0\frac{T_{b,s}+T_{b,p}}{2},\\
P_{\mathrm{front\ exit}}&=T_0\frac{R_{b,s}T_{f,s}+R_{b,p}T_{f,p}}{2},\\
P_{\mathrm{remaining}}&=T_0\frac{R_{b,s}R_{f,s}+R_{b,p}R_{f,p}}{2},\\
R_0+P_{\mathrm{primary}}+P_{\mathrm{front\ exit}}+P_{\mathrm{remaining}}&=1.
\end{aligned}
$$

The last two formulas apply only to certified next-front encounters. Elsewhere, all back-reflected power remains unresolved. The maximum partition error is 2.22e-16.

Among certified front encounters, 72,808 are totally internally reflected or critical. That count does not classify the unresolved next intersections. Remaining internal or unresolved power reaches 7.273 percent; none is discarded or assigned a color.

Front-environment radiance is unobserved. No reflected image, environment replacement or transmission-tone application to specular radiance is justified by this calculation. The current renderer's unit-throughput transmission is unchanged.

## Encoded transmission ceiling

The selected common response has the following bounded-input ceiling:

$$
\begin{aligned}
G(S)&=gS+b, & 0&\le S\le 1,\\
G(S)&\le g+b=0.9252129976035592.
\end{aligned}
$$

A conservative float32 upper enclosure is used for target comparisons. The original rim mask and actual full-coverage pixels remain unchanged.

| Reference | Fully covered rim pixels | Any channel above ceiling | All channels above ceiling |
| --- | ---: | ---: | ---: |
| A | 45,750 | 3,485 | 161 |
| B | 45,750 | 6,005 | 5,866 |

The maximum channel excess is 19.07 eight-bit levels in either reference. Under current coverage and bounded encoded input, transmission grading alone cannot produce these values.

This does not identify reflection as their unique cause. Coverage, illumination, source estimation and photographic response remain alternatives. Optical powers must not be added directly to encoded RGB as if it were linear radiance.

## Decision and reusable implication

Retain the accepted spline, incident blur and tone. Preserve the missing bright rim as unresolved. A painted Fresnel-colored border would not establish a complete optical model.

Any future reflected image needs ordered paths for the actual potentially nonconvex height solid and supported incident radiance. Shared transmission and reflection roles must remain distinct. No new surface, image or fitted illumination is activated here.
