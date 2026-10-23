# Gallery presentation

The [current-model registry](../../reconstruction/current-models.json) selects primary geometric versions. The gallery shows their remaining defects and archives older empirical comparisons.

## Saved-image export

```sh
git lfs pull
node tools/prepare-geometric-gallery.cjs
python tools/format-geometric-gallery.py
```

The formatter uses [declared saved inputs](geometric-gallery-inputs.json). It performs no optical tracing, fitting or rescoring. Existing native arrays and quantized images remain unchanged.

[Verification](geometric-gallery-verification.json) records image hashes, native/presentation dimensions and caption boundaries. Checkerboard denotes unavailable unscored exterior, rather than invented RGB.

## Checks

- The first figure in each primary card must match the model registry.
- Historical figures and motion remain unloaded until opened.
- Wipe, side-by-side, fullscreen, keyboard and touch views preserve both panels.
- Test desktop/mobile layouts with usable system fonts; missing fonts invalidate visual screenshots.

Changing the displayed model does not revise old scores or acceptance records. Follow the [primary-model policy](../decisions/primary-geometric-models.md).
