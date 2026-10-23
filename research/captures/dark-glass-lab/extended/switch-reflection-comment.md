- Pushed shared directional reflection bc9f2a4 and paired pass23; comparison/rim images updated and Pages publication running.
- Separates reflected-field filtering from transmission blur. No painted outline or region-specific color; source-derived incident-field proxy remains an approximation, not Apple's formula.
- Frozen A loss/glass hold254.741/12.615; B improves294.978→277.399 and15.075→14.734. Separate lower-contour MSE7511/10205→1124/1688, without changing native masks. Held-pixel/SSIM values remain visible in records and are not acceptance gates.
- Passed default/zero identity, native/cache, scale2/prepared, moving source, material derivative and both source-footprint gates. Independent23-pass chain replay passed.
- Rainbow remains unresolved. Testing channel-separated rays on this baseline; old pass22 motion is explicitly labeled until regeneration. No app changes/main merge.
— Codex
