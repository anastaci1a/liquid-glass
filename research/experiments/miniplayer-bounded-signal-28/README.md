# Closed-model signal envelopes: body disagreement and missing-light limits

The closed model now has inspectable known-signal envelopes. They retain missing source and untraced reflection power instead of inventing their colors. With the fixed material and scene ceiling, substantial original body regions remain outside the envelopes. These AA2 diagnostics are incomplete and do not establish a reconstructed or accepted image.

## Fixed observation

The [protocol](protocol.json) starts at 08:28:30.774 and ends at 08:58:30.774 UTC. The [checkpoint](checkpoint.json) passed at 08:33:54.364 before native internal segments. Geometry, source, material, incident filter, masks and foreground remain fixed across both lengths.

One shared actual closed surface supplies every intersection and normal. Every original source asset matches its frozen hash before evaluation. Original foreground has fixed alpha/color layers, no response function and no transmission fit. Its positive affine composition preserves the ordering of displayed lower and upper signals.

## Two-interface power

The [shared helper](../../../reconstruction/environment_radiance.py) rotates transmitted polarization intensities into the actual second incidence basis. It handles noncoplanar interfaces without repeatedly averaging scalar unpolarized reflectances. Rotation does not modify any geometric vector.

$$
\begin{aligned}
a_s&=\frac{1-R_{0s}}{2},&a_p&=\frac{1-R_{0p}}{2},\\
b_s&=a_s\cos^2\varphi+a_p\sin^2\varphi,
&b_p&=a_s\sin^2\varphi+a_p\cos^2\varphi,\\
P&=b_s(1-R_{1s})+b_p(1-R_{1p}),\\
W&=b_sR_{1s}+b_pR_{1p},\\
\frac{R_{0s}+R_{0p}}{2}+P+W&=1.
\end{aligned}
$$

An independent three-dimensional coherency-tensor calculation and rigid rotations agree within 2.23e-16 over 108 synthetic vectors, including equal-index and TIR cases. This establishes two-interface intensity weights only. The retained tail is not a post-TIR polarization state for further propagation.

## What is known and unknown

| Contribution | Treatment |
| --- | --- |
| Supported primary background | Existing incident filter, original common material, actual transmission power |
| Unsupported primary background | Material-response range under bounded source RGB; no guessed source value |
| Supported downward front reflection | Raw backdrop, actual first-interface power; no transmission tone or frosting |
| Unsupported downward reflection | Raw source radiance interval from zero to one |
| Upward front reflection | The previously declared conditional annular environment at radiance four |
| Untraced internal reflection | Full retained weight times an assumed radiance range from zero to four |

The finite source and scene ceiling are assumptions of this experiment. They do not bound every possible Apple lighting configuration. The small material-response range pad covers conservative float32 arithmetic; it is not a score tolerance or a guard waiver.

| Member | Primary transmitted samples | TIR samples | Largest retained tail |
| --- | ---: | ---: | ---: |
| Expanded | 885557 | 5291 | 0.956296 |
| Compact | 592570 | 3667 | 0.956317 |

All sampled transmitted primary endpoints have complete incident-kernel and bilinear support in both references. Downward front-reflection support remains incomplete, as recorded [for expanded](expanded-support-BEFORE-RGB.json) and [compact](compact-support-BEFORE-RGB.json). Every actual RGB lookup is supported before sampling; this is not a whole-scene support pass.

## Inspectable envelopes

| Reference | Reference / lower signal / upper signal | Original body pixels outside interval | Relaxed AA2 body RMSE lower bound |
| --- | --- | ---: | ---: |
| Expanded A | [Panel](expanded-a-envelopes.png) | 58672 / 155428 | 22.16596 |
| Expanded B | [Panel](expanded-b-envelopes.png) | 37546 / 155428 | 8.92182 |
| Compact A | [Panel](compact-a-envelopes.png) | 35215 / 83012 | 13.09700 |
| Compact B | [Panel](compact-b-envelopes.png) | 51990 / 83012 | 11.10995 |

The panels preserve full bodies. Neither endpoint is labeled a reconstruction, and no midpoint is generated. The error diagnostic permits independent values inside each channel interval, so lying inside is necessary but insufficient for one globally consistent scene. No E, SSIM, foreground acceptance or reduced-mask score is claimed.

The [grazing quadrature study](../miniplayer-grazing-quadrature-27/README.md) proves that AA2 is unconverged at parts of this closed rim. These are conditional envelopes of the computed ray samples, not certified continuous-image bounds. Geometry solver error, material identification and camera response remain separate limits.

## Work

| Work | Actual |
| --- | ---: |
| Synthetic power fixtures | 108 vectors |
| New internal launches | 1487085 |
| Closed-surface level points | 64835503 |
| Conservative delegate units | 394961358 |
| Native Snell / interface-power points | 2974170 / 2974170 |
| Source endpoint checks | 4484828 |
| Four-corner mask lookups | 17906136 |
| Supported source RGB queries | 4453798 |
| Incident fields / known erosions | 4 / 8 |
| Original constructor mask pixels | 1121600 |
| Displayed lower/upper signals | 8 |

[Input bindings](input-FIRST.json), [result](result.json), [ledger](ledger.json) and retained events preserve all categories. The tensor fixture evaluations are a separate category from native optical inputs. No profile, depth, light, source, material coefficient or scoring epoch is fitted or replaced.

## Decision

The conditional closed shape remains inadequate with this frozen response, and its perimeter still lacks complete scene support. The result does not isolate geometry from material. Preserve the newer completed two-surface working images separately from this incomplete closed-model branch. No accepted count changes.
