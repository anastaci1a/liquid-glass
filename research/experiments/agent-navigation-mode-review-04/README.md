# Navigation: missing longitudinal height freedom

The transferred spline has exactly zero longitudinal curvature in its straight body. Its caps already produce substantial longitudinal transport. Saved evidence motivates one conditional height-modulation test, but identifies neither its sign nor amplitude. This is not a universal failure of splines or geometric optics.

The [sealed pair](../agent-navigation-spline-03/README.md) remains rejected. Its source, interface and parity gates passed; both E and SSIM regressed. No model, source, mask, foreground style or historical acceptance changes here.

## Scope and clock

[Protocol](protocol.json) starts at 22:44:17.104 UTC on 2026-10-23 and ends at 22:54:17.104 UTC, including versioning. This review reads saved arrays and derives symbolic bounds. It performs zero rays, height evaluations, RGB queries, filters, images, fits or surface implementations.

[Analysis](analyze_saved.py) and [results](result.json) retain reductions and input hashes. An old local NPZ was an LFS pointer; safe loading stopped. The [recovery](cache-recovery.json) read the already-materialized, hash-matched historical artifact without downloading or reconstructing it.

## Exact geometric limitation

Let the frozen half-extents and corner radius be in the original case length unit. The actual coordinate and height are:

$$
\begin{aligned}
\rho(x,y)&=\frac{\sqrt{[|x|-(a-r)]_+^2+[|y|-(b-r)]_+^2}}{r},\\
h_0(x,y)&=p(\rho(x,y)),\qquad [u]_+=\max(u,0).
\end{aligned}
$$

Here the radius equals the minor half-extent. In the straight body:

$$
\begin{aligned}
|x|&<a-r=3.4911561983,\qquad \rho=\frac{|y|}{r},\\
\partial_x h_0&=\partial_{xx}h_0=\partial_{xy}h_0=0.
\end{aligned}
$$

With a flat front and normal incidence, the exit direction has zero longitudinal component there. Thus the raw longitudinal source coordinate equals the entry coordinate exactly. Changing the scalar profile cannot add longitudinal stretching in this region. Transverse curvature and cap curvature remain available.

## Saved coordinate measurements

These quantities describe the backward source map, not image displacement estimates or recovered Apple correspondences. The shared geometry is identical across A and B. The original length unit is 113.5 native pixels; cached subray spacing is 0.5 native pixel.

| Saved cohort | Longitudinal source displacement | Transverse source displacement | Mapping derivatives |
| --- | --- | --- | --- |
| Straight body, 716,193 valid stencils | Exactly 0 px | RMS 31.3984 px | Longitudinal derivative 1 within floating arithmetic; both cross derivatives 0 |
| Caps, 159,735 valid stencils | RMS 30.4077 px | RMS 30.2249 px | Longitudinal derivative ranges −4.5563 to 1.0474 |
| Straight section near center | Exactly 0 px | +0.00973 px | Saved section is slightly below zero, not an exact center sample |
| Straight section near upper 0.75 L | Exactly 0 px | +20.9587 px | Constant along the straight segment |
| Straight section near lower 0.75 L | Exactly 0 px | −20.6427 px | Different sampled ordinate explains the unequal magnitudes |

Negative derivatives describe reversals. Their existence alone is not a rejection criterion. The already-reviewed B dark cap arc and extra upper text return occur at incorrect locations relative to the retained reference.

Centered differences use existing neighbors only. All stencil members must be complete inside rays. Straight and cap cohorts exclude a two-subray-width strip around the join; no derivative is filled or smoothed across that seam. Cap and transverse derivatives are finite-spacing diagnostics, not continuum extrema certificates.

| Frozen crop | Lens / straight-miss subrays | Longitudinal RMS, lens | Transverse median, lens |
| --- | --- | --- | --- |
| Left cap | 274,911 / 28,689 | 16.7534 px | −0.0510 px |
| Upper body | 152,092 / 9,108 | 2.6998 px | +17.2267 px |
| Lower body | 175,675 / 10,325 | 2.5186 px | −10.5093 px |

The upper/lower rectangles include a small part of the right cap. Their nonzero longitudinal RMS must not be attributed to straight-body curvature. Every straight miss retains zero raw coordinate displacement. Raw source coordinates match the saved original-frame conversion exactly.

Coverage is a separate quantity: 220,373 full, 1,266 partial and 140,161 zero-coverage pixels. It is bit-identical to the sealed H1 coverage. Raw ray displacement is not alpha, a completed foreground measurement, or an optical scoring-mask change.

## What H1 can and cannot establish

