# Calibrated miniplayer color candidate

One held candidate implements the supplied body and outline anchors. Expanded defines the shared color target; compact color regressions do not veto it. The selected family is unchanged. Final geometry, incident blur, shadow, artwork, one-pixel outline plateau, two-pixel fade and opposing diagonal gaps remain fixed.

[Interactive comparisons and native crops](../../../guide/miniplayer-anchor-colors.md)

## Response

The map consumes blurred refracted encoded RGB before lens grading or exterior shadow. It preserves hue and matches the requested saturation and value. Body and outline have separate frozen responses. The final map replaces old grading, transmission darkening and hypothetical reflected-light brightness; no second optical attenuation follows it.

Let the input saturation and value be S and V. Each role has a frozen neutral curve N, saturation multiplier K and logit offset B. The output is:

\[
S'=K(V)S,\qquad V'=\frac{1}{1+\exp\left[-\left(\log\frac{N(V)}{1-N(V)}+SB(V)\right)\right]}.
\]

Hue is unchanged. Cubic Hermite interpolation uses shape-preserving interior slopes and flat colored endpoint derivatives. Colored coefficients extend constantly outside their anchor range. The neutral curve preserves the old neutral black behavior and shape, with its white endpoint remapped. Old normal transmission enters only this frozen neutral prior, never as a second multiplier.

Four warm colors do not identify a unique global response. Black and unsampled hues remain model assumptions. The user supplied anchor values, not independently established photographic source correspondences. No image residual, held pixel or compact target was used to fit the response.

## Verification

All eight anchor saturation/value checks pass within numerical precision. White maps to #E5E5E5 in the body and #FCFCFC at maximum outline strength. Preserving input hue changes the yellow outline target from #FEF985 to approximately #FEEB85. The full RGB residuals are retained rather than treated as exact color matches.

Independent SciPy interpolation and HSV reconstruction agree with the production response. Dense color and gray controls establish bounded output, neutral gray, monotone neutral value and hue preservation on the declared grids. Four selected identities and four independent complete candidate replays are pixel-exact. Clear samples and zero-gap contributions are exact. No output clipping occurred.

All four full candidate panels were inspected. Expanded yellow remains colored; compact white content is darker under the shared expanded calibration. Aggregate errors increase on all four images. Anchor success is not image fidelity or adoption. Original partial, foreground, body and crop failures remain in results.json.

## Evidence and accounting

Calibration used 48,198 scalar points and 119,354 control colors. Rendering used four Studies, 1,121,600 mask points, 6,133,768 color evaluations, four identities, four candidates and four independent replays. Eight score calls used forty metric Gaussians and eight erosions. Decode totals are 461,145,600 numeric bytes and 33,072,352 bitmap pixels.

There were no new optical rays, source queries, incident fields, material filters or geometry changes. Existing raw samples, source support, masks and finalized shape are reused unchanged. First/last consumed hashes match. Protocol, checkpoint, full arrays, fixed patches, calibration residuals, ledgers and publication receipts are retained beside this report.

The comparison publisher preserves exact native pixels and crop coordinates. The selected reconstruction remains unchanged pending user review.
