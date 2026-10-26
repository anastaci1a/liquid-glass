# Fourth full refinement pass

Status: declared before execution. Test the midpoint shoulder inset `0.75` pixels while retaining the actual two-percent front/back height increase. Fresh physical paths and finite-source gates precede RGB.

The complete sequence revisits blur, body lift, outline, exterior shadow and artwork. The outline holds its maximum for `2.5` pixels, then uses the existing two-pixel fade scale. Three neutral increments target darker colored edges while suppressing changes to high-luminance yellow.

Shadow trials vary vertical spread and downward offset together, preserving their ratio and opacity. Horizontal spread stays fixed. This is a shape contrast, not an isolated width estimate. Artwork tests nearby shared scales with the verified eighteen-pixel corner radius.

All choices use training cohorts. Original masks, held checks, partial cohorts and failure evidence remain unchanged. Dispersion is excluded. Final selection compares all four full passes and may retain an earlier candidate.

## Completed result

All four full comparisons were inspected. The final score is `0.950851`, worse than pass three's `0.912897`. Every final aggregate error also worsens against pass three. The final selection therefore retains the complete third pass.

The zero extra-neutral setting ranks best; both nonzero increments are rejected. The wider vertical shadow improves exterior error. It is not transplanted into another geometry without a new verified composition.

Training choices retain sigma `6.37875`, body lift `0.08`, zero extra edge-neutral lift, vertical shadow sigma `24` with downward offset `8.4`, and artwork scale `0.95`. Original held and local failures remain.

## Verification

All four pre-foreground and complete outputs reproduce exactly. Every original metric and guard decision matches. Fresh native source gates, necessary geometry controls and positive rim quadrature passed. No dispersion stage ran.

The [fixed shadow profiles](shadow-profiles.json) use 168 saved/reference observations. Their conditional source comparison cannot distinguish all background texture, registration and other scene effects. No extra fit or render was performed for these measurements.

## Evidence

- [Results](result.json), [training choices](choices.json), [recipe](final-recipe.json) and [ledger](ledger.json).
- [Own replay](verification.json), [kernel support](blur-source-FIRST.json) and [integration](integration.json).
- [Response controls](response-controls.json) and [clock](cycle-clock.json).