The [original harmonic H1](../navigation-geometry-01/surface.md) already has a longitudinal quadratic height component. Its saved central longitudinal section has second difference −0.00294620 in normalized units, whereas the transferred spline's straight-body second difference is exactly zero. [Section comparison](h1-section-comparison.json) uses cached heights only.

Old H1 source coordinates and exit paths were not retained in its raw material/complete/coverage artifacts. No pointwise old-to-new path delta is asserted or reconstructed. H1 also used distance 2 rather than 2.1. Its different image cannot isolate the missing longitudinal degree of freedom by itself.

Mostly white source regions weakly constrain transport. Temporal mosaic text, incident softness, nonlinear foreground response and unobserved illumination can all affect the visible returns. Target bright bands are landmarks, not established incident boundaries. The saved crop regressions do not identify a unique missing surface mode.

## One conditional actual-height alternative

A single even longitudinal modulation of the existing actual height preserves the accepted footprint:

$$
\begin{aligned}
f_\epsilon(x)&=1+\epsilon\frac{x^2}{a^2},\\
h_\epsilon(x,y)&=f_\epsilon(x)h_0(x,y),\\
\nabla h_\epsilon&=f_\epsilon\nabla h_0
 +\frac{2\epsilon x}{a^2}h_0\begin{pmatrix}1\\0\end{pmatrix}.
\end{aligned}
$$

This is a proposed height, not an implemented adapter or a normal correction. The same height would supply every section, intersection and normal through shared primary tracing. No convex reflected-path claim follows from this modulation.

In the straight body:

$$
\partial_{xx}h_\epsilon=\frac{2\epsilon}{a^2}h_0,
\qquad
\partial_{xy}h_\epsilon=\frac{2\epsilon x}{a^2}\partial_y h_0.
$$

Positive modulation creates opposite longitudinal slope signs to negative modulation. Neither sign is selected here. The transverse center section and its gradient remain unchanged, so this test cannot repair a symmetric central vertical-return error or create missing illumination. It would discriminate whether off-center text spacing and cap-to-body transitions need longitudinal coupling.

## Symbolic primary-path certificate

Let the existing global bounds be height H and slope M. Set the absolute modulation magnitude to e. For e below one:

$$
\begin{aligned}
0&\leq h_\epsilon\leq H_\epsilon=(1+e)H,\qquad e=|\epsilon|<1,\\
\|\nabla h_\epsilon\|&\leq M_\epsilon=(1+e)M+\frac{2eH}{a}.
\end{aligned}
$$

The existing height is positive inside and zero on the boundary. Positive multiplication preserves both facts and C1 joins/center regularity. Boundary creases remain unresolved; no epsilon band or repaired normal is proposed. The footprint remains convex even if the resulting solid is not convex.

The flat-front primary certificate and physical background-plane requirement are:

$$
\begin{aligned}
(n^2-1)M_\epsilon^2&<1,\qquad D>H_\epsilon,\\
\gamma_\epsilon&\geq\sqrt{1-(n^2-1)M_\epsilon^2}>0.
\end{aligned}
$$

Here gamma is a lower bound on outgoing clearance rate. It does not certify reflected paths or supply environment radiance. With H=0.1381819203, M=0.6732687149, a=4.4941392412, n=1.5 and D=2.1, a sufficient strict admissible magnitude bound is:

$$
 e<\min\left(1,\frac{D}{H}-1,
 \frac{\frac{1}{\sqrt{n^2-1}}-M}{M+\frac{2H}{a}}\right)
 =0.3009929444\ldots.
$$

The decimal is descriptive, not a rounded inclusive execution limit or a chosen amplitude. No parameter is fitted or selected. Any future implementation still needs shared-owner review, exact surface controls and a new whole-body/all-guard finite-kernel source audit before RGB.

## Remaining stages and disposition

| Stage | Retained evidence / unresolved question |
| --- | --- |
| Refraction | Fixed spline pair rejected; conditional longitudinal discriminator proposed, not activated. |
| Blur | Retain current incident sigma 6.75 and original radius 21; no width inference from these coordinates. |
| Color | Unit response retained for the pair; no tone adopted from playback. |
| Outline | Missing light and unobserved environment remain unresolved. |
| Shadow | Historical underlay regression remains rejected; no new field or strength. |
| Foreground | Exact ordered nonlinear chain and all original vectors retained; failed guards remain failed. |
| Dispersion | Earlier identification limits remain; this neutral geometric audit does not establish absence. |

The recommendation is a bounded future discriminator only. The current incident Navigation baseline, every historical score and all sealed evidence remain unchanged. No additional family or native observation is authorized by this report.
