# Dark-color neutral increment

The pass-three channel response stays fixed except for a fourth-power neutral term. It has little effect on high-luminance yellow and more effect on dark colored guides. The same rule applies to both player lengths.

$$
\ell=0.12+0.38(1-Y)^2+k(1-Y)^4,\qquad
k\in\{0,0.12,0.24\}.
$$

The three black endpoints are bounded neutral gray; white remains white. The declared exponent is unchanged.

$$
E_i=1-(1-\ell)(1-G_i)^{1.75}.
$$

The existing peak safeguard, encoding and coverage blend remain unchanged. A zero increment must reproduce the pass-three response exactly on the fixed synthetic cube. This is a display hypothesis, not measured spectral radiance.

The plateau is fixed at `2.5` native pixels for this pass. Comparisons against pass three therefore include both the width and geometry changes; the three within-pass neutral trials isolate the added response term.
