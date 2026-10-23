# Liquid Glass research

A reusable, explainable Liquid Glass system, extracted with research-specific history from [Localica](https://github.com/anastaci1a/localica).

Start with the [field guide](docs/README.md), [geometric optics](docs/geometric-optics.md), and [migration status](migration/README.md). The current geometric work is preserved separately from older empirical reconstructions; those historical images do not establish physical model fidelity.

No new scientific pass is authorized. Ana's pending observation is that source blur before refraction may reproduce directional compression better than the current output blur. This remains an untested hypothesis.

## Local checks

~~~sh
npm ci --prefix docs
npm run build --prefix docs
node docs/experiments/check-links.cjs
python3 -m pip install -r docs/experiments/reconstruction/requirements.txt
python3 -m unittest discover -s docs/experiments/reconstruction -p 'test_geometric*.py'
~~~

The static build is local only. Existing [published reconstructions](https://anastaci1a.github.io/localica/liquid-glass/reconstruction.html) remain on Localica; this migration does not replace them or deploy Pages.
