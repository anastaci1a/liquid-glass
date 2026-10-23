# Two-interface comparator

- View is orthographic along -z; front z=f(x,y), back z=-h(x,y), background z=-G. All positions use the same normalized element coordinates.
- Elliptical front: f=a r max(1-(x/A)^2-(y/B)^2,0)^3, a in[-.08,.08]. It is C2 at the ellipse boundary, which is inside the crowned footprint. Derivatives are analytic.
- Edge-localized alternative: f=a r S(d/(w r)), S(t)=6t^5-15t^4+10t^3, clipped at0/1. True inward distance d and its unit gradient are reused. Ordinary blur and colored dispersion are separate.
- Coupled variant keeps vertical thickness fixed: h=h0-f. Both height and gradient change; no separately fitted image displacement. Paraxial entrance/exit gradient sum remains grad(h0) at a shared coordinate, while finite internal travel samples different coordinates. This is a hypothesis, not an assertion about Apple.
- Front outward normal is(-fx,-fy,1), normalized. Entrance uses air/solid Snell. Back intersection solves f+tz*tau+h(x+tx*tau,y+ty*tau)=0 with a conservative negative derivative bound. Reject missing roots, nonpositive thickness, side exits, TIR, invalid exit direction, or insufficient conservative no-reentry bounds. Exit normal is(-hx,-hy,-1); actual transmitted ray intersects the background plane.
- First broad-crown and edge-localized fixed-material proposals harmed A. Constant-thickness elliptic bending changes the center much less and improves B at negative amplitude, but does not qualify by itself. One small joint native settlement tests this remaining direction; no broad blind resweep.
- Tests: exact zero-front equivalence, analytic front gradient errors<2.5e-11, normalized scale consistency, mirrored map errors<1.2e-13 for both shapes/couplings and observations on5000points. Tests are not complete raster/source certification. Inherited material/reflection remains empirical.
- Source, masks, incumbent and accepted count5 remain unchanged. Fixed-point Gaussian-quadrature proposals are not native scores.
