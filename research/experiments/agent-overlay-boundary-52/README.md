# Original partial-pixel diagnosis of the separate outline

The saved failures are concrete changes to already-completed boundary pixels. A white overlay brightens every changed channel. It worsens already-bright backing and can overshoot mixed-color pixels even when another channel needs brightening. The records do not establish a contour displacement, observed coverage or measured outline alpha.

Task 52 started at 20:45:36.666 UTC on 25 October 2026, with deadline 20:55:36.666 UTC including versioning. The header/input checkpoint passed at 20:46:20.453 UTC. Science finished at 20:46:20.742 UTC. The review uses sealed 88 and original inputs from main `6d049e56e5e2f0c773428e0dee7e5584a04dec23`; no merge or shared edit was required.

## Exactly the original cohort

All 76 pixels are retained: 16 per expanded reference and 22 per compact reference. Selection is the unchanged original glass mask intersected with frozen historical coverage below one. Compact uses its original raw coverage archive, not 88 coverage or a new geometric mask. No residual, alpha threshold or result-dependent reselection occurs.

The selected numerical members and target PNG dimensions were checked before decoding. Target access is direct native indexing only, with no resampling, interpolation or new image export. `records.json` retains every native position, frozen coverage, signed distance, saved alpha, target/working 20/working 88 RGB, channel errors and error change.

## Exact partial guard reproduction

| Reference | Pixels | Before RMSE | After RMSE | Worse pixels | Better pixels |
| --- | --- | --- | --- | --- | --- |
| Expanded A |16 |40.326828 |82.505630 |16 |0 |
| Expanded B |16 |26.080431 |18.707460 |12 |4 |
| Compact A |22 |23.813168 |36.654205 |16 |6 |
| Compact B |22 |21.076626 |41.356354 |20 |2 |

Every cohort RMSE matches the sealed 88 scalar record exactly. Expanded B's aggregate partial improvement is carried by four pixels despite twelve local regressions. It does not imply local nonregression. The three rejected partial guards remain rejected; all other old guard results remain unchanged and were not recomputed here.

Expanded A has ten pixels already above the target in all channels; expanded B has twelve. Each compact reference has one such pixel. Most compact errors are therefore mixed-channel cases, rather than a uniformly too-bright grayscale backing. White-only brightening can help one component and harm another.

## Concrete records

At expanded A native (337,463), frozen coverage is 0.75, signed center distance approximately −0.325 native pixels and saved overlay alpha approximately 0.567. The working RGB is approximately (0.712,0.699,0.681), already much brighter than target (0.471,0.463,0.447). Its error necessarily worsens under a positive white addition. This is an already-bright-backing example, not a recovered transparency measurement.

At expanded B native (331,453), coverage is 0.5 and saved alpha approximately 0.488. Working RGB is approximately (0.594,0.594,0.594), while target is approximately (0.910,0.910,0.910). This large improvement helps the aggregate partial guard even though most B partial pixels worsen.

At compact B native (1384,632), frozen coverage is 0.5, signed distance approximately −0.477 and saved alpha approximately 0.532. Working RGB is approximately (0.884,0.653,0.578), while target is approximately (0.973,0.675,0.502). Red needs brightening but blue is already too bright. A white addition cannot independently satisfy those channel demands.

The examples are explanatory members of the complete frozen cohort, not replacement scoring subsets. They illustrate why a single positive overlay can fail boundary guards for different reasons. No coefficients are inferred from them.

## Coverage, placement and composition are distinct

All 76 selected centers have negative signed distance under the actual 88 outline contour. A center being inside does not imply full pixel coverage; these are precisely historical partial pixels. The historical AA2 coverage is a retained numerical sampling field, not measured reference alpha or a demand to multiply the overlay by it again.

The saved outline alpha is already a full-pixel integral. Applying it to a completed mixed pixel changes the existing clear/body mixture through the declared post-completed convention. It is not equivalent to integrating a varying subpixel backing and varying overlay jointly. The following identity explains the selected error behavior without generating another composite:

$$
C_{88}-C_{20}=\bar\alpha(\boldsymbol1-C_{20}).
$$

For channel error and the saved change, the squared-error difference decomposes as:

$$
(C_{88}-T)^2-(C_{20}-T)^2
=2(C_{20}-T)(C_{88}-C_{20})+(C_{88}-C_{20})^2.
$$

An already-positive error necessarily grows under positive white brightening. A negative error may improve or overshoot. This describes the observed completed-pixel effect; it neither estimates physical transmission nor identifies the unique reason the target differs.

The selected pixels lie on cap arcs. Their old coverage and new signed distances reference different retained numerical conventions, especially in compact's corrected footprint. A placement error remains possible, but neither a negative distance nor the brightness mismatch proves it. No reference contour was newly measured, and no pose/width adjustment is justified by this review alone.

## Concrete next question

Before another parameter trial, determine whether the intended display-overlay semantics are the declared post-completed-pixel operation or a jointly integrated overlay over a spatially varying frozen backing.

A discriminator needs legitimate retained subpixel backing and matched integration support; it cannot be fabricated by subtracting foreground or inventing samples. This is a proposed composition question only, not authority to change implementation or masks.

Preserve all original partial guards while reviewing that prerequisite. No width, pose, opacity, color, source or geometry is adjusted here. The data already show that an all-around white contribution cannot be accepted merely because most aggregate scores improve.

## Accounting and checks

| Work | Actual |
| --- | --- |
| Decoded numerical payload |49518400 bytes |
| Target native pixels decoded |8294400 |
| Selected scalar observations reserved |7296 |
| NPY headers |2816 bytes |
| Original mask/coverage selection cells |1121600 |
| Selected pixels |76 |
| Optical/source/integration/composite/filter/image/fit operations |0 |

The selected-observation reservation is 96 scalar entries per pixel, covering recorded values, distance algebra and error summaries. The unavoidable full saved mask/coverage selection is separately disclosed. There are no Study constructors, new mask constructions, image resampling or original full-image score calls. Target decoding stays below nine million pixels; numeric payload stays below 128 MiB.

First/last hashes and immutable 88 input bindings are retained. Only this new folder is staged, and task 46 remains untouched. The diagnosis was sent through Sessionsation before packaging. Original masks, body, selected models, failed guards and historical evidence are preserved.
