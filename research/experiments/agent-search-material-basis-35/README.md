# Global normal-transmission material-basis conversion

**Analytically valid with explicit branch and clipping limits.** The proposed affine conversion preserves both miniplayer neutral responses over the full unit input interval. Accepted Search stays above the sRGB toe, but its converted white response exceeds one. The synthetic toe-crossing response is inapplicable to a single power-law affine conversion.

No selected state changes. This is a global basis conversion prerequisite, not target calibration, a Search rendering, a new material fit or cancellation of physical angle-dependent interface power. Search34 and every earlier record remain unchanged.

## Clock and scope

The task began at 09:30:52.735 UTC on 24 October 2026, with hard deadline 09:38:52.735 including versioning. The checkpoint completed at 09:31:47. No source, target or cache arrays were opened. Only scalar coefficient receipts, four declared sets and eight fixed synthetic inputs per set were used.

## Derivation

For normal air/glass interfaces at index 1.5, the single-interface power reflection is 0.04. Two transmitted events yield the stated primary power, excluding later reflected returns:

$$
T_0=(1-0.04)^2=0.9216,\qquad
k=T_0^{\frac{1}{2.4}}.
$$

Let the old encoded response be affine in a unit encoded component. On the power-law sRGB branch, decoding and encoding use

$$
c_{\rm old}=g_{\rm old}S+b_{\rm old},\qquad
D(c)=\left(\frac{c+0.055}{1.055}\right)^{2.4},\qquad
E(l)=1.055l^{\frac{1}{2.4}}-0.055.
$$

Preservation requires the new incident response to satisfy the following relation before primary attenuation:

$$
T_0D(c_{\rm new})=D(c_{\rm old}),\qquad
c_{\rm new}=\frac{c_{\rm old}+0.055}{k}-0.055.
$$

Therefore the single global coefficient conversion is

$$
g_{\rm new}=\frac{g_{\rm old}}{k},\qquad
b_{\rm new}=\frac{b_{\rm old}+0.055}{k}-0.055.
$$

Substitution proves preservation in real arithmetic on the stated branches, without target measurements or parameter optimization. The independent scalar implementation uses JavaScript algebraic sRGB functions; no shared numerical module is imported or executed.

## Branch and clipping conditions

For the supplied nonnegative gains and unit input, coefficient inequalities determine the complete range without scanning pixels. A sufficient high-branch and unclipped condition is

$$
b_{\rm old}>0.04045,\qquad
0\le b_{\rm new},\qquad
g_{\rm new}+b_{\rm new}\le1.
$$

The original range must also lie in the unit interval. Since the new response increases when transmission is below one, an old range wholly above the toe keeps the new response above it. The attenuated decoded value equals the old decoded value, so output encoding also remains on the high branch, away from rounded threshold conventions.

The upper constraint can equivalently be tested directly on the old coefficients:

$$
g_{\rm old}+b_{\rm old}\le1.055k-0.055=0.9647142471165661.
$$

This ceiling is an encoded range limit under unit incident clipping, not a radiance measurement. Input ranges below unity may permit conversion where the full unit range does not; this task inspected no actual pixel range and makes no such applicability claim for Search.

## Four fixed coefficient sets

| Set | Old gain | Old bias | Converted response range | Full unit-range applicability |
| --- | ---: | ---: | --- | --- |
| Shared numerical miniplayer | 0.596189238519786 | 0.3290237590837732 | 0.3423123519446791 to 0.9591318662516847 | Yes |
| Current working miniplayer | 0.5552987769129158 | 0.3908368353448866 | 0.4062643812900336 to 0.9807784780575345 | Yes |
| Accepted Search | 0.5193880051291454 | 0.4473611800152188 | 0.46474467005311065 to 1.0021053541473972 | No: upper clipping |
| Synthetic toe crossing | 0.06 | 0.02 | 0.022595267717148017 to 0.08467148189086643 | No: branch crossing |

Both miniplayer responses and accepted Search are wholly above the toe by their bias alone. Accepted Search's old maximum is 0.9667491851443642, above the encoded ceiling. Standard incident clipping loses 0.0020349380277980833 at unit input. The derived admissible upper input is 0.9960820465476632; it is not a fitted source threshold or adopted mask.

The synthetic range 0.02 to 0.08 crosses the toe. The power-law affine proposal misses by up to 0.0008237987281236106 on the declared samples, despite staying inside the unit interval. It is explicitly inapplicable; the result is not repaired with an extra coefficient set or numerical search.

If both relevant encoded values remain in the linear toe, the corresponding conversion instead divides the old response by transmission. A response spanning toe and power-law branches generally requires a piecewise transformation, not the proposed single affine coefficients. Rounded sRGB join constants should not be treated as exact mutual inverses at the branch junction.

## Verification and physical scope

Exactly 32 synthetic scalar samples were evaluated across four sets, with no additional sample or tolerance search. Maximum preservation residuals for the two fully applicable sets are 1.11e-16 and 2.22e-16, respectively. The Search unclipped algebra still holds, but its standard clipped response does not preserve the full input range.

At a different actual angle-dependent primary transmission, the converted result retains the physical variation:

$$
E\left(T(\theta)D(c_{\rm new})\right)
=E\left(\frac{T(\theta)}{T_0}D(c_{\rm old})\right).
$$

Only the constant normal-power reference is absorbed into the response basis. No per-ray coefficient, inverse angular transmission or Fresnel modification is proposed. Added reflected radiance, clear samples, foreground, source blur and later unassigned transport are outside this algebra. It neither supplies an environment nor turns an empirical encoded proxy into measured physical material.

Scalar coefficient receipts are hashed. The executable, declared samples, complete residuals and branch/clipping classifications are retained. Optical events, image work, shared numerical imports, fits and selected-state changes are all zero. Any later miniplayer or Search observation requires its own bounded authorization and original guards.
