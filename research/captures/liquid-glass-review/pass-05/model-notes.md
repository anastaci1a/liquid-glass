# Playback transition and icon controls

These are offline image-map/color-response experiments, not an identified Apple solid or shader. General formulas also appear in the research branch's `docs/liquid-glass/model.md` at `610a589`.

## Optical transition

Let `r` be radial distance from the lens center, `R=245px`, inward depth `d=R−r`, and radial displacement `a(d)`. The inverse lookup is `F(v)=(1−a/r)v`, with identity at the center because displacement support ends well before it.

The pass-04 profile was `a0=A clamp(1−d/b,0,1)^p`, where:

- `A=155.2832594px`;
- `b=23.1422324px`;
- `p=2.1002224`.

Its second derivative is proportional to `(1−d/b)^(p−2)` near the inner end. The exponent is only about 0.10: curvature of the **map** approaches zero slowly until extremely close to that endpoint. This is not a measurement of the physical lens's curvature.

For the new trial define `da=b/4`, `ds=b/2`, `w0=b/2`, width factor `k`, shoulder gain `g`, and inner endpoint exponent `q=4`:

```text
S5(u) = 10u³−15u⁴+6u⁵
for d≤ds:
  a = a0(d) [1+(g−1) S5(clamp((d−da)/(ds−da),0,1))]
for ds<d<ds+k w0:
  t = (d−ds)/(k w0)
  a = g A 2^(−p) (1−t)^q
      exp[(q−pk)t + (q−pk²)t²/2]
after that: a = 0
```

- The outermost `da≈5.79px` is identical to pass 04.
- At `ds≈11.57px`, value and first two derivatives match the incoming profile times `g`.
- The inner endpoint has zero first, second and third derivative for `q=4`. The entry splice is C2, not generally C3.
- The grid uses `k=1…4` in 0.5 increments and `g=0.75,1,1.25`. Shoulder displacement is approximately `27.16,36.22,45.27px`; these are optical displacements, **not** surface height/curvature.
- The baseline tail width is `w0≈11.57px`; the 1.5× candidate has a 17.36px tail and becomes identity at inward depth 28.93px. The 2× control becomes identity at 34.71px.
- Setting `k=g=1,q=p` exactly recovers pass 04. The new grid's `q=4` means its 1×/gain-1 cell is not that baseline; pass 04 is shown separately in the combined comparisons.
- Radial/tangential map eigenvalues are `1+a′(d)` and `1−a/r`. All 21 tested combinations retain one radial derivative sign change, without adding the earlier extra outer return. This is finite domain evidence, not a general nonfolding or physical-path guarantee.

## Blur

The independent blur grid filters the completed pass-04 glass material **after** source lookup/shading and before silhouette coverage/icon compositing. It does not blur the icon. The source retains its prior 0.5px Gaussian filtering.

The measured dune crop is native `(920,680)–(1040,728)`, inside the lens and below the icon. Diagnostics compare RGB error and high-pass residuals using a fixed 1px high-pass scale. The score can favor loss of detail when source registration differs; do not interpret its minimum as a unique Apple blur measurement. Images, rather than that score alone, decide acceptance.

## Calculated icon colors

The silhouette and its existing coverage feather are reused; interior reference colors are not reused.

- **Pass04:** `C=1−aRGB(1−B)^gammaRGB`.
- **White plateau:** `C=1−aRGB max(1−B/t,0)^gammaRGB`.
- **Plateau plus chroma:** apply `L+(1+s(1−L))(C−L)`, clipped to `[0,1]`, where `L` is encoded-RGB luma. Independent channels can reverse hue on backgrounds outside the fitting pose.
- **Ordered response:** common strength and exponents ordered red ≥ green ≥ blue. Warm input ordering is retained, at a single-image fitting cost.
- **Shared monotone curve:** apply the **same** monotone PCHIP to each channel. Five parameters determine a floor, three positive increment ratios (a fourth is fixed to one), and the white threshold. Input knots are `t[0,.3,.55,.8,1]` followed by `1`; output knots rise from the floor to white, followed by white. This preserves channel ordering and neutral grays for every RGB input. It is C1, not generally C2.

The shared curve is used in the combined images and motion previews. The narrower single-pose error of an unconstrained response is retained as evidence rather than treated as proof of a more general shader. No spatially painted gradient is used. Additional icon-input blur was tested and rejected by the current fitting objective.

## Motion preview

- Fixed registered uncovered source photograph; no repair/reconstruction work added for the video.
- Pure translation, same path before/after; no elastic deformation or morphing.
- Optical lookup is recalculated at each new background position. Material lighting remains centered on the lens. The icon stays fixed to the lens and its calculated color changes with the background.
- Two subpixels per output axis, 960×540 output, 30fps, six seconds. Comparison is 1920×540.
- Exterior shadow is omitted, and still-image retained exterior context is not used. Offline playback fps is not real-time rendering performance.
