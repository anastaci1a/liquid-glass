# Directional finite-band comparator

- Motivation: the user observes a rainbow-like directional spread on the left quarter, fading in contribution rather than shortening. The inherited model samples one displaced red ray and one displaced blue ray, retaining a single green ray.
- General optical fact: refractive index can vary with wavelength. See [PBRT, Specular Reflection and Transmission](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission). This does not establish Apple's implementation or this particular model.
- Comparator: three positive Gaussian quadrature weights (1/6, 2/3, 1/6) at center wavelength plus/minus sqrt(3) times bandwidth. Centers are 610/550/460nm. A shared inverse-square displacement law can replace the legacy symmetric channel offsets; the original normalized geometry evaluates every ray. Contribution still uses the existing left-side fade.
- Limitations: input RGB is not a recovered spectrum; channel centers/sensitivities and directional displacement are approximations. This is not a measured dielectric or a full ray trace through a recovered 3D solid. No reference-dependent coefficients, painted fringe, or ordinary blur change.
- Invariants: zero bandwidth with legacy linear centroid law recovers the previous field; uniform input stays uniform. Fixed native masks and both reference guards remain authoritative.
