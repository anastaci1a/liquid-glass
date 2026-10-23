# Queue26: predeclared ordinary-filter color-space comparison

OLD source6c68/target5bb5/masksda7d/epochd1d864 and revision2 stay fixed. Source23
is not adopted. Read primary's switch_filter_space.py and active-switch/
rev5-filter-space/model.md as related private research, NOT shared implementation.

Actual accepted order: encoded-RGB Gaussian(source,sigma11 nativepx), encoded
bilinear source sampling; smooth clear/blur mixture in encoded RGB at each ray;
affine directional lighting/material then clip[0,1]; inside conditional4×4 average;
coverage-normalized encoded Gaussian output(sigma1.25 nativepx); sharp alpha
composition with OLD clean source/generated shadow; independent solid SVG glyphs.

Declare exactly SIX comparisons before target evaluation: standard sRGB decode/
encode and inverse-BT709-OETF/BT709-OETF, each at source-only, output-only, both.
No transfer blend, exponent/width fit, per-crop/reference/channel convention or
source-pixel edits. Source alternative decodes the source, Gaussian/bilinear
samples BOTH blurred/clear branches and mixes in decoded space, encodes BEFORE
the current affine/clipped material. Output alternative decodes the shaded,
conditionally averaged RGB, performs G(decode(C)*alpha)/G(alpha), then encodes;
sharp alpha is never decoded/blurred. Remaining AA/material/composition stay
encoded; this is an operator comparator, NOT a complete radiometric renderer.

Inputs, coordinates, original AA4×4, Gaussian widths/borders/precision, material,
shape, transition, glyphs, shadow and guards remain fixed. Added covariance25 is
ZERO; dispersion21 is not implemented. Transfer/filter changes can alter intensity
and apparent edge width but are ordinary achromatic filtering, not dispersion.

sRGB: decode c<=.04045 as c/12.92, otherwise((c+.055)/1.055)^2.4;
encode l<=.0031308 as12.92l, otherwise1.055l^(1/2.4)-.055.
BT709: decode c<.081 as c/4.5, otherwise((c+.099)/1.099)^(1/.45);
encode l<.018 as4.5l, otherwise1.099l^.45-.099. Rounded BT coefficients have a
small knee inconsistency; explicitly measure it, do not silently smooth it.
Zero-width/no-resampling is transfer round-trip (not an exact identity at the
rounded BT knee). Bilinear resampling can differ even when Gaussian sigma0.
Uniform input is preserved within that documented transfer precision. Widths
scale with L; output sigma also scales with raster scale. Encoded mode delegates
baseline exactly. Reuse saved accepted native baseline; ONE necessary new raw
encoded raster supports output-only comparators and exact postfilter verification.

Tests before native target comparison: transfer endpoints/knees/roundtrip,
zero-width/filter identity subject to knee precision, uniform small native crops
at scales1/2 and shared proportional-size units. Persist each raw raster before
filter/scoring; three raw source modes generate six completed operator results.
Original progress_gate plus explicit BOTH foreground/exterior/glass/rim guards;
crops/cohorts advisory. No new accepted pass without independent review/HQ.
27 requires rationale and preselected ONE convention before any shared-material
fit; if no supported useful direction, concise negative/model review instead.

Primary sources read2026-10-21:
- [Apple Core Image guidance](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/CoreImaging/ci_performance/ci_performance.html): default filters work in light-linear space. Does NOT identify Liquid Glass internals.
- [W3C sRGB conversion code](https://www.w3.org/TR/css-color-4/#color-conversion-code): standard piecewise sRGB transfer. ICC PDF independently checked; its inverse blue denominator has an apparent typo, so use standard shared12.92.
- [ITU-R BT.709-6, section1.2](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf): OETF constants/branch. Video BT709 tags do NOT establish UI working space or display EOTF. No new video decoding/registration.
