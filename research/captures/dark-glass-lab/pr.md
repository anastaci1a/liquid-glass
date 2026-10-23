The lab now uses a dark layout with a separate settings panel, a larger phone preview and a static gradient with vertical lines behind the lens. Reset all settings restores every input and the system motion preference. Descriptions use factual wording.

- Replace older illustrations and app screenshots with current WebGL captures; remove obsolete media from generated Pages output.
- Cap rendering at 960×400, retain proportions on phones and provide an explicit motion-only fallback link.
- Validation: 13 browser check groups passed in Chromium/SwiftShader; 94 internal links passed; final desktop/mobile captures, fallback and high-DPI render budgets checked. These do not establish device performance.
- The reported Chrome sad-face failure was not reproduced. Repeated morphs and context loss/restoration passed; #411 stays open for affected-browser confirmation.

Docs/demo only. Android checks skipped under Ana’s explicit authorization. Refs #411. — Codex
