# Compact thin-width neighborhood: negative

Baseline: independently accepted Compact pass1, joint-rim-material/candidate-native.json. Accepted count remains 1/3. Four actual native trial pairs; no derivatives, optimizer, baseline replay, source edits, or additional trials.

| thin_width delta | A E | B E | Failed strict guards |
|---|---:|---:|---|
| -0.00025 | 5.005846825819 | 4.833004101782 | A E + glass |
| 0.00025 | 4.977970146016 | 4.837002810192 | B E + glass |
| -0.000125 | 4.997350234116 | 4.832533521335 | A E + glass |
| 0.000125 | 4.983409343168 | 4.834540620325 | B E + glass |

Baseline E: A 4.989872157275395, B 4.833047741361025. Every exterior RMSE and all ten foreground/artwork MSEs are EXACT unchanged in all four trials. Both signs trade glass/E between references; no candidate, tie pass, tolerance waiver, or acceptance claimed. All eight native material arrays and complete per-trial scores retained under /evidence/extended/helper-toolbar-work/compact-mini-round/thin-width-pass1. No candidate previews generated. Existing rejected joint full step and capped solver record preserved unchanged.

Command: docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/compact-mini-round/thin-width-pass1.py

Source: unchanged map, blur kernel, source/SVG/artwork, shape, masks, epoch and emitted grid; original whole/scored source proof transfers because thin_width is lighting only. Code remains frozen committed main ad934e02, no public edits.

Next task request: ONE bounded joint existing rim_width + thin_width compensation step using retained actual width responses, no repeated derivatives, each movement <=.00025 and at most four native backtracks from accepted pass1. Opposite thin-width E responses rule out a standalone step at these scales; rim-width/material pass1 demonstrates shared lighting compensation can matter. A combined direction must satisfy the original both E/glass/exterior/all10 foreground guards under actual native replay; no feasibility promised. If lead prefers material compensation instead, await its bounded assignment; no unapproved sweep.
