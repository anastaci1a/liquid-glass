# Navigation third-pass candidate: balanced existing lighting widths

FIRST trial qualifies numerically; stopped immediately, zero backtracks. Accepted pass2 baseline441d368. Delta rim_width−.000125, thin_width−.00002, both within .00025. Final widths .01629272149005208/.03220754078699499. ALL other parameters and material coefficients fixed. No derivatives, optimizer, convergence chase, new optical family, public edits, commits or automatic acceptance/count.

|Original native metric|A accepted pass2|A candidate|B accepted pass2|B candidate|
|---|---:|---:|---:|---:|
|E|1.976554458704428|1.975144447494413|7.430088836808378|7.429450917901889|
|glass RMSE|1.608913302421570|1.607869863510132|6.041206836700439|6.040733814239502|
|rim RMSE|2.642439603805542|2.640406370162964|9.942986488342285|9.942068099975586|
|exterior RMSE|8.735226423581446|8.735226423581446|9.774154815950626|9.774154815950626|

ALL16 foreground MSEs EXACTLY unchanged. Original bothE/glass/exterior/foreground guards pass strictly. E decreases .001410011210015/.000637918906489. Advisory interior A .769259691238→.769260048866 tiny worsening explicitly retained; B unchanged2.855348587036. No additional interior gate silently added or waived.

The direction uses SAVED actual scalar responses: half of the accepted −.00025 rim step, plus8% of the failed −.00025 thin step. Rim previously helped both references, thin−helped A while costing B. Predicted changes and limitations (different starting rim width, unknown mixed/clipping effects) are retained in proposal.json. Native direct Study.render alone selected this candidate; old negative thin/material/inner results remain negative, not reclassified.

Both changed widths affect existing neutral lighting basis only. Source lookup geometry, ordinary source/output blur, gamma/material, silhouette, shadow, solid glyphs/styles, source/target/known hashes, original masks and AA unchanged. Primary accepted pass2/pass1 center AND emitted-ray support proof transfers; no repeated source/baseline replay solely for logs. This is not dispersion, source correction or a changed sampling epoch.

Inspected both1080-width target/baseline/candidate stacks (individual1080×335, stack1080×1005). Small change/no obvious new artifact; existing B upper/left dark rim persists. Unknown exterior uses nearest-defined RGB for unscored presentation only on both baseline/candidate; raw material/complete/alpha/scoring/source untouched and generated shadow not copied from target. No4x render or new source adoption.

Private immutable evidence /evidence/extended/helper-toolbar-work/navigation-round/balanced-widths-pass2/{started.json,proposal.json,trials.json,result.json,candidate-native.json,candidate-normalized.json,trial0-ref0-material.npy,trial0-ref1-material.npy,ref0-complete.npy,ref1-complete.npy,ref0-alpha.npy,ref1-alpha.npy,ref{0,1}-{target,baseline,candidate}-width1080.png,ref{0,1}-comparison-width1080.png}. Baseline/input/code freeze remain in rim-width-neighborhood and short-outer-profile. Driver navigation-round/balanced-widths.py; frozen invocation copy short-outer-profile/balanced-widths-run.py.

Exact completed command:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/balanced-widths-run.py

review-ready.json READY_FOR_PRIMARY, candidate=true, accepted_count2. Need primary independent replay/1080visual/source acceptance, then third commit/push and Navigation-only merge before rotation. No premature merge of this incomplete round by helper. Compact mini-player is already approved as next distinct element after those conditions; read-only intake next-element-compact-mini-player.md is prepared, no next-element fit/worktree edits started. Lead next Home, no overlap. Explicit Ana pauses override continuation.
