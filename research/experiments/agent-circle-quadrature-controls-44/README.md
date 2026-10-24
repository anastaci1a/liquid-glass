# Independent circle-area controls for the shared pixel rule

**All eight configurations pass at fixed orders 16 and 32.** The unchanged shared implementation produces positive raw weights and nodes strictly inside both the true disk and the pixel. Maximum normalized area error is 1.11e-16. This is geometric area verification only, not optical convergence, a reflected-scene result or a new image/score acceptance.

## Clock and immutable utility

The task began at 12:45:20.669 UTC on 24 October 2026. Its hard deadline is 12:55:20.669, including publication. The first vertical-segment checkpoint passed at 12:49:09.858, within four minutes. Approved utility pin `46efa5a93e9523d07b2a274f6cc37d28594b9ab3` merged cleanly as `d633a818`, then was immediately pushed and remote-verified before tests.

Only `reconstruction/pixel_quadrature.py` is imported. Its pinned source hash is checked before and after execution. No tracer, actual height adapter, radiance module or real optical profiler is imported or installed. No utility fork, edit, in-place repair or retry occurs. Prior own files remain unchanged.

## Independent clipped-disk area

Every circle has radius one half and both core extents zero. The first pixel has center (0.75, 0), width two and bounds from -0.25 to 1.75 horizontally, and -1 to 1 vertically. It clips exactly one vertical disk edge while covering the entire disk y span.

For a disk centered at the origin and a cut at horizontal coordinate c, the retained area to the right follows directly by integrating its vertical chord:

$$
A(c)=\int_c^R2\sqrt{R^2-x^2}\,dx
=R^2\arccos\left(\frac{c}{R}\right)-c\sqrt{R^2-c^2}.
$$

Here the independent exact expression is

$$
R=\frac12,\qquad c=-\frac14,\qquad
A=\frac{\pi}{6}+\frac{\sqrt3}{16}.
$$

The full pixel area is four. Therefore the normalized expected rule mass is 0.15796298776783843. Both fixed orders return 0.1579629877678384, with absolute difference 2.78e-17. This is not occupied-area normalization; neither rule mass nor individual weights is clipped or rescaled.

## Eight predeclared configurations

| Configuration | Analytic control |
| --- | --- |
| Vertical-edge partial disk | Circular segment above, full disk y span covered |
| Horizontal mirror | Pixel center (-0.75, 0), same exact segment area |
| Fractional translation | Both circle and pixel translated by (0.137, -0.283) |
| Coordinate-axis exchange | Pixel center (0, 0.75), same segment under axis exchange |
| Full disk | Pixel width two contains the complete disk |
| Tangent/empty | Pixel left edge touches only the right disk pole |
| Strictly disjoint | Pixel and disk have no intersection |
| Full interior square | Pixel width one half lies entirely inside the disk |

The complete disk has normalized area equal to pi divided by sixteen. The interior square has normalized area one. Tangent and disjoint configurations return empty node and weight arrays, with mass zero. Their measure-zero boundary is not assigned a regular optical event.

All returned nodes satisfy strict squared disk membership and strict pixel interior membership with no epsilon. Every returned weight is finite and strictly positive. No weight clipping, occupied-area renormalization, node movement or subset selection occurs. Exact inputs, every raw node/weight array and all discrepancies are retained.

Mirror, fractional translation and axis exchange agree on mass and transformed local first moments within the predeclared 1e-10 absolute tolerance. Axis exchange does not require identical node layouts from an x-first rule. All order-16/order-32 mass differences are at most 1.11e-16. No order or tolerance was adjusted after execution.

## Node accounting and stop policy

For the five nonempty vertical/full/interior layouts, there are two covered x pieces and two y pieces per x. The axis-exchanged partial case has four x pieces and two y pieces. Empty cases generate none. Across eight configurations, these fixed partitions reserve a coefficient sum of 28:

$$
N_{\rm reserved}=28(16^2+32^2)=35840<300000.
$$

Reservations precede each utility call. Actual generated nodes equal 35,840 across 16 calls. Each call's raw output and ledger are saved before checking invariants, so a failure would remain visible without repair. All eight configurations complete; there is no invariant, accounting or clock failure.

The checker's only numerical model is the shared area utility. The independent reference uses elementary circular-segment algebra, not another quadrature implementation or an optical surface. Rays, source queries, filters, composites, images and fits are zero. No source/target pixels or radiance functions are read.

## Limits and preserved evidence

These controls cover the declared circle/rectangle intersections, positivity and full-pixel mass, not arbitrary slivers or every rounded-rectangle topology. Positive area does not establish convergence of a sharply varying optical integrand, a cap reflection, an interior narrow lobe or mapped source-texture sampling. Future optical and new-node source-support controls remain separately necessary.

Root49's original AA2 scores and unresolved AA4/AA8 evidence remain unchanged. Root54's tested straight-body conclusions also remain unchanged; they are neither repeated nor widened into a circle optical claim. Selected Search and all older negative evidence are preserved. No subsequent circle, Search optical setting or new integration epoch is activated.
