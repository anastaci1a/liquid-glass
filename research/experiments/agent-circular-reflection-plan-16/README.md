# Circular reflected transport: proposal and accounting

**Propose one bounded geometry-and-power audit; the radiance scene remains incomplete.** Axisymmetry permits meridional s/p bookkeeping under stated assumptions. No launches or source arrays were selected here. Execution requires primary review, an immutable combined accounting callback and a fresh explicit budget.

| Evidence | Record |
| --- | --- |
| Actual clock and planning-only limits | [Protocol](protocol.json) |
| Derived future reservations | [Accounting](proposed-accounting.json) |
| Cache manifest entries, without array reads | [Provenance metadata](cache-provenance-metadata.json) |
| New delegate signatures only | [Schema proposal](schema_proposal.py) |
| Twelve synthetic dispatch checks | [Synthetic result](synthetic-result.json) |
| Synthetic harness | [Checks](synthetic_schema.py) |
| Pinned shared implementation | [Optics](../../../reconstruction/geometric_optics.py) |

## Frozen future question

Measure unit path-power fractions reaching conditionally supported downward backdrop endpoints, unsupported downward endpoints, unknown upward/lateral environment, unresolved events and the encounter-cap tail. Keep the current radius-adapted harmonic circle, index 1.5, background distance two, sources, masks, styles and transmission state frozen. This is not a reflection-image proposal.

Incident sigma 6.75 pixels, finite radius 21 and accepted encoded gain/bias remain transmission components. Neither the Gaussian nor encoded response is automatically applied to specular radiance. Missing white rim structure does not authorize a fitted environment, copied halo or new source.

## Deterministic future cache selection

Use only `agent-music-search-baseline-01/native-paths.npz`, bound to its immutable manifest and generator. Both references share its approved geometry and AA phase. Restrict candidates to cached complete regular launches with finite retained entry, back, normal and outgoing fields. Do not recompute a height or a native grid to select them.

For each radial fraction 0.5, 0.7, 0.85 and 0.95, form upper, lower, left and right targets in original-length coordinates using the fixed radius. Choose the cached launch minimizing represented float64 squared Euclidean distance. Break exact ties by smallest row, then column. Selection never uses target RGB, power or source support.

If target labels select the same cache index, retain one launch with all labels; do not search for a substitute. At most 16 unique launches result. Record actual offsets and azimuths; AA samples need not lie exactly on an axis. The prospective selection scan is bounded by 16 times 225,600 cached records; none is inspected now.

Reuse cached initial front and back events, including their actual coordinates, normals, vertical internal direction and primary outgoing direction. Their origin is analytical primary-height tracing, not ordered-root bisection. Initial bracket fields must say unavailable/not applicable; never invent a measured zero bracket. Every newly traced segment retains its actual bracket and residual.

## Meridional invariance and polarization

For the initial noncentral transverse position, define a fixed meridional plane and tangential s direction:

$$
\begin{aligned}
\boldsymbol{e}_r&=\frac{(x_0,y_0,0)}{\sqrt{x_0^2+y_0^2}},\\
\mathcal{M}&=\operatorname{span}(\boldsymbol{e}_r,\boldsymbol{e}_z),\\
\boldsymbol{s}&=\boldsymbol{e}_z\times\boldsymbol{e}_r.
\end{aligned}
$$

The back height depends only on radius, and its gradient is radial. Front normals are axial; cylindrical normals are radial. Therefore each regular active normal lies in this plane. A straight segment, its reflected direction and Snell's transmitted direction remain in that same plane. Ordered line bisection preserves it as well.

The same fixed s direction is perpendicular to every regular propagation direction. Define the p direction from that s and the current direction. Passing through the axis may reverse a radial sign, but does not require changing the meridional plane. Crease normals remain undefined and stop the path.

At normal incidence the plane-of-incidence basis is degenerate, but an isotropic interface has equal s and p reflectances. The retained tangential basis is therefore a valid continuous choice for power bookkeeping. This does not extend to arbitrary three-dimensional geometry, anisotropy, polarization mixing or coherent thin-film interference.

For an initially unpolarized unit weight, separate incoherent components obey

$$
\begin{aligned}
W_{s,0}&=W_{p,0}=\frac12,\\
W_{j,\mathrm{exit}}&=W_{j,\mathrm{in}}(1-R_j),\\
W_{j,\mathrm{continue}}&=W_{j,\mathrm{in}}R_j,\qquad j\in\{s,p\}.
\end{aligned}
$$

Products are accumulated separately before summing. Repeated products of unpolarized averages are not equivalent. This is exact incoherent bookkeeping for the ideal planar-polarization hypothesis; actual polarized environment radiance is still unknown. Later finite-precision plane checks must report residuals without projecting directions or normals to force invariance.

If a numerical event violates the certified plane or regular-normal assumptions, stop that path and retain incoming power as unknown. Do not silently switch to scalar averages or an interval algorithm. A different polarization algorithm would require a separate reviewed contract.

## Prospective ordered events

Count the two cached initial events within the 24-event cap. At each resolved interface use only root `fresnel_components`, `reflect_direction`, `refract` and `next_convex_boundary`, with actual medium order and outward normal. Reuse unchanged initial transmitted directions; do not retrace those events.

