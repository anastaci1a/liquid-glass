# Music Search: saved white-feature correspondence

The current lower-return footprint can include lower source lettering, but cannot include the upper white field. This corrects any assumption that the lower return must originate above the circle. The target feature's actual identity remains unknown: transmission, geometry, illumination and source uncertainty are not separated by this diagnostic.

Actual start was 24 October 2026 at 00:53:21.699 UTC. The hard deadline is 01:03:21.699, including documentation and versioning. The Search cycle ceiling remains 04:25:20.608. The baseline was already sealed as `95e876b0`; no earlier budget was reopened. See [protocol](protocol.json), [result](result.json) and [ready flag](review-ready.json).

## Scope and unchanged evidence

This analysis reads the frozen B source, target and known PNGs, retained native paths and samples, and previously saved sections. It performs zero rays, height evaluations, optical RGB remapping, fields, filters, composites, rendered images or fits. Component labels and integer envelope counts are image-plane diagnostics, not adopted source or scoring masks.

The original baseline's assets, geometry, source blur, masks and foreground remain unchanged. Conditional temporal-mosaic availability is not hidden photographic truth. The historical recipe fingerprint mismatch and mask-count ordering deviation remain unresolved historical disclosures. No new pass or input adoption is claimed.

## Uncovered controls and source content

The native diagnostic crop is [1395,560,1635,795]. Both prescribed control strips are known and outside the predicted circle with the existing 1.5-pixel exterior margin. Their minimum circle clearances are 24.3071 pixels on the left and 20.9250 on the right. No registration, line fit or source extension is used.

One fixed criterion selects known pixels whose minimum RGB channel is at least 0.85. Both strips are entirely white on rows 560–612 and have no qualifying white pixels on rows 613–659. Their transition intervals agree between pixel-center rows 612 and 613. This is an observed raster interval within the conditional mosaic, not an inferred physical boundary.

The [source-feature record](source-feature-diagnostic.json) retains each control row's known count, white count and mean RGB. Eight-connected components give one 12,720-pixel upper field with bounds [1395,560,1635,613]. Six lower components contain 2,787 white pixels in rows 701–748, consistent with existing source lettering. No threshold search or glyph recovery was performed.

## Finite footprints and cached samples

Each retained source coordinate has a conservative incident-kernel and bilinear envelope. The integer bounds are:

$$
\begin{aligned}
I_x&=[\lfloor X\rfloor-21,\ \lfloor X\rfloor+22],\\
I_y&=[\lfloor Y\rfloor-21,\ \lfloor Y\rfloor+22].
\end{aligned}
$$

The complete 43-by-43 kernel and four bilinear corners motivate these inclusive bounds. White-pixel counts inside an envelope establish only possible contribution; they do not measure its Gaussian weight or prove target correspondence. All analyzed crop envelopes lie within the diagnostic crop. No out-of-crop pixels were invented.

| Frozen defect crop | Inside rays | Upper field possible | Lower lettering possible |
| --- | ---: | ---: | ---: |
| Upper rim | 14,005 | 13,922 | 0 |
| Left cap | 9,947 | 0 | 3,609 |
| Lower return | 13,314 | 0 | 13,314 |
| Glyph region | 36,864 | 0 | 13,756 |

The lower-return source centers span y=711.369–734.906. Their cached mean RGB is [0.88577,0.64986,0.52411]; none meets the diagnostic white criterion after incident filtering. The target crop has 148 white pixels. Upper-rim source centers span y=610.735–635.262; their cached mean is [0.85415,0.42816,0.28109], while the target crop has 2,569 white pixels.

Those differences do not alone identify missing transmission or a correct tone. The target includes foreground, rim and possible illumination. Complete original guards remain as reported by the baseline. This task introduces no new candidate or score comparison.

## Actual saved sections and distance algebra

The nearest saved horizontal sections lie at normalized y=-0.0014081555, -0.6474755712 and +0.6502772378. The vertical section lies at x=+0.0005130687. These are actual AA offsets, not exact axes. All 1,249 saved section rows are retained; 46 predetermined section samples supply 92 endpoint-line root calculations.

For a retained exit position and direction, the exact source-plane intersection is:

$$
\begin{aligned}
\mathbf{p}&=(p_x,p_y,p_z),\qquad \mathbf{d}=(d_x,d_y,d_z),\\
Y(D)&=c_y+L\left[p_y+(-D-p_z)\frac{d_y}{d_z}\right],\\
\frac{\mathrm{d}Y}{\mathrm{d}D}&=-L\frac{d_y}{d_z},\\
D_*&=\frac{p_y-\frac{y_b-c_y}{L}}{\frac{d_y}{d_z}}-p_z.
\end{aligned}
$$

Here L=89 pixels and the boundary candidates are the measured interval endpoints 612 and 613. The plane must lie below the complete back:

$$
D>h_{\max}=0.10909090909090907.
$$

A stationary vertical exit component has no finite root unless the ray already lies on the line. Negative, shallow and distant roots remain in the record. A conservative finite-kernel mixed band evaluates line offsets of ±22 pixels algebraically; it is not another source map or full support proof.

| Saved section | Vertical transport per L | Selected center-line roots |
| --- | ---: | --- |
| Horizontal center | +0.00506 to +0.01872 pixels | All negative, approximately -12014 to -3192 L |
| Horizontal upper | +6.344 to +8.619 pixels | All negative, -0.4384 to -0.2556 L |
| Horizontal lower | -8.646 to -6.388 pixels | Positive but distant, 13.6203 to 18.6626 L |
| Vertical center | -13.180 to +13.245 pixels | Mixed negative and positive; near-top roots 2.0955–2.1710 L |

The upper section's center rays cannot reach the upper boundary at a valid positive distance, but their finite blur bands already intersect it at D2. A shorter distance moves those source centers upward. Lower-section rays move downward toward existing lettering when distance decreases; reaching the upper field instead requires much larger distances for the selected rays.

The almost-horizontal central transport produces very large signed roots. It must not be interpreted as a precise distance estimate. Every selected root and finite band is saved in [correspondence data](saved-correspondence.json), including negative values and validity labels. No distance grid, alternate whole map or rendered setting was computed.

## Discriminating conclusion and next scope

Propagation distance can alter conditional mixing in opposite directions above and below the center. It cannot be selected from these white landmarks alone. The current lower crop's potential lettering contribution is concrete; assigning the reference lower return to that lettering remains unsupported. A new distance or surface hypothesis is therefore not selected from this record.

An independently established reference-to-source feature correspondence or a constrained illumination account is still needed to identify the cause. No source search is activated. Ordinary blur, color, outline, shadow, foreground and dispersion remain separate pending stages; none is declared absent or solved by this diagnostic.
