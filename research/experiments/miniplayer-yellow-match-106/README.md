# Exact yellow anchor and larger artwork

One shared candidate maps the tentative preimage #EBCE48 exactly to #F6F586 at maximum outline strength. Artwork width and height become 1.0183 times revision 105 dimensions, with native-pixel rounding. Both artwork centers and radius 18 remain unchanged. Body grading, optical lighting, shape, blur, shadow and outline geometry remain fixed.

[Interactive comparisons](../../../guide/miniplayer-yellow-match.md)

## Color calculation

The reported output #F7EDB4 has HSV saturation 27.126%; the requested #F6F586 has 45.528%. The increase is approximately 67.84%. Maximum RGB value decreases from 247 to 246, while linear-light luminance rises from 0.836378 to 0.866189. The exact channel change is minus one red, plus eight green and minus 46 blue.

The proposed input hue is 49.325 degrees; the target hue is 59.464 degrees. Therefore exact matching requires a 10.139-degree shift. This new exact-anchor requirement supersedes hue preservation for that warm color. White remains #FCFCFC. The earlier brown anchors retain their previous hue-preserving endpoints, with no new hue shift at their input values.

## Response and controls

The existing neutral curve is retained. Saturation and value curves are recalibrated using the revised input/target yellow anchor. An optional warm-hue correction is added to the existing endpoint API; previous calls without that correction retain their original behavior. The correction depends only on input color, never on image position or reference identity.

Let d be wrapped hue distance from the new input hue, a the fixed 30-degree half-width and D the value-dependent hue offset. The correction is:

$$
H'=H+D(V)w(d),\qquad
w(d)=\begin{cases}
\frac{1+\cos\left(\pi\frac{d}{a}\right)}{2},& |d|<a,\\
0,& |d|\ge a.
\end{cases}
$$

The offset curve is zero at the prior brown input values and reaches the required shift at the new yellow input. Flat endpoint slopes and constant extrapolation preserve bounded interpolation. Neutral colors remain exact, and hue is unchanged outside the warm support. Saturation/value changes still apply through the shared color-response model.

## Verification

The exact yellow endpoint and all declared saturation/value anchors pass. Dense color and neutral controls are bounded; independent scalar HSV reconstruction agrees within numerical precision. Four complete revision-105 identities and scores replay exactly. Four new candidate replays are pixel-exact, with no clipping.

Body pixels outside the artwork union are exact. Both artwork centers are unchanged, and that union has zero outline contribution. The final-white calibration, raw source samples and 1.5-pixel plateau/two-pixel fade alpha field are reused unchanged. No optical rays, source queries, incident fields, filters or quadrature are added.

## Outcome and limits

Expanded aggregate error improves from 11.907829 to 11.733664 in A and 4.808293 to 4.807020 in B. Compact regresses from 14.166782 to 14.993668 and 15.230886 to 15.635873. Original local and foreground failures remain in the records. This is a held candidate, not full-model acceptance or a selected-state change.

The input color is tentative user-supplied evidence. An exact endpoint match does not identify the source of every visible reference pixel. Coverage, fade and angular strength still blend the endpoint with the completed body. The unobserved scene and source-return limitations remain.

Artwork realizes 109 by 112 pixels for expanded and 109 by 111 for compact. Requested fractional dimensions and raster results are recorded separately. The additional Apple comparison behavior remains deferred at the user's request.
