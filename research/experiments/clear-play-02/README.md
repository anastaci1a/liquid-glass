# Clear play: source blur and outline transport

Status: active. No new result or acceptance yet.

## Question

Feedback F-001: compressed edge texture appears too blurred under the accepted output filter. Test whether filtering incident content before refraction preserves central softness while changing edge sharpness through the physical map.

## Frozen state

G05 surface, refractive index 1.5, background distance 2L, original registered source, native 4×4 integration, masks and historical foreground remain fixed. The accepted output filter is 1.7 native pixels. No dispersion, geometric fit, color fit or new source is permitted.

## Blur comparison

Use five declared source widths: 1.25, 1.5, 1.7, 2 and 2.5 native pixels. Select by matching accepted central texture bandwidth in the fixed 140×65 center crop. Reuse previous source widths 0.5 and 1 as historical controls.

Audit the complete finite Gaussian and bilinear footprint against the registered source before sampling. Preserve unfiltered clear exterior contributions. Use cached physical queries; no new ray tracing is required.

Allow at most two new full native candidates and one independent replay. Retain all original guards and inspect the lower-left, upper-left, upper-right and center crops. Never select an edge-specific blur radius.

## Outline investigation

Review saved Fresnel paths and their unresolved power. Permit one bounded continuation or boundary diagnostic using the same surface, up to 64 launches, 4,096 events and two million level evaluations. No reflected RGB image is authorized without supported scene radiance.

Explain what the actual surface predicts, which illumination is missing, and whether transmission softness should affect specular reflection. No painted halo or target-colored environment is allowed.

## Clock and outcome

[protocol.json](protocol.json) records actual UTC start and deadlines. The maximum allocation is 10 minutes intake, 50 blur, 45 outline and 15 verification. Close answered stages early; stop at failed invariants or exhausted budgets.

A visible component improvement, useful negative or incomplete result are valid outcomes. Historical filtered evidence remains labeled; mathematical correctness and visible fidelity are separate claims.
