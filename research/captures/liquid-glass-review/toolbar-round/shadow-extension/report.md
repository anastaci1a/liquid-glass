# Separate wider-shadow study — no optical pass

Authorized by lead06:31. Independent analysis uses accepted revision1 .10/1.25 geometry/material, not the unaccepted inner-profile proposal. All conditional glass/rim pixels and E remain unchanged. Original source, registration, fixed exterior mask and farther-band diagnostics are preserved. No reference residual, original shadow or target pixels are pasted into the generated shadow.

Three bounded Powell starts fit neutral Gaussian-convolved shape coverage, sigma.012–.6L/opacity0–.4/xoffset±.05L/yoffset[-.1,.15]L. All three report local convergence and approach the upper sigma bound. Best recipe in `recipe.json`:

- Opacity .21007040123806414.
- Sigma .5999981597482248L (about102 native px atL170).
- Offset[-.005646641969763537,.012029212673096461]L.
- One shared neutral attenuation field behind the independent sharp glass coverage. Source/material/optical recipe remain revision1.

| Fixed diagnostic | Revision1 shadow | Wider shadow |
| --- | ---: | ---: |
| Exterior0–35px total RMSE | 11.469442019668 | 10.929248298449 |
| 0–10px | 14.856234417577 | 14.335852646670 |
| 10–20px | 8.615009486454 | 8.685168568998 |
| 20–35px | 10.680273642782 | 9.705879445106 |
| Advisory35–55px | 15.765414121129 | 13.217023151108 |
| Advisory55–80px | 18.271628137786 | 14.270167796437 |

The10–20px band regresses slightly and remains visible in the evidence. Farther-tail and total exterior errors improve. Width still reaches the new .6L bound, so no unique physical width/light rig or final shadow accuracy is established. Do not silently extend it beyond the authorized bound; source blank-field assumptions still condition this calibration.

`result.json` correctly fails the optical milestone because E does not change. This is an uncounted shadow analysis, not a new successful optical pass and not a source-epoch correction. Primary can independently assess whether to integrate it with an appropriate complete checkpoint; agent has not combined it with the pending inner-profile candidate or changed that immutable proposal.

Files: study.json preserves all starts/vectors/objectives/convergence; recipe.json/scores.json/result.json; clean-preview.png. Actual profile compositing uses padded crop-independent shape convolution, not a clipped diagnostic shadow. Same renderer primitive as the earlier generated-shadow proposal; no new rendering technique needed. No commits/shared source edits. Queue continues with second-real-observation assessment; promising-geometry final support/crop/replay package follows, with the required next-steps request before that final queue item.
