# Switch model review: four further rejected families

- Optical/core-profile perturbation: full native reductions only 0.154% / 0.139%; below the 0.5% milestone. No change adopted.
- Geometry-scaled RGB displacement: twelve fixed-material comparisons and a shared minimax material refit. The best refitted tested spread (.015) reduces both errors about 0.0975%; below the milestone. This first-order spectral approximation does not resolve the incorrect rainbow/rim distribution. It is distinct from ordinary blur.
- Covered-color output blur: normalizing convolution by lens coverage avoids importing nonexistent exterior glass. On the unchanged recipe, A worsens 2.59%, B improves 1.92%. Shared material recalibration still worsens both. This reveals that the inherited calibration depends partly on its exterior filtering convention; no score-preserving adoption demonstrated. Do not silently switch the renderer or scoring epoch.
- Source-colored rim lighting: a shared 0.5 coupling of the geometric lighting basis to the transmitted source, with the same 23 material coefficients, worsens both errors about 0.146%. This is an empirical lighting test, not dispersion or an identified physical coating. Not adopted.

## Evidence and consequence

- All masks, sources and reference poses remain frozen. Fit iterations and bounded trials are not verified passes. The published switch remains revision 2.
- Nearby video frames, saved in temporal-reference-review.png, show optical shape and blur changing markedly during activation/release. A9.4s and B10.5s are both expanded states, but equality of their unseen 3D shape remains an assumption. Do not claim that a fitted failure proves Apple has no such effect.
- The visible dark inner edge and poorly matched color separation remain unresolved. The current normal map has an orientation multiplier and is not established as the gradient of a physical lens surface.
- Next useful geometry study: compare a declared potential-derived displacement with the inherited empirical normal map, documenting integrability and source-domain support before any score claim. Do not add independent pixel/crop-specific coefficients to force a numerical improvement.
