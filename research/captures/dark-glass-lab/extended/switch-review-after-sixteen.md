# Switch review: potential, deformation and outer-profile tests

- Potential-derived field: a differentiable displacement gradient reduced curl, but worsened reference A even after shared material recalibration. It is a paraxial model, not a recovered thick lens. Not adopted.
- Fixed-volume deformation approximation: using the measured footprint/track dimensions to scale displacement gave aggregate numerical improvements on both observations. Visual review found a roughly 4% rim-error increase on B. Restricting the effect to the central support did not resolve that tradeoff; adding rim nonregression constraints left A below the 0.5% milestone. Not adopted.
- Outer-profile/cap-orientation search: 256 proposal evaluations, then three native step sizes. Best E reductions approximately 0.0405% / 0.0076%; B whole-glass error also increased slightly. No qualifying pass.
- Separate generated-shadow fit improves exterior error but cannot rescue optical errors. Its offset reaches the declared bound and the most distant B band regresses slightly. Not adopted.

## Next investigation

Review the inherited material and dispersion composition against the actual residual crops before fitting another family. In particular, distinguish dark rim shading from misregistered refraction and isolate directional color splitting from ordinary blur. Preserve the two frozen source estimates, pose, masks and current revision2 baseline; any source correction requires a separate scoring epoch, not a claimed optics gain.

Two verified switch improvements this round remain current. These failed families and optimizer iterations are not additional passes.
