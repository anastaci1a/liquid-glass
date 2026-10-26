# Visible feedback

| ID | Control | Observation / request | Disposition |
| --- | --- | --- | --- |
| F-001 | Clear play | Edges look too blurred; test source blur before refraction. | [Tested](../experiments/clear-play-02/README.md): compressed edges sharpen, but original guards regress; no replacement accepted. |
| F-002 | Clear play | Edge reversal can be correct for this lens. | Earlier no-reversal assumption withdrawn. |
| F-003 | Clear play | Thin bright rim and lower-left light structure remain wrong. | Unresolved; output softness is not an outline fix. |
| F-004 | Toolbar | Continuous cap/body, minute crown, progressive d-stroke stretch and compressed underside. | Geometric diagnostics negative; source uncertainty retained. |
| F-005 | Toolbar | Upper crop extends downward; adjacent letter crop meets its bottom. | Preserve expanded crop alignment; no mask change. |
| F-006 | Related pills | Central zoom appears excessive; peripheral compression matters. | Historical observation, not an identified thickness estimate. |
| F-007 | All research | Isolate refraction, blur, grading, outline and foreground. | [Method](../method/README.md). |
| F-008 | All records | Concise, readable, maintainable text throughout the repository. | [Documentation conduct](../../DOCUMENTATION.md). |
| F-009 | Current modeling | Focus on physical correctness and visible fidelity; runtime optimization is outside current scope. | No device benchmarking or optimization task is active. |
| F-010 | Compact / expanded miniplayer | Require one exact shared model; only length differs. | [Required family transfer](../current/state.md#miniplayer-family); no independent compact tuning. |
| F-011 | Miniplayer outline | Double edge lines are incorrect. Prefer an extremely thin outer white maximum with a rapid, smooth inward fade and no sharp inner cutoff. | [Three-proposal review](../experiments/miniplayer-sample-outline-90/README.md); single contour achieved, boundary guards unresolved. Uniform strength remains tentative. |
| F-012 | Outline composition | Place the outline on top of the completed reconstruction, independently of refraction calculations. | Current modeling convention; earlier physical-reflection experiments remain historical evidence. |

Physical interpretations remain hypotheses unless independently established. Explicit modeling requirements constrain implementation. Feedback IDs track the visible issue; a lower aggregate score does not close them.

[Earlier visible requirements](history.md) consolidate related project feedback without importing unrelated app reports.

## Wider asymmetric outline refinement

The confirmed cap pattern fades from lower-right toward upper-right on the right end, recovering before the top join. The left pattern is rotated 180 degrees. Start with three-to-four times the earlier inward width. Compare white with a color-preserving brightness lift; exact angles, width and strength remain adjustable shared hypotheses.

The approved [five-pass study](../experiments/miniplayer-outline-series-91/README.md) verifies registration first and provides draggable reference/result and starting-model/result comparisons. Original guards and rejected candidates stay visible.

The five approved outline passes are complete. No family qualifier was found; [all comparisons](../../guide/outline-review.md) remain available for direct visual feedback. Current sizing is retained with uncertainty.

## Color-aware highlight, smooth joins and exterior shadow

The inner-edge highlight should brighten the underlying color with slight desaturation rather than erase it into white. Cap/body transitions may have continuous curvature, with subtly convex long sides. A slight shadow should affect only the exterior, separately from refraction.

The [native join checkpoint](../experiments/miniplayer-join-inspection-92/README.md) inspects these regions before any shape replacement. Geometry validation precedes separate shadow and highlight comparisons; original masks and shared-family requirements remain fixed.

The [complete refinement](../experiments/miniplayer-complete-refinement-94/README.md) now tests actual smooth geometry, exterior-only shadow and a color-aware inner fade. Own replay and source checks pass. Compact rim visibility improves, but expanded A over-brightens and original guards still fail. [All stage comparisons](../../guide/miniplayer-refinement.md) are available; these visible issues remain open.

## Inward joins, shadow breadth and edge response

Top joins should move down and bottom joins up, toward the center. Far caps should refract more, not retract. The edge should brighten and desaturate existing color without reaching pure white; black should become light gray. Both controls need slightly less blur, and compact body tone appears too dark.

The [completed investigation](../experiments/miniplayer-stronger-joins-98/README.md) tests one shared inward contour, a ten-percent incident-blur reduction, broad exterior-only shadow and a finite color filter. Source proofs and own replays pass. Original local failures prevent adoption; compact tone and exact contour remain unresolved. [Interactive results](../../guide/miniplayer-feedback-review.md) retain every comparison.

## Intermediate joins and color-bearing plateau

[Latest feedback](miniplayer-middle-ground.md) requests intermediate smoothing, retained edge color, a short peak plateau and stronger downward shadow. The blur correction explicitly retains incident filtering. [Results and sliders](../../guide/miniplayer-middle-ground.md) preserve the two shape trials, separate material contrasts and unresolved original guards.

[Final display color anchors](miniplayer-anchor-colors.md) supersede the earlier equal-value outline proposal.

[Restored body controls and wider rim plateau](miniplayer-restored-grade.md) supersede the anchor-map body proposal while retaining its outline colors.

[Final-output white and artwork correction](miniplayer-final-white.md) supersede the grading-stage white target and two-pixel rim plateau.

[Stronger yellow outline and artwork enlargement](miniplayer-yellow-match.md) records the revised exact color target and deferred comparison observation.

- [Hue-preserving horizontal outline taper](miniplayer-outline-taper.md).
