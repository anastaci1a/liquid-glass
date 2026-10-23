- Merged docs/demo PR #412 to main `025b13ffa2623d5c47b27f78d4a96f622c021683`; Pages artifact `39dbae716ac7e489a47b4edb759930a6b3f59c93` built successfully.
- [Live lab](https://anastaci1a.github.io/localica/liquid-glass/lab.html?v=025b13f): dark layout, static gradient/vertical lines, proportional phone preview, full reset, factual wording. Guide media now comes from this renderer; removed older media and versioned asset URLs.
- Local validation: 13 Chromium/SwiftShader groups, 94 internal links, high-DPI render-budget checks and final versioned-asset smoke passed. Captures are browser evidence, not device performance measurements. Android source untouched; app CI skipped with Ana’s approval.
- Remaining: Chrome sad-face failure was not reproduced. Rendering is capped at 960×400; repeated morphs and three loss/recovery cycles passed. Keep this issue open for confirmation in the affected browser; no claim of a confirmed crash fix.
— Codex
