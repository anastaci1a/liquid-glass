<details>
<summary>Colored rim — final review09 crops and measurements</summary>

The current sheet shows Apple, accepted review06, and final accepted review09 in three columns. It reuses the exact historical normalized/native crop rectangles and saved native composites; no optical rerender, recentering, or color matching. Local RGB error increases at A/B lower-left and B center. A right-rim chroma and B right-rim luma also worsen; all changes remain in the advisory metrics. The tiny global gains do not resolve the heavy inner contour, excess softness, or colored fringes.

[![Final09 switch rim crops: Apple, accepted06 and final09](assets/switch-round09-crops.png)](assets/switch-round09-crops.png)

[Accepted06 → final09 native crop metrics](experiments/reconstruction/studies/active-switch/review-round/pass-09-crops.json) · [Final09 A comparison](assets/switch-round09-a-comparison.png) · [Final09 B comparison](assets/switch-round09-b-comparison.png). Both states are recomputed from saved native arrays; do not concatenate these numbers with historical HQ-derived crop scores. Native scoring masks and gates are unchanged.

Historical evidence: [review05 → 06 crop scores](experiments/reconstruction/studies/active-switch/review-round/pass-06-crops.json) · [review06 exterior bands](experiments/reconstruction/studies/active-switch/review-round/pass-06-shadow-tails.json). The older sheet below retains snapshot24. The gray-track reference contains a warm patch near RGB `(251,236,209)` and a cyan lower rim, while the estimated track is near `(190,195,189)`. The modeled hidden input and these hue discrepancies remain uncertain.

[![Historical snapshot24 switch rim details](assets/switch-rim-detail.png)](assets/switch-rim-detail.png)

- Earlier source-derived reflection reduced the unsupported lower dark contour independently of exterior shadow; its historical lower-contour MSE1124/1688 is not a new final09 measurement. Thin inner colored bands remain calibration targets.
- [Historical rim measurements](experiments/reconstruction/switch-rim-analysis.json) and [competing color models](experiments/reconstruction/switch-color-hypotheses.json) retain their own frozen baselines. The present tiny changes do not establish a physical dispersion model or Apple parity.
- Geometry-dependent highlights, ambient color, chromatic transmission, video processing, and source-estimation error remain possible contributors. Defined source support does not establish observed hidden RGB.

</details>
