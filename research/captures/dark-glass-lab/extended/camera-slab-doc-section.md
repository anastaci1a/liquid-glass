## Finite-camera slab control

Use an infinite plane-parallel slab to check camera calibration before fitting a curved solid. Put the pinhole at (0,0,C), front at z=0, back at z=−h and backdrop at z=−G, with C>0, 0≤h≤G and n≥1. Let p be the ray's front-plane position. The unlensed backdrop point is (1+G/C)p; divide physical backdrop coordinates by that factor before comparing image maps.

```text
m = p/C; A = sqrt(n² + (n²−1)|m|²)
F(p) = p + h [m/A − m] / (1+G/C)
f = h/(C+G)
J_tangential = 1 + f(1/A − 1)
J_radial = 1 + f(n²/A³ − 1)
```

- Both derivatives are at least 1−f>0: this finite-camera slab cannot fold/reverse its image. Curved surfaces, sidewalls and multiple paths are outside that result. Changing viewpoint alone does not justify adding a mirrored rim.
- h=0 or n=1 gives identity. C→∞ also gives identity for this parallel slab; a curved surface need not. At the optical axis both derivatives equal 1−h(1−1/n)/(C+G). Central contraction of the source map corresponds to apparent image magnification.
- [Implementation](experiments/reconstruction/camera_slab.py) and [independent vector-Snell controls](experiments/reconstruction/verify-camera-slab.py) check both interfaces, Jacobian, equal-index/no-slab/far-camera limits and unit scaling. Run `python verify-camera-slab.py`. The NumPy oracle tests bounded floating-point cases; the algebra supplies the stated geometric bound. No Apple camera, curved lens or reconstruction pass is inferred.

