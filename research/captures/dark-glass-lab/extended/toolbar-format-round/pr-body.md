- Reduce oversized toolbar/main/rim/underside figures to1080px per side. Use the native Apple frame directly for the left panel and resize the accepted lossless4× reconstruction for the right. Keep the smaller letter detail, crop boundaries and scientific scores unchanged.
- Update exact caption/gutter metadata and record hashes/resampling provenance. This is presentation-only; no optical pass or new scene rendering.
- Validation: reconstruction panel equals its declared resize exactly; caption-metadata tests and diff checks pass. Docs/assets only, no Android/GitHub checks needed.

Refs #222.
