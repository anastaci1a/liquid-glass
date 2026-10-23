# Publishing

The [research website](https://anastaci1a.github.io/liquid-glass/) is generated from this repository.

## Coverage

| Material | Website treatment |
| --- | --- |
| Maintained Markdown | Rendered pages with local links. |
| Historical research reports | Automatically generated evidence-library pages. |
| Mathematical notation | Locally bundled KaTeX and accessible MathML. |
| Arrays, recipes and media | Labeled downloads or reference comparisons. |
| Illustrative Lab | Separate interactive page. |

Documentation links stay on the website. Links to primary references, source code and the repository remain explicit external resources.

## Deployment

Push to `main` runs `.github/workflows/pages.yml`: install locked dependencies, build, validate, upload and deploy through GitHub Pages.

## Local checks

~~~sh
npm ci --ignore-scripts
npm run build
npm test
npm run test:guide
~~~

Browser checks require Playwright Chromium and its operating-system libraries. Python geometry checks use `reconstruction/requirements.txt`.
