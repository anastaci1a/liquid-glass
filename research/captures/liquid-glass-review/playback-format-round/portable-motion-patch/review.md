# Portable playback motion export — private patch ready

Private root `/evidence/extended/helper-toolbar-work/playback-format-round/portable-motion-patch/`: `portable-motion.patch`, staged public `motion.py` and docs delta, `manifest.json`, `verification.json`. Apply after the accepted playback formatting patch; standalone `motion-only.patch` also passes `git apply --check` against current public motion.py. Combined patch dry-run passes in an isolated copy of the normalized docs+original helper. No public edits/commits.

Adds `--width` default1920 and `--fps` default30. Final height is even-pixel aspect rounding (1080width→608height). Model sampling/shape/path/source/icon operations stay identical; only final RGB resizing and output encoder rate/size change. Original2×2 motion integration is unchanged. Native4×4/scoring/accepted3-pass history untouched.

```sh
python motion.py INPUTS OUTPUT --record studies/playback/review-round/pass-03.json --frames 90 --fps 15 --width 1080
```

For this command, movie/GIF90poses at15fps/6seconds match the accepted normalized format. GIF uses Bayer128 initially, then palette-only96/64/48/32 fallback without reducing selected GIFfps (min(movieFPS,15), preserving legacy default15fpsGIF). GIF block delays distribute centiseconds over movie duration;90/15 gives exact6000ms. No re-encoding of image/palette blocks for timing. Size cap remains10,000,000bytes. Defaults retain1920/30movie and original trajectory; current command selects1080/15 explicitly.

Validation generated **ONLY first2rawframes** with the patched real main/render path and intercepted encoder writes; both byteSHA256 values exactly match saved accepted normalization frames0/1, dimensions1080×608. Encoder args are1080×608 at15fps. Test stops immediately after second frame, before the third or real encoding; no full90-frame render, native4×4 test, optimizer or source fit. Real accepted90-frameGIF exercised timing parser:90frames/6000ms and byte-exact unchanged output; no new encoding fixture required. `verification.json` retains exact hashes/encoder argv. Existing source/target hash checks and accepted record used as before.

This patch makes existing accepted export format reproducible; it is not a scientific pass. Lead applies/reviews/commits. Approved new compose source/pose intake starts next, bounded20minutes and no optical fitting until both backgrounds/sources/foreground provenance are usable.
