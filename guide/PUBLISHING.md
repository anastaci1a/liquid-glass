# Publishing

The canonical site is [Liquid Glass research](https://anastaci1a.github.io/liquid-glass/). Its source is this repository.

## Deployment

Push to `main` runs `.github/workflows/pages.yml`: install locked dependencies, build, validate, upload the static artifact and deploy through GitHub Pages.

| Output | Source |
| --- | --- |
| Field guide | `guide/*.md` |
| Illustrative Lab | `lab/` |
| Public reconstruction recipes | Tracked `reconstruction/` files |
| Formula rendering | Locally bundled KaTeX and fonts |

Only the explicit public publishing set enters `guide/site/`. Private recovery snapshots and indexed research artifacts are not exported into the website.

## Compatibility

The former Localica Pages HTML routes redirect to corresponding pages here, preserving fragments and query strings. Frozen compatibility assets remain available for old embeds; Localica no longer builds current research.

## Local checks

~~~sh
npm ci --ignore-scripts
npm run build
npm test
npm run test:guide
~~~

Browser checks require Playwright Chromium and its operating-system libraries. Python geometry checks use the separately pinned `reconstruction/requirements.txt`.
