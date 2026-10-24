# Independent miniplayer working-output review

**PASS WITH LIMITS.** The four frozen factor-0.5 outputs reproduce exactly, including every pre-foreground and completed pixel. Every reported score, fixed crop, partial-boundary and foreground metric matches. The selected and held guard decisions independently match. This verifies implementation, not strict all-guard acceptance or a new fidelity count.

## Clock and frozen scope

The review started at 08:44:23.938 UTC on 24 October 2026. Its hard deadline is 08:54:23.938 UTC, including checks and versioning. The scientific checkpoint is `2c90bd1d`. Root files were read only. Changing factory, working-recipe, registry and gallery metadata were excluded from the frozen hash set.

Only the four half-step outputs were replayed. No alternate factor, baseline reconstruction, geometry evaluation, optical source lookup or new material proposal ran. The existing source-first proofs and input identities were reused, not repeated. Source availability remains conditional mosaic support rather than observed hidden photography.

## Exact reconstruction

The replay uses retained raw source samples, actual inside membership, cached primary power and front-reflection directions/power from inverse-forward 18. The common recorded coefficients are gain 0.5552987769129158 and bias 0.3908368353448866. Outside samples stay unchanged. Both lengths and all four references use the same response.

The incident encoded proxy is decoded before multiplication by actual primary power. Direct-front annular radiance four is added in linearized space. The result is encoded, bounded as in the original recipe, averaged using the original AA2 reshape/mean/cast, and passed through the complete original ordered foreground and artwork chain.

$$
C_{\rm lens}=\operatorname{encode}_{\rm sRGB}
\left(T_{\rm primary}\operatorname{decode}_{\rm sRGB}(gS+b)+4R_{\rm front}E(\boldsymbol d_{\rm front})\right).
$$

The environment term is hypothetical. Incident frosting and encoded tone are not applied to its radiance. Later reflected power remains unassigned. The shared body response is an empirical proxy under explicit interface power, not measured Apple radiometry or a complete scene.

## Exact numerical findings

| Reference | E | SSIM | Frozen partial RMSE | Failures against selected baseline |
| --- | ---: | ---: | ---: | --- |
| Expanded A | 7.883486797181998 | 0.9816307425498962 | 40.32682800292969, 16 pixels | Partial boundary |
| Expanded B | 6.149429642470981 | 0.979114830493927 | 26.08043098449707, 16 pixels | Artwork and artist |
| Compact A | 20.53187643383762 | 0.9635760188102722 | 23.813167572021484, 22 pixels | None |
| Compact B | 19.68186325372886 | 0.9629939794540405 | 21.07662582397461, 22 pixels | None |

Expanded A also fails the explicit-power held partial guard. Expanded B fails that held partial guard despite passing it against the selected baseline. All other reported selected and held decisions match the independent scalar comparisons. Zero clipping is recorded in the frozen primary records; this peer did not add an independent clipping pass.

All original glass, rim, held, interior, aggregate, SSIM and exterior metrics match. All five artwork/vector region metrics per reference and every fixed crop RGB/signed-luminance metric match. The original 16- and 22-pixel cohorts are preserved. No new coverage cohort replaces an old guard.

## Visual review and family scope

All four saved full panels were inspected. The body tone is closer, particularly on compact. Thin lower-perimeter light, cap texture and reference feature placement remain wrong. Expanded A lacks the reference's crisp lower line. Expanded B's left cap and broad right return remain different; artwork and artist backing errors remain numerical failures.

The inverse-18 driver uses one canonical front and inverse back cross-section on both accepted rounded footprints; only major length changes. Case translation, source content and original foreground remain inputs. This review verifies those retained outputs, not a newly changed factory. Compact participated in the four-reference material training, so no color-holdout claim applies.

## Work and provenance

| Work | Actual |
| --- | ---: |
| Cached candidate composites | 4 |
| Study constructors / mask pixels | 4 / 1,121,600 |
| Score calls / metric Gaussians / erosions | 4 / 20 / 4 |
| Cached annular direction evaluations | 1,487,085 |
| New rays, heights, source queries, filters, Fresnel calls and fits | 0 |

Scientific, code and input first/last hashes match. Original input and source-proof identities match the earlier peer26 bindings. The consumed replay definitions match immutable `2c90bd1d`. Current environment code appends an unrelated two-interface helper after that exact source prefix; the helper was not called. No moving code was merged or copied.

An initially overbroad historical-code comparison flagged subsequent geometry/environment additions. This was a metadata-scope check, not a numerical discrepancy. It was documented and narrowed to the consumed definitions and original inputs. No composite, metric, source proof or optical computation was repeated. The scientific replay completed once with no discrepancy.

The unchanged baseline, held failures, original counts and prior negative evidence remain intact. An explicit primary-working display choice is separate from guard acceptance. This report does not authorize source repair, a new material factor, environment calibration, target rotation or a full-pipeline pass.
