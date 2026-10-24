# Foreground provenance and fidelity

**Keep the original foreground.** All 20 asset layers across four cases match their frozen hashes. No independent evidence justifies changing symbol geometry, text, opacity, color or artwork to compensate for glass errors.

| Evidence | Record |
| --- | --- |
| Bounded read-only assessment | [Protocol](protocol.json) |
| Original font, asset, style and placement bindings | [Verification](verification.json) |
| Exact canonical-family replay | [Independent replay](../agent-miniplayer-family-peer-19/README.md) |
| Held geometry/body-dependent foreground failures | [Color assessment](../miniplayer-neutral-response-12/README.md) |

Text and symbols use original SF font outlines with documented font hashes. The app's exact glyph variant, weight and pose remain inferred. Cover artwork is a separately hashed catalogue image. Solid SVGs contain no raster image, script or external reference.

Fixed glyph-box guards include the underlying glass. Their changes do not isolate symbol weight or material. The held split-surface candidates therefore cannot justify a retint or trace by those scores alone.

This stage performs no alpha extraction, rasterization, rendering or fitting. Foreground fidelity remains unresolved; the effect was assessed rather than silently skipped. Shared glass parameters remain independent of per-reference UI content.
