# Playback media normalization — private handoff

Completed **formatting/export only**. Accepted playback3-pass recipe/model/source/glyph/scoring remain unchanged; no new scientific pass or optical fit. Stale toolbar return is cancelled; accepted gamma29/history untouched. Light/dark final media/publication were already completed and remain ready.

Private evidence root: `/evidence/extended/helper-toolbar-work/playback-format-round/`.

| Asset | New format | Evidence |
| --- | --- | --- |
| `playback-round-current.png` |2162×1104;1080 per side,64px caption,2px gutter|Lossless final pass3 panels reused; no optical still render|
| `playback-settled.mp4` |1080×608,90frames15fps,exact6s;391,152bytes|Original accepted material/map/icon and rounded sine path|
| `playback-settled.gif` |1080×608,90frames,exact6s;3,072,914bytes|128-color Bayer4,full decoded-frame/hash checks|

Original public asset paths are preserved. `publication/playback-format.patch` changes only current formatting text, comparison metadata and current motion verification. `publication/staged/` contains three replacement assets and those text files; `publication/manifest.json` has destination→SHA256 mapping. Patch `git apply --check` passes against lead's current public tree, without editing it. Base snapshot is committed95a511ae. No public edit/commit/push.

## Still bounds and body preservation

Final accepted lossless `extended/playback-short-round/pass-03/hq/render.png` is2720×2620. Its old5442×2784comparison has164px caption and2px gutter; saved right pixels EXACTLY equal the lossless render. We extracted left[0,164,2720,2784] and right[2722,164,5442,2784], then resampled each to1080×1040 and added a fresh64px caption/gutter2. Native window[620,220,1300,875] is the compact680×655 control crop, not the whole1920×1080scene enlarged into a thumbnail. Lens bounds[715,297,1205,787] stay fully inside that crop. Its top/bottom margins77/88nativepx remain in the page image; no lens body is cut off by the caption crop.

Both source inputs exactly match accepted recipe: source `ae20f4366287078794c6e84d70aff6e786400456264d88ffd832fd478d7b23f6`; target `f47fba56384d84de3c106812e8b153fe7a826cfbd0dc082a75f62bc4e2df6bb9`. Existing accepted native material is reused unchanged and SHA-recorded; `normalized/native-zero-complete.npy` uses frozen public playback_replay.composite with that material and the clean source. Native original score/replay proof is inherited unchanged, not rerun: E9.064747217016/glass8.040046691895/icon3.211054683477. Reference-derived triangle coverage and independently calculated near-white icon color remain the accepted pipeline; no vector/color/matte changes or copied colored symbol.

## Motion and exact proof limits

No lossless final moving-frame sequence was retained, only lossy H264/paletteGIF. To avoid treating decoded compressed imagery as lossless, regenerated exactly90motion frames using frozen public mapping/lighting/icon_color, clean source and original path `round(960+340sin(2πt)),round(542+120sin(4πt))`, t=i/90. Those centers match every second original180-frame30fpspose. The body/image is resampled to1080width after original1920×1080scene rendering; output height608 is the even-pixel rounding of607.5 for YUV420video. No exterior target context or photographed shadow enters reconstruction/motion.

Motion preserves its original2×2 subpixel integration. Native metric verification remains4×4 and its saved material is unchanged. Motionzero is **not claimed bit-exact to native4×4**; separate native-zero composition and moving2×2material arrays are saved. No scientific acceptance/epoch change follows from resizing or changing frame rate.

Every1080×1080subpixel lookup in the540×540moving body patch was checked for all90poses, including unscored exterior and therefore all scored subsets. Actual bounds x399.221466..1520.778564/y201.221451..882.778564; sourceGaussian finite radius2 plus bilinear1 margin193.221436nativepx. Original static native analytic-domain proof remains inherited as recorded in accepted pass3. The whole output background is the frozen in-image clean source. Defined finite RGB is not independently observed source/registration truth; no Apple generalization or recovered-solid claim. Unmodeled exterior shadow/photograph-specific icon grading remain explicit.

Initial Sierra2_4aGIF palettes256/192/128/96 exceeded10MB; only last96file/its byte count retained, earlier sizes were not fabricated. `normalized/gif-cap-recovery.json` records recovery: reused completed MP4 with Bayer128palette, zero extra scene renders, accepted finalGIF3,072,914bytes. Original rejected96GIF preserved. Both final files fully decoded;90frame hashes in `*-decoded.framemd5`, duration/dimensions in `motion-verification.json`. GIF centisecond delays patched losslessly to exact6s. No rerender after failure.

`freeze.json`, `normalized/{still-verification.json,motion-verification.json,verification.json,frames.json}`, and publication manifest own exact hashes/limits. Completed scripts are `normalize.py`, then encoding-only `finish-encoding.py`; copied at evidence root. `page-verification.json` and desktop/phone screenshots own final actual-viewer checks; no viewer/CSS logic changed. Private archived site substituted only frozen Git HEAD/path inventory because it has no.git; not part of public patch.

```sh
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/playback-format-round/normalize.py
# Completed rendering; GIF cap recovery reused existing video only:
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/playback-format-round/finish-encoding.py
```

Lead owns independent visual/publication review and all public copying/commit/push. Do not count this formatting work as a scientific checkpoint.
