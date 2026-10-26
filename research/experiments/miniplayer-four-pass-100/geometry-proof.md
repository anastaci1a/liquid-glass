# Independent tip and shoulder control

Status: proposed contour with a convex distance coordinate. Numerical controls and source certificates remain required.

Let the previous core ellipse have support function and positive semiaxes:

$$
e(\theta)=\sqrt{a^2\cos^2\theta+b^2\sin^2\theta},\qquad a=A-R,\quad b=B-R>0.
$$

A diagonal shoulder adjustment preserves all axis extrema:

$$
h_{\mathrm{outer}}(\theta)=e(\theta)+R-\delta\sin^2(2\theta),\qquad 0<8\delta<R.
$$

Construct an actual convex core and positive rolling radius:

$$
h_{\mathrm{core}}=e+8\delta-\delta\sin^2(2\theta),\qquad r=R-8\delta.
$$

The core curvature radius is strictly positive:

$$
h_{\mathrm{core}}+h_{\mathrm{core}}''=\frac{a^2b^2}{e^3}+\frac{15\delta}{2}\bigl(1-\cos(4\theta)\bigr)>0.
$$

Therefore its distance is convex and 1-Lipschitz. Distance divided by the rolling radius supplies the actual height coordinate. The same distance gradient supplies both physical surfaces, contour and edge effects.

The unchanged monotone-height escape argument applies to outward, upward reflection over this certified convex core. It does not certify primary completion, outgoing clearance or source support; those remain independent gates.

Reducing the rolling radius changes surface slopes. Rescale the Hermite radial domain and inverse-scale its derivatives consistently. This is an actual geometric change, not an independent normal or image displacement.
