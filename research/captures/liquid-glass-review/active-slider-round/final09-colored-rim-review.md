# Final09 Colored-rim publication packet

READY for leadcopy/relabel. Accepted public09 commit46b888dd, greenround3/3 unchanged. NO opticalrerender/fit/newmask/recrop/source/scoreepoch. All metrics recomputed from accepted06 INTAKE savednativecomplete and final09 ACCEPTED savednativecomplete, samefrozenApple native target. These native06 metrics need not equal historical06HQ-derived values; originalpass06JSON/05to06record is preserved, not overwritten or mixed.

EXACT public pass-06-crops.json normalized AND nativepixel rectangles validated across both originalstates, A/B all4crops. Metrics existing schema: RGB/channel RMSE,luma/chroma RMSE,signedRGBmean,p95. All16 state/crop metrics in16KBpass-09-crops.json; no edge-profilebulk. Signedmeans retained without recolor/alignment.

|Ref/crop|06 RGB RMSE|09 RGB RMSE|deltaRGB|deltaLuma|deltaChroma|
|---|---:|---:|---:|---:|---:|
|A upper-left|11.658240997|11.654608337|-0.003632660|-0.001102674|-0.004887317|
|A lower-left|13.744361045|13.745863306|0.001502260|0.002606103|-0.001885371|
|A right-rim|13.841098346|13.840992791|-0.000105555|-0.000198453|0.000106682|
|A center|1.792193250|1.792192913|-0.000000337|-0.000000555|-0.000000436|
|B upper-left|11.939083790|11.937908381|-0.001175409|-0.001260151|-0.000460584|
|B lower-left|11.826845622|11.827615551|0.000769930|0.000546888|-0.000550063|
|B right-rim|11.231119467|11.231104440|-0.000015027|0.000014286|-0.000027343|
|B center|4.774497501|4.774792772|0.000295272|0.000081833|-0.000031700|

Local regressions preserved: A/B lower-left RGB+luma, BcenterRGB+luma, Aright-rimchroma, Bright-rimluma. Allothermetrics and signedRGBremain unrounded inJSON. Tinyglobalgains do NOT solve rainbow/coloredfringe mismatch; heavy innercontour/softness/sourceestimationambiguity persist. Crops advisory, native whole-frame gates untouched. No newaccepted pass.

Publication files in /evidence/extended/helper-toolbar-work/active-slider-round/final09-colored-rim:

- switch-round09-crops.png:1538x3400,Apple/accepted06/final09 columns across8fixedrows; each panel ownapprovedwidth min(2W,max(W,720)) preservesaspect. No automatic4x.
- a-final09-comparison.png and b-final09-comparison.png: Appleleft/final09right, perimagenative825x590/785x570 (originalwidths>720cap stayoriginal).
- a-06-09-comparison.png,b-06-09-comparison.png: saved06/final09 sidebyside, same nativepixels.
- a-final09-native.png,b-final09-native.png: unmodifiedsavednative finalcomposites quantizedonlyforPNG.
- Individualcropapple/rev06/rev09PNG files forleadoptionaluse, nativecropstats unaffected bypresentation2xBILINEAR.
- pass-09-crops.json:16KB existingmetricsschema, stateorderaccepted06/final09 and explicitadvisory/regressions.
- verification.json:inputarray/target/cropreference hashes unchanged, rect exactness,newopticalrenders0,fitmaskchanges0,assetSHA+sizes.

Sheet inspected; labels/panels align. Presentationresize/PNGquantization does NOT feed metrics. Accepted06 and09 sourcearrays/targets/publiccropreference hash unchanged afterprocessing. Rootdriver final09-colored-rim.py refusescompletedreruns. Exactcompletedcommand:

    docker exec -e PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps localica-dark-lab-check python3 /evidence/extended/helper-toolbar-work/active-slider-round/final09-colored-rim.py

colored-rim-final09-section.md contains a concrete replacement for only the publicColored-rimdetails block: relabel final09, swap currentimage/link, preserve06 andsnapshot24history, removeoldcurrent06gainclaim. publication-copy-manifest.json mapsfiles toproposedasset/JSON destinations; no publictreeedited. Lead owns finalcopy/diff/commit/publish.

Final09 A/B media already complete/sent1b2125b8 (preferredmotion.mp4+motion-6s.gif1080/90frames15fps6s,6.01/3.09MB). Light/dark SOURCE/PROTOCOLintake already complete/read-only: legacy4x4native scoresmatcharchive,independentthemes,estimatedsmooth/blackinputs,nooriginalexteriorguard,targetderivedcontextexplicit. No duplicatebaselinework. Source/protocolnextdirectionrequestd6a3c553 sentbeforeintakepackaging, completedintakefd2367fc sent; reviewlight-dark-round/source-protocol-intake-review.md. No newfit/source/shadowadoption untilleadreview; blue/selectorassets untouched.
