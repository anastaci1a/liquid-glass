# Modeling specification

This contract defines research boundaries, not a recovered Apple implementation or a shipping application requirement.

[Method](../research/method/README.md) · [Geometric optics](geometric-optics.md) · [Reference atlas](sources.md)

## Surface roles

| Component | Modeling responsibility |
| --- | --- |
| Incident scene | Source content, registration, background distance and uncertainty. |
| Solid geometry | Front, back, sides, silhouette and surface-derived normals. |
| Transmission | Valid refracted paths and source sampling. |
| Scattering | Declared neutral or spectral material operator. |
| Reflection | Valid paths, Fresnel weights and supported environment radiance. |
| Foreground | Independent vector geometry and compositing. |
| Generated exterior | Shadow or glow, measured separately from body fidelity. |

Do not use one component to conceal another's failure. Unknown environment radiance must remain unknown rather than become a target-colored rim.

## Input and motion

Declare camera/view geometry and scene placement. For moving references, record pose and state before interpreting source-feature displacement.

An optional illustrative dynamics model may retain position and velocity across changing targets. It remains separate from optical validation.

### Destination and settling

A damped spring is an illustrative state model, not an identified material equation:

$$
m\ddot{x}+c\dot{x}+k(x-x_\mathrm{target})=0.
$$

Report its units, integration method and numerical tolerances when used. Device timing requires separate measurements.

### Shape carries impact

A deformation must change a coherent surface. Recompute intersections and normals from that surface; do not independently move sampled image coordinates.

Approximate volume preservation may be tested as a hypothesis. It does not establish fluid simulation or Apple's private dynamics.

## Settings sliders and switches

Use [control-family observations](controls.md) to distinguish states and informative source features. Transparent and frosted families need not share identical material parameters.

## Geometry and readability

Maintain one authoritative surface description. Silhouette, normals, sections and ray paths must agree within declared numerical tolerances.

Keep foreground shape, optical distortion, softness and illumination as separate measurements. A low whole-image error does not close a named local defect.

## Rendering and measurement

Separate pixel integration from optical blur. Declare source-space and output-space filters explicitly, including finite kernels and boundary handling.

Freeze sources, reference masks and registration during a comparison. Audit whole-body and protected source footprints before sampling RGB. Missing or invalid paths are failures, not replacement pixels.

Encoded color fitting is an empirical operator unless a radiometric interpretation is justified. Do not call neutral filtering dispersion or infer roughness from one blur radius.

## Acceptance checks

| Claim | Required checks |
| --- | --- |
| Mathematical correctness | Surface consistency, branches, boundaries, transforms and numerical convergence. |
| Visual fidelity | Exact reference crops, overall/local measurements and disclosed regressions. |
| Shared model | Transfer across related controls and a suitable held-out reference. |
| Physical identification | Independent source, geometry and material evidence. |
| Runtime performance | Representative device measurements. |

Use the [experiment template](../templates/experiment.md). Negative and incomplete results remain valid research outcomes with explicit scope.
