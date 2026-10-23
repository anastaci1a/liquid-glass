# Liquid Glass research

A reusable, explainable rendering system grounded in explicit geometry and visible reference evidence.

| Start here | Purpose |
| --- | --- |
| [Current research](research/current/state.md) | Accepted components and unresolved defects. |
| [Next hypothesis](research/current/next.md) | Source blur before refraction; awaiting research authorization. |
| [Feedback](research/feedback/README.md) | Visible issues and their dispositions. |
| [Documentation conduct](DOCUMENTATION.md) | Concise formats for all maintained records. |
| [Field guide](guide/README.md) | Apple references and reconstruction comparisons. |
| [Interactive Lab](lab/README.md) | Separate illustrative browser model. |

## Workspace

| Directory | Role |
| --- | --- |
| `research/` | Current state, methods, experiments, feedback and evidence. |
| `reconstruction/` | Shared optics, rendering, historical studies and tests. |
| `guide/` | Reference guide and static publishing tools. |
| `lab/` | Browser Lab; not the physical research engine. |
| `agents/` | Ownership and collaboration rules. |
| `migration/` | Source history, file mappings and validation. |

## Checks

~~~sh
npm ci --ignore-scripts
npm run build
npm test
python3 -m pip install -r reconstruction/requirements.txt
python3 -m unittest discover -s reconstruction -p 'test_geometric*.py'
~~~

See [evidence restoration](research/evidence/README.md) for Git LFS artifacts. Historical scripts remain evidence; current work must use the [geometry-first method](research/method/README.md).

This project was extracted from [Localica](https://github.com/anastaci1a/localica) with research-specific history. Original IDs and file mappings remain in [migration records](migration/README.md).
