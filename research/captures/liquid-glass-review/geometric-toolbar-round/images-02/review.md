Useful negative: the mathematically accepted A adapter does not reproduce the toolbar's visible refraction at either authorized depth. No fitting, new source, third diagnostic or animation was performed.

Two fixed native images were produced only after BOTH fresh source/path preflights passed. The experiment record declares a 15-minute budget, depths .02/.04, n1.5, D2, core0/p3/edge0, softness .1, orthographic camera, original half392/170. The lead-owned core SHA `f3a7fef6e9150164479454417079619670a5577c04eb576c28f01db49cba2abd` matches the invariant packet and committed core b1cec2f6f663948054422a347ef9fe8066c35fe3. No shared files were edited. Mathematical compatibility is retained; visible fidelity is rejected.

All evidence is under `dark-glass-lab/extended/geometric-toolbar-round/images-02/`. Open `full-gallery-0.02.png` / `full-gallery-0.04.png`, then the `crop-upper-*`, `crop-d-stroke-*`, and `crop-underside-*` galleries. Each panel is native width, with no 4x enlargement. Source/reference/historical arrays, masks and crop rectangles were not changed. `measurements.json` includes RGB, luma, neutral-removed chroma and signed RGB for the exact fixed crops.

Source-first result

Each depth freshly traced **8,691,200** actual full-crop4x4 rays. Each includes 4,980,688 scored subrays, of which 1,141,256 miss the predicted outline and correctly retain straight paths. All 3,864,420 whole-footprint rays are included. There are zero incomplete paths, zero exact crease hits and zero unsupported source footprints. Every four floor/floor+1 bilinear texels has registered-domain confidence exactly1. All crop rays, not just centers or an eroded mask, were audited. Source RGB was not sampled until the BOTH-FIRST proof was saved.

The audit uses the original registration matrix and full-confidence registered donor domain; it does not infer confidence from source color. The existing erased lens/shadow rectangle is separately labeled estimated, rather than called directly observed. Around 49% of whole-footprint queries touch that modeled paper: 1,895,089 / 3,864,420 at depth.02 and 1,894,305 / 3,864,420 at depth.04. Unknown hidden words were not recovered or invented. Directly observed texture and estimated blank paper must not be conflated.

All-crop query bounds are [474.625,284.625]..[1444.375,844.375], including straight misses. Whole-footprint query bounds are:

| Depth | Minimum XY | Maximum XY | Maximum displacement |
|---|---|---|---|
| .02 | [578.291376,382.323524] | [1341.708624,701.676476] | 10.206993 native px |
| .04 | [588.539796,392.604879] | [1331.460204,691.395121] | 20.497472 native px |

Source blur and output blur are both ZERO. The finite sampling footprint is exactly the four bilinear source texels; no Gaussian/post kernel is active. Manual bilinear interpolation samples precisely those certified texels, with no clamp, border substitution or extrapolation. The old139M-address proof is not reused.

Saved native coverage is bit-exact to the historical accepted alpha at both depths. Native M and complete arrays range [0,.8745098039], with no raw out-of-range values or optical clipping; PNG quantization is presentation only. The footprint/scoring mask did not change. See frozen-coverage-raw-audit.json.

New M is unit-throughput primary raw source transmission with 4x4 pixel integration, including straight clear misses. It does not invoke the old tensor map, gamma, material coefficients or lighting. The accepted solid vector alpha/placement/color is then applied unchanged, using the existing vector_foreground coverage implementation. New generated shadow and illumination are zero, explicitly labeled. Historical controls retain their original fitted shading, generated shadow and source/post filtering; they are never replacement pixels for the new body. Complete errors therefore mix the deliberately missing appearance stages with geometric and source errors. These diagnostics are not a dielectric-radiance renderer or a new scoring epoch.

Visible and numerical results

| Original region | Historical filtered | New depth .02 | New depth .04 |
|---|---:|---:|---:|
| Glass RMSE | 5.79616 | 45.75017 | 47.07993 |
| Rim RMSE | 8.67757 | 40.74805 | 42.08429 |
| Held RMSE | 5.52561 | 44.82157 | 46.52118 |
| Exterior RMSE | 11.46696 | 19.51282 | 19.47965 |
| Upper crop RGB RMSE | 10.80267 | 42.19491 | 45.48975 |
| Adjoining d crop RGB RMSE | 3.43705 | 91.74099 | 91.08060 |
| Underside crop RGB RMSE | 6.97587 | 12.02206 | 12.00618 |

