# Finite edge filter and broader shadow

Three fixed filter endpoints preserve color and lift black. Their black endpoints are dark gray, approximately 0.19–0.28 encoded intensity. The strongest proposal reduces expanded A's over-bright outline but weakens compact rim contrast. No shared qualifier is found. This motivates the explicitly separate light-gray endpoint test in study97, not an unrecorded extra coefficient here.

The spatial field from study94 is unchanged. Exposure, lift and desaturation vary with that field; the operator does not interpolate toward a pure white image. Input white remains a fixed point, and nonwhite peaks remain below white.

$$
\begin{aligned}
e(\alpha)&=1+(e_1-1)\alpha,&b(\alpha)&=b_1\alpha,&s(\alpha)&=s_1\alpha,\\
p'&=\frac{p+b}{p+b+\frac{1-p}{e}},\\
\boldsymbol C'&=p'\left[(1-s)\boldsymbol n+s\boldsymbol 1\right].
\end{aligned}
$$

Here the input is decoded to linear light; the color direction divides by its largest channel. Black uses a neutral direction. The output is encoded without clipping. This is a display-filter hypothesis, not identified physical radiance.

A separate shadow uses width 32 pixels, exponent 1.5 and strength 0.08. It acts only on clear AA subrays and leaves all lens samples unchanged. Both compact references improve every guard against the preceding combined94 proposal. Expanded boundary/body conflicts remain; no original family acceptance follows.

The original exact-white control exposed sRGB roundoff before any bitmap decode. An explicit exact-white fixed point repaired the operator. The first driver, filter, counters and failure remain preserved; all repeated controls are counted and the original deadline is unchanged.

[Results](result.json), [response controls](response-controls.json), [protocol](protocol.json) and [ledger](ledger.json) retain all sixteen candidates. No new ray, source query, optical field or fit ran.
