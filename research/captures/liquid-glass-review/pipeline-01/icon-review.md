# Icon stage closed: no accepted revision

The original SF play path was tested with uniform scale and translation only (48 raster evaluations). A separate clean symmetric rounded triangle uses three straight edges and circular corner arcs, with equal upper/lower geometry (72 evaluations). Both fit the old approved coverage, not reference RGB. Neither qualifies: correct full-foreground MSE is 98.16660 for the incumbent, 130.63246 for the SF proposal and 120.47261 for the clean trace. The exact UI font weight remains unverified. Both solid vectors and provenance are saved for reuse; no screenshot matte is embedded in either SVG.

![Reference, incumbent and rejected clean symmetric vector](../../dark-glass-lab/extended/playback-pipeline-01/icon/clean-trace-comparison.png)

The inherited icon response was separately tested with current geometric background inputs and common gamma multipliers. Eight actual composites exhausted the declared budget. With the frozen old shape, the current raw geometric input gives foreground MSE143.83281; common gamma1.1 gives117.37453. Neither beats98.16660. No shape/material change is accepted. The final icon still depends on the historical empirical material and raster coverage; this remains an explicit uncompleted part of unification, not a new physical foreground model.

A supplemental-check implementation error initially reversed the xs/ys outputs of points(), making the foreground test sample235 wrong pixels instead of52998. The original scores() function and exterior mask were unaffected. The initial icon result.json and sheet captions are preserved but SUPERSEDED by corrected-checks.json, final-correction.json and trace-result.json. No false tie or false vector acceptance is adopted. Saved-array correction also confirms the blur stage improves real foreground MSE98.65575→98.16660 and exterior24.09012→24.06740. Original body scores remain unchanged.

One syntax error occurred before any execution/raster evaluations, corrected once. The final two material controls used the remaining two of eight evaluations after the measurement correction. The clean-trace comparison supersedes the initial mistaken-acceptance shape sheet. No new ray tracing, source lookup, fit family, dispersion or motion was performed.

Stage closed early within its30-minute cap; useful negative, not a completed solid-icon replacement.
