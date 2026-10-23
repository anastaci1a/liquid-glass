# Expanded playback: reflected outline paths

Status: incomplete reflection model. No outline image, fitted environment or acceptance. The selected transmission geometry and material stay unchanged.

## Question

Can reflected paths on the same physical solid explain a missing bright contour? The audit uses the selected harmonic back, flat front and closed footprint. Intersections, normals and sections share that geometry.

[Protocol](protocol.json) fixes 256 native launch locations, at most 64 interface encounters each and two million level-point evaluations. There are no RGB queries, images or fits.

## Result

| Measurement | Result |
| --- | ---: |
| Launches | 256 |
| Charged interface encounters | 2,932 |
| Level points | 108,900 |
| Unresolved geometric boundaries | 0 |
| Secondary background events | 563 |
| Unsupported secondary events | 49 per reference |
| Paths above residual tolerance at cap | 1 |
| Largest residual power upper bound | 0.0000306645 |

The initial reflected power ranges from 0.0784 to 0.08262 under unit incident radiance. Later bounds allow any polarization state; they are not exact unpolarized power products across changing incidence planes.

[Results](result.json) retain every sampled endpoint and power interval. [Paths](paths.npz) retain actual boundary points, normals and remaining directions. These sparse controls do not certify full native reflection support.

The front environment is unobserved. Forty-nine secondary background endpoints per reference also lack the required finite-kernel source support. One residual upper bound remains above the declared tolerance after 64 encounters. No endpoint replacement, extra bounce allowance or target-coloured halo is introduced.

## Material roles

The normal-incidence front reflectance is

$$
R_0=\left(\frac{n_{\mathrm{glass}}-n_{\mathrm{air}}}{n_{\mathrm{glass}}+n_{\mathrm{air}}}\right)^2=0.04.
$$

For this orthographic flat front, its first reflected direction and reflectance are constant. A distant environment that depends only on direction therefore cannot produce a shape-following rim through that branch alone. Back/internal paths, different actual front geometry or a separately supported scene are distinct possibilities; none is fitted here.

The current encoded transmission response also has a unit-input ceiling:

$$
C_{\max}=g+b=0.9262129976035591.
$$

This is an algebraic operator bound, not measured radiance. Applying the same compression indiscriminately to specular radiance can prevent a bright rim. Transmission tone/softness and scene-supported reflection must have explicit roles before a shared material extension is adopted.

## Timing and limits

Scientific execution finished at 20:01:16 UTC, within the first checkpoint limit. The checkpoint review was recorded late; [closure](stage-close.json) discloses that delay. No further scientific work occurred during it.

The stage closes before its 20:48:30 deadline. It is incomplete, not skipped and not evidence that reflections are absent. Source observed confidence and the accepted primary-source proof remain unchanged.
