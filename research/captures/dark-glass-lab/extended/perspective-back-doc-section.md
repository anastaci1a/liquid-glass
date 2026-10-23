### Curved back surface with a finite camera

For the same flat front, let the back be z=−h(q). Its intersection q differs from the front-plane sample p. Define H(p)=h(q(p)), use the slab's internal slope w=m/A and set q=p+Hw. The desired physical backdrop point is U=(1+G/C)F(p). With unit internal/outgoing directions t and v, Snell's normal is N=nt−v. A back graph has gradient b=N_xy/N_z. The chain rule gives:

```text
B(p,H) = (I + H Dw)^T b / (1 − w·b)
∇p H = B(p,H)
∂x B_y − ∂y B_x + B_x ∂H B_y − B_y ∂H B_x = 0
```

Partial x/y derivatives include the prescribed F(p), holding H fixed. The expanded condition includes H's unknown derivatives through the last two terms; raw image-map curl alone remains insufficient. Require 0<H<G, N_z<0, n(t·v)>1 and 1−w·b>0 on this transmitted local branch. Do not clamp failures into rays. Boundary conditions, first-hit/sidewall paths and global height consistency remain separate checks.

[Executable inverse equation](experiments/reconstruction/perspective_back_surface.py) and [independent forward controls](experiments/reconstruction/verify-perspective-back-surface.py) recover known quadratic surfaces from vector Snell paths. Tests cover height derivatives, the expanded condition, unit scaling, wrong-branch rejection and the orthographic limit. Run `python verify-perspective-back-surface.py`. These validate the stated equations, not a finite-camera realization of Apple's images or of the current fitted switch map.

