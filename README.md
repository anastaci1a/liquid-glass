# Liquid Glass research

Mathematical models of Apple's Liquid Glass: explicit surfaces, optical transport, material response and reference-based validation.

[Research website](https://anastaci1a.github.io/liquid-glass/) · [Reference comparisons](guide/reconstruction.md) · [Current findings](research/current/state.md)

## Research questions

- Which physical surfaces explain the observed distortion and edge reversal?
- How do refraction, scattering, reflection and compositing contribute independently?
- Which parameters transfer between control families and held-out references?
- What can the available source imagery actually identify?

A visually close image does not establish Apple's private implementation. Mathematical validity, perceptual fidelity, parameter identification and runtime performance are separate claims.

## Explore

| Area | Contents |
| --- | --- |
| [Current research](research/current/state.md) | Accepted components, limitations and next questions. |
| [Method](research/method/README.md) | Physical contracts, isolated stages and bounded experiments. |
| [Observations](research/feedback/README.md) | Visible defects and their disposition. |
| [Experiments](research/experiments/README.md) | Results, negative findings and historical reports. |
| [Evidence](research/evidence/README.md) | Hash-verified arrays, reference excerpts and configurations. |
| [Reconstruction engine](reconstruction/README.md) | Shared optics, geometry adapters and tests. |
| [Illustrative Lab](lab/README.md) | Separate interactive demonstrations. |
| [Documentation](DOCUMENTATION.md) | Recording and mathematical notation standards. |

## Reproduce

~~~sh
npm ci --ignore-scripts
npm run build
npm test
python3 -m pip install -r reconstruction/requirements.txt
python3 -m unittest discover -s reconstruction -p 'test_geometric*.py'
~~~

See [evidence restoration](research/evidence/README.md) for large artifacts and [publishing](guide/PUBLISHING.md) for the website. Apple reference excerpts retain their attribution; source videos and font packages are not redistributed.
