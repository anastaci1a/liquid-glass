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
