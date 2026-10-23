# Compact miniplayer: geometric and material transfer

Status: paired material progress; outline audit closed, remaining stages parked. No parameter was fitted on this control.

## Question

Test the shared geometric surface and frosted-material response on the compact Music playback control. Distinguish central scale, peripheral compression and missing rim light rather than treating depth as uniform zoom.

The two original references are at 2.5 and 2.0 seconds. Artwork, text and symbols remain fixed. Both backgrounds constrain the same parameters; no per-reference material is allowed.

## First geometry

Use the same harmonic height and shared Snell tracer as the expanded control. Preserve the compact control’s accepted smoothed-cap footprint and pose. Intersections, derivatives and sections must use that same surface.

Depth 0.15, longitudinal depth 0.4, index 1.5 and background distance 2 use the frozen minor-half-extent unit of 88.5 native pixels. The cap join is fixed at 0.35 in that unit.

The first raw diagnostic has unit throughput and zero added blur, lighting, grading or shadow. The original foreground/artwork chain follows geometric integration.

## Before RGB

- Verify actual surface gradients, convexity/bounds, circle limit and exact boundary status.
- Check every whole-body and original protected subray, including samples outside the corrected outline.
- Use all four bilinear source texels and retain the original exterior-reference shape.
- Save exact subray and pre-foreground data, dtypes and phase for later zero controls.

## Budget and transfer

[Protocol](protocol.json) records actual clocks and the four-hour maximum. The first checkpoint has 20 minutes, 12,000 height evaluations and 512 fixture rays. One paired raw proposal permits 1,766,400 preflight rays and the same renderer count.

Later stages test the expanded control’s common neutral response and ordinary output PSF without per-control fitting first. Source-space filtering is a separate hypothesis. Geometry, material transfer and visible fidelity are separate claims.

The supported geometric version becomes primary under the [selection policy](../../decisions/primary-geometric-models.md). Historical image fits and failed variants remain evidence.

## Raw result

Both [source preflights](source-preflight.json) pass all 883,200 emitted subrays per reference, including the 30 scored subrays outside the physical outline. No source sample is repaired or omitted.

The [surface checkpoint](geometry-check.json) passes 5,293 height evaluations and 486 fixture rays. Actual-gradient error is below 6.4×10⁻¹¹. The [surface definition](surface.md) explains the frozen join and convexity certificate.

| Raw score | A | B |
| --- | ---: | ---: |
| Legacy material E | 76.71960 | 70.89441 |
| Completed-image E | 76.71303 | 70.89349 |

Both original score masks are preserved. Material-only and completed-image scores remain distinct; neither is ranked against a differently controlled historical fit.

The raw body preserves sharp, strongly colored background content where the reference is frosted and lighter. Bright rim light is missing. These images establish a supported geometric state, not visible parity or measured Apple parameters.

![Second reference and raw geometric baseline](b-raw-comparison.png)

[Native results](raw-result.json) confirm bit-exact coverage, retained-subray replay and original foreground/artwork replay. Exact pre-foreground images and float64 sample/clear data are saved for later stages.

## Material result

Both fixed softness operators improve body metrics but fail foreground guards. Source-space softness is visibly closer in compressed edge texture. Neither operator is accepted alone.

The first full shared colour prior, applied with source-space softness, passes every paired guard. It also improves or ties every guard relative to the source-softness-only control. No backtrack or colour fit was needed.

| Completed-image E | A | B |
| --- | ---: | ---: |
| Raw geometry | 76.71303 | 70.89349 |
| Source softness only | 69.46921 | 61.29849 |
| Source softness + shared colour | 43.57911 | 38.03234 |

The selected material uses source width 6.75 native pixels, common gain 0.701980827595718 and bias 0.22423217000784113. The coefficients are unchanged from the expanded study; the source-space placement is a changed operator convention, not unchanged full-material transfer.

![Second reference and selected geometric material state](b-colour-selected.png)

Frost and colour are visibly closer. The body remains too dark, with missing bright rim and incorrect edge structure. This is material progress within the new geometry, not reference parity or measured radiance.

[Selected state](selected.json), [all colour guards](colour-result.json), [softness failures](blur-result.json), [support proof](blur-support-FIRST.json) and [exact zero controls](colour-zero-controls.json) preserve the scope. All sampled channels remain unclipped.

## Outline and handoff

The [same-surface audit](outline-result.json) uses 1,202 height and 1,204 Fresnel evaluations, with zero rays, RGB queries or images. Back reflectance varies weakly along the long-axis edge.

The front environment is unobserved. Power bounds do not predict encoded image brightness. No supported reflection image or outline improvement is claimed.

Shadow, foreground, dispersion identification and final cycle review remain pending, not skipped. This partial cycle closes under the [current sequence](../../method/refinement-sequence.md).

Historical source width was nominally 6.873701880782254 native pixels, quantized to 6.75 by its quarter-pixel cache. The selected incident width matches that effective seed. Historical output filtering remains separate evidence.