The transmitted exterior branch is classified, while one reflected interior continuation proceeds to the next ordered boundary. The shared solver remains at tolerance `1e-11` and at most 64 bisections, without an origin nudge. Actual brackets, winding, critical/TIR status, normals and every endpoint are retained.

TIR or critical grazing has no transmitted replacement. If shared Fresnel and transmission status cannot be reconciled at a numerical critical event, preserve incoming power as unresolved and stop that path. A crease or failed intersection likewise retains its incoming power as unknown. There is no low-power deletion threshold.

After event 24, retain the reflected tail regardless of magnitude. Partition each s/p component into supported downward, unsupported downward, unknown environment, unresolved and tail categories. Report numerical closure error without renormalizing it away. No small residual is assumed before measurement.

At the initial normal front, the symbolic lossless reflectance is

$$
R_{\mathrm{front}}=\left(\frac{1.5-1}{1.5+1}\right)^2=0.04.
$$

That branch alone needs unknown front radiance. Its dimensionless unit-power weight is not a pixel value, a brightness prediction or an upper bound on unobserved HDR illumination. No Fresnel function was called to obtain this symbolic expression.

## Downward endpoint roles and support

A downward exterior direction can intersect the frozen background plane only at positive distance:

$$
t=\frac{-D-z_{\mathrm{exit}}}{d_z},\qquad d_z<0,\quad t>0.
$$

Classify each such endpoint against both conditional mosaics, even when its weight is small. Upward, lateral or invalid-plane branches retain unknown scene roles. The two-dimensional case does not establish other objects, occlusion or environmental radiance along those branches.

Use two separately labeled availability roles: unfiltered backdrop support at all four bilinear corners, and incident-compatible support for the complete radius-21 finite footprint at those corners. The second is a conservative transmission-material compatibility diagnostic. It does not license applying the transmission PSF or encoded tone to reflected radiance.

Reuse `known` and `incident_known` only from the exact retained support containers, with matching source/known hashes, dimensions, binary-mask semantics, 43-square erosion, constant-zero border and kernel radius. The generator and container digests are recorded without opening arrays here. If any prerequisite fails, stop before future transport rather than constructing a new mask or source.

For unchanged primary endpoints only, reuse the exact previous primary proof after identity checks. Every secondary endpoint needs a new audit. Bounds failures or unknown corners are recorded as unsupported; no coordinate clamp, inpainting or domain extension is permitted. Conditional temporal-mosaic availability never establishes hidden photographic truth.

## Derived future budget

With 16 launches and 24 total events, there are at most 352 new ordered segments. Each needs at most 67 level calls: initial boundary, outer bracket, 64 bisections and final evaluation.

$$
\begin{aligned}
S&=16(24-2)=352,\\
L_{\mathrm{level}}&=67S=23584,\\
Q_{\mathrm{geometry}}&=5L_{\mathrm{level}}+6S=120032.
\end{aligned}
$$

Each level call counts itself, radius height, base height, bevel and harmonic delegates. Each segment adds the nonsmooth wrapper and its four height delegates, plus the solver interface. Initial cached events add no new intersection. Setup allows six constructor/property units for one shared solid and base.

| Proposed future operation | Upper count |
| --- | ---: |
| Total interface events, including cached initial events | 384 |
| New segment calls | 352 |
| Fresnel component rows | 384 |
| Reflection vector rows | 384 |
| New refraction vector rows | 352 |
| Nested total, including six setup units | 121,158 |
| Closed-level subset | 23,584 |
| Per-launch nested bound, excluding shared setup | 7,572 |
| Per-launch level bound | 1,474 |

The old 100,000 nested cap is insufficient for this proposal. A future authority must explicitly approve the derived new budget; no old ledger is reset. Metadata/power bookkeeping is separately bounded by 384 event records and 1,536 s/p component products. The shared-level subset is already included in the nested total.

At most 368 possible exterior background endpoints give 736 per-reference endpoint checks. Four raw and four retained-eroded corners require at most 5,888 mask lookups, plus 32 optional primary-proof bit checks: reserve 5,920 actual mask lookups. The corresponding finite envelope covers at most 5,443,456 logical corner/kernel texels; those are not actual lookups under certified erosion reuse.

No new erosion, source field or RGB is proposed. The two new schema entries use matched three-component vectors for reflection and one-dimensional cosine rows with scalar indices for Fresnel. Pinned source has no additional shared delegates inside those functions. `fresnel_unpolarized` is intentionally rejected. Twelve synthetic fixtures validate these additions without importing shared optics or installing a profiler.

## Missing inputs and review gate

Observed front/environment radiance, reflected-branch material response, actual polarization and full scene geometry remain missing. The native cache does not contain ordered secondary paths or their brackets. The next audit can measure model power and conditional endpoint availability; it cannot render missing radiance or establish Apple fidelity.

All previous Search and instrumentation evidence remains sealed. The block runs from 03:18:48.333 to 03:28:48.333 UTC on 24 October 2026, including checks and versioning. Primary review must approve the coherent protocol, combined instrument pin and new explicit reservations before any future ray execution.
