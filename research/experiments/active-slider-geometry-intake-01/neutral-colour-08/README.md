# Neutral colour: protected-center half-step candidate

The half-step passes all original H1 guards and both protected center checks. Its green and gray center tones are visibly closer to the references. The full step fails both center checks and whitens the track too much despite improving every original aggregate guard. No geometry, source, blur, mask or historical acceptance changed. The half-step awaits independent primary review.

## Declared scope and clock

The [protocol](protocol.json) started at 21:08:13.097 UTC with a fixed 21:28:13.097 deadline. The original latest colour deadline remains 21:50:40.688 UTC and the total deadline remains 23:50:40.688 UTC. Early completion does not transfer unused time. The last actual candidate evaluation finished at 21:12:13.914141 UTC.

H1 D2 remains the geometry. Original incident widths remain 4.25 and 4.00 native pixels; the wider blur was not adopted. Native antialiasing remains two-by-two. Lighting, shadows and dispersion remain absent from this experimental state. The modeled source has observed confidence zero, with unresolved transition-state and illumination ambiguity.

The visible question is whether one shared neutral tone can improve the dark track without erasing useful color to imitate missing returns. The same center rectangles were protected before fitting. These supplementary criteria do not alter the original source, scoring masks or historical metrics.

## One bounded training proposal

For retained inside source samples, the empirical encoded response is

$$
\mathbf{S}'=\operatorname{clip}\left(g\mathbf{S}+b\mathbf{1},0,1\right).
$$

The same two scalars apply to all channels and both references. Clear samples remain unfiltered and unchanged. The response occurs before antialiasing and composition:

