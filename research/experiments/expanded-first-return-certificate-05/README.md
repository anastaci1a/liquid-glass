# Expanded spline: first reflected return certificate

**The unchanged intended surface has a certified next-front first return.** A global curvature bound excludes an earlier back hit for every regular initial back reflection. No convex-solid assumption, new ray, normal calculation, Fresnel call, source query, fit or image is used.

This is an analytic intended-surface certificate. It is not a globally interval-verified floating-point implementation, a complete multi-bounce path or a radiance result. Selected images and the earlier sampled audit remain unchanged.

| Evidence | Record |
| --- | --- |
| Declared hypothesis, clock and limits | [Protocol](protocol.json) |
| Exact coefficient arithmetic | [Derivation](derive.py) |
| Rational bounds, source hashes and transfer scope | [Result](result.json) |
| Intended-surface versus numerical transfer | [Precision scope](precision-scope.json) |
| Earlier partial next-front audit | [Original audit](../expanded-outline-role-04/README.md) |
| Accepted geometry and tone | [Selection](../expanded-contrast-guard-02/README.md) |

## Same surface, bounded derivatives

The selected height is the fixed clamped cubic spline composed with distance to the fixed inner rectangle. The corner join width is zero. Heights, breaks, radius, pose and every nuisance stage remain frozen.

$$
\begin{aligned}
\rho(\mathbf{x})&=\frac{\operatorname{dist}(\mathbf{x},Q)}{R},\\
h(\mathbf{x})&=f(\rho(\mathbf{x})),\qquad 0\le\rho\le1,\\
f'(0)&=0,\qquad f(1)=0.
\end{aligned}
$$

Here Q is the fixed inner rectangle. The exact center derivative follows from equal first two spline controls. The clamped endpoint interpolates the zero final height control.

For degree-three knots and height controls, derivative coefficients are

$$
\begin{aligned}
d_i&=\frac{3(c_{i+1}-c_i)}{t_{i+4}-t_{i+1}},\\
e_i&=\frac{2(d_{i+1}-d_i)}{t_{i+4}-t_{i+2}}.
\end{aligned}
$$

Nonnegative B-spline bases give convex-hull bounds on each derivative. The calculation treats stored binary64 coefficients and knots as exact rational inputs. Conservative dyadic upward rounding is applied only to certificate constants, never to geometry or scoring.

$$
\begin{aligned}
|f'|&\le\max_i|d_i|,\\
|f''|&\le\max_i|e_i|,\\
\|\nabla h\|&\le M,\\
\operatorname{Lip}_{\Omega}(\nabla h)&\le K
=\frac{\max_i|e_i|}{R^2}.
\end{aligned}
$$

The gradient Lipschitz bound is on the closed footprint, not across its zero extension. Within each rectangle/corner region, the Hessian eigenvalues are bounded by the radial second derivative and tangential first derivative divided by radius. The latter is bounded by the former because the center derivative is zero.

Gradients agree across the piecewise coordinate joins. Bounded piecewise Hessians therefore give the stated Lipschitz gradient on the convex footprint, despite second-derivative jumps. No concavity of the selected back is assumed.

## First-return clearance

Let the initial regular back point lie below the flat front. Reflection of the vertical internal ray about the normal from that same height gives

$$
\begin{aligned}
\boldsymbol{a}&=\nabla h(\mathbf{x}_0),\qquad s^2=\|\boldsymbol{a}\|^2,\\
\mathbf{r}_{xy}&=\frac{2\boldsymbol{a}}{1+s^2},\\
r_z&=\frac{1-s^2}{1+s^2},\\
G(t)&=z(t)+h(\mathbf{x}(t)),\\
G(0)&=0,\qquad G'(0)=1.
\end{aligned}
$$

The last identity is specific to the initial vertical incidence and exact surface normal. It is not an independently adjusted normal or a reusable assumption for later bounces.

Using the same curvature bound until the footprint boundary,

$$
G(t)\ge t\left(1-\frac{K\|\mathbf{r}_{xy}\|^2t}{2}\right).
$$

Since the slope bound is below one, the reflected ray points upward. Its time to the front has the following uniform bounds:

$$
\begin{aligned}
v_{z,\min}&=\frac{1-M^2}{1+M^2},\\
v_{xy,\max}^{2}&=\frac{4M^2}{(1+M^2)^2},\\
T_{\max}&=\frac{H}{v_{z,\min}},\\
\eta&=1-\frac{Kv_{xy,\max}^{2}T_{\max}}{2}>0.
\end{aligned}
$$

| Bound | Conservative value |
| --- | ---: |
| Maximum height | 0.138181920263 |
| Slope upper bound | 0.672341456609 |
| Gradient Lipschitz upper bound | 2.891448712183 |
| Front-return time upper bound | 0.366171264040 |
| Clearance-factor lower bound | 0.546005539162 |

The clearance stays positive before the front. A first footprint exit below the front would have zero height and negative clearance, contradicting this bound. Thus neither the back nor footprint boundary is reached first; the next interface is the flat front.

This proves one event order for all regular initial reflections of this intended surface. It does not provide a generic nonconvex intersector or certify the next back event after another front reflection.

## Relation to the preserved sampled audit

The old audit certified 800,823 first-front encounters using a weaker slope cone and left 90,025 next events unresolved. Its measured first-front TIR/critical count was 72,808. Those as-run records are immutable.

For an old cone-unresolved unit direction, its positive vertical component obeys

$$
\begin{aligned}
r_z&\le M\|\mathbf{r}_{xy}\|+\delta\le M+\delta,\\
(M+\delta)^2&<1-\frac{1}{n^2},\qquad n=1.5.
\end{aligned}
$$

The margin is the old numerical cone threshold, not a scoring allowance. Once the actual next front is established analytically, these formerly unclassified directions lie in its TIR region. Conditional on transferring the saved cone cohorts to the intended-surface model, the predicted count is

$$
72{,}808+90{,}025=162{,}833.
$$

This is a conditional analytic transfer, not a new ray or Fresnel measurement. No global interval enclosure has established that cohort transfer for every floating-point normal. It does not rewrite the old unresolved status, claim globally certified floating-point propagation or alter any color/power array. The old unresolved power remains retained; no environment color or low-power deletion is introduced.

## Numerical and scene limits

The rational inequalities certify the intended real spline defined by the stored inputs. They do not enclose every floating-point basis evaluation, normal normalization or reflected vector operation. The positive separation margin is reported, but no unproved global numerical error bound is substituted for an implementation certificate.

Observed environment radiance remains unavailable. Even an established first interface does not supply its illumination. Later internal returns, secondary source footprints, polarization through general three-dimensional paths and physical material interpretation remain separate questions.

This reusable sufficient condition can apply to other flat-front height families with valid height, slope and gradient-Lipschitz bounds. Failure of the inequality would be inconclusive. It does not justify changing a surface to satisfy the certificate.

## Work and decision

The block derives 33 scalar entries, including ten first-derivative and nine second-derivative controls. It imports no optical, spline-evaluation or image library. Source hashes match before and after. No native or target array is opened.

Retain this as a useful analytic advance. No selected-model pass, image improvement, source adoption or full radiance acceptance follows. A later implementation can consume the certificate under an explicit numerical contract; this task makes no shared code change.
