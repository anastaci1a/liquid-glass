# Local Snell-dispersion comparator

- Question: can stronger nonlinear chromatic bending near the critical angle explain the colored switch rim more consistently than uniform RGB displacement scaling?
- Evidence baseline: accepted switch revision 3, source commit `0d64f30`. The earlier uniform-scaling family was tested again because the accepted normal-cap map changed; it still fails the paired milestone. No failed experiment is a pass.
- Primary optical reference: [PBRT 4e, Specular Reflection and Transmission](https://www.pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission), especially Snell's law and wavelength-dependent index. The following inverse construction is our derivation, not an Apple claim.

## Assumptions and equations

At an output coordinate p, retain the archived green map F and define D=F(p)-p. Assume a vertical ray in a dielectric of index n0=1.5, a locally tilted exit interface, and a constant effective gap g from that interface to the background. Set delta=atan(|D|/g). Snell's relation sin(alpha+delta)=n0 sin(alpha) gives

`alpha = atan2(sin(delta), n0 - cos(delta))`.

For nc=n0±delta_n, compute `delta_c=asin(nc sin(alpha))-alpha`, then

`F_c(p)=p + g tan(delta_c) D/|D|`.

At D=0 the map is p. At delta_n=0 it exactly recovers F. The subcritical inverse branch requires `cos(delta)>=1/n0`; every transmitted channel additionally requires `|nc sin(alpha)|<1`. Trials violating either condition are rejected, not clipped. Outside the silhouette the old continuation remains unchanged, preserving the current output-filter convention.

## Limits and controls

- The inferred normal field is not proven integrable to a height surface. A constant effective gap does not describe an identified thick lens. This is a local-normal approximation testing nonlinear chromatic response, not a geometric reconstruction.
- RGB is not a spectrum; three sampled indices do not identify a real dielectric's dispersion. No Fresnel energy weighting or internal-reflection model is claimed.
- The source, shape, masks, ordinary blur and existing directional transmission stay fixed in the screen. A separate joint settlement permits the same existing shared material coefficients to compensate; that remains the same experiment family.
- Gap is chosen from the maximum native in-footprint displacement across both observations and common critical-margin values. No per-reference gap or target-pixel modifications.
- Analytical inverse/zero-dispersion identities and native zero-spread recovery pass. New source-domain rays, original replay and visual review would still be necessary before adoption.

## Screen result

- Twelve fixed-material comparisons include the exact zero-dispersion control. None meets the paired milestone; one high-index/near-critical trial correctly fails for total internal reflection. Replacing the prior directional contribution substantially worsens A.
- Joint material settlement remains within this same family, not a separate pass. Its result and full trust-step history are in joint-settlement.json; no candidate is adopted from screen scores alone.
