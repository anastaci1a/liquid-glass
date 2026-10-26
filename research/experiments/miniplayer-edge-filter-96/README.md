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

## Saved comparisons

- [compact a broad shadow comparison](compact-a-broad-shadow-comparison.png).
- [compact a broad shadow crops](compact-a-broad-shadow-crops.png).
- [compact a f0 comparison](compact-a-f0-comparison.png).
- [compact a f0 crops](compact-a-f0-crops.png).
- [compact a f1 comparison](compact-a-f1-comparison.png).
- [compact a f1 crops](compact-a-f1-crops.png).
- [compact a f2 comparison](compact-a-f2-comparison.png).
- [compact a f2 crops](compact-a-f2-crops.png).
- [compact b broad shadow comparison](compact-b-broad-shadow-comparison.png).
- [compact b broad shadow crops](compact-b-broad-shadow-crops.png).
- [compact b f0 comparison](compact-b-f0-comparison.png).
- [compact b f0 crops](compact-b-f0-crops.png).
- [compact b f1 comparison](compact-b-f1-comparison.png).
- [compact b f1 crops](compact-b-f1-crops.png).
- [compact b f2 comparison](compact-b-f2-comparison.png).
- [compact b f2 crops](compact-b-f2-crops.png).
- [expanded a broad shadow comparison](expanded-a-broad-shadow-comparison.png).
- [expanded a broad shadow crops](expanded-a-broad-shadow-crops.png).
- [expanded a f0 comparison](expanded-a-f0-comparison.png).
- [expanded a f0 crops](expanded-a-f0-crops.png).
- [expanded a f1 comparison](expanded-a-f1-comparison.png).
- [expanded a f1 crops](expanded-a-f1-crops.png).
- [expanded a f2 comparison](expanded-a-f2-comparison.png).
- [expanded a f2 crops](expanded-a-f2-crops.png).
- [expanded b broad shadow comparison](expanded-b-broad-shadow-comparison.png).
- [expanded b broad shadow crops](expanded-b-broad-shadow-crops.png).
- [expanded b f0 comparison](expanded-b-f0-comparison.png).
- [expanded b f0 crops](expanded-b-f0-crops.png).
- [expanded b f1 comparison](expanded-b-f1-comparison.png).
- [expanded b f1 crops](expanded-b-f1-crops.png).
- [expanded b f2 comparison](expanded-b-f2-comparison.png).
- [expanded b f2 crops](expanded-b-f2-crops.png).
