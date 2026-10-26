# Peak color without a luminance floor

The first pass's luminance floor can neutralize a saturated yellow endpoint. The revised display response protects peak-channel brightness instead. Lower channels may decrease as chroma increases; this is not a claim of increased physical radiance.

Let the guide and completed backing be decoded linear colors:

$$
\mathbf{G}=\operatorname{decode}(\mathbf{c}_{\mathrm{guide}}),\qquad
\mathbf{B}=\operatorname{decode}(\mathbf{c}_{\mathrm{body}}),\qquad
m=\max_i G_i,\qquad b=\max_i B_i.
$$

A smooth neutral term vanishes toward a unit guide peak:

$$
\ell=\lambda(1-m)^3,\qquad
\mathbf{q}=\frac{\mathbf{G}+\ell\mathbf{1}}{m+\ell},\qquad
\lambda=0.4378927114042099.
$$

The endpoint uses one common peak and chroma exponent:

$$
p=\max\left(\frac{e(m+\lambda)}{e(m+\lambda)+1-m},\ b+\eta(1-b)\right),\qquad
E_i=pq_i^s,\qquad e=3,\quad\eta=0.12.
$$

The spatial plateau and fade remain separate:

$$
\mathbf{c}_{\mathrm{out}}=(1-\alpha)\mathbf{c}_{\mathrm{body}}+\alpha\operatorname{encode}(\mathbf{E}).
$$

A pure-white backing remains exactly white. Near-black guide colors approach the same gray endpoint continuously. All channels remain bounded without clipping. The source guide retains incident blur and refraction but excludes the neutral body grade.

This is an encoded display-layer hypothesis. It does not change optical normals, source coordinates, shadow, or source availability. Chroma changes can alter perceptual hue; exact color-ratio preservation is not claimed.
