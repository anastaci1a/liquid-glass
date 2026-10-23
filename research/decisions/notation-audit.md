# Mathematical notation audit

Status: documentation correction; no new rendering experiment or acceptance decision.

## Findings

| Issue | Correction |
| --- | --- |
| Slash divisions and programming subscripts | Stacked fractions and mathematical component/label subscripts. |
| Literal `grad`, `gradient` and flattened derivatives | Nabla, partial derivatives and explicit differential measures. |
| Ambiguous vector/scalar expressions | Bold vectors, explicit dot/Hadamard products and broadcast vectors. |
| Piecewise prose embedded in equations | Cases with mathematical branch conditions. |
| Compressed source-field names | Mathematical symbols with a code-to-model glossary. |
| Three-dimensional color matrix applied to 23 coefficients | Explicit block-diagonal material operator. |
| Tangent derivative could imply the full faded field | Base-envelope derivative identified explicitly. |

## Verification

All 328 original maintained display expressions were reviewed. Additional display equations replace algebra previously embedded in prose. The current set contains 348 display equations. Strict parsing and notation checks run with documentation validation.

[Surface/slab and 24 geometry controls](notation-checks/independent-controls.log) pass. [Browser checks](notation-checks/browser.log) verify 696 desktop/mobile equation views, actual fraction layout, subscripts and gradients. No source image, reference mask, physical parameter, numerical score or renderer implementation changes in this audit.

Historical reports preserve their recorded notation. They are evidence, not the maintained mathematical specification.

[Notation conventions](../../guide/mathematics.md) · [Working method](../method/README.md)
