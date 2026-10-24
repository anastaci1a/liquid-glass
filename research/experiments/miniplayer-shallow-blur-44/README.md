# Shallow-model incident blur: keep the existing width

Neither fixed incident width passes all four shallow-model guards. The narrower width worsens every aggregate error. The wider width helps expanded B and compact B but retains body, foreground or partial-boundary failures. Sigma 6.75 native pixels stays frozen; no blur increment is adopted.

| Reference | Shallow baseline E | Sigma 5.0625 E | Sigma 8.4375 E |
| --- | ---: | ---: | ---: |
| Expanded A | 8.190509 | 8.656948 | 8.541322 |
| Expanded B | 7.072735 | 8.433636 | 6.888818 |
| Compact A | 22.547641 | 22.939613 | 22.694715 |
| Compact B | 21.610871 | 22.195552 | 21.229290 |

## Correct operation and support

Filtering acts on the incident background before refraction. Actual shallow42 coordinates, primary power, annular light 4, common tone, AA2 and original foreground stay fixed. Reflected light is not blurred. Clear samples remain cached and unchanged.

All eight finite-kernel gates pass before changed RGB. Four pre-foreground, completed-image and score identities are exact. Input, mask and shared-code hashes match. The [source proof](source-FIRST.json), [checkpoint](checkpoint.json), [input bindings](inputs-FIRST.json), [ledger](ledger.json) and [result](result.json) preserve exact decisions.

Radii are 16 and 26 native pixels. Exact new widths are not quarter-bin rounded. All original current-working, numerical-baseline and shallow42 guards remain separate. No partial pixel, source region, score threshold or foreground style changes.

## Accounting and clock

The [protocol](protocol.json) runs from 10:50:57.762 to 11:10:57.762 UTC. Science finishes at 10:54:37.853. The [prospective continuation](continuation.json) records remaining stage caps without retroactively inventing an earlier full-cycle clock.

| Work | Actual |
| --- | ---: |
| Inside source audits / RGB queries | 5948340 / 5948340 |
| Bilinear known-mask lookups | 23793360 |
| Incident fields / source-known erosions | 8 / 16 |
| Candidate composites / cached identities | 8 / 4 |
| Score calls / metric Gaussians / metric erosions | 12 / 60 / 12 |
| Original mask constructor pixels | 1121600 |
| Rays, heights and fits | 0 |

The result is an assessment of ordinary transmitted softness, not roughness identification. Thin-rim brightness, cap illumination and source-feature placement remain unresolved. The next isolated common-color stage keeps the original width and light fixed; no rejected width transfers into it.
