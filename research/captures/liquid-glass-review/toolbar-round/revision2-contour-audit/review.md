# Queue31: contour proxies measured; physical boundary correction unsupported

Existing toolbar pose/size are inherited center[960,542],half[392,170],radius170;
reviewed artifacts contain no independent toolbar contour extraction/uncertainty
dataset supporting these exact values. Softness.10 was selected by earlier image
scores, NOT independently measured alpha. pass03 is geometric experimentation/
Ana's qualitative preference, including explicit uncertainty between2Dsilhouette
and3Ddepth crown. contour.json is the SLIDER; selector crown measurements belong
to that separate element. None supplies missing toolbar silhouette measurements.

New measurement protocol was declared in model.md BEFORE extraction or any shape
optimization.978geometrically generated original-boundary normal profiles at2px
arc spacing, raw native-target/source profiles[-8,12] at.125px; original boundary
implicit error<=6.67e-16. No shape/material/pose fit, optical render, registration,
mask change or accepted epoch. Zero foreground-box overlap; source AND target
exterior guards remove text/contrast contamination. Base retained799profiles,
786with required ridge prominence, then proxy-specific ambiguity exclusions.

Raw unsmoothed observables, signed outward relative to ORIGINAL boundary:

|Proxy|profiles|median offset nativepx|32px-block bootstrap95%CI|
|---|---|---|---|
|Bright ridge|696|-.02056|[-.12255,.01623]|
|Outer negative gradient|760|+1.06491|[.83605,1.31250]|
|Outer25%peak-to-background level|695|+1.63710|[1.47426,1.81418]|
|Outer50%level|696|+1.13893|[1.00910,1.34212]|
|Outer75%level|696|+.64973|[.51472,.79128]|

A persistent positive OUTER-EDGE-PROXY offset exists. It is not an independently
identified alpha boundary or proof that half-extents must grow by this amount.
Ridge and edge are different optical features; picking whichever moves geometry
in a convenient direction would hide systematic measurement bias.

Region effects matter. Raw top ridge-.04159(CI[-.80789,-.01686]) versus gradient
+.5625([.31250,.81250]); bottom ridge+.70327([- .43224,.99486]) versus gradient
+1.81250([1.25181,2.31250]). Left ridge+.05880/right-.12189 both span0; right
gradient+1.07872([.94014,1.27525]). Bottom ridge ambiguity prevents treating its
positive median as a measured vertical pose change. Shoulders also have wide
intervals. Complete per-region results preserved, not collapsed into a cancelling
global mean.

Across27predeclared guard/smoothing variants: ridge medians-.57989..-.01827,
outer-gradient+1.06404..+1.23007,25%level+1.62953..+2.23950,50%+1.13636..+1.45438,
75%+.64363..+.80958. At base exterior guards, adding measurement smoothing.5/1px
moves ridge medians to-.26042/-.57862. Bootstrap1000resamples of32pxarc blocks
was computed for EACH proxy/region at all THREE smoothing levels with base guards;
the nine exterior threshold settings per smoothing have separate medians/counts.
No bootstrap interval silently covers unknown systematic alpha/ridge bias.

All raw profiles/flags, observable positions,27variants, bootstrap summaries and
threshold ranges retained. Native reference is only native resolution; subpixel
profile interpolation/extrema do not create independent image detail. Fixed source
contains modeled blank regions; paired target exterior guard is necessary. Hidden
source content and broad shadow/PSF can bias apparent boundaries.

Optional plotting stage failed AFTER all measurements persisted because the
container lacks matplotlib; its Python also lacks pip. No runtime/service was
installed, no scientific extraction/bootstrap repeated. Original plotting-stage
script preserved; resumed audit now reuses complete sensitivity output. Numeric
tables are the evidence artifact; no missing plot is presented as completed.

Conclusion: no nominal common crown/pose correction is identified with uncertainty
smaller than the ridge-to-edge bias. This is specific missing measurement evidence,
not proof the inherited footprint is correct.32conditional review follows; no
arbitrary shape sweep. Candidate29 remains frozen/unaccepted pending primary.
