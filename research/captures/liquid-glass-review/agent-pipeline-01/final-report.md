# Expanded Miniplayer pipeline 01: final review

The experimental model does not replace historical public pass 03. Its final E is 49.127159783974385 for A and 19.81850988475171 for B, versus historical values of 5.388044996117163 and 3.1168641397713484. Primary independently accepted ordinary blur and neutral grading as incremental component results. Refraction fidelity and the complete model were not accepted. Research is complete and stopped.

## Frozen inputs and ownership

The private branch is research/agent-expanded-pipeline-222 in ../localica-agent-expanded-pipeline, based on commit 665171506829f42a278e4a74467f07ee4370b9f3. The helper added only its own expanded_surface.py adapter. Root owns shared optics, rendering and material APIs, independent verification, and public integration. The helper made no public edits, commits, pushes, media or app changes.

Evidence is under dark-glass-lab/extended/agent-pipeline-01. Source, target, confidence, canonical case, vector and artwork hashes remain unchanged. Each reference retains 155,428 glass pixels, 45,766 rim pixels, 38,118 held pixels and 46,409 exterior pixels. All ten foreground and artwork guards remain active.

## Stage results

| Stage | Work and outcome |
| --- | --- |
| Inspection | Reused the Music references at 0 and 6.033 seconds and the current historical pass 03 inputs. No source search or fallback was needed. |
| Refraction | Tested three families through eight full native observations: the harmonic back surface, a closer background at D = 0.5, and profile powers 4 and 5. Whole-shape and original guard source proofs checked all four contributing bilinear texels. Alternatives traded improvement between references; none qualified. |
| Ordinary blur | Tested the shared coverage-normalized output Gaussian at 4, 6.75 and 9 native pixels. Selected 6.75 pixels for text detail rather than minimum aggregate error. Shape coverage, clear underlay and foreground stayed fixed. Primary accepted this incremental result. |
| Color | Tested one common affine response with all RGB channels tied. The full least-squares step failed B artwork and artist guards. The half-step, g = 0.701980827595718 and b = 0.22423217000784113, passed every original paired guard and was independently accepted. It is empirical encoded-color grading, not a radiance model. |
| Outline | Stopped at the first failed invariant: two zero-height endpoint checkpoints had been classified as regular. All 890,848 native whole-shape samples had positive height. No reflected image was produced. A separate bounded analysis established conditional Fresnel and scene-support limits, not complete radiance. |
| Shadows | All three fixed opacity trials failed B glass, rim, held and E guards despite improving exterior error. All 16 partial-coverage glass pixels were retained. No new shadow or glow was accepted. |
| Foreground | A common opaque gray was unsupported. One shared black-opacity candidate improved B but failed A artist, core and edge measurements. Original vectors, artwork and styles remain unchanged. No font search was performed. |
| Dispersion | B text and lower-edge target pixels are achromatic. Weak upper-B chroma was retained in the diagnosis, while A source colors and incorrect returned features confound attribution. No independently supported spectral direction was identified. Dispersion modeling is not applicable on the available evidence; no spectral fit or image was produced. |

## Geometry, source and path limits

The final prototype uses the H1 harmonic back surface and flat front, with orthographic viewing, air/lens/air indices 1/1.5/1, depths 0.15 and 0.4, and background distance D = 2. These lengths use the frozen nominal reference L0 = 88.5 native pixels. The fitted footprint has an actual minor half-extent of 89.60653 pixels. final-review/units.json records the equivalent normalization by that actual extent. This is a unit conversion, not a geometry change or evidence of identical physical dimensions across controls.

One actual height function supplies surface gradients, sections and Snell normals. There is no empirical coordinate warp or independent normal correction. The temporal source mosaic is a frozen input contract, not proof of hidden photographic content. Unsupported unscored exterior remains NaN or transparent; it was never filled from the target or extended.

The original 101 by 41 checkpoints mislabeled two exact zero-height long-axis poles as regular. At those points, rho was 0.9999999999999998 and height was zero. The failed packets remain preserved. The corrected interpretation has 3,789 regular points and 176 crease points. No native grid sample had zero height, so this does not establish a change to saved native pixels or scores.

Root subsequently committed the path-status guard dbff69f0, with core SHA beginning a48224f4. It marks inside zero-height rays unresolved and rejects invalid heights. The helper did not restart the expired outline checkpoint, patch normals, clamp heights or claim repaired-as-run evidence. This is a safety correction, not optical progress.

## Visible limitations

The XY footprint is an ordinary rounded rectangle with flat central top and bottom intervals. It does not implement Ana’s subtle outward pill bow. Longitudinal back-surface curvature does not satisfy that separate silhouette requirement.

The lower colored return in A has incorrect correspondence. Bright rim illumination and parts of the body remain missing. Reflected-path environment and camera response are unobserved. Ordinary frosting cannot repair the refraction map. The shared foreground-opacity trial was rejected because improvement on B did not justify regression on A. Original SF outlines are genuine, but exact Apple UI weight and layout remain unproven.

Edge reversal is desired where the reference supports it. Its location, extent and transition must be compared to the reference; absence of folds is not an objective. Equality with the circle fixture is mathematical implementation evidence, not visual transfer acceptance. Conditional Fresnel bounds do not identify Apple's lighting or HDR pipeline. Dielectric conventions are described in the [PBRT reflection and transmission reference](https://pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission).

## Timing and protocol deviations

schedule.json preserves actual stage timings and the earlier nominal schedule. Allocations were wall-clock caps, not minimum waiting periods. Early closure did not extend subsequent stages. Dispersion was marked not applicable from this element's own reference audit, shortening the nominal latest deadline by 15 minutes to 11:42:35 UTC. Actual completed audit timings remain unchanged.

Two administrative overruns are explicit. Shadow arrays and the report were complete at 09:06:03 UTC, before the 09:07:54 cap, but the transition record was 44.523 seconds late. No additional shadow trial or packaging occurred after the cap. The final audit and main report were complete by 09:49:27 UTC, but metadata and handoff finished at 09:51:15.977, which was 68.56 seconds after the 09:50:07.417 final-review cap. A failed tool serialization preceded that delay. This was a protocol overrun, not compliant completion. No rays, renders, fits or new scientific results ran after the cap.

## Evidence and reproduction

Primary acceptance is recorded in primary-stage-acceptance.json and in playback-pipeline-01/peer-expanded/verification.json and blur-guards.json. Primary verified exact native material and composite arrays, including NaN support, exact scores, all ten foreground/artwork guards, exterior guards and input hashes. Historical pass 03 remains incumbent.

Other entry points are final-review/verification.json, code-pins.json, units.json, refraction/trial-ledger.json and refraction/checkpoint-crease-erratum.json. Each stage retains its report, results and rejected trials. Final arrays are color-grading/{a,b}-step0.5-{material,complete,lens}.npy. Historical comparison panels came from saved native PNGs and were not rescored.

The helper packaged the following cached validation command but did not run it. It refuses to overwrite an existing output and performs no fit. It is not a complete geometry or source replay.

~~~bash
docker exec -e OPENBLAS_NUM_THREADS=1 \
  -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps \
  localica-dark-lab-check python3 \
  /evidence/extended/agent-pipeline-01/final-review/replay_cached.py \
  --output /evidence/extended/agent-pipeline-01-primary-cache-review
~~~

Original experiment recipes and deadline guards remain preserved. Do not restart expired trials. A possible future comparison of saved H2 and power-5 fields under the same final frosting and tone is only a recommendation requiring fresh authority. No further study, new target, interaction or final media is active.
