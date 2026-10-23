# Compact thin width + shared material candidate

READY for independent primary verification; accepted count remains **1/3** until primary replay, source and visual acceptance. Baseline is accepted Compact pass1 a92fc7bd.

| Ref | Baseline E | Candidate E | Baseline glass | Candidate glass | Exterior RMSE |
|---|---:|---:|---:|---:|---:|
| A | 4.989872157275395 | 4.988892430407189 | 4.370216369628906 | 4.3695149421691895 | 4.954218705118386 (unchanged) |
| B | 4.833047741361025 | 4.831039280838589 | 4.3235859870910645 | 4.321903228759766 | 4.243026628824928 (unchanged) |

| Protected full-box MSE | Baseline | Candidate |
|---|---:|---:|
| A jupiter.jpg | 1802.8433133848011 | 1802.8430711477995 |
| A title.svg | 413.3821669500321 | 413.37720109149814 |
| A artist.svg | 13.200667555793189 | 13.20065052350401 |
| A play.svg | 64.97493572824169 | 64.97489030880388 |
| A forward.svg | 150.10429279063828 | 150.09487582719885 |
| B jupiter.jpg | 1901.9035917241126 | 1901.9035917241126 |
| B title.svg | 362.18246980570257 | 362.18240924645215 |
| B artist.svg | 19.895269376866054 | 19.89027702366002 |
| B play.svg | 64.94619279401377 | 64.94458040397149 |
| B forward.svg | 153.31376652466133 | 153.3030778169632 |

ONE bounded existing thin_width + shared 23-material proposal. Thin increases by 0.0000625 (quarter of proposed 0.00025); maximum material movement 0.00042343111596820487, below allowed 0.005 each. All geometry, source kernel, output blur, gamma, shadow, shape, SVG/artwork, foreground styles and native masks remain fixed. No per-image/glyph coefficients.

Saved accepted-pass1 thin +/-0.00025 responses reused; no repeated thin derivatives. The pre-pass1 material basis uses another rim_width and clipping state and was not assumed compatible. Constructed ONE accepted-state analytic 23-material Jacobian per reference. Cached zero controls are exactly0 against saved accepted material arrays for both references; no duplicate full native baseline render. Saved formulas/normalized material J are in packet. Files called normalized-rim-J.npy inherit the earlier driver's label but contain the SAVED THIN secant in this study; no rim parameter varied.

Solver reached its 60-iteration cap with success=false; model residual minimum -1.999006199051144e-9. Preserved in proposal.json, never used as acceptance. Full native step rejected B title MSE +0.000030279625207185745. Half step rejected B artwork MSE +0.00024223700165748596. Quarter step passes EVERY original both E/glass/exterior + all ten foreground/artwork guards without epsilon. Exactly three native trial pairs; stopped first qualifier. All three pairs of native material arrays retained. Quantization-derived meaningfulness floor is used only to reject ties, never to forgive regression; both E improvements exceed it.

Candidate native recipe: /evidence/extended/helper-toolbar-work/compact-mini-round/thin-material-pass1/candidate-native.json. Public normalized recipe: candidate-normalized.json. Selected material arrays are trial2-ref0-material.npy and trial2-ref1-material.npy (NOT rejected trial0 or trial1). Also saved ref0/ref1 complete.npy and alpha.npy, target/baseline/candidate-width1080.png, complete score records result.json and trial history. No success count or public edit.

Both candidate and accepted-baseline 1080x282 previews visually inspected: subtle changes, no new apparent artifact. Existing broad B upper transition and A cap/text refraction remain; numerical gain is small. Preview is approved width1080 presentation from native920x240 arrays, not a fresh high-resolution optical replay or 4x source grid. Nearest-defined presentation background only, scored material unchanged, no copied target shadow. Independent primary visual review remains required.

Original whole587896 + allscored332048 ray source proof per scene transfers: only lighting thin width and shared material changed, no map/kernel/grid/input/foreground/mask change. Proof is discrete native grid + finite Gaussian3sigma support, not a continuous/infinite-support theorem. Original source confidence/epoch unchanged.

Reproduce (immutable driver refuses completed reruns): docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/compact-mini-round/thin-material-pass1.py

Code remains private committed-main ad934e02 snapshot; primary independently replays using current public Study. Original rim failures, prior joint full-step rejection/capped solver, thin failures and balanced zero model are untouched. No further local settlement started. Next bounded task requested from lead, pending acceptance.
