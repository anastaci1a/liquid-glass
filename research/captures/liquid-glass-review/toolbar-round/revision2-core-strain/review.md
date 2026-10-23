Queue13 potential core strain — tested local family rejected, zero new passes

Accepted rev2 bb1ee80131d39e7661c3d55174767c4d15182e05, epoch d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d; no source/shape/material/glyph/mask/sampling changes and NO unverified curvature combination. One shared scalar, deterministic major axis (horizontal here). Primitive only in agent worktree toolbar_core_strain.py. This adds a potential field to the empirical baseline; only the addition is integrable, not an identified Apple optical solid.

    Psi=(lambda/2)*(e dot position)^2*S(u), u=clip(d/w_core,0,1)
    S=10u^3−15u^4+6u^5
    delta_F=−lambda*[z*e*S + .5*z^2*Sprime*grad(d)/w_core]
    grad(d)=−L*grad(T)/(2sqrt(T)), d=L*(1−sqrt(T))

ACTUAL gradient of the crowned coordinate is used, not its unit normal. The zero-gradient assignment at T0 is harmless because S'=0 in that deep core. Fixed w_core=.30L comes from the accepted material core transition, declared before scores. Deep core is pure major-axis strain(−lambda*z*e). Boundary addition vanishes and baseline edge refraction remains; potential C2/added vector C1 at joins, no C2vector claim.

Declared maximum added displacement.12L gives analytic lambda bracket±.006341257469600858 from triangle bound|delta_F|/|lambda|<=a+.5*a²*(15/8)*max|grad(d)|/w, plus numerical margin. Actual native endpoint maximum.085772363369L. Gradient-vs-finite-potential error2.99e-10L; added-curl/lambda4.13e-7; substituting unit normal gives field error.05243L perlambda. Mirror/90rotation/scale/support/deep strain, zero native material/coverage EXACT and uniform-source endpoint renders EXACT pass.17,382,400native endpoint rays within defined source with47pxmargin; affine coefficient dependence covers the intervening bracket. Defined source remains partly estimated.

Required pre-fit sensitivity, before any bounded proposal: five native points0,±.25/±.5of bracket. Negative−.00317063 improves d3.110433→3.074456 but worsens fullE6.870491→7.057220 and ALL guards. Positive+.00317063 improves upper9.200723→9.136900 but worsens d3.159239 and plusFG. Both signs of tested nonzero strain fail fullnative/foreground gates; no crop-only success. Even hypothetical perfect d with all other frozen pixels unchanged would lower E only to6.83950793(~0.4510%), below.5%; crop success cannot substitute for the whole reference.

Native constrained local proposal analysis at h=bound/32and/64 includes glass/rim/exterior/BOTH foreground quadratics during formation. Largerh admits onlylambda0; finerh admits[0,.00007270302936]. This raster-scale disagreement is retained, not hidden as convergence. Exact native endpoint validation fails a guard; half step+.00003635151468 passes all guards. Eleven unique points/ten new native renders plus one cached baseline across sensitivity, local derivatives and bounded line confirmation. Every phase is ONE study, not separate pass attempts. No previous render repeated.

Best tested guard-feasible E6.870104461783, reduction0.005620% — FAR below.5%(requiredE<=6.836138144960). Glass5.842747688293/rim8.813237190247/exterior11.469442006962; archiveFG13.241892224662/plusFG3.667070319303 hold. Conditional upper9.200723→9.199090, d3.110433→3.110957, underside5.073945→5.073976. Admissible tiny positive strain does not solve the d feedback. Gate false/count0; no independent/visual/HQacceptance claim.

Scope/termination: bounded local confirmation after mandatory sensitivity and conflicting constraint cones, not a global optimization/exhaustive infeasibility proof. No whole-bracket optical search or arbitrary bound widening was launched. Broad tested amplitudes worsen fullframe and protected roles; the locally admissible step gives only numerical-scale gain. No first-threshold stop because no milestone was crossed. Stronger negative-d strain cannot be declared a pass while other errors regress. Current source/glyph assumptions remain fixed; source/provenance work is the authorized next route.

Model review after three substantive families:9outer-normal−.21489% with upper regression;11curvature-normal−.29410% with both local crops slightly better/dzero;13core-potential best admissible−.00562%, with d-only gains opposed to full/foreground guards. Prior saved sensitivity shows weak global direction degeneracy but strong local source-dependent tradeoffs. These failures do not prove physical exhaustion. They justify investigating missing incident content/photometry before another unstructured sweep. Source audit14and separate input proposal15 must not become an optical gain, epoch reset or B714activation.

Artifacts: protocol.json; toolbar_core_strain.py/test_toolbar_core_strain.py; checks/invariants.json; pre-fit sensitivity script and immutable pre-fit/native buffers; guard-cone.py; validate-proposal.py; native-study/{pre-fit-sensitivity,guard-cone,result,native-evaluations,native-crops}.json; native-study/best-feasible/{recipe,scores,measurement}.json and float buffers; all point caches. Hash manifest and implementation-inputs.json identify exact code/inputs. No expensive fresh HQacceptance render for this failed milestone.

Completed commands (not restart instructions):
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-code/test_toolbar_core_strain.py
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-core-sensitivity.py
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-core-guard-cone.py
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-core-validate-proposal.py

Next14source-only A-donor/unocclusion audit, bounded same-example original footage beyond assessed720/724/rejected726+; reuse exact prior native frames/provenance where possible.15only justified separate source proposal/unchanged incumbent reevaluation, current source/history/count2stayfrozen. Request7before15; continue monitoring and explicit Ana pause wins. No shared edits/commits/pushes; lead final verifier, switch separate.
