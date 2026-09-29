# Yidan Huang — personal site

A bilingual research portfolio, writing space, and public CV for
[yidanhai.github.io](https://yidanhai.github.io/). The site is static HTML, CSS,
and a small amount of JavaScript. GitHub Pages serves the repository root with
`.nojekyll`.

## Update the site

Edit the page fragments in `site_src/pages/` and the shared frame in
`site_src/layout.html`. English and Chinese copy sit together in
`data-lang="en"` and `data-lang="zh"` elements. Page titles, descriptions,
canonical URLs, the RSS feed, redirects, and the sitemap are defined in
`build_site.py`.

```bash
python build_site.py
python scripts/check_site.py
```

The committed root-level HTML files are the generated site. Commit them
together with their sources. The site does not need a JavaScript package manager
or a GitHub Actions build step.

## Regenerate the public CV PDFs

The CV page at `site_src/pages/cv.html` is the source for the English and
Chinese PDFs. Its print layout is in `assets/css/site.css`.

```bash
python build_site.py
python scripts/build_cv_pdfs.py
```

PDF generation uses Python Playwright and a locally installed Chrome/Chromium
browser. Set `CHROME_BIN` if the browser is not on `PATH`. Both PDFs are
committed to `assets/` so site visitors do not need any build tools.

The portrait comes from Yidan Huang's own CV materials. The site self-hosts
DM Sans and Space Grotesk; their SIL Open Font License texts are in
`assets/fonts/`. Research links and editorial source notes are recorded in
`site_src/SOURCES.md`.
