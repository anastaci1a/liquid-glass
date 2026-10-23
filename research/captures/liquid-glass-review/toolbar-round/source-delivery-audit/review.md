# Queue40: original Apple4K delivery and bounded native frame proposal

New to this investigation, NOT claimed newly released: Apple's current [Meet Liquid Glass page](https://developer.apple.com/videos/play/wwdc2025/219/) embeds an [official CMAF master](https://devstreaming-cdn.apple.com/videos/wwdc/2025/219/4/476dabc8-f3bb-4190-8929-4ba7131c939d/cmaf.m3u8) with original3840×2160 HEVC Main10 deliveries. The retained reference used its separate1080pHDdownload. This is a genuinely different ORIGINAL delivery fetched from Apple, not a local enlargement/recompression. Its stored precision/sample grid is verified; the original UI acquisition/render bandwidth and exact spatial PSF are NOT certified merely by a4Klabel.

|format|retained HD download|bounded highest-advertised4K HLS delivery|
|---|---|---|
|video|1920×1080 AVC High|3840×2160 HEVC Main10|
|source samples|8bit yuv420p|10bit yuv420p10le|
|chroma grid|960×540|1920×1080|
|range/primaries/transfer/matrix|limited BT709|limited BT709|
|rate|30000/1001|30000/1001|
|timebase|1/30000|1/90000|
|bitrate evidence|whole-video stream1406967bps|master peak14982329/average2653639bps; selected fragment≈2.063Mbps over6.006s including fragment overhead|

Main10/BT709 is not HDR or proof of the original UI working-light space.4K has4×stored luma samples and4×chroma samples with10bit quantization versus8, but compression, embedded source resolution and temporal animation still limit information. Direct native outside-text/d crops are preserved and were visually inspected; they do not magically recover hidden ink or a physical alpha boundary. Do NOT claim native4Kformat alone proves extra independent optical truth or a successful pass.

## Original provenance and bounded interval

Retained HD file235716228bytes, source-manifest SHA3d58f9e843f0b8c22e99d76de6b5201ef5b17de5bb4bf5732862ba7dbf9be60e. Old710PNG differs in PNG encoding bytes from frozen target, but decoded RGB SHA64891d0d0d98c4dccf89adba63489e484095e450d72dac7ba939531025f03fe8is identical, maximum pixel difference0. No old-source frame extraction/720/724 donor registration was repeated.

Fetched official master6210bytes SHA8290e9bfbaff56984e7c8ef4eefdae8d778db0bf4df9dff696451ebf94f019b3. Source variant selected by highest advertised native resolution/bandwidth BEFORE frame comparison, not optical score: cmaf/hvc/2160p_16800/hvc_2160p_16800.m3u8, SHA595c7242f362370d16e877cba9aec6c0cce0927682b6fb8d9989b945b1632cb1. Alternate2160p_11600 and1080p_6000 playlist metadata retained; no whole videos fetched. Masterwrapperlast-modified2025-09-17 while variant/fragmentsdate2025-06-09: this is not evidence the4Kcontent itself was newly introduced inSeptember.

Only originalinit825bytes SHAba0174aa96dfb7b2459ba1cf05c0a81034554ed0693b8b14c4f8e7c30c6e16d7 plus ONE originalsegment119,1548644bytes SHA036e2583f9d0026d00f16b4059d050252ee8e6af038fa34893507eb888810d9e downloaded. Logical playlist interval708.708–714.714s;180nativeframes/6.006s. Local original-4k-segment119.mp4 is BYTE CONCATENATION of those exact files, not remux/reencode/rescale. Full source fragment hashes/headers/officialURLs retained. ffprobe reports absolute end timestamp714.747367 as format.duration; its resulting tiny containerbitrate is NOT the actual6.006second fragmentrate and is not used as such.

## Presentation phase — one frame matters

OldHD21279nativeframe PTS710.009300 maps to the chosen HLS SAMECONTENT at PTS710.042667 (integer63903840/90000), one3003/90000frame later. HLSsegment starts PTS708.741367, oneframe beyond its logical playlist position. Three original adjacent4Kframes decoded without resize or lossy recompression into16bitRGBPNG (source10bit YUV converted using taggedvideo decode); original compressed fragments remain the source of truth.

|HLS segment frame|original HLS PTS|whole-frame phase-control RMS against oldHD|
|---|---:|---:|
|38|710.009300|8.66523|
|39|710.042667|1.26508|
|40|710.076033|8.67704|

Fixed2×AREA reduction is used ONLY to diagnose content phase/codec differences at the old native grid; it is NOT a reference proposal, optical E or fitted registration. Full frame comparison, no crop coefficient, mask selection or optimizer. Outside-known-text control similarly15.0476/1.3930/15.1356. This independently supports the metadata-derived+oneframe offset at this interval/variant. Do not assume PTS equality across deliveries or claim other examples' phases verified automatically.

Representative original proposal: phase-02-original4k-rgb16.png,3840×2160, SHA590a3352922e756b424173bede87e6151c7f9383bc958931732c6202c811bc8b. Native d/outside-text crops and both adjacent controls retained. The proposal has no local enlargement, sharpening, font synthesis, optical render or source correction. Native4Kencoding is confirmed; UI acquisition bandwidth, exact color conversion/PSF and under-glass incidentRGB remain limitations. Further same-delivery independent source checks belong to a separate authorized task, not automatic adoption.

Accounting: one failedFFmpegfilter syntax attempt saved0frames, then one successful bounded decode of3representative frames. One phase-analysis import failed before processing because privatecv2PYTHONPATH was missing; corrected persisted driver completed once. Failure receipts retained. ZERO optical renders/fits/Ecomparisons, source replacements, epoch changes, successful passes, public edits or commits. All three-source frames are same physical observation/encoding phase controls, not a third element or activated paired-background stage.

## Source-stage separation

39matrix and current accepted revision3/count3/OLDsource stay fixed.41must evaluate exactly the independently verified23input against CURRENTrev3, not silently substitute4Kdelivery or change target/resolution/masks. Any later4Kinput/target proposal needs explicit primary stage/provenance/native reevaluation and cannot count raw-resolution/encoding/source changes as optical progress. This delivery alone does not supply the required same-pose CLEAN underlying RGB/paper, calibratedPSF or directphysicalalpha/contour. Its additional stored samples may improve measurement, but conceptual source/silhouette identification limits remain.

Request23 was sent BEFORE41 while40continued; no repeated source scans or donors. Exact metadata-fetch URLs/hashes are in official-metadata-fetch.json, variant-fetch.json and fragment-fetch.json. All originals and PNGs remain private under /evidence/extended/helper-toolbar-work/agent-toolbar-source-delivery; canonicalpacket here references largefiles rather than duplicating them under nearly-full containerroot. See recipe.md for completed decoder/probe/analysis commands. Lead owns review/adoption/publication.
