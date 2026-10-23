# Documentation conduct

This contract applies to every maintained text document in this repository.

## Writing

- Lead with the result or decision.
- Use one fact per sentence; prefer familiar words.
- Keep paragraphs under 60 words and bullets under 30 words.
- Use tables for comparisons, parameters, outcomes and ownership.
- Use lists for steps or genuinely parallel items.
- Put commands and literal data in code blocks. Use LaTeX display blocks for formulas.
- Link evidence; do not paste logs into explanations.
- Remove duplicate rules and obsolete instructions.

A longer passage needs a concrete reason: a quotation, mathematical derivation, or verbatim frozen evidence. Mark the exception. Do not use this allowance for routine narration.

## Mathematics

Use LaTeX display blocks delimited by double dollar signs for formulas, inequalities, derivations, vectors and matrices. Do not substitute code fences, screenshots or inline code for mathematics.

Keep executable code, API identifiers and literal preset values in code formatting. Immutable historical evidence stays verbatim; maintained explanations follow this contract. The guide renders display mathematics with locally bundled KaTeX.

## Where records live

| Record | Home | Update rule |
| --- | --- | --- |
| Current state and next action | `research/current/` | Replace stale state. |
| Visible feedback | `research/feedback/` | Assign a stable ID; track its disposition. |
| Experiment | `research/experiments/` | One short record per declared experiment. |
| Decision | `research/decisions/` | Record choice, rationale and consequences. |
| Reusable method | `research/method/` | One authoritative explanation. |
| Reference material | `guide/` | Separate observation from interpretation. |
| Lab behavior | `lab/` | Keep illustrative behavior separate from physical claims. |
| Historical evidence | `research/evidence/` | Preserve bytes and provenance; summarize elsewhere. |
| Migration provenance | `research/provenance/` | Keep maps, exclusions and verification. |

## Experiment format

Use [the experiment template](templates/experiment.md). Declare the defect, hypothesis, parameters, frozen stages, references, budgets, checkpoint and stop rule before execution.

Record outcome, local and overall measurements, regressions, uncertainty and the next discriminating observation. A rejected proposal is a result; a smaller aggregate score alone is not a visible fix.

## Observations and decisions

Use the [observation](templates/observation.md) and [decision](templates/decision.md) templates. Label claims as observed, inferred, assumed, proposed or verified. Keep current instructions separate from historical authority.

## Git is the working record

- Save useful work in progress with an explicit status.
- Commit code, configuration, notes and evidence together when they form one result.
- Push each new commit immediately; verify the remote tip.
- Keep raw numerical/media evidence in indexed Git LFS objects.
- Exclude credentials, private session dumps, caches and downloaded software packages.
- Preserve source hashes and exact historical evidence; never rewrite it to fit a conclusion.

## Review

Run `npm run check:docs` before committing text. The checker enforces links and prose limits on maintained Markdown. Machine records, code blocks, tables and indexed verbatim artifacts have separate formats.