$$
\mathbf{C}_p=\frac{1}{4}\sum_{k=1}^{4}
\left[I_{p,k}\mathbf{S}'_{p,k}+(1-I_{p,k})\mathbf{S}_{p,k}\right].
$$

The declared parameter constraints are

$$
\begin{aligned}
0.25&\leq g\leq1.25,\\
-0.1&\leq b\leq0.75,\\
g+b&\leq1.
\end{aligned}
$$

The white constraint and bias lower bound imply a tighter feasible gain maximum of 1.1. This is a consequence of the declared constraints, not a changed bound. Their feasible polygon has three vertices, allowing one finite active-set quadratic solve without restarts or a parameter sweep.

Let the original training pixels exclude the original held set. With retained premultiplied lens color, coverage and clear contribution, the unclipped model minimizes

$$
\mathcal{L}(g,b)=\frac{1}{2}\sum_{j\in\{A,B\}}
\frac{1}{3|\mathcal{T}_j|}
\sum_{p\in\mathcal{T}_j}
\left\|g\mathbf{L}_{j,p}+b\alpha_{j,p}\mathbf{1}
+\mathbf{K}_{j,p}-\mathbf{T}_{j,p}\right\|_2^2.
$$

The training cohorts contain 179,036 pixels in A and 155,786 in B. Each reference receives weight one-half. Held pixels never enter this objective. The fit does not optimize the supplementary center metric; center pixels belonging to the original training cohort participate normally.

[fit.json](fit.json) records one solve, eight charged quadratic evaluations and condition number 135.465245. The feasible stationary proposal has gain 0.5341480927022242, bias 0.4627718635737796 and white response 0.9969199562760038. The equal-reference training MSE falls from 0.0432563607043 to 0.0171049358147. This is a proposal model, not an acceptance score.

The original [as-run fit record](fit-as-run.json) mislabeled center participation. The [metadata correction](metadata-correction.json) explains the distinction between normal training-center pixels and the separate center guard. No arithmetic, training cohort or parameter changed, and the fit was not repeated.

## Exact zero control and actual composites

The [unit control](zero-control.json) recovers both saved H1 sample arrays and complete composites bit-exactly. It uses retained samples only, with no rays, source query, filter or geometry render. The two cached unit controls are recorded separately from candidate observations.

Actual response arithmetic promotes inside samples to float64, multiplies and adds, audits values before clipping, clips, then casts to the original sample dtype. Clear samples are copied unchanged. Native float32 mean composition follows the original order. [run.py](run.py) preserves every raw response, sample array, coverage, lens/clear contribution and complete composite.

The quadratic model uses float64 accumulation. Its unit residual against native composition is at most 7.46e-8 in normalized RGB. At the half-step, actual/model differences are below 1.0e-7. Original native scoring decides all guards; these model discrepancies are disclosed, not used as regression tolerances.

Whole and required inside samples have zero out-of-range values before material, before clipping and after clipping. Coverage and clear samples remain exact. The finite source proof transfers because source coordinates, incident kernels, source bytes and every scoring mask remain unchanged.

## Predetermined factors and guards

Only the full and half factors ran. The half-step is the first strict candidate, so the declared quarter and eighth factors were not evaluated. Its exact response is

$$
\begin{aligned}
g&=0.7670740463511121,\\
b&=0.2313859317868898,\\
g+b&=0.9984599781380019.
\end{aligned}
$$

| Case | Candidate | E | SSIM | Center RGB RMSE | Disposition |
| --- | --- | ---: | ---: | ---: | --- |
| A | H1 baseline | 68.286560329 | 0.864096463 | 21.289446987 | Reference |
| A | Full | 44.126319577 | 0.894484758 | 29.969479729 | Center failure |
| A | Half | 51.541175601 | 0.888453722 | 4.994948446 | All proposal guards pass |
| B | H1 baseline | 36.215046603 | 0.935159802 | 12.158390735 | Reference |
| B | Full | 22.811385145 | 0.946173906 | 17.929280083 | Center failure |
| B | Half | 26.858636776 | 0.943035066 | 5.083740190 | All proposal guards pass |

The [full result](1p0-result.json) improves original E, glass, rim, held, interior, SSIM and exterior in both cases. It is nevertheless rejected by the predeclared center criteria. The [half result](0p5-result.json) passes those same original guards and both center criteria. No epsilon or tie waiver is used.

Supplementary center guards use float64 residual accumulation from the frozen native float32 target, consistently for baseline and candidates. Historical crop diagnostics retain their float64 PNG decoding convention. Their few-millionth-level differences are disclosed; neither original metrics nor historical crop results were rewritten.

## Fixed crops, color and unresolved structure

Both half-step [A](0p5-a-comparison.png) and [B](0p5-b-comparison.png) previews were inspected. Central tones improve without the full step's excessive whitening. The entire lens remains too uniform, and the wide upper/lower returns and reflective rim remain absent. No physical illumination, refraction improvement or successful transfer is claimed.

[A](a-fixed-crops.png) and [B](b-fixed-crops.png) crop sheets retain the exact four historical rectangles. [diagnostic.json](diagnostic.json) reports RGB, luminance, chroma, signed RGB and detail measures for every crop. The following advisory RGB errors expose the full-step regressions instead of hiding them behind aggregate improvement.

| Case and crop | H1 RGB RMSE | Full RGB RMSE | Half RGB RMSE |
| --- | ---: | ---: | ---: |
| A upper-left | 45.606394 | 34.196912 | 35.850863 |
| A lower-left | 58.463013 | 33.132742 | 42.495966 |
| A right-rim | 90.954823 | 48.849616 | 69.130108 |
| A center | 21.289442 | 29.969485 | 4.994953 |
| B upper-left | 25.074438 | 10.840472 | 16.966020 |
| B lower-left | 44.797152 | 22.904499 | 33.663496 |
| B right-rim | 14.509311 | 20.471253 | 11.961633 |
| B center | 12.158388 | 17.929283 | 5.083742 |

The half-step improves aggregate RGB, luminance and chroma errors in all four crops of both references. This does not mean every pixel improves. A center retains signed RGB residuals about positive 6.053, negative 0.462 and positive 5.441 levels. B right-rim changes to a small positive mean bias, despite its lower aggregate error.

The full step worsens both center RGB/luminance errors and B right-rim RGB/luminance/chroma errors. Its A center chroma error rises from 5.470 to 12.952. These failures support the need for the protected-center criterion. No crop mask was changed or used as a per-region material coefficient.

## Budgets, status and next review

| Quantity | Actual | Declared cap |
| --- | ---: | ---: |
| Proposal fits / starts | 1 / 1 | 1 / 1 |
| Quadratic fit evaluations | 8 | 128 |
| Candidate pairs | 2 | 4 |
| Candidate native composites | 4 | 8 |
| Cached unit controls | 2 | Predeclared controls |
| New rays / graph evaluations | 0 / 0 | 0 / 0 |
| New source queries / filters | 0 / 0 | 0 / 0 |
| Baseline geometry renders | 0 | 0 |

The [ledger](ledger.json) retains actual usage. Candidate model-residual diagnostics are not additional fits. Source/mask hashes, the original H1 cache and all previous evidence remain fixed. Historical pass09 stays separate and better overall; its original error guards still fail here. No new acceptance or fidelity count is recorded.

The half-step is proposed for primary review only. No subsequent fitting is authorized by this packet. Outline, shadows/glow, foreground, dispersion and final review remain required or explicitly incomplete. No reflection environment, new light, shared tracer change or surface revision was invented to manufacture a rim.
