# Compact saved outer/material backtracks: .125 qualifier

READY for independent primary replay/source/visual/precision review. Accepted count remains **2/3**. Original score/source epoch is unchanged. One saved proposal, no new solver or derivatives, no repeated full trial. Remaining exactly .5/.25/.125 steps rendered from accepted pass2; total original+remaining = four authorized native trial pairs.

| Ref | Accepted pass2 E | Candidate E | Baseline glass | Candidate glass | Exterior RMSE |
|---|---:|---:|---:|---:|---:|
| A | 4.988892430407189 | 4.988887781303395 | 4.3695149421691895 | 4.369511127471924 | 4.954218705118386 (exact unchanged) |
| B | 4.831039280838589 | 4.831007502658002 | 4.321903228759766 | 4.321866035461426 | 4.243026628824928 (exact unchanged) |

| Protected full-box MSE | Accepted pass2 | Candidate |
|---|---:|---:|
| A jupiter.jpg | 1802.8430711477995 | 1802.8430711477995 |
| A title.svg | 413.37720109149814 | 413.37720109149814 |
| A artist.svg | 13.20065052350401 | 13.20063349121483 |
| A play.svg | 64.97489030880388 | 64.97489030880388 |
| A forward.svg | 150.09487582719885 | 150.09458817075938 |
| B jupiter.jpg | 1901.9035917241126 | 1901.9035917241126 |
| B title.svg | 362.18240924645215 | 362.18204589094967 |
| B artist.svg | 19.89027702366002 | 19.890261883847415 |
| B play.svg | 64.94458040397149 | 64.94438358640764 |
| B forward.svg | 153.3030778169632 | 153.30300211790018 |

Actual .125 movement: c0/c1/c2 [0.0000018179535899019578,0.00001869507122668451,-0.000125]; max shared-material movement 0.00002292333768837903. Other optical/shape/source/kernel/foreground/shadow/mask parameters fixed.

**Primary precision check:** SAME saved float32 arrays, target, and masks reduced in float64, using direct mean(2*baseline_error*pixel_delta+pixel_delta²) to expose residual changes without subtraction cancellation. A weighted loss change -0.0000433290033581452, E change -0.000004342549401847862; B weighted loss change -0.0003057668485732267, E change -0.000031646177384381247. Both glass/rim residual MSEs decrease under this review. This supplements primary acceptance only; it does not replace the original float32 gate or create a new epoch. No epsilon allowances.

Preserved outcomes: full step PASS original float32 gate, HOLD primary acceptance due genuine advisory A residual increase; no retroactive relabeling. .5 step: both native/advisory E improve, but A play MSE worsens +0.000007569906301796436, strict rejection. .25 step: both E improve, A title worsens +0.00006055925041437149, strict rejection. .125 passes original all ten foreground/artwork, both E/glass/exterior AND nonincreasing advisory double E, so stop. No fifth trial, resettlement, optimizer restart or hidden failure. Parent artifacts/capped60 solver/model tiny negative constraints remain immutable.

Fresh smaller-map source check: **each** observation whole587896 and ALLscored332048 subrays, including30 scored rays outside corrected outline. Defined and observed confidence minimum1 for all cohorts; zero unsupported; Gaussian radius21 nativepx (3sigma). Unsupported-ray arrays empty. Earlier full-step map proof was not reused for the new map. Discrete original2x2 grid + finite3sigma support only, not continuous/infinite kernel theorem. No source, masks, glyph/artwork or epoch changes.

Packet: /evidence/extended/helper-toolbar-work/compact-mini-round/outer-material-pass2/precision-backtracks. Recipes candidate-native.json and candidate-normalized.json; selected material arrays trial3-ref0-material.npy and trial3-ref1-material.npy (index3 of total original4, NOT trial0full or remaining1/2 failures). Saved ref0/1-complete.npy, alpha.npy, all scores/review residuals in result.json/trials.json, fresh-source-proof.json. Both1080-width candidate previews inspected: tiny change, no obvious new artifact; independent primary visual review required. Target/baseline/candidate1080x282 PNGs are presentation resizes of native920x240 arrays, no4x/new optical sampling. Existing material/source/artwork uncertainties remain.

Command: docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/compact-mini-round/outer-material-precision-backtracks.py

Driver refuses completed reruns. Frozen code ad934e02, current-public replay to be performed independently by lead. No public edits/commits. Shared flag READY_FOR_PRIMARY_PRECISION_PASS and native queued lead message561a620f-973d-41e9-b0cb-87ffc40e0282. Queue acceptance is not consumption/primary acceptance. Requested next task: if accepted third, final1080 motion plus rotation; otherwise primary bounded guidance. No further fitting started.
