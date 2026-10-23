# Flat front, smooth back-surface comparator

Exploratory geometry, not an Apple reconstruction or a counted pass. Motivation: the retained empirical map compresses the central image while folding the rim. A simple positive-power convex back surface need not have that combination. A back surface with a central depression and thicker surrounding region can change optical power with radius. Test the geometry rather than add another painted rim term.

## Declared model

- Orthographic camera looking along negative z; front surface z=0. The incident ray enters normally and remains vertical inside the glass.
- Air index1; glass index n initially fixed1.5. Normalized crowned footprint T(x,y)≤1 is unchanged. Minor half-size r owns all lengths.
- Back surface z=−h, h=r[t0+bT+cT²]; t0=.2 is a declared positive offset. Background plane z=−r(t0+g). Parameters b,c,g shared across observations.
- h and its actual gradient define one surface. Positive b and negative c allow a thinner center with a thicker surrounding region before the edge; this is not a claim that Apple uses that geometry.
- Outward back normal N=(−h_x,−h_y,−1)/sqrt(1+|grad h|²). Internal propagation D=(0,0,−1), a=D·N>0. K=1−n²(1−a²). For K>0, transmitted propagation V=nD+(sqrt(K)−na)N.
- Sample source F=(x,y)+(G−h)V_xy/(−V_z), restoring the existing shape translation afterward. Flat front, full thickness, background gap and refractive index are explicit. Outside the footprint, use the ordinary source plane; do not invent a continuation surface.
- Snell/vector reference: [PBRT4, Specular Reflection and Transmission](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission). Direction convention here is propagation into the interface, not PBRT's outward wi. These equations are independently derived in that convention.

## Validity and scope

- Require h>0, G>max(h), n≥1 and a declared global gradient bound M<1/sqrt(n²−1). Reject invalid configurations; never clip a TIR ray into a transmitted one.
- Under orthographic normal entry, the maximum outgoing tilt is δ(M)=asin[n sin(atan M)]−atan M. Subcriticality gives δ(M)<atan(1/M), hence M tanδ(M)<1. Therefore an outgoing ray descends faster than any point on this Lipschitz back surface: it cannot reenter the back or hit the vertical side wall. This sufficient bound is conservative; it does not prove behavior for an arbitrary camera or other surface family.
- For the crowned footprint, |grad T|≤2 max(1,|q'(a)|)/r inside. Thus M≤2 max(|b|,|b+2c|) max(1,|q'(a)|). Check analytic bounds and numerical samples separately.
- A folded source map is distinct from TIR. Inspect the map Jacobian; transmission validity alone does not imply an orientation-preserving image.
- Only ray geometry is physical in this comparator. Existing empirical material/highlights/shadow are separate. A full Fresnel/environment renderer, spectral integration, roughness and exact Apple geometry are not established.
- Fit bounds and all original image/source guards remain frozen. Any changes to the estimated background need a separate source review and cannot count as optical gains.

## Footprint limitation found by validation

- The inherited crowned-footprint formula does not become a rotationally symmetric circle when its two half-sizes are equal: its longitudinal softening remains anisotropic. The 90-degree rotation test exposed this. This comparator is restricted to the unequal-axis switch footprint; no circle limit or universal shape support is claimed. A future shared-footprint correction must be separate from this fixed-silhouette optical study and must preserve/reassess existing baselines.

## Biaxial extension

- The first three-start map projection settled at b upper bound, map RMSE .18032 normalized units, native E26.655/17.167 (worse than14.152/15.448). This is a proposal screen against the existing map, not a full image-fit exhaustion proof.
- Its central x power is constrained by the nearly flat longitudinal footprint coordinate. A separate back surface h/r=t0+bx(x/r)²+by(y/r)²+cT² supplies independently defined biaxial central curvature and one shared quartic edge term. The actual gradient still owns all rays. This is a surface family, not a position-dependent image patch.
- Conservative slope bound: M≤2 hypot(|bx| hx/r, |by| hy/r)+4|c|max(1,|qprime(majorhalf)|). Height bounds use the extrema of each term separately. The previous Snell and no-reentry bound then apply. Initial parameter box bx/by±.06,c±.1,g[.5,25],n1.5,t0.5 is declared before fitting. It passes analytic-gradient, Snell/vector, unequal-axis rotation/mirror/scale, subcriticality and sampled-clearance checks.
