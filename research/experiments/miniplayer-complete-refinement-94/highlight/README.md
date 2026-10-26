# Color-aware highlight and combined result

Three shared desaturation settings were evaluated with one bounded training scalar each. The highlight brightens the existing linear-light color and gently reduces saturation. It is composited over the completed image, separately from refraction. The strongest allowed lift was approached in all three searches; none established a converged interior optimum.

Each search consumed its declared twenty-four evaluations. The lowest sampled equal-reference training loss used desaturation `0.25` and lift `1.4999855326864824`. These are a development proposal, not accepted parameters. No additional coefficient, width or angular setting was tested.

## Response

Let the linear-light pixel be a nonnegative color vector, its largest channel the peak, and the integrated edge field the opacity weight. The display response is:

$$
\begin{aligned}
p&=\max_i C_i, & t&=1-\exp(-e\alpha),\\
p'&=p+(1-p)t, & s&=\eta t,\\
\boldsymbol C'&=p'\left[(1-s)\frac{\boldsymbol C}{p}+s\boldsymbol 1\right].
\end{aligned}
$$

Black is explicitly fixed. Zero lift returns the original bytes. The result is encoded to sRGB without clipping. This is a bounded display-effect hypothesis, not identified physical radiance or a reconstruction of a particular grading application.

## Edge integration

The new contour is integrated with positive full-pixel weights. Horizontal partitions include pixel centers, axes, core extents and every horizontal-edge intersection. A sine parameter removes the cap-tip coordinate singularity. Vertical intervals are clipped to the actual contour and split at centers and axes. Occupied area is never renormalized.

The two orders differ by at most `7.735e-8` in expanded opacity and `7.688e-8` in compact opacity. Both satisfy the declared successive-order criterion. This is numerical agreement, not a rigorous global integration error bound. The omitted deep-interior opacity is bounded by `1e-12`.

Circle area, segment, empty, symmetry and bounded-response controls pass. The subsequent own verification also checks anisotropic ellipse-plus-disk areas against the independent ellipse-perimeter formula. No old rounded-rectangle quadrature certificate was transferred silently.

## Result

The compact rim becomes clearer and retains background color. Expanded A becomes too bright. Original interior, foreground and partial-boundary failures remain. No setting passes every original family guard.

The final combination uses the training-selected highlight and the strongest tested exterior shadow. It improves aggregate error on expanded B and both compact references, but worsens expanded A. All original failures remain; the selected model is unchanged.

[Results and guards](result.json), [scalar trial histories](fits.json), [integration checks](integration.json) and [ledger](ledger.json) retain every proposal. No optical work, source sampling or additional material fit occurred during combination.
