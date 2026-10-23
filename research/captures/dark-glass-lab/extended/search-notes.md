# Detached Search control

- Circular silhouette and sampling field remain radial; directional material lighting is allowed.
- Initial coordinate-descent passes became trapped in a heavily blurred, weak-refraction local minimum. Do not accept this merely because pass count is met.
- Add a seeded global signed radial-profile comparator, followed by spline refinement. Keep masks, source recovery, and native score gate unchanged; record rejected trials.
- Native reference glyph is gray/translucent black over orange. A neutral-RGB seed rejected it incorrectly; remove neutral-only restriction from foreground extraction. Glass score mask is unchanged.
