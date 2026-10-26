# Slight blur reduction and light-gray edge endpoint

One fixed ten-percent incident-width reduction slightly sharpens transmitted texture, but worsens aggregate error on all four references relative to smooth94. It remains a development observation, not an accepted PSF estimate. The source filter acts before refraction; no output blur or new ray was introduced.

| Reference | Smooth94 E | Less-blurred E |
| --- | ---: | ---: |
| Expanded A | 7.9566 | 8.0341 |
| Expanded B | 5.9386 | 6.2896 |
| Compact A | 20.2544 | 20.3129 |
| Compact B | 19.5653 | 19.7955 |

Both changed source gates pass before either field in each pair. Sigma is exactly `6.075` native pixels, with finite radius `19`. Clear coordinates and samples remain exact; their original support proof is unchanged. Queried lens samples and complete filtered source rasters are retained.

## Revised filter control

Review of the three study96 endpoints found that they only lift black to dark gray. A separately declared endpoint now maps black to encoded gray `0.65` at full edge strength. Exposure is `1.4`, desaturation `0.1`, and lift is derived from that endpoint. No target fitting or extra endpoint search occurred.

$$
q=\mathcal D(0.65),\qquad b_1=\frac{q}{(1-q)e_1}.
$$

Black becomes `(0.65, 0.65, 0.65)`, white remains exactly white, and the yellow control `(0.8, 0.7, 0.05)` becomes approximately `(0.899, 0.800, 0.319)`. Nonwhite input peaks stay below white. The same spatial start/end and inward fade vary the filter strength, not a white overlay.

The light-gray endpoint plus broad exterior shadow improves every smooth94 guard on expanded B and both compact references. Expanded A remains a conflict. Against original working20, failures remain. The additional less-blurred combination preserves every original failure rather than being accepted by aggregate score alone.

[Results](result.json), [fixed recipe](filter-recipe.json), [source gates](source-FIRST.json) and [ledger](ledger.json) retain all twelve candidates and eight identities. Geometry, original masks, glyphs and shared material gain/bias remain unchanged. The separate compact darkness diagnosis is not repaired by an unreported compact-only exposure.