These are descriptive same-array measures, not claims that rescoring float64 changed the original float32 score epoch. Original historical accepted records remain authoritative and immutable. Current local scoring code reports full RGB/luma/chroma/signed residuals, including every regression.

The fixed crops are upper[650,369,1270,468], adjoining d[960,468,1120,550], underside[650,650,1270,726]. Both full comparisons and the crops were visually inspected. Neither new image reproduces the upper compressed/stretched text, d curvature or smoothly compressed/inverted underside. Depth.04 makes slightly more geometric movement, but its d crop still shows sharp, essentially ordinary-looking source strokes instead of the reference's softened curved appearance. Its tiny d/underside metric difference versus .02 is not a visible success. Whole glass, rim, held and upper crop are worse at .04. The outline, crown illumination and shadow are largely absent from the raw-transmission view. Their absence is separate from refraction, not evidence to fit a painted rim or hide the geometry with blur. Chroma error is small compared with luminance/structure; there is no dispersion operator here and no basis to call ordinary blur dispersion.

There is also an analytic limitation of A: accepted q is even with q(0)=q'(0)=0, so T_xx(0,y)=0. Consequently h_xx(0,y)=0 (with the C2 center extension), and the orthographic source-X derivative at x=0 is exactly1. Increasing sag or D alone cannot introduce the missing central horizontal curvature in this family. Away from the symmetry axis the cached strict-interior horizontal source derivative ranges [.87869,1] at .02 and [.75089,1] at .04. These are grid observations excluding boundary-crossing stencils, not global bounds or a source-independent image-fit lower bound. They support a local geometry diagnosis, while unknown hidden text and historical PSF prevent claiming the entire image mismatch is geometrically identified.

Same-surface geometry and procedural record

`actual-sections-rays-*.npz` stores sections/mesh vertices from actual height and corresponding actual Snell ray segments. `sections-rays-*.svg` plots those saved arrays only: black front, blue back, gray vertical input, red transmitted exit segments shortened for readability. No alternate decorative profile or independent normal was used. Exact crease remains unresolved; section endpoints are labeled one-sided geometric limits. The original infinite-plane background and physical units are unchanged.

The cached presentation helper initially failed before calculations because matplotlib is not installed; no package was installed. It was replaced by a standalone SVG plot of saved geometry. A subsequent empty off-footprint row reduction failed during cached summaries; that bookkeeping was corrected by skipping empty rows. Neither failure repeated tracing, source sampling or either native image. Both failures are retained in packaging-notes.json. All new large caches are under /evidence, not /tmp.

Exact commands, run in the existing container:

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/images-02/experiment.py
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/images-02/experiment.py --render
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/geometric-toolbar-round/images-02/package_cached.py
```

The optical driver enforces the original absolute deadline and refuses a repeated render after render-started.json exists. These are historical recipes, not permission to restart or extend the experiment. The package helper reads saved arrays and makes no optical queries.

Held-out provenance check and next request

A bounded metadata/hash-only check of existing Music Navigation B finished in seconds, under its <=5-minute read-only allowance. All source/target/known-mask hashes match its declared case. It is a masked temporal translation mosaic with explicit confidence, not glass-derived reconstruction. It contains recovered text but is mostly white and has a computed selected backing, so it is only a potential text-cohort held-out control, not strong broad textured cross-validation. Original-font labels coexist with clean traced icons and inferred styles. No source, ray or image evaluation/adoption was performed for it. The check is in navigation-b-provenance.json. Mail remains a tone/placement control only.

Immediate readiness and next-budget request were queued to lead before packaging; native queue acceptance is confirmed, consumption unknown. Suggested next review: the missing longitudinal curvature must come from a justified actual surface/camera change, not a fitted normal or blur. Conditional proposal B would need its ordered-intersection API/certificate and explicit new budget before activation. No B, third image, new camera, fit, further source acquisition, animation or public edit was started. Root owns all final integration/commits. This two-image experiment is stopped.
