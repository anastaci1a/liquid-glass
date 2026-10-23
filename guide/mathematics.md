# Mathematical notation

Equations describe stated model hypotheses. Their typography, algebraic validity, numerical implementation and agreement with Apple references are separate checks.

## Conventions

| Notation | Meaning |
| --- | --- |
| Bold lowercase | Vectors, including positions, directions and RGB colors. |
| Bold uppercase | Matrices, or explicitly identified vector-valued maps. |
| Subscripted labels | Components, reference values or named physical roles. |
| Roman differential | Integration measure or total derivative. |
| Nabla | Gradient; the Hessian is written as an explicit matrix operator. |
| RGB multiplication | Componentwise when marked by the Hadamard product. |

Symbols are defined locally. A shape exponent and an empirical strength can use different parameters even when an implementation historically called both `power`.

$$
\begin{aligned}
\nabla f&=\begin{pmatrix}\partial_xf\\\partial_yf\end{pmatrix},&
\operatorname{Hess}f&=\begin{pmatrix}\partial_{xx}f&\partial_{xy}f\\\partial_{yx}f&\partial_{yy}f\end{pmatrix},\\
\mathbf a\odot\mathbf b&=(a_1b_1,a_2b_2,a_3b_3),&
\mathbf a\cdot\mathbf b&=\sum_i a_ib_i.
\end{aligned}
$$

Scalar clipping and powers act componentwise on RGB vectors. A scalar added to RGB is multiplied by the all-ones vector explicitly.

## Code and model symbols

| Implementation field | Mathematical role |
| --- | --- |
| `core`, `depth`, `edge` in the height bevel | Plateau coordinate, sag amplitude and edge thickness. |
| `core`, `edge`, `power` in the illustrative displacement field | Core strength, edge strength and shared multiplier. |
| `cap_normal_gain`, `cap_tangent_fade` | Orientation response of a historical empirical map. |
| `tangent_band`, `tangent` | Band width and tangential strength. |
| `material[0:3]`, `[3:6]`, `[20:23]` | Rim RGB gains, shared RGB bias and core RGB gains. |
| `material[6:20]` | Fourteen scalar illumination coefficients. |

A coefficient slice includes its first index and excludes its last. Code identifiers remain code; equations use mathematical components and labels.

## Filtering units

A Gaussian operator uses the coordinate units of its argument. Normalized widths become pixel widths by the reference scale. The native implementation's finite kernel and boundary rules remain part of its protocol.

$$
\sigma_{\mathrm{pixels}}=L\,\sigma_{\mathrm{normalized}}.
$$

Source filtering and output filtering are distinct operations. Neither notation identifies physical roughness or radiometric scattering by itself.

## Audit scope

The maintained equations use fractions, true subscripts, explicit gradients, aligned relations, vectors and piecewise definitions. Historical reports retain their original scientific notation as archived evidence.

The audit corrected the dimensional description of the context response: a 3-by-3 RGB contraction extends to a 23-by-23 material operator. Renderer code and measured results did not change.

The tangent coupling uses the derivative of the base envelope, not the full orientation-weighted field. Its empirical status remains explicit.

[Detailed disposition](../research/decisions/notation-audit.md) · [Geometric optics](geometric-optics.md) · [Illustrative equations](model.md) · [Historical recipes](recreation-models.md)
