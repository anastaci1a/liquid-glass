# Accepted toolbar revision2 — short replay/evidence package

Source snapshot: primary commit `bb1ee80131d39e7661c3d55174767c4d15182e05` (research/toolbar-inner-profile-222). Primary independently accepted, committed and pushed the inner-normal-profile improvement; last owner note says deployment underway. No main merge/publication action or commit by agent. Two verified toolbar improvements in this round per primary; this package is verification, not another pass.

## Frozen evidence

`recipe.json` is the exact public pass-02.json, including measured pose, source hashes and canonical foreground metadata. `primary-verification.json`, `primary-scores.json`, `primary-crops.json`, `protocol.json` and epoch hashes are immutable copies from that commit. `code/` snapshots the81 top-level Python/JSON code files required by the replay. `manifest.json` records code/input/vector hashes and private-vector provenance.

Prepared `inputs/` contains hash-verified source.png, target.png, archivebox.svg and plus.svg. Agent tested the actual packaged command at native resolution: every glass/rim and both foreground RMSE values exactly match the committed primary scores (`package-verification.json`). No source correction, recolor, registration change, mask edit or fitting occurred. The source contains explicitly estimated hidden paper; hash/defined-domain support does NOT establish independently observed RGB in that region.

Native conditional-glass RMSE5.843130588531, rim8.813648223877, E6.870490597950; fixed exterior11.469442017232. The previous accepted E6.998512744608 improves by1.829276%, an error reduction, not Apple accuracy. Native4×4 protocol remains authoritative; primary8× diagnostic glass5.839861392975 is recorded only as convergence evidence, not a better replacement score.

Primary source-support proof checks ALL139,059,200 emitted4× HQ lookups, with source-kernel/bilinear margin34px, bounds x474.53125–1444.46875/y284.53125–844.46875 inside1920×1080. It separately declares hidden background estimated. Primary independent source/replay/visual evidence and gate are true in the committed artifact; agent's packaged native replay confirms the immutable inputs/code behave identically.

Fixed advisory crops (unchanged positions/masks): upper rim[650,369,1270,435] glass9.022676→8.964386; d-stroke[960,450,1120,550] glass3.739308→3.110434. Both foreground boxes improve; primary fresh4× full/crop images were inspected. Archive is a clean symmetric vector approximation, not an exact identified Apple outline; plus uses the original SF outline. No source symbol RGB is pasted.

## Reproduce without fitting

From this package directory in an environment with the existing NumPy/SciPy/OpenCV/Pillow/vector dependencies:
```
python3 code/tensor_replay.py inputs recipe.json output-native --scale 1
python3 code/tensor_replay.py inputs recipe.json output-4x --scale 4
```
The first command was tested. The identical committed primary implementation already verified the4× output/source support, so agent did not repeat that heavy run merely to create another test record. Original fonts/screenshots remain private; replay verifies all declared source and solid-vector hashes.

Existing container invocation used:
```
docker exec -e OPENBLAS_NUM_THREADS=1 -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /tmp/agent-toolbar-evidence-package/code/tensor_replay.py /tmp/agent-toolbar-evidence-package/inputs /tmp/agent-toolbar-evidence-package/recipe.json /tmp/agent-toolbar-evidence-package/native-replay --scale 1
```
No services were installed/restarted and no GPU/native-app/live-lab work occurred.

## Remaining limits and next work

The whole inherited tensor map is empirical, not a recovered thick solid or Apple shader. d-stroke curvature still differs, the .3L shadow width is provisional, source paper is estimated, archive outline approximate. Separate wider-shadow analysis improves total/far exterior but regresses one narrow band and does not change optical E; it is not another pass or silently substituted into this recipe.

Second-observation proposal B714s is in ../second-observation/report.md. About30% provisional footprint lacks conservative donor support; no clean B source/paired epoch exists. Paired fitting waits for20 qualifying singles and lead source/pose review. Existing A history/baseline stays frozen.

Required next-steps request was sent/saved before this final prior-queue package. Continue the replenished queue: bounded tangential-onset study against THIS accepted revision2, conditional coupled family, clean-B-background proposal if feasible. Do not optimize against an unaccepted predecessor or subdivide a study into passes. Primary alone accepts/counts/commits/publishes; explicit Ana pause overrides continuation.
