# Accepted pass2 private publication delta

`/evidence/extended/helper-toolbar-work/light-dark-round/publication-pass02/` contains `publication-after-pass01.patch`, staged accepted `pass-02.json`/independent primary verification, four current720/1080-width-per-side comparison PNGs, and `publication-manifest.json` with destination paths/hashes and explicit64px captions. Apply text hunks after pass1; copy only the manifest's binary assets. Whole staged markdown is for review, not overwriting lead's newer history. No public edit/commit.

The patch changes current record links/count to2/3 and shared original-offset multiplier to s=1.1; original four coefficients, independent material recipes and source/input hashes remain fixed. Recipe contains the unchanged original score dictionaries. Cached standalone replay reproduces accepted s1.1 complete arrays EXACT and all original scores EXACT; `cached-replay/replay-verification.json`. No optical rerender. Original native4×4 coverage, sources, masks and source uncertainty unchanged. OpticalE ties; reconstruction-only. Far-band/local shortcomings remain explicit. Pass3s1.2 is an independently queued candidate, not included or counted in this accepted-pass2 packet.

Public native replay after integration:

```sh
python regular_exterior.py INPUTS OUTPUT --recipe studies/light-dark/review-round/pass-02.json
```

The pass1 standalone helper already handles declared offsets, so no code change is needed. Current cached verification used original source/target PNGs at `/evidence/extended/helper-toolbar-work/light-dark-round`, `--material-cache` there and `--expected` sibling `offset-neighborhood`. Images resample existing native700px arrays; no4x.
