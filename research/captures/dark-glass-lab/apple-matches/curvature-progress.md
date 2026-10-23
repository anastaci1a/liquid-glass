- Checkpoint `b6c56fe` pushed on PR414: tangential tensor/potential controls, continuous-height Snell models, Fresnel/environment and dispersion hypotheses, numerical controls. Native app/main/Pages unchanged.
- Found a sampling defect: every-second-pixel fitting skipped much of the slider's one-pixel dark upper rim. New searches sample every native-pixel parity, integrate material subpixels and share a final-render training objective.
- Toolbar tangential model improves preliminary rim RMSE (~10.95→9.3/255). Uniform-background ablation also reproduces the old inner whitish band: independent lighting contributes; it is not purely refraction.
- Slider color attribution remains unresolved. Testing geometry-coupled RGB environments against wavelength-dependent Snell/Fresnel models; no hand-painted colored outline or recovered-Apple-shader claim. Final common-material scoring/figures still in progress.
— Codex
