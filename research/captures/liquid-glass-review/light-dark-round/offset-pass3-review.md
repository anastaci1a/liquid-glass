# Pass3 offset-only candidate — primary review required

From accepted pass2s1.1, tested **s1.2 first**, relative to ORIGINAL K/H offsets. It qualifies numerically; stopped after one pair. No1.15/1.05 probes, new derivative, fit, opacity/width/source/theme coefficient change. Reconstruction count stays2/3 until independent acceptance.

| Exterior guard | Accepted pass2 | s1.2 candidate |
| --- | ---: | ---: |
| Light frozen0..35L | 3.799672037830 | 3.794838170659 |
| Light full visible | 4.590210164616 | 4.565301503964 |
| Dark frozen0..35L | 2.085315225597 | 2.057697422423 |
| Dark full visible | 3.878724477517 | 3.712516472305 |

Every original float32 score dictionary remains EXACT, including SSIM/gradient/selection_loss. Four opacity/sigma coefficients fixed; only shared offsets K=(0,.072)L/H=(0,−.48)L. Original geometry/material/source/body4×4 AA and masks remain frozen. Original finite whole/ALL-scored source-domain proof transfers unchanged; estimated/unobserved-source limitations remain. Exterior-only reconstruction/Eoptical tie, no refractive identification or credit for copied-context removal.

Both720px/side triptychs inspected. Advisory far-upper light .35–.7L improves2.382126→2.241636 and .7–1.2L2.439108→2.406392 relative to pass2, but remains worse than zero-generated baseline1.636898/.893942. Dark lower .2–.35L .035272→.024408 still exceeds zero-generated0. Dark lower .7–1.2L .141483755947653→.141483755955542 rises slightly; retained without epsilon waiver. Far bands never change native scoring masks. Broader dark gray field, Ksigma.7 bound and lighting/source ambiguity remain explicit.

Evidence: `/evidence/extended/helper-toolbar-work/light-dark-round/offset-pass3/` contains exact candidate recipe, complete arrays, one-trial ledger, guard result, comparison PNGs and `far-bands-advisory.json`. Driver `light-dark-round/offset-pass3.py`, copied at evidence root as `offset_pass3.py`. Completed command:

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/light-dark-round/offset_pass3.py
```

Immediate readiness queued61522d7d-a791-444a-b485-a429e6931c7a; sharedflag raised. Accepted pass2 publication delta is separately ready, queued424fb4c0-7b2b-4e89-b787-cac01106635b. Motion planning only, no export before final recipe review/direction. No public edit/commit or additional fit.
