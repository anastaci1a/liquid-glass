# Mathematical models for the reference recreations

**Historical image-fit recipes.** Primary versions follow the [geometry-only contract](geometric-optics.md) and [current model registry](../reconstruction/current-models.json). Empirical maps below remain archived diagnostic controls; they do not establish realizable optical surfaces.

These are **rendering-method-independent inverse image maps and material functions**. They can be evaluated by a shader, a mesh with sufficient sampling, a CPU renderer or another implementation. The Python replay is a reference implementation, not the specification's coordinate system or required rendering technology.

[Comparisons and scores](reconstruction.md) · [Exact parameter records](../reconstruction/recipes.json) · [General optical models](model.md) · [Replay](reconstruction.md#reproduce)

The circular playback control was the most polished empirical calibration. The toolbar, slider and uniform light/dark surfaces also have frozen historical recipes. These reproduce particular studies; they do not identify Apple's shader or establish defaults for every background.

## Common contract

- Let the element's shorter dimension be `D`; use [the expression below](#recreation-models-equation-1) as the length unit. Local output coordinates are [the expression below](#recreation-models-equation-2).
- Every spatial parameter in `recipes.json` is dimensionless in these units, including blur, rim lighting and shape dimensions. Multiply by `L` only when sampling the backdrop or rasterizing.
- `reference_length` records the source-image scale; it is not an extra model parameter.

Across differently sized observations, use each pose's `Lᵢ`: [the expression below](#recreation-models-equation-3). Optimizer records may store `σref` at an explicitly declared `Lref`, giving [the expression below](#recreation-models-equation-4); published normalized lengths remain [the expression below](#recreation-models-equation-5).
- Source and output blur use the same conversion. Raster sampling/quarter-pixel kernel quantization remain implementation approximations.
- `F(v)` is the **inverse map**: the backdrop sample is `B(center+L F(v))`. It describes where to read pixels, not the direction in which the visible feature moves.
- Independent foreground content is composited afterward.

The examples operate on **encoded RGB values in [0,1]**. This is a calibrated image-space approximation; changing to linear-light processing changes the output. Coordinates increase rightward/downward, and the camera is frontal.
- Preserve opaque RGB input precision: divide 8-bit code values by 255 and 16-bit values by 65535.

A decoded 10-bit video stored as RGB16 must not pass through an 8-bit image reader. [Raster input helpers](../reconstruction/raster_input.py) preserve code values without transfer/ICC/exposure changes; [controls](../reconstruction/verify-raster-input.py) check exact legacy equality and high-bit preservation.
- Record decoding precision in the input epoch.
Uniform raster resizing preserves the half-pixel center convention. Rescale registrations by composition, rather than multiplying their translations alone:

$$
\begin{aligned}
D_s(p)&=s\left(p+\frac12\right)-\frac12,\\
T_{\mathrm{resized}}&=D_{\mathrm{destination}}\circ T\circ D_{\mathrm{source}}^{-1}.
\end{aligned}
$$


- Integer-factor array crop indices scale directly; center/vector positions use D. [Coordinate controls](../reconstruction/verify-raster-coordinates.py) verify both paths without refitting image features.
- Let `s(v)` be signed distance to the outline, negative inside, [the condition below](#recreation-models-equation-101) the outward unit normal and [the expression below](#recreation-models-equation-6). Shape coverage is independent of material color.

<a id="recreation-models-equation-101"></a>

$$
\mathbf n=\nabla s.
$$

- Evaluate the equations continuously before coverage/raster filtering.
- Gaussian `σ` is standard deviation, not kernel diameter. Source blur, glass blur after refraction/shading, and foreground-color blur are different operations. The foreground's coverage remains sharp.
- Foreground geometry must use a verified exact vector, or a clean symmetric trace when none is available.
- Solid coverage is independent of tint, transmission and blur, and is rasterized anew at each output resolution.
- The Home/Search follow-up uses private SVG inputs with frozen hashes; older photo-derived masks below remain historical calibrations pending replacement. Optical masks/scores stay fixed when foreground measurements change.
- Parameters and operation order are fixed for replay. Re-optimizing coefficients produces a new calibration, not an exact reproduction of this one.
- Source registration, the estimated hidden backdrop, video decoding and raster conventions are additional inputs.
- Missing backdrop pixels may be extended for presentation, with the method and valid-mask numerical effect recorded.
- Preserve the original recovered inputs and native benchmark; completed pixels are estimates, not new observed evidence.

<a id="recreation-models-equation-1"></a>

$$
L=\frac D2.
$$

<a id="recreation-models-equation-2"></a>

$$
\mathbf v=\frac{\mathbf p-\mathbf p_{\mathrm{center}}}{L}.
$$

<a id="recreation-models-equation-3"></a>

$$
\sigma _{i}=\widehat{\sigma} L_i
$$

<a id="recreation-models-equation-4"></a>

$$
\sigma_i=\sigma_{\mathrm{ref}}\frac{L_i}{L_{\mathrm{ref}}}.
$$

<a id="recreation-models-equation-5"></a>

$$
\widehat\sigma=\frac{\sigma_{\mathrm{ref}}}{L_{\mathrm{ref}}}.
$$

<a id="recreation-models-equation-6"></a>

$$
d=\max(-s,0)
$$

## Model responsibilities and evidence

- These historical models own the footprint, front/back surfaces or explicitly empirical map, thickness, transmission/reflection, dispersion, ordinary blur, foreground response, contrast, highlights and exterior shadows.
- Each stage has declared normalized parameters and operation order; no renderer-specific tricks are required by the specification.
- **Ordinary blur and dispersion are separate. ** Ordinary blur averages neighboring samples with one spatial kernel shared by the channels.
- Dispersion changes the sampling/transport by wavelength (or a declared RGB proxy); it can produce colored edge spreading without ordinary blur.
- Corner color highlights require a separate lighting test before attributing them to dispersion.
- Geometry-led candidates must state camera, surfaces, IOR, background distance and valid ray branches.
- Derive normals from one surface and check its [ray-map compatibility](model.md#flat-front-inverse-map-compatibility); zero image-map curl alone neither establishes nor rejects a refracting solid.
- Empirical maps remain labeled approximations; folds and total internal reflection are distinct phenomena.
- Pill silhouettes should be tested for smoothly joined shoulders and a minute center crown rather than assumed to be a straight capsule.
- Curvature is a parameter of the element family, not a pixel correction on one reference.
- Do not retain the photographed element's shadow in a reconstruction backdrop. Recover an unobstructed frame or reconstruct the incident background, recording uncertainty; generate the modeled shadow separately.
- Earlier retained-context figures remain historical estimates until corrected.
- No target-pixel painting, hidden per-image optical coefficients, artifact copying or blur that conceals an incorrect shape. Icons use reusable solid geometry; their material is evaluated separately.
- Additional brightness or saturation beyond the sampled scene needs an explicit lighting/material hypothesis.

## Verified improvement protocol

The legacy records below predate this stricter protocol. Preserve their experiment counts and inputs; do not relabel them as qualifying improvements without an audit.

- Freeze an input epoch: reference/source hashes, registration, masks, color space, native sampling, quantization and measurement definitions.
- Source confidence and target visibility are separate: extending an incident backdrop must not expand scoring masks. The replay accepts an independently hashed `target_observation_mask`; legacy cases retain `known.png`.
- Changed input evidence requires a separately reported epoch and baseline, not an apparent model improvement.
- For each observation, measure RGB errors in 0–255 units: [the expression below](#recreation-models-equation-7).
- A new qualifying pass requires [the condition below](#recreation-models-equation-102) **on every active background independently**, at least one measurable improvement beyond known numerical uncertainty, and no whole-glass regression.

<a id="recreation-models-equation-102"></a>

$$
E_{\mathrm{new}}\le E_{\mathrm{previous}}.
$$

- This prospective nonregression policy replaces the earlier 0.5% minimum; preserve earlier acceptance records unchanged. Retain foreground and exterior-shadow nonregression guards where measured. Ties and rejected trials do not count.

Preview widths are per individual image/side. Iterations use `min(2W, max(W, cap))`, where W is the original reference crop width; cap is720px for small controls or1080px for navbars/player bars. Preserve aspect ratio.
- Originals wider than cap retain their width; high-quality exports are1080px wide. [Sizing reference](../reconstruction/preview_size.py). Native measurement resolution never follows preview resizing.

A numerical win also requires independent replay, source-footprint validation and visual review against known defects. [Acceptance gate](../reconstruction/progress_gate.py) consumes those separate evidence decisions; it cannot infer them from a low error.
- There is no promised minimum compound gain. The gate retains `--policy relative` for reproducing historical 0.5% decisions. Prefer short bounded proposals and reuse valid unchanged-stage evidence.
- Display `100(1−E/E₀)` as **residual reduction from baseline**, never percent Apple accuracy. A zero residual is terminal, not another successful tie.
- Review assumptions and model deficiencies after every three substantive experiments, including rejected trials.
- If the milestone stalls, revise the hypothesis or report the limitation; do not reset the baseline or accept known visual regressions to advance a counter.
- Work on two distinct elements concurrently. Commit and push each verified pass; after three verified non-regressive passes per element, merge and rotate. This replaces the earlier 15/20-pass targets prospectively.
- Retain all active backgrounds and historical evidence; adding a reference is a documented new stage, not an excuse to drop older scores.
- [Local crop diagnostics](../reconstruction/crop_diagnostics.py) are advisory: fixed masks/positions, RGB and channel-edge errors, contour/refraction landmarks, and shadow/highlight profiles. Do not realign or recolor crops independently.
- Their purpose is to expose local defects hidden by the global average.

<a id="recreation-models-equation-7"></a>

$$
E=\sqrt{0.7\,\mathrm{RMSE}_{\mathrm{glass}}^2+0.3\,\mathrm{RMSE}_{\mathrm{rim}}^2}.
$$

## Continuous pill footprint candidate

This optional footprint replaces the capsule's exactly straight central interval. It is a **2D geometry hypothesis**, not a recovered Apple solid. Optical calibration must be evaluated separately. The existing recipes retain their original footprint unless `crown_softness` is enabled.

For major/minor half-extents [the condition below](#recreation-models-equation-103), softness [the condition below](#recreation-models-equation-104), and [the expression below](#recreation-models-equation-8), define [the expression below](#recreation-models-equation-9) and:

<a id="recreation-models-equation-103"></a>

$$
a \ge  b > 0
$$

<a id="recreation-models-equation-104"></a>

$$
0 < w \le  1
$$


<a id="recreation-models-equation-8"></a>

$$
e=wb.
$$

<a id="recreation-models-equation-9"></a>

$$
\operatorname{sp}(t)=\ln(1+\exp(t))
$$

$$
\begin{aligned}
c&=\operatorname{sp}\!\left(\frac{e-(a-b)}e\right),\\
D&=\operatorname{sp}\!\left(\frac{\sqrt{a^2+e^2}-(a-b)}e\right)-c,\\
q(x)&=\frac bD\left[\operatorname{sp}\!\left(\frac{\sqrt{x^2+e^2}-(a-b)}e\right)-c\right],\\
T(x,y)&=\frac{q(x)^2+y^2}{b^2}.
\end{aligned}
$$


The boundary is [the condition below](#recreation-models-equation-105). [the condition below](#recreation-models-equation-106), [the expression below](#recreation-models-equation-10), and `q` is even, smooth and convex. Hence the top/bottom have a unique maximum extent at the center and no exactly straight interval.

<a id="recreation-models-equation-105"></a>

$$
T=1
$$

<a id="recreation-models-equation-106"></a>

$$
q(0)=0
$$

- This does not require an abrupt cap/body join.
- At [the expression below](#recreation-models-equation-11), this softened longitudinal formula does **not** become a circle: X/Y remain inequivalent. Use the separate radial footprint for circles.
- The current pill study does not establish a continuous pill-to-circle morph.
- Use [the expression below](#recreation-models-equation-12) for the boundary normal.

The reference image-map coordinate [the condition below](#recreation-models-equation-107) has the correct boundary/sign but is **not Euclidean signed distance**; do not substitute it into a distance-based physical derivation without accounting for its gradient.

<a id="recreation-models-equation-107"></a>

$$
b(\sqrt{T}-1)
$$

- Switch review revision 9 uses softness `0.08`, one material across both observations and generated exterior shadows.
- [Recipe](../reconstruction/studies/active-switch/review-round/pass-09.json) records the kernel length basis; the dimensionless source/output blur widths are `sigma/216.5` and `post_sigma/216.5`.
- This incremental image-score improvement does not validate the inherited empirical displacement field as a physical solid.

Reproduce the revision from private frozen `a/` and `b/` study inputs: `python revision_replay.py INPUTS studies/active-switch/review-round/pass-06.json studies/active-switch/review-round/pass-09.json OUTPUT --scale 1` from `experiments/reconstruction/`. The script independently replays both states and all emitted transmission rays; human visual approval remains separate.
- [Implementation](../reconstruction/crowned_footprint.py) evaluates normalized geometry and analytic derivatives. The same `T` could define a 3D height field, but that height, camera and IOR must be specified and tested separately.

Independent fits to the two selector silhouettes suggest softness about0.185. This is a calibration candidate, not a default for all pills. [Contour measurements](../reconstruction/studies/active-segmented-selector/crown-diagnostics.json) describe the fixed white-ridge sample and its limits.
- The initial clear optical trials did not pass the improvement gate.

<a id="recreation-models-equation-10"></a>

$$
q(a)=b
$$

<a id="recreation-models-equation-11"></a>

$$
a=b
$$

<a id="recreation-models-equation-12"></a>

$$
\mathbf n=\frac{\nabla T}{\|\nabla T\|_2}.
$$

## Playback: radial map and smooth inner transition

For the circle, [the condition below](#recreation-models-equation-108), [the condition below](#recreation-models-equation-109), and [the expression below](#recreation-models-equation-13). At the center set [the condition below](#recreation-models-equation-110); the displacement has already reached zero there. Use the following constants:

<a id="recreation-models-equation-108"></a>

$$
r=\|\mathbf v\|_2.
$$

<a id="recreation-models-equation-109"></a>

$$
d=1-r
$$

<a id="recreation-models-equation-110"></a>

$$
F(0)=0
$$


<a id="recreation-models-equation-13"></a>

$$
\mathbf F(\mathbf v)=\left(1-\frac{a(d)}r\right)\mathbf v.
$$

| Parameter | Value |
| --- | ---: |
| Outer displacement `A` | 0.6344430313360516 |
| Initial transition width `b` | 0.09445809156460266 |
| Initial exponent `p` | 2.10022237760162 |
| Inner-tail width multiplier `k` | 4.5 |
| Inner endpoint exponent `q` | 4 |
| Displacement gain | 1 |
| Source Gaussian σ / L | 0.0020408163265306124 |
| Glass post-refraction σ / L | 0.006530612244897959 |
| Final foreground-color σ / L | 0.012244897959183673 |

For [the condition below](#recreation-models-equation-111), use [the expression below](#recreation-models-equation-14). For [the condition below](#recreation-models-equation-112), define [the expression below](#recreation-models-equation-15) and use:

<a id="recreation-models-equation-111"></a>

$$
d\le\frac b2.
$$

<a id="recreation-models-equation-112"></a>

$$
\frac b2<d<\frac{(1+k)b}{2}.
$$


<a id="recreation-models-equation-14"></a>

$$
a=A\left[\operatorname{clamp}\!\left(1-\frac db,0,1\right)\right]^p.
$$

<a id="recreation-models-equation-15"></a>

$$
t=\frac{d-\frac b2}{\frac{kb}{2}}.
$$

$$
a=A2^{-p}\exp\!\left[q\ln(1-t)+(q-pk)t+\frac{q-pk^2}{2}t^2\right].
$$

For larger `d`, use [the condition below](#recreation-models-equation-113). The join matches value, first and second derivatives; the inner endpoint has zero derivatives through order three. This controls the transition from the strongly refracted rim to the quiet center without inserting a discontinuous shoulder. It does **not** prescribe a 3D height or thickness.

<a id="recreation-models-equation-113"></a>

$$
a=0
$$


The map has a fold in its supported calibration; reversed rim details are intentional in this still-image fit.

### Glass and play-symbol processing

The [current playback recipe](../reconstruction/studies/playback/review-round/pass-03.json) multiplies all original material coefficients by 1.005 before clipping/shading integration. The original coefficients remain archived in `recipes.json`; the round record contains the exact resulting vector. Replay the frozen inputs with `python playback_replay.py INPUTS studies/playback/review-round/pass-03.json OUTPUT --scale 4`; add `--record` with the same file to `motion.py` for the moving preview.

1. Blur the backdrop with the source σ, sample it through `F`, and apply the common material function below.
2. Blur that calculated glass color with the glass σ. This is after refraction and shading.
3. Calculate the foreground color [the expression below](#recreation-models-equation-16), componentwise. Use the exact three-channel coefficients from the recipe:

<a id="recreation-models-equation-16"></a>

$$
\mathbf C_0=\mathbf1-\mathbf s\odot(\mathbf1-\mathbf C_{\mathrm{glass}})^{\boldsymbol\gamma}.
$$

$$
\begin{aligned}
\mathbf s&=\begin{pmatrix}0.9999999999999285\\0.9999999999999999\\0.4829334270156419\end{pmatrix},&
\boldsymbol\gamma&=\begin{pmatrix}11.731766541351298\\8.166089277320348\\5.294455609674747\end{pmatrix}.
\end{aligned}
$$

4. Let [the expression below](#recreation-models-equation-17) and [the expression below](#recreation-models-equation-18). Increase dark-region saturation: [the expression below](#recreation-models-equation-19).
Componentwise, set [the expression below](#recreation-models-equation-20) and [the expression below](#recreation-models-equation-21). This reduces near-white highlights without creating an early white plateau. For a general strength `h`, the function is monotone for [the condition below](#recreation-models-equation-114); `.48` is the current value.

<a id="recreation-models-equation-114"></a>

$$
0\le h\le 4
$$

6. Gaussian-blur **C2**, with the final foreground-color σ. This is the last color operation. Composite it through the sharp triangular coverage: [the expression below](#recreation-models-equation-22).

<a id="recreation-models-equation-17"></a>

$$
Y=\mathbf C_0\cdot(0.2126,0.7152,0.0722).
$$

<a id="recreation-models-equation-18"></a>

$$
w=\left[\operatorname{clamp}\!\left(\frac{1-Y}{0.15},0,1\right)\right]^2.
$$

<a id="recreation-models-equation-19"></a>

$$
\mathbf C_1=\operatorname{clamp}\!\left[Y\mathbf1+(1+0.2w)(\mathbf C_0-Y\mathbf1),0,1\right].
$$

<a id="recreation-models-equation-20"></a>

$$
\mathbf u=\operatorname{clamp}\!\left(\frac{\mathbf C_1-0.9\mathbf1}{0.1},0,1\right).
$$

<a id="recreation-models-equation-21"></a>

$$
\mathbf C_2=\mathbf C_1-0.48\,\mathbf u^3\odot(\mathbf1-\mathbf C_1).
$$

<a id="recreation-models-equation-22"></a>

$$
\mathbf C_{\mathrm{out}}=(1-\alpha)\mathbf C_{\mathrm{glass}}+\alpha\mathbf C_{\mathrm{blurred}}.
$$

The included [playback coverage mask](../reconstruction/playback-mask.png) is a reference-derived triangle silhouette with its antialias fringe, not copied Apple icon colors. Its box is stored in normalized coordinates. There is no stroked icon outline. The foreground response was fitted on this photograph and can produce unsuitable hues elsewhere; this is not a universal contrast algorithm.

A light icon also needs a different treatment over a white backdrop.

## Toolbar: normal displacement and tangential compression

The current footprint uses the continuous crown above, half-extents `[392/170,1]` and softness `0.10`. The inherited normal-profile length basis is [the condition below](#recreation-models-equation-115); its boundary coordinate is not Euclidean distance. The fitted map allows normal displacement and tangential scaling to vary separately. With tangent [the condition below](#recreation-models-equation-116):

<a id="recreation-models-equation-115"></a>

$$
\rho =1
$$

<a id="recreation-models-equation-116"></a>

$$
\mathbf t=(-n_y,n_x).
$$


$$
\begin{aligned}
a(d)&=\sum_{i=0}^{6}c_iN_i\!\left(\frac d\rho\right),\\
u&=\operatorname{clamp}\!\left(\frac d{\rho b_{\mathrm{band}}},0,1\right),\\
W&=(1-u)^4(1+4u),\\
\mathbf F(\mathbf v)&=\operatorname{diag}(1-c_x,1-c_y)\mathbf v-a(d)\mathbf n-\tau W(\mathbf t\cdot\mathbf v)\mathbf t.
\end{aligned}
$$

The cubic B-spline basis has knots `[0,0,0,0,.015,.04,.09,.2,.45,.75,1,1,1,1]`; append three zero coefficients after the seven stored coefficients. Clamp the basis argument to `[0,1]`. Displacement is in `L` units. Coefficients 4–6 have supports beginning at `d/r` values `.015`, `.04` and `.09`; value and first two derivatives vanish at their support endpoints.

The signed coefficients describe the inverse map, not lens heights. The complete coefficients, core terms and tangential strength are in the [current recipe](../reconstruction/studies/archive-plus/review-round/pass-03.json).

This is a tensor image field, **not a recovered solid or a proved gradient-potential lens**. In the straight-edge limit, [the expression below](#recreation-models-equation-23): a smaller positive source derivative makes displayed text wider. Crowned boundaries add derivatives of the changing normal. Both displacement directions follow the outline.

<a id="recreation-models-equation-23"></a>

$$
\frac{\partial F_x}{\partial x}=1-c_x-\tau W.
$$

For the toolbar only, blend unblurred and source-blurred samples using [the expression below](#recreation-models-equation-24), with [the expression below](#recreation-models-equation-25). Use the recipe's source σ `11/170`. Apply [the expression below](#recreation-models-equation-26) componentwise, with one shared [the condition below](#recreation-models-equation-117), **before** the common affine material and clipping. The revised material coefficients are stored directly in the recipe.

<a id="recreation-models-equation-117"></a>

$$
\gamma =1.0456395525912732
$$


<a id="recreation-models-equation-24"></a>

$$
H=6u^{5}-15u^{4}+10u^{3}
$$

<a id="recreation-models-equation-25"></a>

$$
u=\operatorname{clamp}\!\left(\frac d{b_{\mathrm{blur}}},0,1\right).
$$

<a id="recreation-models-equation-26"></a>

$$
\mathbf C_{\mathrm{input}}=\max(\mathbf C_{\mathrm{blend}},\mathbf0)^\gamma.
$$

This empirical encoded-RGB curve is strongly confounded with material/source photometry; it does not identify Apple's pipeline. Positive gamma and positive material gains preserve nondecreasing response under fixed lighting and positive filtering.

After the common material, apply ordinary color blur with [the expression below](#recreation-models-equation-27) in normalized units. This is distinct from dispersion (none added in this revision). For conditional glass color `C` and coverage `α`, use [the expression below](#recreation-models-equation-28), then retain the original sharp coverage for composition. Filtering zero-padded RGB directly would create an unsupported dark edge.

<a id="recreation-models-equation-27"></a>

$$
\sigma=\frac{1.25}{170}.
$$

<a id="recreation-models-equation-28"></a>

$$
\mathbf C'=\frac{\mathcal G_\sigma[\alpha\mathbf C]}{\max\{\mathcal G_\sigma[\alpha],\varepsilon\}}.
$$

The neutral exterior shadow is [the expression below](#recreation-models-equation-29): opacity [the condition below](#recreation-models-equation-118), width [the condition below](#recreation-models-equation-119), offset [the condition below](#recreation-models-equation-120). Generate the whole shape with at least four-sigma padding before cropping. Composite `C′α + B(1−A_s)(1−α)`; no reference shadow is retained. The fitted width reaches its declared bound, so these are provisional appearance parameters, not a recovered lighting rig.

<a id="recreation-models-equation-118"></a>

$$
o=0.21968065
$$

<a id="recreation-models-equation-119"></a>

$$
s=0.29999995 L
$$

<a id="recreation-models-equation-120"></a>

$$
\delta =[-0.002930886,0.007772859] L
$$


<a id="recreation-models-equation-29"></a>

$$
A_s(\mathbf x)=o\,\mathcal G_s[\alpha](\mathbf x-\boldsymbol\delta).
$$

Finally apply solid SVG coverage with constant foreground color. The plus comes from the original font; the archive is a symmetric geometric trace. Font/vector provenance and pose are independent of optics. Native source and SVG hashes are frozen in the recipe. Reproduce from private inputs with `python tensor_replay.py INPUTS studies/archive-plus/review-round/pass-03.json OUTPUT --scale 4` from `experiments/reconstruction/`.

The command verifies hashes and renders fresh high-resolution geometry, glass, shadow and icons without fitting.

## Active slider: oval outline and channel-separated map

The outline is **not a capsule**. Set [the expression below](#recreation-models-equation-30), [the condition below](#recreation-models-equation-121), [the expression below](#recreation-models-equation-31), [the expression below](#recreation-models-equation-32), and [the expression below](#recreation-models-equation-33), where:

<a id="recreation-models-equation-121"></a>

$$
h_y=1
$$


<a id="recreation-models-equation-30"></a>

$$
h_x=\frac{118.5}{56.5}.
$$

<a id="recreation-models-equation-31"></a>

$$
U=\frac{x}{h_x}.
$$

<a id="recreation-models-equation-32"></a>

$$
V=\frac{y}{h_y}.
$$

<a id="recreation-models-equation-33"></a>

$$
Q(U)=1+a U^{2}+b U^{4}
$$

$$
\begin{aligned}
a&=0.4994011732582939,\qquad b=-0.23031415352591186,\\
T(U,V)&=U^2+\left(\frac V{Q(U)}\right)^2.
\end{aligned}
$$

The boundary is [the condition below](#recreation-models-equation-122). Use Euclidean distance to this curve for `s`, and its normalized implicit gradient for `n`. The radius parameter [the expression below](#recreation-models-equation-34) controls the spline's distance scale; it is not a claim that the whole outline has constant radius. The top dark ridge constrains the measured outline; bottom/right symmetry remains an assumption.

<a id="recreation-models-equation-122"></a>

$$
T=1
$$


<a id="recreation-models-equation-34"></a>

$$
\rho=\frac{43.38}{56.5}.
$$

Use the same tensor map as the toolbar with the **slider's** independent recipe. For channel wavelengths [the condition below](#recreation-models-equation-123) in micrometers, use:

<a id="recreation-models-equation-123"></a>

$$
\lambda =[.650,.550,.450]
$$


$$
\begin{aligned}
f_\lambda&=1+d_{\mathrm{disp}}\left(\lambda^{-2}-0.550^{-2}\right),\\
\mathbf F_\lambda(\mathbf v)&=\mathbf v+f_\lambda[\mathbf F(\mathbf v)-\mathbf v].
\end{aligned}
$$

Read the red, green and blue channels at their respective `F_λ`, then apply the common material. No Gaussian blur is selected. This is an RGB dispersion proxy; it does not prove that Apple's colored rim comes from physical dispersion. It is not a wavelength-resolved radiometric model.

The recovered background includes an antialiased track of height `20/56.5` in normalized units, centered `(.9295089030362/56.5)` below the lens center. Its hidden blue endpoint is estimated. The replay fixes this input explicitly; source reconstruction uncertainty remains part of the comparison.

The generated contact shadow uses the same footprint, scaled by [the expression below](#recreation-models-equation-35), [the expression below](#recreation-models-equation-36), with normalized vertical offset [the condition below](#recreation-models-equation-124). It stays horizontally centered and bottom-aligned. Let [the expression below](#recreation-models-equation-37), `α_c` be the contact coverage, `sd_normalized` be signed distance to the original normalized footprint, and `B` the frozen incident input:

<a id="recreation-models-equation-124"></a>

$$
\delta _y=-(s_y-1)
$$


<a id="recreation-models-equation-35"></a>

$$
s_x=\frac{1963}{1896}.
$$

<a id="recreation-models-equation-36"></a>

$$
s_y=\frac{929}{906}.
$$

<a id="recreation-models-equation-37"></a>

$$
\mathbf p=\frac{\mathbf x_{\mathrm{pixel}}-\mathbf x_{\mathrm{center}}}{L}.
$$

$$
\begin{aligned}
\mathbf C_0&=(1-q\alpha_c)\mathbf B,\\
s_h&=\operatorname{sd}_{\mathrm{norm}}(\mathbf p-(0,0.1)),\\
h&=a\exp\!\left[-\frac12\left(\frac{\max(s_h,0)}\sigma\right)^2\right],\\
\mathbf B_{\mathrm{out}}&=(1-h)\mathbf C_0+h\beta\mathbf C_{\mathrm{accent}},\\
\mathbf C_{\mathrm{complete}}&=\alpha\mathbf C_{\mathrm{body}}+(1-\alpha)\mathbf B_{\mathrm{out}}.
\end{aligned}
$$

The frozen coefficients are:

$
q=0.17375816993464055,\quad a=0.09639485214612539,\quad\sigma=0.7051111669310818,\quad\beta=0.9999999999999999.
$

 The recipe freezes the accent from an exposed blue-track patch. Contact opacity comes from the owner's nominal-white samples and remains photometrically uncertain. Initial halo coefficients use nine fixed exterior profile patches; the final halo footprint is offset downward by .1L. no reference shadow/residual is pasted.

This empirical accent response is not identified Apple lighting or image blur/dispersion. Fixed coefficients preserve a nondecreasing response to B; scales are proportional to L.

All original optical/body coefficients, inputs and native scores stay fixed. Near/full-visible exterior and their spatial train/held blocks are protected separately. Gray-track profile transfer is advisory; its hidden input and compressed interaction geometry are not a calibrated optical pair. [Current recipe](../reconstruction/studies/slider-exterior/review-round/pass-03.json) freezes the original body and contact/halo parameters. From `experiments/reconstruction/`, run:

```sh
python slider_exterior.py INPUTS OUTPUT --recipe studies/slider-exterior/review-round/pass-03.json
```

INPUTS contains the frozen slider-source.png and slider-target.png. The target is read only for scoring and the comparison; it never enters the generated exterior. Optional `--material-cache` verifies the original array hash and avoids repeating an unchanged body render. The native command verifies the original calibration. For final1080px stills and motion, run:

```sh
python slider_motion.py INPUTS studies/slider-exterior/review-round/pass-03.json OUTPUT --width 1080 --frames 90 --fps 15
```

[ClearField](../reconstruction/clear_field.py) caches only fixed outline/map/material fields and omits zero-weight source queries; each moving position samples the source again. The body matches the original native renderer bit-for-bit at zero and a distinct17px translation. Nearly96× faster per-frame native sampling in this offline case is not an Android benchmark. Source/output blur are unsupported by this cache.

Rebuild it when shape or material changes. Final stills/motion use4×4 samples per output pixel; native scoring is inherited unchanged. [Source-domain/media evidence](../reconstruction/studies/slider-exterior/review-round/motion.json) covers contributing and unused pack queries; defined input is not observed hidden RGB. This exterior is calibrated only to the observed blue-tinted control on light backgrounds; other themes/tints remain unvalidated.

## Uniform light and dark surfaces

These use a rounded rectangle with half-extents `[245/106.5,1]` and radius `1`. Let [the expression below](#recreation-models-equation-38), [the condition below](#recreation-models-equation-125), [the expression below](#recreation-models-equation-39), and:

<a id="recreation-models-equation-125"></a>

$$
v=1-u
$$


<a id="recreation-models-equation-38"></a>

$$
u=\operatorname{clamp}\!\left(\frac d{\rho b_{\mathrm{band}}},0,1\right).
$$

<a id="recreation-models-equation-39"></a>

$$
S=6u^{5}-15u^{4}+10u^{3}
$$

$$
\begin{aligned}
P&=r_{\mathrm{mix}}v^3(1+3u)+(1-r_{\mathrm{mix}})\frac{256}{27}uv^3,\\
a&=\rho b_{\mathrm{band}}e_{\mathrm{edge}}P,\\
\mathbf F(x,y)&=((1-c_{\mathrm{core}}S)x,(1-c_{\mathrm{core}}S)y)-a\mathbf n.
\end{aligned}
$$

The `regular-light` and `regular-dark` recipes independently specify field parameters and material coefficients. Neither uses Gaussian blur. Their nearly uniform backdrops cannot identify an optical model; high scores here validate tone/rim approximation, **not refraction**.

The third current reconstruction checkpoint adds a **shared generated exterior**, with the original independent body recipes, source PNGs and native 4×4 coverage unchanged. This empirical component improves exterior reconstruction; optical scores tie. It does not identify refraction, the incident background, or Apple's lighting setup.

Use the original rounded-rectangle signed distance in normalized coordinates. The shared offset multiplier and final offsets are:

$$
\begin{aligned}
L&=106.5\ \mathrm{px},&\mathbf p&=\frac{\mathbf x_{\mathrm{pixel}}-\mathbf x_{\mathrm{center}}}{L},\\
s&=1.2,&\boldsymbol\delta_K&=s(0,0.06)=(0,0.072),\\
&&\boldsymbol\delta_H&=s(0,-0.4)=(0,-0.48).
\end{aligned}
$$



$$
\begin{aligned}
\alpha_i(\mathbf p)&=o_i\exp\!\left[-\frac12\left(\frac{\max\{\operatorname{sd}(\mathbf p-\boldsymbol\delta_i),0\}}{\sigma_i}\right)^2\right],\\
\mathbf B_1&=(1-\alpha_K)\mathbf B,\\
\mathbf B_{\mathrm{out}}&=\mathbf B_1+\alpha_H(\mathbf1-\mathbf B_1),\\
\mathbf C_{\mathrm{complete}}&=\alpha\mathbf C_{\mathrm{body}}+(1-\alpha)\mathbf B_{\mathrm{out}},\\
o_K&=0.028644737086080185,\qquad\sigma_K=0.7,\\
o_H&=0.0391166614246353,\qquad\sigma_H=0.11786013768786802.
\end{aligned}
$$

Both themes use these exact coefficients. B is the existing frozen source PNG, not a fitted background plane. The light paper is polynomial-estimated; dark underbody source0 remains an assumption. No copied target residual or reference shadow enters this exterior law. Gaussian distance falloff is an exterior opacity law, not image blur or chromatic dispersion.

The black sigma reaches its declared .7L limit; upper light far bands regress and the broader dark gray field remains unresolved.

For exact native replay, coordinates/signed distances retain the existing float32 staging and Gaussian parameters/compositing use float64. A pure-float64 coordinate control differs by up to 4.63e−9; no regression tolerance was changed. [Recipe and original independent body materials](../reconstruction/studies/light-dark/review-round/pass-03.json) · [Independent verification](../reconstruction/studies/light-dark/review-round/pass-03-verification.json).

Run the standalone [replay](../reconstruction/regular_exterior.py) from the reconstruction directory, with the four frozen regular-light/dark source/target PNGs in INPUTS:

```sh
python regular_exterior.py INPUTS OUTPUT --recipe studies/light-dark/review-round/pass-03.json
```

This performs the original native body render and separately generates the exterior; it never invokes the old context compositor. Reuse immutable native material arrays with --material-cache CACHE when those arrays already match the recipe. Output includes all original score checks, frozen-range/full-visible exterior scores and 720/1080-width per-side comparisons with explicit 64px captions.

## Music and switch profile family

The newer [paired studies](reconstruction.md#apple-music-studies) use one normalized image-map family. Each `studies/<id>/paired/accepted.json` supplies the shared coefficients; `a.json` and `b.json` supply measured poses and frozen input hashes. Home's corrected chain protects the retained single-background result; the earlier invalid pairing is archived separately.

Subtract the recipe's shape offset from `v`, then apply its half-extent/radius corrections. Obtain boundary coordinate `s`, outward unit normal `n`, and [the condition below](#recreation-models-equation-126). The usual outline is a rounded rectangle/capsule. For a circle, keep equal half-extents and use [the condition below](#recreation-models-equation-127) with no directional optical parameters.

<a id="recreation-models-equation-126"></a>

$$
d=\max(-s,0)
$$

<a id="recreation-models-equation-127"></a>

$$
c_y=c_x.
$$


For `spline=true`, evaluate a cubic B-spline at `clamp(d/R,0,1)`, with knots `[0,0,0,0,.015,.04,.09,.2,.45,.75,1,1,1,1]` and coefficients `[c0,…,c6,0,0,0]`. Otherwise use [the condition below](#recreation-models-equation-128). Signed spline coefficients permit folds and reduced center images; they are not lens heights.

<a id="recreation-models-equation-128"></a>

$$
a=A\left[\max\!\left(1-\frac d b,0\right)\right]^p.
$$


$$
\begin{aligned}
q&=\begin{cases}n_x^2,&\text{horizontal major axis},\\n_y^2,&\text{vertical major axis},\end{cases}\\
a&\gets a(1+g_{\mathrm{cap}}q)+q\sum_i b_iB_i\!\left(\frac dR\right),\\
u&=\operatorname{clamp}\!\left(\frac d{b_T},0,1\right),\\
W_0&=(1-u)^m(1+mu),\qquad W=W_0(1-f_{\mathrm{cap}}q),\\
W_d&=\frac{\partial W_0}{\partial d}=-\frac{m(m+1)u(1-u)^{m-1}}{b_T},\\
\tau_p&=-n_yx+n_xy,\\
K&=\frac12\,c_{\mathrm{coupling}}\,t_{\mathrm{strength}}\,W_dx^2,\\
F_x&=(1-c_x)x-an_x+t_{\mathrm{strength}}W\tau_pn_y-Kn_x,\\
F_y&=(1-c_y)y-an_y-t_{\mathrm{strength}}W\tau_pn_x-Kn_y.
\end{aligned}
$$

The optional [the condition below](#recreation-models-equation-129) uses the same cubic basis as `a`; missing coefficients are zero. The current switch uses three terms, whose added displacement vanishes with two continuous derivatives at [the condition below](#recreation-models-equation-130). This changes normal refraction near the caps without altering the silhouette or deeper interior. Coefficients are dimensionless source-coordinate displacements, not surface heights.

<a id="recreation-models-equation-129"></a>

$$
\mathbf b_{\mathrm{cap}}=(b_0,b_1,\ldots).
$$

<a id="recreation-models-equation-130"></a>

$$
\frac dR=0.09.
$$


Here [the condition below](#recreation-models-equation-131) (default 4). Restore the shape offset to `F` before backdrop lookup. Missing cap gains/fades are zero. `W_d` is deliberately the base falloff derivative **without** the orientation weight; with these empirical tensor terms, the field is not asserted to be a gradient potential or ray trace through an identified solid.

<a id="recreation-models-equation-131"></a>

$$
m=m_{\mathrm{tangent}}.
$$


The compact mini-player additionally smooths the capsule's cap/body join. Along its major axis let [the condition below](#recreation-models-equation-132), [the condition below](#recreation-models-equation-133), and [the condition below](#recreation-models-equation-134). Replace `max(z,0)` by [the condition below](#recreation-models-equation-135) for [the condition below](#recreation-models-equation-136), where [the condition below](#recreation-models-equation-137); use 0 below and `z` above that interval. The boundary coordinate is [the condition below](#recreation-models-equation-138); normalize its analytic gradient for `n`.

<a id="recreation-models-equation-132"></a>

$$
a=\max(h)-R
$$

<a id="recreation-models-equation-133"></a>

$$
z=|x|-a
$$

<a id="recreation-models-equation-134"></a>

$$
w=w_{\mathrm{join}}.
$$

<a id="recreation-models-equation-135"></a>

$$
q=w(2t^{3}-t^{4})
$$

<a id="recreation-models-equation-136"></a>

$$
|z|<w
$$

<a id="recreation-models-equation-137"></a>

$$
t=\frac{z+w}{2w}.
$$

<a id="recreation-models-equation-138"></a>

$$
\sqrt{q^{2}+y^{2}}-R
$$


This is a C2 implicit join, **not exact Euclidean distance** in the join band. Rotate axes for a vertical capsule.

Sample the source-blurred backdrop through `F`. When [the condition below](#recreation-models-equation-139), blend clear and source-blurred samples with quintic smoothstep of `d/blur_transition`, then apply `sample^gamma`. Apply the common material, average subpixels, then apply output Gaussian blur. Coverage, exterior shadows and solid-vector foreground layers remain separate.

<a id="recreation-models-equation-139"></a>

$$
b_{\mathrm{blur}}>0.
$$


Exact normalized coefficients, foreground styles and any context option are part of each recipe, not inferred from its preview image.

## Common material function

All five frozen recipes have 23 coefficients. Define [the condition below](#recreation-models-equation-140), [the condition below](#recreation-models-equation-141), [the condition below](#recreation-models-equation-142), [the condition below](#recreation-models-equation-143), [the condition below](#recreation-models-equation-144). Let [the condition below](#recreation-models-equation-145) and [the condition below](#recreation-models-equation-146). The 14 lighting basis values, in order, are:

<a id="recreation-models-equation-140"></a>

$$
X=\frac{x}{h_x}.
$$

<a id="recreation-models-equation-141"></a>

$$
Y=\frac{y}{h_y}.
$$

<a id="recreation-models-equation-142"></a>

$$
\phi_{\mathrm{thin}}=\exp\!\left[-\left(\frac d{w_{\mathrm{thin}}}\right)^2\right].
$$

<a id="recreation-models-equation-143"></a>

$$
e=\exp\!\left[-\left(\frac d{w_{\mathrm{rim}}}\right)^2\right].
$$

<a id="recreation-models-equation-144"></a>

$$
f=\exp\!\left[-\left(\frac d{4w_{\mathrm{rim}}}\right)^2\right].
$$

<a id="recreation-models-equation-145"></a>

$$
z=\operatorname{clamp}\!\left(\frac d{0.30},0,1\right).
$$

<a id="recreation-models-equation-146"></a>

$$
c=6z^{5}-15z^{4}+10z^{3}
$$


$$
\begin{aligned}
\mathbf J={}&\bigl(\phi,\phi n_x,\phi n_y,e,en_x,en_y,f,fn_x,fn_y,\\[-2pt]
&\hspace{2em}X,Y,X^2,Y^2,XY\bigr),\qquad\phi=\phi_{\mathrm{thin}},\\
\mathbf g={}&(1-c)\boldsymbol\theta_{0:3}+c\boldsymbol\theta_{20:23},\\
\mathbf C_{\mathrm{glass}}={}&\operatorname{clamp}\!\left[\mathbf C_{\mathrm{sample}}\odot\mathbf g+\boldsymbol\theta_{3:6}
+(\mathbf J\cdot\boldsymbol\theta_{6:20})\mathbf1,0,1\right].
\end{aligned}
$$

The scalar lighting term is added to all RGB channels. This is a bounded fitted basis, not a Fresnel/environment reconstruction. In particular, the white inner band in some earlier fits can arise from these terms independently of refraction. Do not interpret a fit coefficient as physical radiance or encode it as an extra painted outline.

### Source-context color response

The active-switch study optionally contracts the **material's** RGB bias on neutral backgrounds. Let `μ` be the area mean of the unrefracted, encoded-RGB backdrop over the current footprint, and [the condition below](#recreation-models-equation-147). With shared sensitivity [the condition below](#recreation-models-equation-148), floor [the condition below](#recreation-models-equation-149), and encoded-luma weights [the condition below](#recreation-models-equation-150):

<a id="recreation-models-equation-147"></a>

$$
\chi =\max(\mu )-\min(\mu )
$$

<a id="recreation-models-equation-148"></a>

$$
k\ge 0
$$

<a id="recreation-models-equation-149"></a>

$$
f\in [0,1]
$$

<a id="recreation-models-equation-150"></a>

$$
\mathbf w=(0.2126,0.7152,0.0722).
$$


$$
\begin{aligned}
t&=f+(1-f)\operatorname{clamp}(k\chi,0,1),\\
\mathbf A&=t\mathbf I+(1-t)\mathbf1\mathbf w^{\mathsf T},\\
\mathbf c_{\mathrm{effective}}&=\mathbf A\mathbf c_{\mathrm{shared}}.
\end{aligned}
$$

Apply `A` to the rim gain, offset and core gain triplets before the common material calculation. Leave the 14 scalar lighting coefficients and sampled RGB ray colors unchanged. Thus [the condition below](#recreation-models-equation-151): contraction preserves each coefficient triplet's encoded-luma response, while reducing its color bias. This is not desaturation of the final image or a radiometric conservation law.

<a id="recreation-models-equation-151"></a>

$$
\mathbf w^{\mathsf T}\mathbf A=\mathbf w^{\mathsf T}.
$$



Use the same `k,f` and 23 base coefficients on both backgrounds; recompute `μ` when the backdrop or footprint moves. The reference implementation uses native-center area quadrature, independent of target/foreground/scoring masks.

An absent context option means [the condition below](#recreation-models-equation-152), preserving earlier recipes. The current switch selects [the condition below](#recreation-models-equation-153); it still misses colored rim detail. This empirical adaptation is not an identified Apple formula.

<a id="recreation-models-equation-152"></a>

$$
\mathbf A=\mathbf I.
$$

<a id="recreation-models-equation-153"></a>

$$
k=10,f=0
$$


### Source-brightness response of neutral rim lighting

An optional three-value response adjusts neutral thin/broad rim terms using the unrefracted source mean `μ`. Its sampling footprint may be inset by a declared distance `iL`; Home uses [the condition below](#recreation-models-equation-154) to avoid an unrecovered boundary strip. Let [the condition below](#recreation-models-equation-155), shared responses `r₀,r₁,r₂` and existing radial lighting bases `thin,e,f`:

<a id="recreation-models-equation-154"></a>

$$
i=.08
$$

<a id="recreation-models-equation-155"></a>

$$
y=\mu \cdot (.2126,.7152,.0722)
$$


$$
\begin{aligned}
L_{\mathrm{add}}(\mathbf x)&=\left(y-\frac12\right)[r_0\phi_{\mathrm{thin}}(\mathbf x)+r_1e(\mathbf x)+r_2f(\mathbf x)],\\
\mathbf T&=\operatorname{diag}(\mathbf A,\mathbf A,\mathbf I_{14},\mathbf A),\\
\boldsymbol\theta_{\mathrm{effective}}&=\mathbf T\boldsymbol\theta+\mathbf b(y),\\
b_6&=\left(y-\frac12\right)r_0,\quad b_9=\left(y-\frac12\right)r_1,\quad b_{12}=\left(y-\frac12\right)r_2,\\
b_j&=0,\qquad j\notin\{6,9,12\}.
\end{aligned}
$$

- The added light is identical in all three RGB channels; it cannot assign independent RGB materials to each background.

It changes lighting, not the ray map or the sampled transmission colors. The block extension applies the color matrix to three RGB triplets; the 14 scalar lighting coefficients remain unchanged.

- Recompute the source mean when the backdrop moves. Every mean sample must have defined input, including interpolation support; average coverage cannot excuse a missing pixel.
- Check context-mean support separately from scored rays. The block operator transforms material derivatives; the offset also affects clipping.
A declared calibration interval optionally bounds the source brightness with this smooth interpolation:

$$
y_{\mathrm{bounded}}=l+(h-l)S\!\left(\operatorname{clamp}\!\left(\frac{y-l}{h-l},0,1\right)\right).
$$

It preserves the measured endpoints and prevents uncontrolled extrapolation.
- Switch revision 6 retains shared nonnegative responses `[2.793309,1.311647,~0]` with no inset or luma-range remapping. The two source means are `0.758766` and `0.814351`.
- Positive grayscale gains, positive gamma and nonnegative radial bases/response imply a nondecreasing uniform-gray output; clipping and positive filtering preserve that order.

This limited [response audit](../reconstruction/studies/active-switch/review-round/pass-06-response-audit.json) does not validate arbitrary colored or spatial backgrounds. The context operator itself does not alter geometry; the revision 6 joint fit separately changes existing optical coefficients.
- Kernels and shadow stay fixed.
- This is an empirical encoded-brightness response, not radiometric illumination or an Apple formula. Home tests a narrow range of approximately 0.413–0.436; outside behavior is bounded but unvalidated.
- Zero response preserves the prior material.

### Directional grazing reflection

The switch follow-up separates a reflected field from the transmission's output blur. With normalized inward distance `d`, outward normal `n`, unit lighting direction `l`, [the condition below](#recreation-models-equation-156), width [the condition below](#recreation-models-equation-157), angular exponent [the condition below](#recreation-models-equation-158), and quintic smoothstep `S`:

<a id="recreation-models-equation-156"></a>

$$
0\le a\le 1
$$

<a id="recreation-models-equation-157"></a>

$$
w>0
$$

<a id="recreation-models-equation-158"></a>

$$
p>0
$$


$$
\begin{aligned}
u&=\operatorname{clamp}\!\left(\frac dw,0,1\right),\\
F&=a[1-S(u)]\,[\max(\mathbf n\cdot\boldsymbol\ell,0)]^p,\\
\mathbf E&=\mathcal G_{\frac{\sigma_{\mathrm{env}}}{L}}[\mathbf B_{\mathrm{unrefracted}}],\\
\mathbf C_{\mathrm{final}}&=(1-F)\mathbf C_{\mathrm{trans,blur}}+F\mathbf E.
\end{aligned}
$$

- The reflection width and source kernel scale with each pose's `L`. Sample `E` at the unrefracted surface position; update its source offset during motion.
- Keep shape coverage, exterior shadow and foreground separate.
- Reflection and transmission have independent filtering. Applying the transmission blur again after this mixture changes the model. Material derivatives therefore acquire `(1−F)` **after** their output filter.
- This bounded mixture approximates the incident field from the available backdrop.
- It is not a recovered environment, a Fresnel law, or Apple's shader; the directional lobe does not explain the observed rainbow. No target RGB is used as its input.
- Exponent [the condition below](#recreation-models-equation-159) selects an isotropic rim. An explicitly declared RGB environment may replace the backdrop proxy; it adds no background sample or photographic observation.

<a id="recreation-models-equation-159"></a>

$$
p=0
$$

- Home tests a uniform white field to improve the fitted material's poorly constrained outer edge.
- This remains an empirical lighting assumption, checked on both full composites as well as the frozen glass masks.
- An absent option preserves the earlier calculation exactly. Source coverage includes the environment kernel separately. Frozen native gates remain unchanged; the excluded outer-contour band needs an additional visual/error check.

### Directional chromatic transmission

The switch's lateral color-fringe hypothesis separates background channels **before** common lighting. For the existing map `F(x)`, source `B`, gamma `γ`, fixed direction [the condition below](#recreation-models-equation-160) and signed separation `δ`:

<a id="recreation-models-equation-160"></a>

$$
u=(\cos \theta ,\sin \theta )
$$


$$
\begin{aligned}
s_R&=1,\qquad s_G=0,\qquad s_B=-1,\\
\mathbf q_c&=\mathbf x+s_c\delta\mathbf u,\\
\mathbf F_{\mathrm{out}}(\mathbf q)&=\begin{cases}\mathbf F(\mathbf q),&\mathbf q\text{ inside the footprint},\\\mathbf q,&\mathbf q\text{ outside},\end{cases}\\
D_c(\mathbf x)&=\left[\max\{B_c(\mathbf F_{\mathrm{out}}(\mathbf q_c)),0\}\right]^\gamma,\\
z&=\frac{x_1-\delta_x}{h_x},\\
w(\mathbf x)&=a\left[1-S\!\left(\operatorname{clamp}\!\left(\frac{z-z_0}{w_f}+\frac12,0,1\right)\right)\right],\\
T_c(\mathbf x)&=(1-w)\left[\max\{B_c(\mathbf F(\mathbf x)),0\}\right]^\gamma+wD_c(\mathbf x).
\end{aligned}
$$

- `B` uses the existing source-filter rule. Apply material gain and lighting at **x**, then subpixel integration, output filtering and the preceding reflection mixture.
- Do not shift the finished highlights/shadow or multiply gamma twice.
- `δ` uses the pose's `L`; the fade center/width use horizontal half-width. The separation remains constant across the fade: its contribution decreases, not its length.
- Check each displaced ray and source kernel separately, including during backdrop movement.
- Symmetric RGB offsets are a controllable approximation to lateral chromatic aberration, not measured wavelengths, a dispersion law or Apple's implementation.
- Direction and left-side fade remain hypotheses calibrated across the two references. An absent option, zero strength or zero separation preserves the prior model.

## Solid-vector foreground responses

Selection studies may declare separate incident and exterior content layers. The optical map samples the incident layer; uncovered pixels sample the exterior layer in the same coordinate system. This permits testing selected-text recoloring independently of optical displacement. Both inputs require frozen hashes and explicit estimation provenance.

With no separate exterior declared, both use the same source, preserving existing studies. Recoloring is a content-state assumption, not an optical property or evidence of Apple's pipeline.

Foreground coverage `α` comes from solid geometry, independently of material color. Its input `B` includes preceding layers, such as a fixed selection backing. Affine styles use [the condition below](#recreation-models-equation-161); response styles use the shared per-channel function:

<a id="recreation-models-equation-161"></a>

$$
\mathbf F(\mathbf B)=(1-o)\mathbf B+o\mathbf C.
$$


$$
\begin{aligned}
F_c(\mathbf B)&=t_c\left[1-s_c\left(1-\operatorname{clamp}(B_c,0,1)\right)^{\gamma_c}\right],\\
\mathbf C_{\mathrm{out}}&=(1-\alpha)\mathbf B+\alpha\mathbf F(\mathbf B).
\end{aligned}
$$

For [the condition below](#recreation-models-equation-162) and [the condition below](#recreation-models-equation-163), the function stays bounded and monotone. The affine operation embeds exactly with [the condition below](#recreation-models-equation-164), [the condition below](#recreation-models-equation-165), [the condition below](#recreation-models-equation-166), [the condition below](#recreation-models-equation-167) and [the condition below](#recreation-models-equation-168); set [the condition below](#recreation-models-equation-169) when [the condition below](#recreation-models-equation-170). Response styles already contain opacity, so applying it again would change the model.

<a id="recreation-models-equation-162"></a>

$$
t,s\in [0,1]
$$

<a id="recreation-models-equation-163"></a>

$$
\gamma >0
$$

<a id="recreation-models-equation-164"></a>

$$
v=1-o
$$

<a id="recreation-models-equation-165"></a>

$$
q=oC.
$$

<a id="recreation-models-equation-166"></a>

$$
t=v+q
$$

<a id="recreation-models-equation-167"></a>

$$
s=\frac vt.
$$

<a id="recreation-models-equation-168"></a>

$$
\gamma =1
$$

<a id="recreation-models-equation-169"></a>

$$
s=0
$$

<a id="recreation-models-equation-170"></a>

$$
t=0
$$


One fitted response is used on both observed backgrounds; it is an empirical color function, not a Fresnel law. Glass and foreground errors remain separate.

## Reproducing and transferring a model

- Preserve equations, operation order, color space, shape and all normalized parameters when changing renderer. The source image's registration and the glyph coverage are separate inputs.
- Use the [frozen replay command](reconstruction.md#reproduce); optimization commands are for research only.
- The reference implementation uses bilinear lookup, separate shape coverage and reflected-border Gaussian filtering. Earlier HD recipes use four samples per output axis; the newer Music/switch studies use two.
- Preserve each study's native protocol when replaying its scores. These sampling choices affect exact raster pixels; they are not physical model constants.
- Compare native-resolution glass, rim, interior and foreground separately. Use identical source/mask definitions for cross-renderer scores. PNG rounding changes the reported errors slightly; record whether measurements precede or follow quantization.
- Transfer the light circular playback recipe first to other Clear circular media controls. Preserve normalized blur width rather than a fixed reference pixel width.
- Toolbar and active-slider geometry require their own mappings; a circular model should not be stretched into either shape without verification.
- Do not score an unrecovered or moving backdrop as though it were known.
- Other media controls and Music toolbar footage are useful next references, but require their original glyphs and independent backdrop recovery. They remain candidates, not additional calibrated successes.
- Display captures may extend unrecovered source pixels with the nearest known RGB.

Stills blend estimated contact context into the reference by distance from the shape; movies translate the completed source consistently inside and outside the lens, avoiding a fixed strip at the moving confidence boundary.
- Frozen benchmark inputs stay unchanged; report completion's RGB difference on the score mask, including filter/subpixel spill. Missing context remains estimated.

### Current vector-control revisions

The [Search recipe](../reconstruction/studies/music-search-vector/review-round/pass-03.json) refines the shared affine material with map, blur, SVG geometry and generated shadow fixed. The [Navigation recipe](../reconstruction/studies/music-navigation/review-round/pass-03.json) adjusts its existing empirical outer-normal profile. Both freeze native pixel blur widths, normalized map coefficients, case fingerprints and vector hashes. Scale pixel widths with the source short half-size L.

Replay: `python vector_revision.py INPUTS RECORD OUTPUT` with either linked recipe and the original private a/b source, target, known masks and SVGs. The command checks case, source and vector hashes. Unknown exterior uses nearest defined RGB for presentation only; no photographed shadow or foreground is copied.

For final figures add `--high-quality` (1080px per side). Moving exports accept `extended_media.py INPUT --width 1080`; sampling uses a binary integer scale above the requested size before downsampling. Original native scoring and default media commands are unchanged.

### Compact mini-player revision

The [current Compact recipe](../reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json) refines existing rim lighting, outer-normal refraction and shared material. Blur, SVGs and separate catalogue artwork stay fixed; changed-map source support is checked over all original emitted and scored subrays. Replay with `python vector_revision.py INPUTS studies/music-mini-compact-vector/review-round/pass-03.json OUTPUT`. INPUTS contains the original frozen a/b cases, source/target masks, SVGs and independently hashed artwork.

The compositor accepts declared vectors and separately hashed catalogue content; screenshot-derived foregrounds remain excluded.

### Home finite-incident-domain epoch

The [current Home record](../reconstruction/studies/music-home-vector/boundary-round/pass-03.json) uses fixed SVG geometry and an explicit nearest-defined RGB extension of the recovered mosaic. Shared material and bounded icon response are calibrated on both backgrounds. This is a conditional boundary approximation; no pixels are promoted to observed content. The independent `target_observation_mask` retains every original scoring/train/held mask.

Old paired21 and its incomplete incident domain remain historical, and source changes receive no optical credit.

Replay with `python vector_revision.py INPUTS studies/music-home-vector/boundary-round/pass-03.json OUTPUT`, using the frozen new-epoch inputs. An optional record-level `foreground_response` overrides model coefficients after input fingerprint verification; both backgrounds share it. Fixed nonlinear SVG response uses the declared coefficients directly, with independently rasterized coverage; it does not fit a matte or color from target pixels.

Estimated-source coverage and the remaining black-rim discrepancy are reported separately from material-fit gains.

### Expanded mini-player revision

The [current Expanded recipe](../reconstruction/studies/music-mini-expanded-vector/review-round/pass-03.json) refines the existing outer-normal spline and shared material on both backgrounds; shape, blur, SVG geometry, catalogue artwork and generated shadow remain fixed. Native blur widths use reference pixels; divide by the source short half-size L before transferring to another scale. Replay with `python vector_revision.py INPUTS studies/music-mini-expanded-vector/review-round/pass-03.json OUTPUT`, using the original frozen a/b cases and hashed assets.

Positive crown replacements failed the original guards and are not part of this record.

## Safari circular controls: conditional material transfer

The [Safari comparison](reconstruction.md#safari-circular-controls) retains a failed cross-background transfer. It is a source-limited material study, not a new refraction model. Both controls reuse the detached Music Search map and material; the magnifier and plus are separate solid vectors. The complete [coefficient records](../reconstruction/studies/safari-circles/baseline-transfer.json) fix each private case fingerprint; [input construction](../reconstruction/studies/safari-circles/input-construction.json) records normalized affine coefficients, pose and solid-vector placement.

Normalize by the reference center and radius. Fit the incident affine RGB field only on uncovered panel controls, then freeze it.

$$
\mathbf u=\frac{\mathbf p-\mathbf c}{L},\qquad\|\mathbf u\|_2\le1.
$$



$$
\begin{aligned}
\mathbf B(\mathbf u)&=\mathbf b+\mathbf G\mathbf u,\\
\mathbf G&=L\begin{pmatrix}\dfrac{\partial\mathbf B}{\partial x}&\dfrac{\partial\mathbf B}{\partial y}\end{pmatrix}.
\end{aligned}
$$

The field is encoded RGB. Its fitted gradients and intercept are input construction, not lens parameters. Hidden pixels remain modeled, observed confidence0. Mathematical source-domain coverage does not establish panel segmentation or hidden RGB truth; the parent-panel corner is omitted and its exterior error is retained.

Source and output Gaussian widths scale with radius as follows. Dimensionless displacement, material coefficients and shadow dimensions stay fixed in the unfitted transfer.

$$
\frac{\sigma_{\mathrm{source}}}{L}=\frac{5.554174315475217}{72.894},\qquad\frac{\sigma_{\mathrm{post}}}{L}=\frac{1.2089179687310392}{72.894}.
$$



The existing generated shadow operates on the modeled exterior independently of the sharp vector foreground:

$$
\begin{aligned}
d_s(\mathbf u)&=\|\mathbf u-\mathbf o\|_2-1,\\
q(\mathbf u)&=a\exp\!\left[-\frac12\left(\frac{\max(d_s(\mathbf u),0)}s\right)^2\right],\\
\mathbf B_{\mathrm{shadow}}&=(1-q)\mathbf B,\\
\mathbf C&=\alpha\mathbf M+(1-\alpha)\mathbf B_{\mathrm{shadow}}.
\end{aligned}
$$

Here a is opacity, s is dimensionless width, o is normalized offset, α is independently sampled circle coverage and M is the conditional glass color. Apply the solid SVG afterward. This Gaussian is empirical; neither the fitted field nor shadow identifies Apple's lighting. Sampling is native2×2; caption/image resizing never changes native scores.

Reproduce frozen native outputs without fitting:

```sh
python safari_transfer.py --search-input /private/proposed-a --plus-input /private/b-proposed --output /private/new-replay
```

Input hashes include the source PNG, target visibility, source-defined/observed masks and foreground vector. The replay refuses a different case fingerprint or existing output directory. The retained large cyan/brightness error on the darker plus control demonstrates a material-transfer limitation; low-frequency gray panels cannot determine a refraction field or dispersion.

Final plus exports use the three-pass shadow recipe (opacity 0.05622886993343976), with all optical/material coefficients unchanged. Reproduce the 1080px comparison and motion from the reconstruction directory:

```sh
python vector_revision.py /private/safari-inputs studies/safari-circles/plus-round/pass-03.json /private/still --high-quality
python circular_motion.py /private/safari-inputs/b-proposed studies/safari-circles/plus-round/pass-03.json /private/motion
```

The motion retains 90 frames at 15fps,1080×720, a fixed circle and actual moving source queries. Its coordinate viewport is 360×240 reference units at 3× output scale. The parent-panel boundary is omitted; the entire source field is an estimate.

A continuous radial-map bound includes the actual finite automatic Gaussian support (conservative 4σ+1 pixel radius) and bilinear taps for every pose. This is stronger than the earlier separately labeled 3σ diagnostic; it does not establish observed RGB or physical lens accuracy. Cache identity excludes only shadow: changing source, geometry, material or filters invalidates it.

Frozen recipe stage labels retain their original input/transfer-proposal status; accepted exterior passes are recorded separately in their linked verification files. They do not certify the failed shared-material transfer.

## Neutral material response

For the [Mail component study](reconstruction.md#mail-three-action-toolbar), sample the frozen incident field through the declared empirical ray map, then apply one encoded-RGB interpolation:

$$
\begin{aligned}
\mathbf C&=\tau\mathbf S+(1-\tau)\mathbf1,\qquad0\le\tau\le1,\\
\frac{\partial C_i}{\partial S_i}&=\tau.
\end{aligned}
$$

- This is a neutral material term, not the adaptive-contrast setting or a physical radiance law. It introduces no independently fitted RGB gains, hue offsets, directional lighting or per-pixel corrections.
- It preserves channel order and cannot reverse brightness. Reflections are not modeled by this term.
- The current implementation applies it per subpixel before averaging. Source and post blur are0 in this conditional experiment. Native measurement stays Study2×2; larger comparisons do not change scores.
- It is exactly expressible in the existing 23-coefficient shader: rim/core RGB gains all τ, RGB offsets all 1−τ, all 14 light coefficients0.
- The [helper](../reconstruction/neutral_material.py) rejects a record with extra context or reflection terms. No native app or live lab code changes.
- The [frozen case](../reconstruction/studies/mail-toolbar/case.json) records the affine source, pose, masks, glyph placement/provenance and unresolved source/shape assumptions. Source corrections are not accepted material passes.
- The underlying ray profile is a prior and is not calibrated by this smooth background.

From the reconstruction directory, replay a frozen input directory without fitting:

```sh
python neutral_material.py /private/mail/a-canonical studies/mail-toolbar/round/pass-01.json /private/replay
```

Use `--high-quality` for a 1080px-wide export. Canonical vectors: [trash](../reconstruction/studies/mail-toolbar/foreground/trash-outline.svg), [folder trace](../reconstruction/studies/mail-toolbar/foreground/folder-clean-trace.svg), [reply](../reconstruction/studies/mail-toolbar/foreground/reply-outline.svg). The trace uses cubic rounded-corner extents, not exact circular arcs; it is an approximation. Full source/target frames remain private and hash-checked.

Motion and HQ export for the frozen Mail or Safari tab-count inputs: `python neutral_motion.py INPUTS RECORD NEW_OUTPUT`. The helper accepts the two recorded cases, checks matching solid-vector hashes, zero filters and the shared neutral response, and extends only their declared mathematical source field into the illustrative exterior.

It checks every rectangular-crop source query at the HQ grid and each moving pose; no refraction or blur calibration follows from these smooth-source checks.

### Neutral additive playback response

One encoded-RGB affine class represents both the white-mixture and shared additive studies. Apply it after source sampling and before pixel integration and output filtering.

$$
\begin{aligned}
\mathbf C&=\operatorname{clamp}(g\mathbf S+b\mathbf1,0,1),\\
\text{White mixture: }g&=\tau,\qquad b=1-\tau,\\
\text{Shared additive: }g&=1,\qquad b\text{ common to RGB}.
\end{aligned}
$$

All 14 lighting terms are zero. Rim/core gains and bias encode the same shared parameters, not independent channels. Audit clipping separately.

This is empirical grading, not linear-light radiance or evidence of Apple's pipeline.

The next-track case uses the existing dimensionless radial-tail playback map and kernels, a solid white forward-end vector, and two native subpixels per axis. Remove the old play-icon grade; no new map or blur is inferred from the affine sky. [Recipe](../reconstruction/studies/flower-next/round/pass-01.json) · [Case](../reconstruction/studies/flower-next/case.json).

Replay from this directory: `python neutral_affine.py INPUTS RECORD NEW_OUTPUT`. The [helper](../reconstruction/neutral_affine.py) checks the frozen case/vector hashes and tied gain/bias, then produces native scores and the approved iteration preview. Source images remain private.

The [export helper](../reconstruction/settled_export.py) reproduces the1080px still and illustrative source motion from the same circle model: `python settled_export.py INPUTS RECORD NEW_OUTPUT --native-reference NATIVE.npz`. It first checks its native operation order against the saved accepted material/composite arrays, then reevaluates at the larger grid, scales only the output kernel, checks source support and encodes the motion. `--check-native-only` stops after that control.

The source kernel remains in reference coordinates. Internal power-of-two resolution is chosen to reach at least1080px before final downsampling. Optional `--travel` changes source-motion distance in native pixels; `--trim` removes a presentation border after rendering, leaving native scores untouched.

The bag export uses `--travel 4 --trim 1` and the same material/map contract; its estimated quadratic panel does not establish optical transfer. Add `--rim-record RIM_RECORD` to include the shared boundary-normal response, and provide that final render's native arrays for the control.

Finite source support is checked on contributing lens queries and the visible presentation exterior; a trimmed-off border is not treated as visible. This export does not alter native scores.

### Shared neutral rim response

On the fixed NEXT and Safari bag circles, add a neutral boundary-normal response after the existing material and before the unchanged pixel/postfilter integration:

$$
\begin{aligned}
d&=\max(-\operatorname{sd},0),\\
\boldsymbol\ell&=\frac{(1,1)}{\sqrt2},\\
H&=\exp\!\left[-\left(\frac dw\right)^2\right](\mathbf n\cdot\boldsymbol\ell)^2,\\
\mathbf C&=\operatorname{clamp}(\mathbf C_0+aH\mathbf1,0,1).
\end{aligned}
$$

Here n is the unit outward footprint normal and w is measured in units of L. In the crowned-pill extension, the declared boundary coordinate s replaces signedDistance; it is not exact Euclidean distance. The inherited shape, analytic normal and ray map stay fixed, so w is a coordinate width rather than identified physical thickness.

The response has two opposite lobes; it is invariant under n→−n and scales with the footprint. Outside the silhouette, d remains0 and the normal field continues for the fixed postfilter before alpha composition. The source/map/kernel/foreground are unchanged. This is an empirical illumination basis, not Fresnel reflection or an identified environment.

Neither smooth estimated source identifies optics. [Replay](../reconstruction/neutral_rim.py): `python neutral_rim.py INPUTS BASE_RECORD RIM_RECORD NEW_OUTPUT`. Use the corresponding accepted pass03 base record and the shared rim record. For the supported unfiltered crowned-pill export, add `--rim-record RIM_RECORD --native-reference FINAL_NATIVE.npz` to `neutral_motion.py INPUTS BASE_RECORD NEW_OUTPUT`; the source/pixel integration stays fixed and the native control precedes HQ/motion.

Circumference-dependent highlights remain approximate; calibrated strength may differ between references and is not an identified shared lighting environment.
