# Bounded color contrasts

Incident blur remains before refraction. Interior chroma changes after the existing display grade, at constant linear luminance. A common gamut limit prevents channel clipping.

$$
Y=\boldsymbol{w}^{\mathsf T}\boldsymbol{C},\qquad
\boldsymbol{C}'=Y\boldsymbol{1}+k(\boldsymbol{C}-Y\boldsymbol{1}).
$$

The outline starts with the existing guide-derived endpoint. Its brightness contrast raises each linear channel before a separate peak-preserving encoded chroma expansion.

$$
E'_i=1-(1-E_i)^e,\qquad
M=\max_i\operatorname{encode}(E'_i),\qquad
Q_i=M-s\left(M-\operatorname{encode}(E'_i)\right).
$$

The common chroma factor stops at the first zero channel. White stays white; black receives a neutral lift. The angular gap has exactly zero overlay contribution. This is a bounded display hypothesis, not calibrated radiance.

[Controls](color-controls.json) verify unit bounds, fixed white, zero-overlay identity, interior luminance and opposing angular gaps. Expanded references lead outline ranking; compact transfer remains separately scored.

## Second-pass contrast

Uniform extra exposure over-brightened neutral edges. The next hypothesis scales only that extra exposure by guide chroma. Neutral colors retain the first-pass endpoint; the same rule applies to both sizes and all hues.

$$
c=\begin{cases}
\frac{\max_i G_i-\min_i G_i}{\max_i G_i},&\max_i G_i>0,\\
0,&\max_i G_i=0,
\end{cases}\qquad
e_{\mathrm{effective}}=1+(e-1)c.
$$

[Second controls](color-controls2.json) verify the unchanged neutral response and bounded colored endpoints. The body-grade contrast separately increases gain and reduces the neutral bias; it is not a hue-specific correction.
