# Co-designed back: nonconvex solid

**Useful negative.** The current co-designed back cannot use the shared convex-only event solver. Three exact rational chords leave the intended solid. The primary refraction tracer remains valid because its clearance proof does not require convexity.

## Question and frozen geometry

The missing thin bright rim motivates additional reflected paths. Before tracing them, this audit tests the solver's convexity prerequisite. The [co-designed back](../miniplayer-perimeter-inverse-77/README.md), power-eight front, source, material and all existing images remain unchanged.

## Exact polynomial result

| Quantity | Result |
| --- | --- |
| Hermite intervals | 1,024 |
| Intervals with positive second derivative | 291 |
| Exact chord evaluations | 9 |
| Largest reported chord gap | 7.5916151121e-8 original length units |
| Maximum first derivative | 0 |
| Absolute radial second-derivative bound | 2.08450660875 |
| Rays, source queries, images and fits | 0 |

Let the actual lower boundary be the negative of the radial back height. For each saved witness, the chord midpoint lies below that boundary:

$$
\Delta=\frac{B(r_{-})+B(r_{+})}{2}-B\!\left(\frac{r_{-}+r_{+}}{2}\right)>0.
$$

Both chord endpoints belong to the actual back surface. Their midpoint is outside the solid. This directly disproves convexity; it is stronger than a failed sufficient certificate.

The [witnesses](witnesses.json) retain exact numerators and denominators. The [interval record](intervals.json) retains every derivative result. Inputs are exact rational interpretations of the stored binary64 knots, heights and slopes.

## Scope and consequences

This certifies the intended Hermite polynomial, not an enclosure of all floating-point evaluation error. The derivative bound applies inside the profile domain; extension across the silhouette has a crease.

Do not pass this solid to the convex-only intersector. This finding does not invalidate its primary clearance tracer, alter an image, identify Apple's geometry or establish a visible improvement.

The next discriminating task is a first back-reflection-to-front certificate using global directional clearance. It must establish event ordering on these actual surfaces without assuming whole-solid convexity. No reflected radiance or new image is authorized by this audit alone.

## Timing

Numerical analysis finished at 18:01:46 UTC, within the declared ten-minute cap. Documentation was unfinished at the 18:11:45 UTC deadline. Publication is late; the [overrun record](publication-overrun.json) preserves that failure. No additional science ran after the deadline.
