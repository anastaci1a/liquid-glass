# Broad direct-front light cannot repair the frozen rim

A uniform white upper environment at the existing emitter peak washes out the body and fails all four references. Thousands of original rim pixels remain above its computed direct-front envelope. Rearranging angular light bounded by that same peak cannot repair those pixels with the frozen primary signal and geometry.

| Reference | Working E | Uniform-light E | Original full-coverage rim pixels above envelope | Above by more than one level |
| --- | ---: | ---: | ---: | ---: |
| expanded A | 7.883487 | 30.213772 | 3094 / 45750 | 2996 |
| expanded B | 6.149430 | 21.192590 | 3333 / 45750 | 2775 |
| compact A | 20.531876 | 24.124779 | 9232 / 31753 | 8687 |
| compact B | 19.681863 | 23.190595 | 8853 / 31753 | 8313 |

Every candidate fails original glass, rim, held, interior, E, SSIM and several foreground guards. All clipping counts are zero. Original partial-boundary pixels remain scored; the full-coverage envelope cohort is an additional diagnostic, not a changed mask or waiver.

## Bound and scope

Primary transmission and material are frozen. Each direct-front reflected direction samples an assumed nonnegative environment bounded by radiance 4. The uniform scene attains the largest permitted contribution at every retained direction simultaneously.

$$
\begin{aligned}
0\leq L_{\mathrm{environment}}(\boldsymbol\omega)&\leq4,\\
\boldsymbol L_j
&=T_j\mathcal D\left(g_0\boldsymbol S_j+b_0\boldsymbol1\right)
+R_{0,j}L_{\mathrm{environment}}(\boldsymbol\omega_j)\boldsymbol1,\\
\boldsymbol U_p
&=\frac{1}{4}\sum_{j\in p}
\operatorname{clip}_{[0,1]}\mathcal E\left[
T_j\mathcal D\left(g_0\boldsymbol S_j+b_0\boldsymbol1\right)
+4R_{0,j}\boldsymbol1\right].
\end{aligned}
$$

The encoder, nonnegative interface weights and original four-subray average are monotone. Actual retained reflected directions all point upward. Thus the computed uniform image bounds direct-front angular rearrangements within this coded operator, with primary signal fixed.

This is floating computation, not a certified rounding interval. Counts above one eight-bit level are separate advisory diagnostics, not acceptance tolerances. The radiance cap is an existing hypothetical scene parameter, not a measured reference value. Unknown later reflections, brighter environments, other material responses and changed surfaces lie outside the bound.

## Visible evidence

| Reference | Whole reference / working / uniform scene | Original-coordinate crops at 2× |
| --- | --- | --- |
| expanded A | [Comparison](expanded-a-comparison.png) | [Crops](expanded-a-crops.png) |
| expanded B | [Comparison](expanded-b-comparison.png) | [Crops](expanded-b-crops.png) |
| compact A | [Comparison](compact-a-comparison.png) | [Crops](compact-a-crops.png) |
| compact B | [Comparison](compact-b-comparison.png) | [Crops](compact-b-crops.png) |

All four whole comparisons were inspected. Expanded B's light body becomes nearly white, while compact still lacks the correct thin peaks and source returns. Enlarging the angular support brightens broad regions instead of isolating the observed rim. No new environment is selected.

The [fixed sections73](../miniplayer-rim-observation-73/README.md) locate distinct rim peaks and ordinary backing transitions. The largest remaining channel excess above this envelope reaches 69.56, 28.04, 93.40 and 92.19 levels across the four references. It does not uniquely identify reflection or prove a particular replacement surface.

## Frozen stages and controls

Actual18 paths, normals, primary Fresnel power and direct-front power remain unchanged. Incident sigma6.75/radius21 stays before refraction. Working20 gain/bias, source bytes, pose, masks, foreground, AA2 and shadow zero remain fixed. Compact differs only in major length. Later reflected power is still unassigned.

Four pre-foreground and complete identities pass before any candidate. First/last original input, cache and code hashes match. Finite source support transfers for unchanged queries and kernels; no new source is sampled or completed. Conditional mosaics are not hidden photographic truth.

## Clock and accounting

The [protocol](protocol.json) starts at 15:27:27.070 UTC, with checkpoint due 15:32:27.070 and hard end 15:47:27.070. The checkpoint passes at 15:27:31.583. [Results](result.json) retain all original/current guards, envelope cohorts and original numerical comparisons.

Each cached reflectance/direction and old angular-signal inspection covers 1487085 points. Candidate/identity composites total four each. Four score calls use twenty SSIM Gaussians and four metric erosions; envelope observations total 631846 pixels. Original mask construction covers 1121600 pixels. No new ray, Fresnel calculation, source query, optical field, filter or fit runs.

## Three-scene review

[Finite scenes66](../miniplayer-working-finite-light-66/README.md) and this uniform scene all fail family guards. The latter also bounds every angular rearrangement under the same direct-front peak. No fourth emitter placement or intensity fit follows. Actual rim geometry, missing later transport and material/source ambiguity remain separate unresolved questions.

The selected working family, historical baselines and acceptance counts are unchanged. Pre-foreground, completed and coverage arrays, exact recipes, fixed crops and every failure remain archived.
