# Active colored slider: geometry intake

Status: intake complete; conditional proposal awaits primary ownership and interface review. No new fit, optical trace, rendering or source construction was performed. The active green slider remains suitable for testing a declared modeled-input hypothesis. It cannot establish recovered hidden imagery or uniquely identify Apple's surface.

## Reference and preservation

| Item | Frozen evidence |
| --- | --- |
| A | Apple details video, 9.4 seconds, frame 564; green track. |
| B | Same video, 10.5 seconds, frame 630; gray transition track. |
| Input | Explicit symmetric track estimate from exposed contours and colors; distant observed pixels retained. |
| Confidence | Defined support is one, but hidden whole-body and scored historical queries have observed confidence zero. |
| Incumbent | Historical review 09, E 14.0759353 / 15.3170726; separate primary verification establishes acceptance. |
| Counts | Historical 24 paired checkpoints and review rounds remain preserved. This intake adds zero passes. |
| Foreground | Both cases declare no foreground boxes or layers; inspected reference panels show no glyph or artwork on this thumb. |

All eight source, target, defined and observed PNG objects were decompressed and their hashes verified against the evidence index. This read-only check did not infer source truth. [Evidence manifest](evidence-manifest.json) and [frozen records](frozen-records.json) identify the original bytes. No source search or donor registration was started.

A and B have different positions, sizes and transition colors. Equal material state is an assumption, not established by calling them a pair. Original masks and the fixed exterior guard remain authoritative. A future actual surface may have different coverage; every original scored subray still contributes, with misses traveling straight.

## Visible question and previous failures

The historical comparison has a heavy inner dark contour, excess softness, and incorrect colored fringes. Inspect compressed track-edge position, polarity and transition independently of RGB error. Retain the requested left-quarter fade and upper-right cyan observations. Source color, reflection, video processing and ordinary filtering can confound spectral interpretation.

The saved A and B comparisons were viewed directly. No new crop or image was generated. Exact advisory crop rectangles from pass-09-crops.json remain frozen. They are diagnostic regions, not replacement scoring masks.

Three archived reviews were inspected: physical-back-surface, physical-surface-review and physical-two-surface. Prior polynomial back/front, Euclidean-distance, two-interface, actual-index dispersion, and angle/fade trials did not qualify. Their failures are local evidence, not global impossibility. No completed historical probe will be repeated.

## Proposed geometry and interface

Reuse the existing HarmonicCrownedBack, CrownedBevel and crowned_footprint implementations. The accepted footprint has softness 0.08 and a continuous bow. An ordinary rounded rectangle would alter it. Preserve the accepted pose deltas and normalized half-extents for each reference, with a private translation adapter if needed.

Let T be the existing crowned footprint field and H the shared harmonic cap. The proposed solid is:

$$
h_1=d(1-T^{\frac{3}{2}}),\qquad h_2=c\left(1-\frac{x^2}{a^2}\right),\qquad h=H(h_1,h_2),
$$

$$
\Omega=\{(x,y,z):T(x,y)\leq1,\;-h(x,y)\leq z\leq0\}.
$$

One height supplies intersections, full analytic gradients, sections and branch normals. The normalized footprint gradient is not a substitute for the height gradient. Exact tangent and zero-thickness rays remain unresolved. No coordinate warp, independent normal adjustment, painted edge, or inherited empirical displacement enters this proposed model.

The first unfitted prior uses d = 0.15, c = 0.4, refractive index 1.5 and background distance 2L. Here L is each original case's minor half-extent: 216.5 and 200 native pixels. The camera is orthographic, x points right, y down and positive z toward the viewer. Air indices are one.

This is a proposed baseline, not an accepted improvement or proof of Apple geometry. Instantiate the existing concavity, slope and clearance certificates for both poses before sampling. The lead must approve the interface and neutral initial material. No adapter or shared-code modification was implemented during intake.

## Incident blur and finite support

| Quantity | A | B |
| --- | ---: | ---: |
| Historical nominal source sigma, native pixels | 4.3393201194 | 4.0086098100 |
| Historical effective quarter-pixel-bin sigma | 4.25 | 4.00 |
| Proposed incident finite radius | 13 | 12 |
| Original AA | 2 by 2 | 2 by 2 |

The historical shared parameter-length reference is 216.5 pixels. Preserve the element's effective incident widths as initialization. Reuse incident_source_filter with radius ceil(3 sigma), then the shared surface tracer. This explicit finite truncation needs a source-support proof; it is not claimed numerically identical to the old automatic OpenCV kernel.

Keep source filtering before refraction and clear exterior rays unfiltered. The historical output sigma of 2.1642183469 pixels at the reference scale stays archived. Do not add its variance to the source width or claim operator equivalence. Native AA offsets remain minus/plus 0.25 pixels, separate from optical blur.

Before RGB, audit every actual whole-body ray and every subray of all original glass, rim, held, interior, SSIM and exterior guards. Audit the complete incident kernel and all four bilinear texels. Historical changed-map support does not transfer to a new surface. Undefined required samples stop the proposal; masks and source cannot be repaired.

Propose fixed neutral gain one and bias zero for the first physical baseline, with incident blur active. This requires primary agreement. The historical RGB material, independent-normal lighting, directional color smear and reflection approximations remain comparisons. Missing illumination cannot be hidden by resetting score baselines or calling a raw unblurred view the reconstruction.

## Proposed cycle after review

| Stage | Maximum minutes | Required disposition |
| --- | ---: | --- |
| Refraction, including this intake | 80 | Source-limited paired feature correspondence and original guards. |
| Ordinary blur | 20 | Incident operator and compression; AA stays fixed. |
| Color | 20 | Shared response with disclosed source uncertainty. |
| Outline | 60 | Same actual surface; unresolved paths or environment mean incomplete. |
| Shadows and glow | 15 | Generated, source-supported behavior and original exterior guards. |
| Foreground | 20 | Verify declared absence; do not invent a glyph task. |
| Dispersion identification | 10 | Distinguish spectral evidence from source, blur and video effects; blocked if unresolved. |
| Final review | 15 | Independent review, retained failures and next decision. |

The total remains 240 minutes. Charge this intake to the 80-minute refraction allowance; no reset or borrowed time. Absolute later deadlines start only with reviewed ownership and a declared execution schedule. Waiting for review does not create fitting authority.

The proposed first subpass is at most ten minutes, 10,000 checkpoint rays including comparators, and one paired native baseline with zero fitting. Declare the exact counts before execution. Review after at most three substantive hypotheses, including rejects. No microscopic score settlement is proposed.

## Ownership and handoff

The helper owns only this experiment directory and a future private element adapter in the isolated linked worktree. The lead owns shared optics, materials, rendering, acceptance and public integration. Expanded playback, circular play, Navigation and toolbar are outside this assignment.

The proposal was submitted through Sessionsation using the preserved research-lead identity. The receipt is tracked outside Git under the workspace coordination directory. A local queue entry is not delivery or review. No dependent fit begins before primary review. Any explicit user pause overrides continuation.
