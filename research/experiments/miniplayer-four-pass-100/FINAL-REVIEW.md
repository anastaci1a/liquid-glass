# Four-pass final review

Select **pass three** as the current shared working reconstruction. Four complete passes are finished; dispersion was excluded. Every pass retained contour/refraction, incident blur, color, outline, exterior shadow, artwork and own verification.

[Interactive comparisons](../../../guide/miniplayer-four-pass.md) show all four references, previous/current sliders and native edge details for every pass. The main reconstruction gallery uses the selected third pass.

## Complete-pass comparison

| Pass | Combined category score | Decision |
| --- | ---: | --- |
| 1 | 0.984664 | Held: expanded tone washes out. |
| 2 | 1.037390 | Rejected: yellow becomes orange; compact contour gains unwanted color. |
| 3 | 0.912897 | Selected working compromise: yellow, compact tone and artwork improve. |
| 4 | 0.950851 | Held: wider shadow helps, but complete results regress against pass three. |

The starting proposal is normalized to one. The selected score improves about `8.7%`; this is an equal-category ranking, not an image-error percentage. Category ratios are glass `1.0056`, rim `1.1054`, exterior shadow `0.9564` and artwork `0.5841`. Artwork and compact improvements dominate; average rim error worsens.

## Selected behavior

| Component | Selected setting |
| --- | --- |
| Contour | Smooth shoulder-core family; half-length increases `1.5` native pixels, center shifts left `0.5`; diagonal shoulder inset parameter `0.5`. |
| Physical surfaces | Front and back heights increase `2%`; actual gradients and ordered transport change together. |
| Incident blur | Sigma `6.37875` native pixels, finite radius `20`, before refraction. |
| Body response | Shared original gain/bias plus low-luminance lift `0.08`. |
| Outline | Blurred pre-grade guide, soft channel power `1.75`, two-pixel plateau and two-pixel fade scale. |
| Exterior shadow | Gaussian widths `25/20` pixels, downward offset `7`, opacity `0.23`; clear subrays only. |
| Artwork | Shared centered scale `0.95`, upward shift `3`, absolute corner radius `18` pixels. |

The tip corrections imply about two pixels outward on the left and one on the right. Shape parameters remain shared; only major length differs between expanded and compact. The parameterized contour is a hypothesis, not a subpixel silhouette measurement.

At one fixed expanded yellow sample, target RGB is `255,238,119`; pass three gives approximately `253,236,117`. Other samples retain brightness and feature-placement errors. The response retains color rather than painting a white endpoint over every edge.

## Limits and local failures

Expanded A retains original glass, rim, held, interior, aggregate, SSIM, partial and several foreground failures. Expanded B retains body and several foreground failures. Compact A passes its original comparisons; compact B retains its original partial-boundary failure.

Expanded category scores are worse than the starting proposal; compact scores improve. This working selection uses the approved visual-compromise policy. Full fidelity, full pipeline acceptance and new historical acceptance counts remain false.

Source mosaics remain conditional. The annular environment is hypothetical and later reflected power remains unassigned. No mask, source pixel or accepted historical count was changed. No case-specific optical or color coefficient was introduced.

The wider pass-four shadow improves exterior error but is not transplanted into pass three without another verified composition. Its extra neutral edge increments are rejected. The final model is one complete tested pass, not an untested collection of favorable components.

## Verification and clocks

All sixteen final pre-foreground/completed outputs replay exactly, with exact metrics and original guard decisions. The selected public factory also reproduces all four compositions exactly. Its thirty-two sampled physical paths match retained positions, normals, directions, source coordinates and powers exactly.

Changed blur widths retain exact queried samples rather than full filtered rasters. Original sources and finite-kernel contracts permit separately declared reconstruction.

All changed native maps and finite blur kernels pass required source gates before RGB. Positive full-pixel rim quadrature meets the declared successive-order criterion. This is not a continuous optical-integration or full-radiance certificate.

The ten-hour ceiling was `15:17:24 UTC`, from `05:17:24 UTC`. Stages closed early when their declared questions were answered; no unused time was transferred. Actual starts, deadlines and completion instants remain in each pass and native packet.

## Retained procedural limits

The initial geometry control exceeded its direct-coordinate allowance; its overrun remains disclosed. The first outline control and physical-unit projection failures are preserved. The resumed display reused completed fields and candidates under the original clock.

The first area reference failed convergence before pixel integration; an independent analytic area reference subsequently passed. The first optional diagnostic JSON failed after successful replay because unavailable values were not serializable; a separate supplement preserved null availability.

Passes one and two ranked exploratory full-mask results. They are not held-out validation. A saved-output audit preserves this limitation. Passes three and four exclude held pixels before ranking; all reference images still participate in final visual review.

The exported profile initially copied stale descriptive bounds. Its constructor ignored those fields and recomputed valid bounds during verification. The metadata-only correction preserves every numerical array, original verification and before/after binding; no optical replay was repeated.

## Records

- [Selection](selection.json), [current recipe](../../../reconstruction/families/music-mini-player-working.json) and [starting recipe](starting-family.json).
- [Selected factory replay](selected-verification/result.json) and [metadata binding](selected-verification/metadata-binding.json).
- [Cumulative category ledger](cumulative-ledger.json), [selection audit](selection-audit.json) and [fixed outward shadow profiles](pass3/shadow-profiles.json).
- [Pass one](pass1/README.md), [pass two](pass2/README.md), [pass three](pass3/README.md) and [pass four](pass4/README.md).

Reference assets require Git LFS, indexed evidence restoration and the pinned Python/Cairo dependencies. Original input restoration scripts live in expanded-geometry-02 and compact-geometry-01. As-run drivers are bound to their historical commits and clocks; use a separately declared output directory for reproduction rather than overwriting sealed records.
