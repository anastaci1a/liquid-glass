# Portable optical and motion equations

[Guide](README.md) · [Observed Apple evidence](optics.md) · [Lab](../lab/index.html) · [Executable reference](../lab/model.js)

**Status:** mathematically specified Localica hypotheses, not recovered Apple formulas. These equations define a candidate for future rendering, not the current Android renderer. The small reference has no browser, GPU or framework dependency. The [portable fixtures](experiments/model-fixtures.json) provide boundary, core and corner coordinates/normals/derivatives for later backend comparisons.

Use the same units and conventions when porting it; do not copy a shader's constants without its domains.

The frozen reference recreations have their own [dimensionless recipes](recreation-models.md). This page also describes experimental models preserved on `research/glass-lab-preserved-222`; mentions of their lab controls do not describe the deployed lab. Its executable reference is separate from the deployed renderer.

## Coordinates and validity


Shape-local position [the condition below](#model-equation-101), positive X right, positive Y down; positive Z toward the viewer. All lengths use one logical coordinate system. Convert device pixels only at rasterization/sampling boundaries.

<a id="model-equation-101"></a>

$$
p=(x,y)
$$

- Rounded rectangle half-size [the condition below](#model-equation-102); [the condition below](#model-equation-103). Circle and capsule are special cases. Zero radius is outside this model's domain.

<a id="model-equation-102"></a>

$$
h=(\mathrm{hx},\mathrm{hy})>0
$$

<a id="model-equation-103"></a>

$$
0<r\le \operatorname{min}(h)
$$

- Rays propagate **toward** the interface. This differs from conventions that store a vector pointing back toward the ray origin.
- `F(p)` is an **inverse image map**: output position `p` samples source position `F(p)`. Source-feature movement has the opposite interpretation. Add the surface's backdrop-space origin after evaluating this local map.
- Material/optical state, source transform, clip, foreground and shadow must use the same frame and geometry. Optical mapping does not include foreground text.
- Valid finite input is a caller precondition. The reference is an oracle, not an untrusted-input API. Production adapters must reject invalid dimensions, nonfinite values and unsupported optical ranges.

For component-wise absolute value and maximum:

$$
\begin{gathered}
q = \operatorname{abs}(p) - h + r \\
\mathrm{sd}(p) = \operatorname{length}(\operatorname{max}(q,0)) + \operatorname{min}(\operatorname{max}(\mathrm{qx},\mathrm{qy}),0) - r \\
d = -\mathrm{sd}(p)\quad\text{positive inside} \\
b = \operatorname{min}(r, \operatorname{min}(h) \times  \mathrm{band})\quad\text{0 < band at most 1} \\
u = \operatorname{clamp}(d/b, 0, 1) \\
n = \operatorname{gradient}(\mathrm{sd})\quad\text{unit outward normal where differentiable} \\
S(u) = 6u^{5} - 15u^{4} + 10u^{3}
\end{gathered}
$$

Inside the active band, straight sides have constant `n`; circular corner contours have curvature [the expression below](#model-equation-1). **Straight segments have zero curvature even when one component of `max(q,0)` is positive. ** The medial axis has no unique normal; the edge contribution and its first derivative vanish before or at that axis.

<a id="model-equation-1"></a>

$$
\kappa_d=1/(r-d)
$$

The signed-distance outline is C1 at straight/arc joins, not globally C2. One-sided derivatives are appropriate there.

## Boundary field: displacement is not compression

This is a designed image warp, not an optical solid. It allows separate core magnification, edge strength, band width and outline displacement.

$$
\begin{gathered}
R(u) = (1-u)^{3}(1+3u) \\
H(u) = (256/27) u(1-u)^{3} \\
P(u) = \rho  R(u) + (1-\rho ) H(u)\quad\text{0 at most rho at most 1} \\
c = \mathrm{core} \times  \mathrm{power} \\
a(d) = b \times  \mathrm{edge} \times  \mathrm{power} \times  P(u) \\
F(p) = (1 - c S(u)) p - a(d) n
\end{gathered}
$$


[the expression below](#model-equation-2), so a positive `ρ`, edge and power retain displacement at the outline. [the expression below](#model-equation-3), so the map also has a rising compression band when [the condition below](#model-equation-104).

<a id="model-equation-104"></a>

$$
\rho <1
$$

- [the expression below](#model-equation-4): no artificial inner shoulder join. [the condition below](#model-equation-105); the maximum edge contribution is bounded by `b×edge×power`.

<a id="model-equation-105"></a>

$$
0\le P\le 1
$$

- In the core, [the condition below](#model-equation-106); displayed magnification is `1/(1−c)`, provided [the condition below](#model-equation-107). The slider named optical power is dimensionless gain, **not geometric thickness**.

<a id="model-equation-106"></a>

$$
F=(1-c)p
$$

<a id="model-equation-107"></a>

$$
c<1
$$

The older shoulder profile forces displacement and its derivative to zero at the outline. It explains an apparently inactive outer strip.

$$
P_{\mathrm{old}}(u)=16u^2(1-u)^2
$$
- The alternative `R` retains outline displacement but has a negative inward derivative: much of that band magnifies rather than compresses. Both remain explicitly labeled comparisons.
- None of these outline continuations is calibrated to Apple's outermost rim.
- A physical interface can have a source-coordinate discontinuity at its silhouette; that is different from an unwanted seam inside the material.

<a id="model-equation-2"></a>

$$
P(0)=\rho
$$

<a id="model-equation-3"></a>

$$
P'(0)=(1-\rho )256/27
$$

<a id="model-equation-4"></a>

$$
P(1)=P'(1)=P''(1)=0
$$

![Inverse displacement and normal derivative across the edge band](assets/edge-profile.svg)

### Jacobian and folds

Let [the condition below](#model-equation-108), [the expression below](#model-equation-5) within the band, and [the expression below](#model-equation-6). On a differentiable boundary segment:

<a id="model-equation-108"></a>

$$
t=(-\mathrm{ny},\mathrm{nx})
$$


<a id="model-equation-5"></a>

$$
S_d'=30u^{2}(1-u)^{2}/b
$$

<a id="model-equation-6"></a>

$$
a_d'=\mathrm{edge}\times \mathrm{power}\times P'(u)
$$

$$
\begin{gathered}
J = \partial F/\partial p = (1-c S)I + c S_d' p\otimes n + a_d' n\otimes n - a \kappa_d t\otimes t \\
\mathrm{Jnn} = 1-c S + c S_d'(p\cdot n) + a_d' \\
\mathrm{Jtt} = 1-c S - a \kappa_d \\
\mathrm{Jtn} = c S_d'(p\cdot t); \mathrm{Jnt} = 0 \\
\mathrm{det}(J) = \mathrm{Jnn} \times  \mathrm{Jtt}
\end{gathered}
$$

- A straight-edge normal derivative above 1 compresses source detail in the output; between 0 and 1 magnifies it. A large constant lookup offset is translation, not compression.
- Singular values of `J` describe general local directional scale; their reciprocals describe displayed feature scale. Determinant alone cannot establish isotropic compression.
- Zero determinant is a local collapse; a sign reversal indicates a fold.
- For nonnegative core, edge and power, the following **sufficient local nonfolding bounds** follow from [the condition below](#model-equation-109) and [the condition below](#model-equation-110):

<a id="model-equation-109"></a>

$$
p\cdot n\ge 0
$$

<a id="model-equation-110"></a>

$$
b/(r-\mathrm{bu})\le 1/(1-u)
$$


```text
power × (core + edge × D) < 1
power × (core + edge × T) < 1
```

The derivative and tangential bounds compare as follows.

$$
\begin{array}{lcc}
\text{Profile} & D\ge -P' & T\ge P/(1-u) \\
\text{Old shoulder} & 16\sqrt{3}/9 & 64/27 \\
\text{Rim-only }R & 16/9 & 256/243 \\
\text{Finite rim + compression} & 16\rho/9+64(1-\rho)/27 & 256\rho/243+1024(1-\rho)/729
\end{array}
$$

These are conservative: failing a bound means **uncertified**, not necessarily folded. They certify local orientation, not global one-to-one mapping. Motion changes effective power, so repeat the bound with its maximum depth multiplier. Extreme controls intentionally permit folds for inspection; do not silently ship those ranges as safe defaults.

## Refracting cap comparator

A second model relates a surface normal, thickness and backdrop distance through geometric optics. Its assumed solid has a rounded top and a flat exit plane; the camera is orthographic. Apple does not document this geometry. Generic transmission and reflection are distinct parts of the [Snell/Fresnel model](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission).

### Height and analytic normal

$$
\begin{gathered}
v = 1-u; f^{2} = 1-v^{3}; f = \sqrt{f^{2}} \\
C(p) = 1 - 0.036[(x/\mathrm{hx})^{2} + (y/\mathrm{hy})^{2}] \\
h_{\mathrm{cap}}(p) = H f C(p) \\
\mathrm{grad}(C) = (-0.072x/\mathrm{hx}^{2}, -0.072y/\mathrm{hy}^{2}) \\
N = \operatorname{normalize}( H[1.5v^{2} C n/b - f^{2} \mathrm{grad}(C)], f )
\end{gathered}
$$


The last expression is `(-grad(hcap),1)` multiplied by `f`. It evaluates the **vertical limiting rim normal** without a finite-difference stencil or division by zero. For [the condition below](#model-equation-111), `Nz→0` as `d→0+`.

<a id="model-equation-111"></a>

$$
H>0
$$

- At [the condition below](#model-equation-112), `f` joins the weak curved crown with zero first and second shoulder derivatives.

<a id="model-equation-112"></a>

$$
u=1
$$

- The crown coefficient is an adjustable-model choice fixed here at 0.036; it is not an Apple measurement.
- The former quintic-height ramp made the normal vertical in Z at the outline, flattening the rim and suppressing its refraction. Increasing height alone could not correct that boundary condition.

`H` is geometric height; [the condition below](#model-equation-113) is the separate distance from the exit plane to the backdrop. The lab uses [the condition below](#model-equation-114), [the condition below](#model-equation-115), with `L` the shorter **unstrained** half-size.

<a id="model-equation-113"></a>

$$
G\ge 0
$$

<a id="model-equation-114"></a>

$$
H=L\times \mathrm{thickness}\times \mathrm{power}\times \mathrm{dynamicDepth}
$$

<a id="model-equation-115"></a>

$$
G=L\times \mathrm{gap}
$$

- No fixed 14/5-pixel geometry remains.

### Two-interface ray

For unit incident propagation vector `I`, unit normal `N` opposing it, and index ratio [the condition below](#model-equation-116):

<a id="model-equation-116"></a>

$$
\eta =\mathrm{nIncident}/\mathrm{nTransmitted}
$$


$$
\begin{gathered}
c = -\operatorname{dot}(I,N) \\
k = 1 - \eta ^{2}(1-c^{2}) \\
k < 0\quad\text{no transmitted ray (total internal reflection)} \\
T = \eta I + (\eta c - \sqrt{k})N
\end{gathered}
$$

For this comparator:

$$
\begin{gathered}
I = (0,0,-1) \\
T_{\mathrm{inside}} = \operatorname{refract}(I, N, 1/n) \\
Q = p + T_{\mathrm{inside}}.\mathrm{xy} \times  h_{\mathrm{cap}}(p)/(-T_{\mathrm{inside}}.z) \\
T_{\mathrm{out}} = \operatorname{refract}(T_{\mathrm{inside}}, (0,0,1), n) \\
F(p) = Q + T_{\mathrm{out}}.\mathrm{xy} \times  G/(-T_{\mathrm{out}}.z)
\end{gathered}
$$


Restrict [the condition below](#model-equation-117) here. With orthographic incident rays, the first transmitted ray has [the condition below](#model-equation-118); at exit [the condition below](#model-equation-119). This avoids TIR and grazing denominators in this specific construction.

<a id="model-equation-117"></a>

$$
1\le n\le 1.4<\sqrt{2}
$$

<a id="model-equation-118"></a>

$$
-T_{\mathrm{inside}}.z\ge 1/n
$$

<a id="model-equation-119"></a>

$$
-T_{\mathrm{out}}.z\ge \sqrt{2-n^{2}}>0
$$

- It is **not** a general guarantee for tilted cameras or other shapes.
- Never replace a failed refraction with a zero vector or clamp a ray denominator to an arbitrary positive constant: both silently change the model.
- A more general renderer must handle reflection/visibility explicitly.
- The reference rejects exits outside the projected body. Tests sample ray segments beneath the top surface; they do not prove global solid-path validity for every future shape/parameter.
- Treat unvalidated geometries as unsupported.
- At the outline, thickness is zero but a nonzero gap can still yield a finite limiting offset. With [the condition below](#model-equation-120), outline displacement vanishes for a legitimate geometric reason.

<a id="model-equation-120"></a>

$$
G=0
$$

- A physically correct grazing interface also reflects strongly; finite lookup displacement alone does not imply visible transmitted detail there.

[the condition below](#model-equation-121) or [the condition below](#model-equation-122) explicitly gives the identity map. The `H→0` limit is not uniform at an exactly vertical rim when [the condition below](#model-equation-123); this comparator is unsuitable as a fade-to-zero-opacity formula.

<a id="model-equation-121"></a>

$$
H=0
$$

<a id="model-equation-122"></a>

$$
n=1
$$

<a id="model-equation-123"></a>

$$
G>0
$$

- Fade material coverage independently.
- Full Fresnel-weighted energy, internal reflections, absorption, dispersion, caustics and multiple scattering are absent.

The lab adds an independent synthetic highlight (the field model uses a fixed 0.3-reference-height cap for that lighting only), so calling its complete output a physically accurate renderer would be incorrect.

## Flat-front inverse-map compatibility

This separate comparator has an orthographic camera looking along −z, a flat front at z=0, one back surface z=−h(x,y), index n>1, and background plane z=−G. All lengths use the same normalized unit; h>0 and s=G−h>0. It is a test of a specified geometry, not an identified Apple lens.

For a proposed inverse image map F, let v=F−(x,y). Normal entry leaves the internal ray vertical. Snell's law requires:

$$
\begin{gathered}
M = \operatorname{dot}(v,v), R = \sqrt{M+s^{2}}, D = n R-s \\
\nabla h = v/D \\
\text{transmitted branch}\quad s > \sqrt{M/(n^{2}-1)}
\end{gathered}
$$

- h is one unknown surface; s cannot be fitted independently at each pixel. The branch inequality rejects the wrong-side solution and critical/grazing rays. Do not clamp them into validity.
- Define c=∂x(vy)−∂y(vx) and K=vy·dot(v,∂xv)−vx·dot(v,∂yv). Equality of the surface's mixed derivatives gives **Dc−nK/R=0**. Terms containing ∇s cancel because ∇s=−v/D. A valid surface may therefore have nonzero image-map curl.
- For reliably nonzero c, set ρ=K/c. The transmitted branch requires **ρ>M**. Its necessary clearance is:

$$
\begin{gathered}
s^{2} = [2n^{2}(\rho -M)+M+\sqrt{M^{2}+4n^{2}\rho (\rho -M)}] / [2(n^{2}-1)]
\end{gathered}
$$

- This root still must satisfy −∇s=v/D, compatible boundary conditions, positive thickness and valid complete ray paths. It does not establish a surface by itself.
- Near-zero curl, derivative noise and footprint-crossing differences require separate treatment; do not turn them into impossibility claims.
- The inequality follows from ρ=DR/n=M+s²−s·sqrt(M+s²)/n, which increases from M on the strictly transmitted branch.
- Failure rules out an **exact** map in this stated family; it supplies no lower bound on image error from an approximate surface or a different camera/front surface.

[Executable equations](../reconstruction/surface_compatibility.py) and [independent controls](../reconstruction/verify-surface-compatibility.py) check scalar versus vector Snell refraction, a known quadratic surface with nonzero map curl, inverse recovery, scale invariance and invalid branches. Run `python verify-surface-compatibility.py` in the reconstruction directory.
- These require NumPy, not private images.

The [sampled audit](../reconstruction/map_compatibility_audit.py) applies this necessary condition to an existing inverse map. On the [current switch revision 6](../reconstruction/studies/active-switch/review-round/pass-06-map-compatibility.json), 39.38% / 39.49% of sampled interior points fail it with a large margin over finite-step disagreement; uncertain points remain unresolved. The preceding revision 5 gives [38.51% / 38.65%](../reconstruction/studies/active-switch/review-round/pass-05-map-compatibility.json). Lower image error therefore does not imply a more physically realizable map.

This is numerical evidence against an exact flat-front/single-back realization of that map, **not** a bound on approximate image agreement or other surface families. [Controls](../reconstruction/map-compatibility-controls.json) distinguish a known physical surface, a rotational displacement and a zero map; nonfinite inputs are rejected. Run `python verify-map-compatibility-audit.py` for those controls, or the audit's documented command with frozen private study inputs.

The equations above use the stated propagation convention. [Bösel and Gross](https://arxiv.org/html/1510.01129) discuss the broader coupling between surface integrability and ray maps, including the limits of small-angle constructions. Their later [two-surface study](https://arxiv.org/html/1701.03076) also couples refraction, surface continuity and optical path length; adding a second freeform surface does not by itself certify a chosen image map.

That paper assumes collimated input/output beams, so its beam-shaping PDE must not be applied unchanged to this camera/backdrop configuration. Physical radiometry, dispersion, reflection, side-wall visibility and source recovery remain separate requirements.

## Finite-camera slab control

Use an infinite plane-parallel slab to check camera calibration before fitting a curved solid. Put the pinhole at (0,0,C), front at z=0, back at z=−h and backdrop at z=−G, with C>0, G>0, 0≤h≤G and n≥1. Let p be the ray's front-plane position.

The unlensed backdrop point is (1+G/C)p; divide physical backdrop coordinates by that factor before comparing image maps.

$$
\begin{gathered}
m = p/C; A = \sqrt{n^{2} + (n^{2}-1)|m|^{2}} \\
F(p) = p + h [m/A - m] / (1+G/C) \\
f = h/(C+G) \\
\mathrm{J\_tangential} = 1 + f(1/A - 1) \\
\mathrm{J\_radial} = 1 + f(n^{2}/A^{3} - 1)
\end{gathered}
$$

- Both derivatives are at least 1−f>0: this finite-camera slab cannot fold/reverse its image. Curved surfaces, sidewalls and multiple paths are outside that result.
- Changing viewpoint alone does not justify adding a mirrored rim.
- h=0 or n=1 gives identity. C→∞ also gives identity for this parallel slab; a curved surface need not. At the optical axis both derivatives equal 1−h(1−1/n)/(C+G).
- Central contraction of the source map corresponds to apparent image magnification.

[Implementation](../reconstruction/camera_slab.py) and [independent vector-Snell controls](../reconstruction/verify-camera-slab.py) check both interfaces, Jacobian, equal-index/no-slab/far-camera limits and unit scaling. Run `python verify-camera-slab.py`. The NumPy oracle tests bounded floating-point cases; the algebra supplies the stated geometric bound.
- No Apple camera, curved lens or reconstruction pass is inferred.

### Curved back surface with a finite camera

For the same flat front, let the back be z=−h(q). Its intersection q differs from the front-plane sample p. Define H(p)=h(q(p)), use the slab's internal slope w=m/A and set q=p+Hw. The desired physical backdrop point is U=(1+G/C)F(p). With unit internal/outgoing directions t and v, Snell's normal is N=nt−v. A back graph has gradient b=N_xy/N_z.

The chain rule gives:

$$
\begin{gathered}
B(p,H) = (I + H \mathrm{Dw})^T b / (1 - w\cdot b) \\
\nabla_p H = B(p,H) \\
\partial_x B_y - \partial_y B_x + B_x \partial_H B_y - B_y \partial_H B_x = 0
\end{gathered}
$$

Partial x/y derivatives include the prescribed F(p), holding H fixed. The expanded condition includes H's unknown derivatives through the last two terms; raw image-map curl alone remains insufficient. Require 0<H<G, N_z<0, n(t·v)>1 and 1−w·b>0 on this transmitted local branch. Do not clamp failures into rays. Call the scalar compatibility residual Q(p,H).

A pointwise depth root also requires ∇p Q + Q_H B=0 along the surface; independently choosing a root at each pixel is insufficient. Boundary conditions, first-hit/sidewall paths and global height consistency remain separate checks.

[Executable inverse equation](../reconstruction/perspective_back_surface.py) and [independent forward controls](../reconstruction/verify-perspective-back-surface.py) recover known quadratic surfaces from vector Snell paths. Tests cover height derivatives, the expanded condition, unit scaling, wrong-branch rejection and the orthographic limit. Run `python verify-perspective-back-surface.py`. These validate the stated equations, not a finite-camera realization of Apple's images or of the current fitted switch map.

## Reconstruction comparators

The [HD study](reconstruction.md) tests offline hypotheses beyond the portable lab's circle/capsule equations:


**Superellipse control:** [the condition below](#model-equation-124). The earlier slider used visually selected [the condition below](#model-equation-125). Measuring the dark upper contour exposed its error; it remains a shape/control test, not the final slider outline.

<a id="model-equation-124"></a>

$$
|x/\mathrm{hx}|^n+|y/\mathrm{hy}|^n=1
$$

<a id="model-equation-125"></a>

$$
n=2.5
$$


**Measured smooth oval:** [the condition below](#model-equation-126), [the condition below](#model-equation-127), [the condition below](#model-equation-128), [the condition below](#model-equation-129). The [contour fit](../reconstruction/contour.json) gives `a≈0.49940`, `b≈−0.23031` and half-extents 118.5 × 56.5. Thus [the condition below](#model-equation-130), [the condition below](#model-equation-131). Nearest-boundary distance and implicit-gradient normals use the same curve.

<a id="model-equation-126"></a>

$$
u=x/\mathrm{hx}
$$

<a id="model-equation-127"></a>

$$
v=y/\mathrm{hy}
$$

<a id="model-equation-128"></a>

$$
Q(u)=1+a u^{2}+b u^{4}
$$

<a id="model-equation-129"></a>

$$
T=u^{2}+[v/Q(u)]^{2}=1
$$

<a id="model-equation-130"></a>

$$
T_x=[2u-2v^{2}Q'/Q^{3}]/\mathrm{hx}
$$

<a id="model-equation-131"></a>

$$
T_y=2v/(\mathrm{hy} Q^{2})
$$


Its sampled minimum curvature radius is about 43.39 pixels; the optical band is limited to 43.38. A measured dark ridge is still a silhouette proxy, not proof of Apple's equation.
- Bottom/right symmetry is assumed; numeric convexity sampling is not a proof for arbitrary coefficients.

**Flexible inverse-map profile:** [the condition below](#model-equation-132), with cubic B-splines on knots `[0,0,0,0,.015,.04,.09,.2,.45,.75,1,1,1,1]`. Seven coefficients are fitted and the final three are zero. Therefore `a`, `a′` and `a″` vanish at the inner join.

<a id="model-equation-132"></a>

$$
a(d)=\operatorname{min}(\mathrm{hx},\mathrm{hy}) \sum  \mathrm{ci} \mathrm{Bi}(\operatorname{clamp}(d/r,0,1))
$$

- The map is [the condition below](#model-equation-133), with quintic `S` evaluated at `d/r`. This allows independently fitted central X/Y scale and a flexible folded rim, without a fitted displacement image.

<a id="model-equation-133"></a>

$$
F=(x(1-\mathrm{cxS}), y(1-\mathrm{cyS}))-a n
$$

- It is an empirical comparator, not a physical surface reconstruction or a nonfolding guarantee.

### Radial transition and foreground-color controls

For the circular playback study, a radial inverse map isolates the rim-to-center transition from silhouette and lighting. With [the condition below](#model-equation-134), inward depth [the condition below](#model-equation-135), and displacement `a(d)`, use [the condition below](#model-equation-136); the center is identity when the displacement support ends before `R`. The initial profile is [the condition below](#model-equation-137), [the condition below](#model-equation-138).

<a id="model-equation-134"></a>

$$
r=|v|
$$

<a id="model-equation-135"></a>

$$
d=R-r
$$

<a id="model-equation-136"></a>

$$
F(v)=(1-a/r)v
$$

<a id="model-equation-137"></a>

$$
\mathrm{a0}=A \operatorname{clamp}(1-d/b,0,1)^p
$$

<a id="model-equation-138"></a>

$$
p>2
$$


An exponent barely above two is mathematically C2 at its inner endpoint but its second derivative approaches zero very slowly. C2 continuity alone does not ensure a perceptually gradual transition at pixel scale.

The following splice preserves the outer map and independently varies the inner tail. Define [the condition below](#model-equation-139), [the condition below](#model-equation-140), [the condition below](#model-equation-141), width factor [the condition below](#model-equation-142), shoulder gain [the condition below](#model-equation-143), and inner-end exponent [the condition below](#model-equation-144):

<a id="model-equation-139"></a>

$$
\mathrm{da}=b/4
$$

<a id="model-equation-140"></a>

$$
\mathrm{ds}=b/2
$$

<a id="model-equation-141"></a>

$$
\mathrm{w0}=b/2
$$

<a id="model-equation-142"></a>

$$
k\ge 1
$$

<a id="model-equation-143"></a>

$$
g>0
$$

<a id="model-equation-144"></a>

$$
q>2
$$


$$
\begin{gathered}
\mathrm{for} d\le \mathrm{ds}: \\
a = \mathrm{a0}(d) [1+(g-1) \mathrm{S5}(\operatorname{clamp}((d-\mathrm{da})/(\mathrm{ds}-\mathrm{da}),0,1))] \\
\mathrm{for} \mathrm{ds}<d<\mathrm{ds}+k \mathrm{w0}: \\
t = (d-\mathrm{ds})/(k \mathrm{w0}) \\
a = g A 2^{-p} (1-t)^q \\
\times  \operatorname{exp}[(q-p k)t + (q-p k^{2})t^{2}/2] \\
\text{after that}\quad a = 0 \\
\mathrm{S5}(u) = 10u^{3}-15u^{4}+6u^{5}
\end{gathered}
$$


At `ds`, value, first and second derivative match `g a0`; the gain ramp also joins C2. [the condition below](#model-equation-145) makes the **inner endpoint** C3; it does not make the entire splice C3.

<a id="model-equation-145"></a>

$$
q>3
$$

- [the condition below](#model-equation-146) recovers the original profile exactly.

<a id="model-equation-146"></a>

$$
k=g=1, q=p
$$

- Require [the condition below](#model-equation-147) for a quiet center. The outermost `b/4` is unchanged.

<a id="model-equation-147"></a>

$$
\mathrm{ds}+k \mathrm{w0}<R
$$


Tail support grows with `k`, but visible transition width need not grow proportionally: matching the entry derivatives constrains the tail. Neither `g` nor `q` is a measured physical surface curvature.
- The radial/tangential Jacobian eigenvalues are `1+a′(d)` and `1−a/r`. A sign change can invert source detail.
- Test supported parameters for additional folds; smoothness and gradient-potential integrability do not establish a valid refracting solid or Apple fidelity.

Foreground color is a separate control. Independent RGB power responses can fit one pose yet reverse warm hues when moved over a different part of the source. A shared monotone scalar response [the condition below](#model-equation-148) preserves channel ordering and neutral grays, with a white plateau if [the condition below](#model-equation-149) above a threshold.

<a id="model-equation-148"></a>

$$
C=(f(\mathrm{BR}),f(\mathrm{BG}),f(\mathrm{BB}))
$$

<a id="model-equation-149"></a>

$$
f(u)=1
$$


One compact approximation uses monotone PCHIP through input knots `t[0,.3,.55,.8,1]` followed by `1`, with increasing output values from a configurable floor to `1`, followed by `1`. Positive normalized output increments enforce ordering. This interpolation is C1, not generally C2. It may fit the measured icon less closely than independent channels; retain that accuracy/generalization tradeoff.

These are empirical encoded-RGB shading controls, not identified Apple lighting equations.

A highlight-reduction alternative retains the existing response and applies [the condition below](#model-equation-150), [the condition below](#model-equation-151), independently to each component. For [the condition below](#model-equation-152) it is monotone: within the shoulder, [the condition below](#model-equation-153). It leaves values below `t` unchanged, joins them C2, preserves the black/white endpoints and introduces no white plateau. Increasing `k` delays near-white output.

<a id="model-equation-150"></a>

$$
f(c)=c-k u^{3}(1-c)
$$

<a id="model-equation-151"></a>

$$
u=\operatorname{clamp}((c-t)/(1-t),0,1)
$$

<a id="model-equation-152"></a>

$$
0\le k\le 4
$$

<a id="model-equation-153"></a>

$$
f'=1-k u^{2}(3-4u)\ge 1-k/4
$$


This operator preserves existing channel ordering; it does not repair hue inversions already produced by a preceding independent-channel shader.

Express blur and lighting lengths in the same geometry units as the element, then convert at rasterization. For these circular controls, [the condition below](#model-equation-154) and [the condition below](#model-equation-155). The selected playback-study calibration uses width factor 4.5, gain 1, glass post-blur `1.5D/490`, dark saturation 0.2, highlight taper 0.5 and final icon-color blur `3D/490`, retaining the pass04 independent-channel response.

<a id="model-equation-154"></a>

$$
D=\operatorname{min}(\mathrm{width},\mathrm{height})
$$

<a id="model-equation-155"></a>

$$
\sigma =\mathrm{ratio}\times D
$$


These are visual-study choices, not Apple constants or native-app defaults. Normalize every lighting length too, including thin-rim terms. Source-space filtering, filtering after refraction/shading, and filtering only the calculated icon-color field are distinct operations. Icon-color blur is the last color operation before sharp coverage/compositing; do not blur the symbol silhouette or silently exchange filtering stages.

### Tangential curvature and smooth crowns

A scalar normal offset cannot explain all two-dimensional distortion. On the toolbar's straight horizontal edge, [the condition below](#model-equation-156): [the condition below](#model-equation-157) changes Y while leaving X unchanged. A displaced strip is not necessarily a widened strip. The following alternatives expose that restriction rather than increasing one depth gain.

<a id="model-equation-156"></a>

$$
n=(0,\pm 1)
$$

<a id="model-equation-157"></a>

$$
F=p-a(d)n
$$


**Tensor field. ** Let [the condition below](#model-equation-158), [the condition below](#model-equation-159), [the condition below](#model-equation-160), and [the condition below](#model-equation-161). With the same spline `a(d)`:

<a id="model-equation-158"></a>

$$
t=(-\mathrm{ny},\mathrm{nx})
$$

<a id="model-equation-159"></a>

$$
\mathrm{bT}=r\times \mathrm{tangentBand}
$$

<a id="model-equation-160"></a>

$$
v=1-\operatorname{clamp}(d/\mathrm{bT},0,1)
$$

<a id="model-equation-161"></a>

$$
B=v^{4}(5-4v)
$$


$$
\begin{gathered}
F(p) = (I-\operatorname{diag}(\mathrm{cx},\mathrm{cy}))p - a(d)n - \tau B(d)(p\cdot t)t
\end{gathered}
$$

[the condition below](#model-equation-162), [the condition below](#model-equation-163), [the condition below](#model-equation-164), [the condition below](#model-equation-165). On a straight horizontal edge, [the condition below](#model-equation-166); its reciprocal is displayed horizontal scale. The central scale is retained while tangential stretch grows toward the silhouette. `B`, `B′` and `B″` vanish at its inner join.

Normals/tangents rotate around curved ends, so the deformation follows the outline instead of fixed screen axes.

<a id="model-equation-162"></a>

$$
0\le \tau \le 0.8
$$

<a id="model-equation-163"></a>

$$
0.05\le \mathrm{tangentBand}\le 1
$$

<a id="model-equation-164"></a>

$$
\mathrm{cx}\in [0,0.3]
$$

<a id="model-equation-165"></a>

$$
\mathrm{cy}\in [0,0.65]
$$

<a id="model-equation-166"></a>

$$
\partial \mathrm{Fx}/\partial_x=1-\mathrm{cx}-\tau B
$$


A circle has [the condition below](#model-equation-167), providing a useful zero-effect control. This is a designed image field, not a recovered solid or a nonfolding guarantee.

<a id="model-equation-167"></a>

$$
p\cdot t=0
$$


**Gradient-potential control. ** A competing, more restrictive hypothesis uses [the condition below](#model-equation-168), with [the condition below](#model-equation-169), [the condition below](#model-equation-170) and [the condition below](#model-equation-171):

<a id="model-equation-168"></a>

$$
\Psi =V(d)+K(d)x^{2}/2+\mathrm{cy} y^{2}/2
$$

<a id="model-equation-169"></a>

$$
V'=-a
$$

<a id="model-equation-170"></a>

$$
K=\mathrm{cx}+\tau B
$$

<a id="model-equation-171"></a>

$$
F=p-\nabla \Psi
$$


$$
\begin{gathered}
F = ((1-K)x, (1-\mathrm{cy})y) + [-a + K'x^{2}/2]n \\
K' = -20\tau u(1-u)^{3}/\mathrm{bT}, u=\operatorname{clamp}(d/\mathrm{bT},0,1)
\end{gathered}
$$

The extra normal term is required by this potential; dropping it would break equality of mixed derivatives. This control tests integrability, not exact thick-lens optics. It did not improve the toolbar fit. The better tensor fit cannot therefore be relabeled as a verified phase surface.

**Smooth height surface. ** A continuous crown removes the old cap's explicit inner shoulder join. Define the footprint field `T` and height:

$$
\begin{gathered}
\text{circle / oval}\quad T = |x/\mathrm{hx}|^{n} + |y/\mathrm{hy}|^{n} \\
\text{measured oval}\quad T = u^{2} + [v/Q(u)]^{2} \\
\text{capsule}\quad T = [\operatorname{max}(|x|-(\mathrm{hx}-r),0)^{2} + y^{2}]/r^{2} \\
s = 1-T^{m} \\
A = \mathrm{cx}(x/\mathrm{hx})^{2}+\mathrm{cy}(y/\mathrm{hy})^{2}; W = (1-k)+k T; C = 1-A W \\
z(p) = H s^{\beta} C\quad\text{inside T<1} \\
N \propto  ( H[\beta m T^{m-1}T_x C - s C_x], \\
H[\beta m T^{m-1}T_y C - s C_y], s^{1-\beta} )
\end{gathered}
$$

Domains: [the condition below](#model-equation-172), [the condition below](#model-equation-173), [the condition below](#model-equation-174), [the condition below](#model-equation-175); [the condition below](#model-equation-176) for the circle, or the fitted polynomial field for the measured oval. Earlier broad-crown trials use [the condition below](#model-equation-177), [the condition below](#model-equation-178), [the condition below](#model-equation-179). Independent X/Y crowns and [the condition below](#model-equation-180) vary how cross-sections change with depth; require [the condition below](#model-equation-181).

Increasing `m` concentrates curvature near the boundary. At [the condition below](#model-equation-182), a circle/ellipse has an ellipsoidal meridian.

<a id="model-equation-172"></a>

$$
H=\operatorname{min}(h)\times \mathrm{height}
$$

<a id="model-equation-173"></a>

$$
\mathrm{height}\in [0.01,1.8]
$$

<a id="model-equation-174"></a>

$$
m\in [1,40]
$$

<a id="model-equation-175"></a>

$$
\beta \in [0.2,0.95]
$$

<a id="model-equation-176"></a>

$$
n=2
$$

<a id="model-equation-177"></a>

$$
\mathrm{cx}=\mathrm{cy}=c/2
$$

<a id="model-equation-178"></a>

$$
c\in [0,0.7]
$$

<a id="model-equation-179"></a>

$$
k=0
$$

<a id="model-equation-180"></a>

$$
k\in [0,1]
$$

<a id="model-equation-181"></a>

$$
C>0
$$

<a id="model-equation-182"></a>

$$
m=1, \beta =1/2, \mathrm{cx}=\mathrm{cy}=0
$$


Height, central curvature and rim curvature are distinct parameters.

The capsule formula uses its long-axis frame, [the condition below](#model-equation-183); rotate coordinates for a vertical capsule. It is not a general rounded-rectangle height field. Those additional footprints need their own validated implicit geometry before reuse.

<a id="model-equation-183"></a>

$$
\mathrm{hx}\ge \mathrm{hy}=r
$$


The exponential alternative substitutes [the condition below](#model-equation-184), with [the condition below](#model-equation-185). It provides another smooth crown without an inner join; use `expm1` near small arguments. Both families use the same two-interface Snell construction, [the condition below](#model-equation-186), [the condition below](#model-equation-187) and reference IOR 1.33.

<a id="model-equation-184"></a>

$$
s=[1-\operatorname{exp}(-m(1-T))]/[1-\operatorname{exp}(-m)]
$$

<a id="model-equation-185"></a>

$$
-\mathrm{ds}/\mathrm{dT}=m \operatorname{exp}(-m(1-T))/[1-\operatorname{exp}(-m)]
$$

<a id="model-equation-186"></a>

$$
G=\operatorname{min}(h)\times \mathrm{gap}
$$

<a id="model-equation-187"></a>

$$
\mathrm{gap}\in [0,1.5]
$$


The outline does not identify `H,m,β,c` uniquely. For a height graph, principal curvatures are eigenvalues of `I⁻¹II`, where [the condition below](#model-equation-188) and [the condition below](#model-equation-189) (sign depends on chosen orientation). Height alone is not a curvature radius. The current checks establish analytic-normal/scale/mirror limits; full path-validity and temporal calibration remain open.

<a id="model-equation-188"></a>

$$
I=\mathrm{Id}+\nabla z\otimes \nabla z
$$

<a id="model-equation-189"></a>

$$
\mathrm{II}=\mathrm{Hess}(z)/\sqrt{1+|\nabla z|^{2}}
$$


**Independent transverse curvature. ** A preferred longitudinal section need not produce the desired optical onset across Y. For a separable footprint [the condition below](#model-equation-190), set [the condition below](#model-equation-191), [the condition below](#model-equation-192) inside the body and use:

<a id="model-equation-190"></a>

$$
T=U(x)+V(x,y)
$$

<a id="model-equation-191"></a>

$$
S=1-U
$$

<a id="model-equation-192"></a>

$$
W=V/S
$$


$$
\begin{gathered}
T^{\ast} = U + S W^{p}, p\ge 1 \\
T^{\ast}x = U_x[1+(p-1)W^{p}] + p W^{p-1}V_x \\
T^{\ast}y = p W^{p-1}V_y
\end{gathered}
$$

Use `T*` consistently in the height, crown and analytic normal. At [the condition below](#model-equation-193) it recovers the original field. It preserves the silhouette ([the condition below](#model-equation-194)) and longitudinal Y=0 section ([the condition below](#model-equation-195)), while larger `p` reduces central transverse curvature. The implementation's `cross_section_power` controls `p`; exterior occupancy retains the original field to avoid singular perspective extrapolation at [the condition below](#model-equation-196).

<a id="model-equation-193"></a>

$$
p=1
$$

<a id="model-equation-194"></a>

$$
W=1
$$

<a id="model-equation-195"></a>

$$
W=0
$$

<a id="model-equation-196"></a>

$$
U=1
$$


This is a geometric hypothesis for a quiet interior and strong near-rim refraction, not a measured Apple parameter. Preserve coverage and validate convexity/path behavior before using a new combination.

### Cap joins and closed-body tracing

The capsule's [the condition below](#model-equation-197), [the condition below](#model-equation-198), gives a C1 surface with a jump in second derivatives at the straight/circular join. A continuous normal does not ensure continuous curvature or optical magnification. The optional geometric transition uses [the condition below](#model-equation-199), width [the condition below](#model-equation-200), and:

<a id="model-equation-197"></a>

$$
q=\operatorname{max}(|x|-a,0)
$$

<a id="model-equation-198"></a>

$$
a=\mathrm{hx}-r
$$

<a id="model-equation-199"></a>

$$
s=|x|-a
$$

<a id="model-equation-200"></a>

$$
0<w<a
$$


$$
\begin{gathered}
u = \operatorname{clamp}((s/w+1)/2, 0, 1) \\
q = 0\quad\text{for sat most-w} \\
q = w(2u^{3}-u^{4})\quad\text{for -w<s<w} \\
q = s\quad\text{for sat leastw} \\
q' = 3u^{2}-2u^{3}\quad\text{within the transition}
\end{gathered}
$$

Value, first and second derivative match both adjoining pieces. Use this `q` in the footprint and its derivatives; [the condition below](#model-equation-201) controls the width. The silhouette changes slightly, so coverage must follow the modified footprint too. This is not a promise of C2 smoothness for arbitrary footprints or a reconstruction of Apple's shape.

<a id="model-equation-201"></a>

$$
\mathrm{cap\_join}=w/r
$$


The offline [closed-body comparator](../reconstruction/solid.py) replaces the flat exit with [the condition below](#model-equation-202), inside [the condition below](#model-equation-203). Front and rear normals come from the same height gradient. Changing `cx,cy,k` therefore changes the actual body and all traced interfaces, rather than directly widening a sampled image.

<a id="model-equation-202"></a>

$$
-\mathrm{rear}\times z(x,y)\le Z\le z(x,y)
$$

<a id="model-equation-203"></a>

$$
T\le 1
$$


For unit incident direction `I`, an opposing unit normal `N`, index ratio [the condition below](#model-equation-204), [the condition below](#model-equation-205) and [the condition below](#model-equation-206):

<a id="model-equation-204"></a>

$$
\eta =\mathrm{ni}/\mathrm{nt}
$$

<a id="model-equation-205"></a>

$$
\mathrm{ci}=-I\cdot N
$$

<a id="model-equation-206"></a>

$$
K=1-\eta ^{2}(1-\mathrm{ci}^{2})
$$


$$
\begin{gathered}
\mathrm{reflected}   = I + 2\mathrm{ci} N \\
\mathrm{transmitted} = \eta I + (\eta \mathrm{ci}-\sqrt{K})N\quad\text{when Kat least0}
\end{gathered}
$$

Unpolarized dielectric Fresnel weights split each path. At total internal reflection ([the condition below](#model-equation-207)) there is no transmitted direction; its entire weight continues along reflection. Subsequent transmissions hit the background plane or the environment. A finite path series reports remaining untraced energy; it must not silently become fabricated background detail.

<a id="model-equation-207"></a>

$$
K<0
$$


A local first-path Jacobian does not describe this entire multi-path image.

- Intersection bisection requires a convex supported body. The general parameter family is **not certified convex**; new combinations need geometry/path checks before interpretation. Body continuity alone is insufficient.
- The [material fit](../reconstruction/solid_material.py) still uses encoded-RGB nuisance lighting, including signed coefficients. Correct Snell paths do not make that fitted lighting radiometrically physical.
- [Independent controls](../reconstruction/verify-solid.py) compare intersections with an analytic ellipsoid, check Snell/Fresnel, explicit TIR, energy accounting, scale/mirror limits, analytic cross-coupled normals and C2 join derivatives.
- Example horizontal stretch emerges from geometry, but these checks do not calibrate it to Apple.
- This comparator is separate from the interactive lab's existing field/flat-exit models. No Apple-shader or live-lab parity claim follows from the offline experiment.

### Reflection versus color separation

For a view direction along +Z, the reflected lookup direction is [the condition below](#model-equation-208). The surface comparator fits a low-order environment evaluated at **that direction**, weighted by unpolarized dielectric Fresnel reflectance. It replaces independently positioned Gaussian highlight bands; changing the surface changes reflection and transmission together.

<a id="model-equation-208"></a>

$$
R=(2\mathrm{NzNx},2\mathrm{NzNy},2\mathrm{Nz}^{2}-1)
$$


The first-order RGB environment uses [the condition below](#model-equation-209); the quadratic alternative adds these terms per channel.

$$
R_xR_y,\quad R_xR_z,\quad R_yR_z,\quad R_x^2-R_y^2,\quad 3R_z^2-1
$$

Neither paints a particular edge. The environment is inferred nuisance lighting, not a measured Apple light rig; signed polynomial coefficients do not enforce a nonnegative physical environment. Encoded-RGB fitting is not energy-conserving radiometry.

<a id="model-equation-209"></a>

$$
E(R)=\mathrm{e0}+\mathrm{exRx}+\mathrm{eyRy}+\mathrm{ezRz}
$$


[Dispersion](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission) means wavelength-dependent refraction; a colored rim alone does not identify it. Two explicit controls are tested:

- **Snell RGB proxy:** [the condition below](#model-equation-210), [the condition below](#model-equation-211), [the condition below](#model-equation-212). Trace one ray per channel and evaluate wavelength-dependent entry Fresnel factors.

<a id="model-equation-210"></a>

$$
n(\lambda )=1.33+B(\lambda ^{-2}-0.55^{-2})
$$

<a id="model-equation-211"></a>

$$
\lambda ={0.65,0.55,0.45} \mu m
$$

<a id="model-equation-212"></a>

$$
B\in [0,0.025] \mu m^{2}
$$

- Transmission is scaled relative to the reference wavelength by `(1−Fλ)/(1−FG)`; reflected-environment terms use `Fλ`. At [the condition below](#model-equation-213) both recover the common-IOR comparator.

<a id="model-equation-213"></a>

$$
B=0
$$

- All indices stay below `\sqrt{2}`, preserving its flat-exit TIR bound. This is not spectral-to-RGB integration or complete internal/exit-reflection transport.

**Image-map sensitivity:** [the condition below](#model-equation-214), [the condition below](#model-equation-215). This tests channel separation on the better-fitting flexible map; it is not equivalent to changing a physical IOR. [the condition below](#model-equation-216) recovers the common lookup exactly.

<a id="model-equation-214"></a>

$$
F\lambda =p+[1+D(\lambda ^{-2}-0.55^{-2})](\mathrm{F0}-p)
$$

<a id="model-equation-215"></a>

$$
D\in [0,0.2] \mu m^{2}
$$

<a id="model-equation-216"></a>

$$
D=0
$$


[curvature.py](../reconstruction/curvature.py) implements these hypotheses. [verify.py](../reconstruction/verify.py) checks finite-differenced height normals, scale/mirror/Snell/Fresnel limits, potential mixed derivatives, tangential scale and integrated material regression. The 30 older fixtures still cover only the original field/cap. Image scores and color evidence belong to the [comparison study](reconstruction.md), not mathematical proof of Apple's renderer.

## Sampling, coverage and color

- Optical coordinates extend to the boundary. Apply antialiasing to final **coverage**, not by multiplying displacement by a several-pixel edge ramp.
- The lab uses a one-framebuffer-pixel coverage band; filtering can still soften the first visible pixel.
- Capture enough backdrop beyond the body: a conservative field padding is `b×edge×power + core×power×max|p| + blurFootprint`. Cap padding must cover its validated ray offsets.
- Clamping to the capture boundary can mimic an inactive edge; repeating the last texel is not extra optical information.
- Scale all geometric lengths, backdrop coordinates and source padding together. Coverage width depends on raster density. The optical band has no fixed two-pixel floor.
- Shadows/highlight widths are separate artistic lengths, not optical invariants.
- The lab interpolates and blurs **encoded sRGB channels**, then tints, illuminates and applies its tone curve. This is an image-space approximation, not radiometric scattering.

Physical-light processing requires decoding, linear-light filtering and re-encoding, including alpha/compositing conventions; [W3C defines those conversions](https://www.w3.org/TR/css-color-4/#color-conversion-code). [Apple documents default light-linear filtering in Core Image](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/CoreImaging/ci_performance/ci_performance.html#//apple_ref/doc/uid/TP30001185-CH202-SW4). That supports testing linear-light alternatives, but does not identify Liquid Glass's private pipeline.
- Nine blur taps have nonnegative weights summing to one: center 1/4, four axial taps 1/8 each, four diagonals 1/16 each. Radius is an offset, not Gaussian sigma.
- At large compression, production sampling needs source-footprint filtering; nine taps do not guarantee alias-free reconstruction.

For an encoded channel [the condition below](#model-equation-217), trim [the condition below](#model-equation-218) and exponent [the condition below](#model-equation-219):

<a id="model-equation-217"></a>

$$
x\in [0,1]
$$

<a id="model-equation-218"></a>

$$
\tau \in [0,0.5]
$$

<a id="model-equation-219"></a>

$$
\gamma \in [1,2]
$$


$$
\begin{gathered}
\text{light foreground}\quad f(x) = x - \tau x^\gamma  \\
\text{dark foreground}\quad g(x) = 1-f(1-x) = x + \tau (1-x)^\gamma  \\
f'(x) = 1-\tau \gamma x^{\gamma-1} \ge  0
\end{gathered}
$$

Endpoints are `[0,1−τ]` and `[τ,1]`; darker inputs cannot wrap above brighter ones. This is a channel bound, not a physical-luminance curve or a guarantee of a WCAG contrast ratio. Applying it after synthetic illumination preserves the chosen material endpoint. Foreground ink is outside the operation.

## Pressure and dynamics

Normal finger contact and a side-wall reaction act along different axes. Strictly, pressure is scalar; the boundary traction (force per area) has direction, and a stress tensor describes the general internal state. The lab models prescribed deformation, not a stress solution.

A homogeneous, approximately incompressible deformation has principal stretches with product one; it does not require one specific redistribution law.

$$
\begin{gathered}
\mathrm{sx} = \operatorname{exp}(q - z/2) \\
\mathrm{sy} = \operatorname{exp}(-q - z/2 - f p) \\
\mathrm{sz} = \operatorname{exp}(z + f p) \\
\mathrm{sx} \mathrm{sy} \mathrm{sz} = 1
\end{gathered}
$$

`q` is in-plane strain including the wall contribution, `z` is normal strain (negative while held), `p` is positive wall-compression magnitude, and [the condition below](#model-equation-220) apportions wall compensation into depth. During recovery `p` is a signed spring state. At fixed `z`, increasing `p` increases depth when [the condition below](#model-equation-221); simultaneous normal pressure can still leave total depth below rest.

<a id="model-equation-220"></a>

$$
f\in [0,1]
$$

<a id="model-equation-221"></a>

$$
f>0
$$


This answers the pressure-direction question without assuming Apple uses a volume law.

- This determinant-one construction conserves an affine volume **only if the entire original body is transformed**. Rebuilding corner radius and the height function is not that transformation.
- The lab's scale product is a proxy, not exact integrated volume.
- For exact conservation of a reconstructed cap, compute [the condition below](#model-equation-222) and choose [the condition below](#model-equation-223). The lab does not enforce that integral.

<a id="model-equation-222"></a>

$$
V=H\int D \mathrm{fC} \mathrm{dA}
$$

<a id="model-equation-223"></a>

$$
H=\mathrm{Vtarget}/\int D \mathrm{fC} \mathrm{dA}
$$

- An exact-volume model must also resolve constraints when maximum depth is reached.

Pin the contacting edge by setting center to `wallPosition ± deformedHalfWidth`; do not compress about the old center. Changing footprint, optical band and depth must use the same strain state.
- Held normal pressure uses a critically damped approach; release retains velocity and uses configurable damping. Critical damping prevents oscillatory eigenmodes, not every overshoot from arbitrary initial velocity.
- A strict monotonic-contact rule requires a separate velocity/force constraint; abruptly clamping velocity sacrifices derivative continuity. This remains an interaction design tradeoff, not an automatic property of the spring.
- A retargeted spring does not reset its velocity. Constant area, constant perimeter and constant volume are different constraints; none is interchangeable.

For each spring coordinate with mass [the condition below](#model-equation-224), stiffness [the condition below](#model-equation-225), damping [the condition below](#model-equation-226), constant target `x*` over a step, let [the condition below](#model-equation-227), [the condition below](#model-equation-228) and [the condition below](#model-equation-229):

<a id="model-equation-224"></a>

$$
m>0
$$

<a id="model-equation-225"></a>

$$
k>0
$$

<a id="model-equation-226"></a>

$$
c\ge 0
$$

<a id="model-equation-227"></a>

$$
y=x-x*
$$

<a id="model-equation-228"></a>

$$
a=c/(2m)
$$

<a id="model-equation-229"></a>

$$
\mathrm{w0}^{2}=k/m
$$


$$
\begin{gathered}
y'' + 2a y' + \mathrm{w0}^{2} y = 0 \\
\text{underdamped}\quad w=\sqrt{\mathrm{w0}^{2}-a^{2}} \\
y(t)=\operatorname{exp}(-a t)[ y(0) \operatorname{cos}(w t) + (v(0)+a y(0)) \operatorname{sin}(w t)/w ] \\
\text{critical}\quad y(t)=\operatorname{exp}(-a t)[ y(0) + (v(0)+a y(0))t ] \\
\text{overdamped}\quad y(t)=A \operatorname{exp}(r_1 t)+B \operatorname{exp}(r_2 t) \\
r_1,2=-a\pm \sqrt{a^{2}-\mathrm{w0}^{2}}; A=(v(0)-r_2 y(0))/(r_1-r_2); B=y(0)-A
\end{gathered}
$$

The reference returns both position and the derivative of these expressions. Fixed-target energy cannot grow.

$$
E=\tfrac12 mv^2+\tfrac12 ky^2
$$

Exact steps compose independently of frame partition; changing targets/forces and contact constraints still require event-time sampling. The lab retains bounded substeps for those inputs, with analytic spring updates.

Its braking impulse, strain clamps and frame-delta cap are interaction approximations, not a solved fluid/stress system. Test pauses, interruptions and boundary ownership separately.

## Verification and remaining gates

Run `node experiments/equations-test.cjs` without browser dependencies, with no browser required. Seeded tests cover limits, independently differenced Jacobians, both ray interfaces, pressure and exact spring evolution. Random coverage is evidence, not proof of untested domains. Experimental browser-oracle work remains on the preserved lab branch; it is not part of this publication.

GPU/software agreement alone could reproduce the same bug.

Required before native adoption:

1. Freeze supported parameter domains; reject or clearly distinguish folding/unsupported cases. Retain a shared source-coordinate and color-space contract across backends.
2. Port reference fixtures, scale/mirror tests, endpoint and interruption cases to both native adapters. Measure device frame times separately from functional correctness.
Calibrate on exposed-source Apple scenes with known state/settings, then hold out independent scenes. The [HD reconstruction study](reconstruction.md) now measures three conditional still-image fits, with explicit source/foreground exclusions. Independent-scene and temporal validation remain open.
4. Keep the measured evidence, artistic choices and mathematical guarantees separate. Neither the finite-rim profile nor the cap has established Apple rendering parity.
