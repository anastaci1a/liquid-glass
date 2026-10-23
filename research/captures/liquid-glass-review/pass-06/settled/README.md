# Settled playback study

Ana's final selection: **width 4.5 / gain 1; glass blur 1.5px; dark saturation 0.2; taper 0.5; icon-color blur 3px**. Spatial pixel values are equivalents at the 490px reference diameter; both blur amounts scale with the shorter lens dimension.

- [Final video](playback-final.mp4): **1920×1080**, six seconds, 30fps H.264; approximately 0.93MB.
- [Full-size GIF](playback-final.gif): **1920×1080**, six seconds, 15fps, 128-color palette; **7,960,291 bytes**, below the strict 10,000,000-byte limit. It loops continuously.
- [Reference-pose still](playback-reference.png).
- [Progressive scores](progression.md), including earlier pre-numbered PR commits.
- [Preset and pipeline](preset.json).
- [Video/GIF verification](media-verification.json), [unquantized settled scores](scores.json), and [common frozen-image score data](progression.json).
- [File hashes](files.sha256).

The icon pipeline is **pass04 response → dark-weighted saturation → highlight taper → 3px-equivalent color blur → sharp coverage**. Blur is already the last color operation; the final mask preserves the triangle outline. Glass blur occurs after refraction/shading, before the foreground icon is composed.

The video/GIF have no diagnostic captions. They use the same uncovered dune background and show translation without deformation. Exterior shadow is omitted in motion; the still retains the previous estimated/retained exterior. These are offline model previews, not Android performance evidence or an identified Apple shader.

Both files were fully decoded and checked for full-HD dimensions. The GIF was tried first at 192 colors / 15fps (10,485,973 bytes), then at 128 colors / 15fps to satisfy the cap without reducing frame rate or dimensions.

[Pass06 comparisons](../README.md) · [All passes](../../README.md)
