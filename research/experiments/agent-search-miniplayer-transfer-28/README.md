# Shared miniplayer profile on Search: transfer proposal

**Yes: Search can use the same actual front/back profile through a true circular footprint and physical scaling.** This is a proposal for a later conditional observation, not a new Search height solve, renderer, material adoption or fidelity acceptance. No pending bridge code is imported and no optical or height function is evaluated.

## Scope and clock

This read-only task starts at 07:05:14.701 UTC and ends by 07:15:14.701 UTC, including versioning. Search27 remains sealed. Shared geometry, material, sampling and bridge implementations remain root-owned. Implementation and a source-first observation require an agreed immutable root pin.

The canonical front is the selected family spline used by miniplayer18. The back is inverse17's actual positive C1 Hermite profile. Neither is replaced with Search27 coefficients. Canonical profile data and receipts are inspected as metadata only; no profile is evaluated.

## Parameter mapping

Let the family corner radius and the accepted Search radius define the physical scale in their original coordinate units. Search keeps its original normalization rather than pretending it is the family's normalization.

$$
\begin{aligned}
R_F&=1.0043663048754772,\\
R_S&=0.9972124917582454,\\
s&=\frac{R_S}{R_F}=0.9928772868200525,\\
D_S&=sD_F=2.0850423023221105.
\end{aligned}
$$

Back node radii and heights both scale; derivatives remain unchanged. This preserves the same intended polynomial under similarity rather than fitting a new Search profile.

$$
\begin{aligned}
r_{i,S}&=s r_{i,F},&B_{i,S}&=s B_{i,F},&m_{i,S}&=m_{i,F},\\
B_S(r)&=sB_F\!\left(\frac{r}{s}\right),&B'_S(r)&=B'_F\!\left(\frac{r}{s}\right).
\end{aligned}
$$

The front uses the canonical spline in normalized radial coordinate. Prepare the full front function once, then use shared solver front multiplier one; do not apply the half factor or size scale twice.

$$
\begin{aligned}
r&=\sqrt{x^2+y^2},&\rho&=\frac{r}{R_S},\\
F_S(x,y)&=\frac{s}{2}H_F(\rho),&z_f&=F_S,&z_b&=-B_S(r).
\end{aligned}
$$

## Exact gradient and scale semantics

For a general height under physical similarity, height and horizontal coordinates scale together. Its gradient is unchanged at corresponding positions; this is a chain rule, not an independent normal rescaling. Second derivatives scale inversely with size.

$$
\begin{aligned}
h_S(\boldsymbol x)&=s h_F\!\left(\frac{\boldsymbol x}{s}\right),\\
\nabla h_S(\boldsymbol x)&=\nabla h_F\!\left(\frac{\boldsymbol x}{s}\right),\\
\nabla^2h_S(\boldsymbol x)&=\frac{1}{s}\nabla^2h_F\!\left(\frac{\boldsymbol x}{s}\right).
\end{aligned}
$$

For the circular front, the gradient points along the actual radial coordinate. At the center, the profile's exact zero derivative supplies the regular zero gradient.

$$
\nabla F_S=\frac{s}{2R_S}H'_F(\rho)\left(\frac{x}{r},\frac{y}{r}\right),\qquad r>0.
$$

Index 1.5 is unchanged. Height bounds scale by the size factor; slope bounds remain unchanged. Background distance scales with the same geometry. This is the prescribed family similarity, not a fitted change from Search's old distance two.

Changing the footprint from a bar to a circle is not a global similarity of the complete bar. The common profile transfers, but old bar ray coordinates, source support and visible correspondence do not. New circular paths must be traced independently later.

## True circle and core interface

The circular coordinate must be exactly the radial norm divided by the frozen Search radius. The family's finite inner rectangle degenerates to a point. Its minor half-extent 1.012503164339156 is not the family profile radius and must not become Search's circle radius.

Thus the shared transition profile transfers, while the bar's finite flat-core width does not. Exact zero center slope is not permission to insert a finite circular plateau. No rounded capsule, inherited rectangular offset or new core coefficient is proposed.

Both actual height graphs need one shared certified circular coordinate object. It must supply the same radius, gradient convention, membership and boundary semantics to the front and back. The generic independent-front solver requires that shared identity. Root owns the pending bridge; its moving implementation is neither imported nor treated as published.

A future pin must preserve exact edge arithmetic, zero-height crease handling and original field meanings. Regular entry is not complete transmission or source availability. No crease normal, epsilon mask band, normalized-gradient repair or convex-solid wrapper for an unproved Hermite solid is allowed. Use the existing ordered graph solver and actual gradients.

## One proposed common material initialization

The [proposal](proposal.json) freezes one common choice for later review. It transfers canonical family tone and dimensionless incident width, rather than silently adopting Search's separately accepted empirical coefficients. The current selected Search state stays untouched.

| Quantity | Current Search | Proposed transfer |
| --- | --- | --- |
| Encoded common gain | 0.5193880051291454 | 0.596189238519786 |
| Encoded common bias | 0.4473611800152188 | 0.3290237590837732 |
| Incident sigma, native pixels | 6.75 | 6.739785650363237 |
| Explicit finite kernel radius | 21 | 21 |
| Native AA | Original 2-by-2 | Original 2-by-2 |
| Output blur and generated shadow | Zero | Zero |
| Extra primary Fresnel attenuation | Not added | Not added |

Physical native size includes the distinct original length units. The proposed width preserves incident sigma relative to radius, without quarter-bin quantization or a width fit.

$$
\begin{aligned}
a_{\mathrm{pixels}}&=s\frac{89}{88.5}=0.9984867630167759,\\
\sigma_{S,\mathrm{pixels}}&=6.75a_{\mathrm{pixels}}=6.739785650363237,\\
k_{\mathrm{radius}}&=\left\lceil3\sigma_{S,\mathrm{pixels}}\right\rceil=21.
\end{aligned}
$$

Blur remains in the original incident-source domain before refraction; clear exterior remains unfiltered. Source pixels and crops are not scaled or resampled to imitate family inputs. Foreground remains the exact original Search style and ordered compositor, not miniplayer glyphs or artwork.

For one later conditional pair, the single scene proposal is the unchanged miniplayer18 annulus at radiance four, with the same angular support and shoulders. It remains hypothetical and unobserved. Root19's rejected primary-power attenuation is not silently added. Reflection does not receive transmission tone or PSF, and later reflected power stays unassigned.

This is a combined shared-family initialization. A future score change cannot be attributed to geometry alone because the proposed tone and incident-width initialization also differ from selected Search. No alternative coefficient, emitter or width trial is authorized here.

## Required future source and fidelity gates

Original Search pose, accepted radius, masks, original 38-pixel partial cohort, all scored misses, source mosaics, vector and style remain frozen. Historical fingerprint mismatch, receipt/order disclosures, trace authenticity limits and observed confidence zero remain explicit. No source construction or hidden fill is proposed.

Changed actual paths require fresh whole-body and all-original-guard source certification for both references, including foreground/backing dependencies, the full finite kernel and all four bilinear texels. Old miniplayer or Search map proofs do not transfer. Unsupported required input must stop the proposal before RGB.

The shared scalar profile has no photographic authority. Root17's design prior and root18's corrected near-map agreement do not establish Search correspondence. Root18's expanded A partial failure and incomplete reflected scene remain inherited evidence, not waived acceptance criteria.

## Decision

Recommend the common profile mapping and single frozen initialization for interface review. Require a published root pin, a certified circular footprint bridge and a separate one-pair source-first budget before implementation. No optical, height, source, Fresnel, filter, composite, image, fit or next-target work occurs in this task.
