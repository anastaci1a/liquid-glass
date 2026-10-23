# Short navigation proposal: outer normal neighborhood

Prospective Ana rule applied: no minimum percentage gain; E and original glass/exterior/foreground guards must not regress in either reference, with meaningful improvement beyond numerical noise. No historical result reclassified. Toolbar41 already completed once and remains unadopted; toolbar42/43 remain deferred under current authoritative rotation.

One compact neighborhood completed on the paired public pass24 baseline: shared c0,c1,c2 each ±.002, six neighbors total, no optimizer. Material, gamma, blur, geometry, shadow, sources, all SVGs/styles, native AA and original masks fixed. Every trial retained; zero accepted proposals and no counted passes.

|Shared change|E A|E B|
|---|---:|---:|
|baseline|1.979013168449|7.434360042278|
|c0 −.002|1.979129501772|7.434308850188|
|c0 +.002|1.978894027130|7.435570794651|
|c1 −.002|1.977593195975|7.435431771810|
|c1 +.002|1.980473665593|7.433312521359|
|c2 −.002|1.976158607158|7.436548534860|
|c2 +.002|1.981931390007|7.432016558098|

All six fail both-reference nonregression: improving one reference worsens the other, in both E and glass. All eight scored foreground MSEs per reference and generated exterior RMSEs remain exactly unchanged. No rim-only or crop-only result accepted.

Both original native Study.render baselines reproduce public loss within 1e−6; public ProfileCache at zero differs by exactly0 in every material pixel and E. All candidate scores use the original native source sampler and float32 reduction, not a smooth surrogate. Final independent Study.render and source-support checks are scripted only for a qualifying candidate; that branch did not activate. Thus no changed-map source confidence or final replay/HQ/visual acceptance is claimed. Frozen code/input digests and masks are saved; old source provenance remains conditional, not unknown-ink truth.

Next short proposal: use these retained score responses to assess ONE joint outer-normal trust step with total coefficient movement ≤.002 and linearized E/glass nonregression in BOTH references. At most one direct native proposal and one predetermined half-step check if supported; if the retained responses do not support it, stop without rendering. Coordinate-neighborhood failure is not proof that a joint direction cannot improve. No new derivatives, source/shape/material changes or speculative operator needed. This is a proposed next budget, not an evaluated candidate or pass.

Artifacts: dark-glass-lab/extended/helper-toolbar-work/navigation-round/short-outer-profile/{run.py,freeze.json,baseline-public.json,baseline.json,zero-controls.json,trials.json,result.json,0-baseline-material.npy,1-baseline-material.npy,0-frozen-masks.npz,1-frozen-masks.npz,code/,a/,b/}. All large data are on the evidence mount. Canonical private driver: navigation-round/short-outer-profile.py. The completed-run guard prevents an accidental repeat; partial runs require explicit artifact inspection.

Exact completed command:

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile/run.py

Advisory toolbar diagnostic update preserved separately: upper rim [650,369,1270,468]; letter-refraction crop should adjoin the bottom edge. No old diagnostic overwritten and no full scoring mask changed. These toolbar coordinates are not transplanted onto navigation's different geometry.
