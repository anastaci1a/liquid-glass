# Final accepted Navigation3: A/B media ready

Both exports COMPLETE; no rotation blocker. Independently accepted pass3/balanced recipe, own private accepted.json per reference with actual accepted scores. Original case/source/known/SVG inputs symlinked into private export folders, never edited. Current public export helper/dependencies copied and hashed privately; no public tree changes, commits or source/score epoch changes.

|Preferred publication files|MP4|GIF|
|---|---:|---:|
|A final/motion.mp4 + final/motion-6s.gif|252522bytes|3784219bytes|
|B final/motion.mp4 + final/motion-6s.gif|413038bytes|7808957bytes|

Both videos1080×336,90frames,15fps, EXACT6.000seconds. Original content1080×335; one replicated bottom row is codec padding, no aspect stretch. Both preferred GIFs1080×336,90frames, EXACT6.000seconds,256-color full-size palette;3.784/7.809MB, below10MB. No4x render or downsampling. Native metrics reproduce accepted state.

Important filename: publish motion-6s.gif. The approved helper's original motion.gif remains preserved at5.990seconds (GIF centisecond quantization). A SEPARATE lossless streamcopy changes only final frame delay6→7centiseconds. Full90-frame RGBA decode hashes match the original exactly for EACH GIF; no frame/palette/size/image change or optical rerender. Original helper verification remains unchanged; exact-duration-verification.json records the corrected file/hash and every decoded-frame hash.

Motion_support retained requested45px vertical travel on BOTH references (±45sine motion, fixed element/model). At33native-grid shifts, minimum scored Gaussian3sigma and whole-shape observed/defined source fractions ALL1.0. Keep the public protocol limitation: this is sampled native-grid evidence, not a continuous/all-subpixel proof. Recovered input translated consistently in glass and exterior; no invented text or pasted reference shadow/strip. Nearest observed RGB completion is presentation-only; measured native valid-glass completion delta max/RMSE EXACT0 on both. Frozen benchmark inputs remain unchanged.

Approved helper completed native accepted-state check, prepared-renderer zero control, full MP4/GIF decode and SHA256 hashing. Additional metadata probing confirms90frames/15fps/6s MP4; the timing-corrected GIFs were fully decoded/hashed independently and all90frames equal original GIF. Sample quarter-cycle frames inspected; no obvious new motion-context cut. This remains a rendered illustrative scroll, not captured Apple animation timing or a new optical pass.

Private export root:

    /evidence/extended/helper-toolbar-work/navigation-round/navigation-final-1080/

Each a/final and b/final includes motion.mp4, preferred motion-6s.gif, original motion.gif, verification.json, exact-duration-verification.json, render.json, comparison.png and quarter-cycle frame PNGs. Root recipe.json freezes both exact commands/code digests/primary-acceptance digest; export-summary.json preserves original helper verification and probes; exact-duration-summary.json describes final publication GIFs. Canonical copies of small verification manifests are in navigation-round/final-motion-*.json, large media remain on/evidence.

Exact render commands (already complete, do not rerun for logs):

    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/navigation-final-1080/code/extended_media.py /evidence/extended/helper-toolbar-work/navigation-round/navigation-final-1080/a --scale 1 --width 1080 --frames 90 --fps 15 --travel 45 --gif-max-mb 10 --gif-full-size
    docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/navigation-round/navigation-final-1080/code/extended_media.py /evidence/extended/helper-toolbar-work/navigation-round/navigation-final-1080/b --scale 1 --width 1080 --frames 90 --fps 15 --travel 45 --gif-max-mb 10 --gif-full-size

Lossless GIF timing command per a/b (original preserved):

    ffmpeg -v error -threads 2 -i final/motion.gif -c:v copy -loop 0 -final_delay 7 final/motion-6s.gif

Navigation accepted count3/3; lead owns final public copy/commit/push/merge. Await Navigation merge ACK, then rotate to approved compact mini-player; read-only intake already prepared. No more Navigation fitting, toolbar42/43, lead Home overlap or premature next-element fitting. Explicit Ana pauses override continuation.
