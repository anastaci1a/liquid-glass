# Outline color and non-left thickness choices

Two dropdowns expose 55 combinations across four references. Color A is series 111's Step 5. Colors B–K are ten further adjustments. Non-left thickness offers 100%, 120%, 140%, 160% and 180%. No combination is adopted automatically.

Each color multiplies saturation by 0.9509900499 and hue-shift strength by 0.88689046875, adding 0.010 to HSV value. The hue reduction is half of the originally proposed larger increment. These are repeated relative increments. HSV value is bounded at one, with ceiling counts retained.

Thickness changes the top, bottom and right endcap beyond the existing horizontal transition. Pixels wholly left of that transition retain the original moments exactly. The transition blends into the chosen right-side width. Plateau and fade scale together; angular gaps, body, artwork, geometry, incident blur and shadow remain fixed.

| Non-left choice | Plateau | Fade scale | Fixed left plateau |
| --- | ---: | ---: | ---: |
| 100% | 1.20 px | 1.60 px | 0.685714 px |
| 120% | 1.44 px | 1.92 px | 0.685714 px |
| 140% | 1.68 px | 2.24 px | 0.685714 px |
| 160% | 1.92 px | 2.56 px | 0.685714 px |
| 180% | 2.16 px | 2.88 px | 0.685714 px |

## Verification

Width integration evaluates the same contour distance and angular profile at positive full-pixel nodes. Orders 16 and 32 identify pixels requiring orders 64 and 96. The unchanged 100% width reuses the previous adaptive moments. This successive-order comparison is a reporting criterion, not a universal error bound.

The matrix uses four exact base identities and independent scalar HSV/composition replays. All pixels remain present. The completed body and artwork are reused; finite guide support is checked wherever a wider outline contributes. No optical transport, source sampling, incident filtering, fitting or aggregate rescoring occurs.

[Two-axis protocol](two-axis-protocol.json) · [Results](results.json) · [Width integration](integration.json) · [Dropdown comparisons](../../../guide/miniplayer-outline-range.md)

## Earlier color-only preparation

The initial color-only execution completed three expanded-A candidates before the helper's old 0.05 value-lift guard rejected the next requested value. Those observations and their source remain retained. The parameter range was extended to 0.2, with the unit HSV ceiling preserved.

Subsequent instructions expanded the task to two axes. The amended protocol records the original deadline, actual expansion time and new combined deadline. The three earlier observations remain separate from final matrix accounting. The superseded single-axis publisher was never executed.

[Initial protocol](protocol.json) · [Initial limitation](initial-color-failure.json) · [Initial driver](initial-color-driver.py)

## Completed matrix

All 220 output replays are pixel-exact. Color A at 100% reproduces the previous Step 5 exactly in all four references. For every color, the thin left region is pixel-exact across all thickness settings. Source/code hashes remain unchanged during execution.

The maximum refined integration differences are about 2.54e-7 for expanded and 3.21e-7 for compact, below the declared 1e-6 criterion. All original pixels are retained. Representative full images at the widest and brightest settings were inspected; the options await visual choice rather than automatic score-based adoption.

[Verification](verification.json) · [Value-ceiling counts](value-ceiling-summary.json) · [Integration ledger](integration-ledger.json) · [Final execution](finished.json)
