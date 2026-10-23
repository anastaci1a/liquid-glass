# Offset-only numerical qualifier — pending primary acceptance

From independently accepted reconstruction pass1, fixed all four coefficients and tested s in the prescribed order. s=.9 fails; **s=1.1 qualifies**, so stopped after two pairs. No .95/1.05 probes or conditional joint fit. Count remains1/3.

| Guard | Accepted pass1 | s=1.1 |
| --- | ---: | ---: |
| Light frozen0..35L exterior | 3.805386046630 | 3.799672037830 |
| Light full visible exterior | 4.615888110966 | 4.590210164616 |
| Dark frozen0..35L exterior | 2.120522492242 | 2.085315225597 |
| Dark full visible exterior | 4.041905064989 | 3.878724477517 |

All original score dictionaries, including SSIM and selection_loss, remain exact. The frozen near exterior has49,800 pixels and full visible original sd>0 has171,369/theme. Only offsets change to K=(0,.066)L/H=(0,−.44)L; original shape/rays/AA/source/material/four Gaussian coefficients unchanged. Source-domain proof transfers, retaining estimated/unobserved limitations. This is exterior-only reconstruction/Eoptical tie, not optical identification or copied-context removal credit.

720-width-per-side triptychs inspected. Far-upper light bands improve relative to pass1 but retain their regressions relative to zero-generated baseline. Dark lower .7–1.2L advisory RMSE rises .141483755935078→.141483755947653 (tiny tail, no tolerance waiver or gate change); all actual guards strictly improve. Broader dark field and possible lighting/source ambiguity remain unresolved. No image-specific coefficients, source fit, new optical render or public edit.

Exact recipe, complete arrays, comparisons, two-trial ledger and advisory bands: `/evidence/extended/helper-toolbar-work/light-dark-round/offset-neighborhood/`. Driver: `offset-neighborhood.py` here, copied as `offset_neighborhood.py` at the private evidence root. Completed command:

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/light-dark-round/offset_neighborhood.py
```

Readiness queued immediately584d9e03-0516-442f-a415-213ac832bdf8; shared flag raised. No further fits before primary review. Accepted pass1 private publication package is separate and remains pass1, not silently updated to this candidate.
