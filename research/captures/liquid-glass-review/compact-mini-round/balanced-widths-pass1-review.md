# Compact balanced widths: zero proposal

Accepted baseline: Compact pass1 a92fc7bd; fixed material, source, shape, masks, SVG/artwork and native scoring. Accepted count remains 1/3.

One two-width quadratic proposal used ONLY retained +/-0.00025 images. Thin response uses accepted pass1; rim response comes from nearby PRE-pass1 material and width, explicitly a proposal surrogate, not a compatible exact Jacobian. No repeated derivatives or source/native baseline replay.

The bounded optimizer returned delta rim_width=0 and delta thin_width=0, predicted objective change zero. Four coordinate-extremum linear programs over normalized saved-response guard gradients independently found only the zero tangent-cone point. No native candidate was proposed: ZERO actual native backtracks, no tie pass, no new preview, no acceptance/count.

Reason in the saved model: A title/artist/play/artwork request nonpositive rim movement, while A forward and B title/artist/play/forward request nonnegative rim movement; thin-width has zero protected-foreground response here. Thus rim must be zero. With rim zero, A E/glass request nonnegative thin movement and B E/glass nonpositive thin movement. The corresponding local quadratic forms are positive semidefinite; no modeled guarded descent remains. This model limitation does not prove all native nearby combinations impossible, especially because the rim surrogate uses older material. No precision waiver or invented direction was used.

Evidence: /evidence/extended/helper-toolbar-work/compact-mini-round/balanced-widths-pass1/{started.json,saved-response-forms.json,proposal.json,guard-cone-check.json,result.json}. Script: same parent/balanced-widths-pass1.py. Original rejected four rim trials, joint full-step rejection/solver-cap evidence, and four thin trials are unchanged. Original whole/scored source proof transfers unchanged; no new rays or target/source changes.

Command: docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/compact-mini-round/balanced-widths-pass1.py

Next task request: ONE bounded thin_width + common-material compensation proposal, using retained thin responses and prior material-response evidence only as a proposal surrogate where not exactly compatible. The thin step changes glass residual without changing protected glyph/artwork scores at all four tested samples, while the previous accepted rim/material compensation established a useful shared-material direction. Any proposed compensation still needs actual strict all-guard native replay, at most four backtracks, with source/shape/glyphs fixed. No fit started; lead should authorize its bounds or assign another short existing family.
