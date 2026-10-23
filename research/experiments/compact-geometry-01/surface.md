# Frozen smoothed-cap surface

The compact control reuses the harmonic height law. Its accepted contour requires a smoothed capsule coordinate; changing that coordinate would change the silhouette.

## Footprint

The fixed reference length is 88.5 native pixels. Let the normalized half-extents be the recorded major and minor extents, with join width 0.35. Define:

$$
u(s)=\operatorname{clip}\left(\frac{s+w}{2w},0,1\right),\qquad
q_w(s)=
\begin{cases}
0,&s\leq-w,\\
w\left(2u(s)^3-u(s)^4\right),&-w<s<w,\\
s,&s\geq w.
\end{cases}
$$

The actual footprint coordinate is:

$$
\rho(x,y)=\frac{\sqrt{q_w\!\left(|x|-(a-b)\right)^2+y^2}}{b}.
$$

This is an implicit boundary coordinate, not Euclidean distance to the boundary. It is exactly the frozen smoothing used by the accepted contour.

## Height and normals

$$
h_1=d(1-\rho^p),\qquad
h_2=c\left(1-\frac{x^2}{a^2}\right),\qquad
h=\frac{h_1h_2}{h_1+h_2}.
$$

The solid lies between the flat front and this back:

$$
\Omega=\{(x,y,z):\rho\leq1,\;-h(x,y)\leq z\leq0\}.
$$

Both interface derivatives come from the height itself:

$$
\nabla h=
\frac{h_2^2}{(h_1+h_2)^2}\nabla h_1+
\frac{h_1^2}{(h_1+h_2)^2}\nabla h_2,\qquad
\mathbf n_{\mathrm{back}}=
\frac{(-\partial_xh,-\partial_yh,-1)}{\sqrt{1+\|\nabla h\|^2}}.
$$

The zero-height crease has no unique transmitted path. Exact poles remain unresolved; no replacement normal or sampled pixel is supplied.

## Certificate

Inside the smoothing interval:

$$
q_w'=u^2(3-2u),\qquad
q_w''=\frac{3u(1-u)}{w},\qquad
0\leq q_w'\leq1,\quad q_w''\geq0.
$$

Thus the footprint coordinate is convex. Both nonnegative heights are concave on the footprint; their harmonic composition is concave and nondecreasing in either input.

$$
h\leq\frac{dc}{d+c},\qquad
\|\nabla h\|\leq\max\left(\frac{pd}{b},\frac{2c}{a}\right).
$$

These bounds satisfy the shared primary tracer’s subcritical-slope and background-clearance requirements. The background plane is two reference lengths behind the flat front; refractive index 1.5 is a declared hypothesis.

[Checkpoint results](geometry-check.json) cover actual derivatives, footprint equality, mirror symmetry, unit-index identity and pole status. The true circular fixture removes the join and uses the shared radial quadratic; it matches the circular harmonic surface.
