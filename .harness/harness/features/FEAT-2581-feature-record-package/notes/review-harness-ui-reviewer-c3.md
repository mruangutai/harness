# FEAT-2581 · round 3 · UI scope census (Mode B)

**Out of scope.** The pinned diff contains no rendered product UI. Accessibility, focus, theme parity, and layout were not applicable; no rendering or UAT was performed.

- `git diff --name-only --no-renames -z e12381fde910eb05728004476a10d741d6918010 c039c32dea25d26e3235ee90e1343d7280ddfd4e` yielded **156 paths** (prior pin `a03103b0`: 146): 74 `.py`, 55 `.md`, 17 `.json`, 7 `.yaml`, 2 `.gz`, 1 `.js`. The final commit itself changed only three Python receipt scripts and three Markdown notes.
- Zero case-insensitive extension matches for markup, styles, components, image/font assets, and UI templates: `html htm xhtml css scss sass less styl jsx tsx vue svelte astro svg png jpg jpeg gif webp avif ico woff woff2 ttf eot otf hbs handlebars jinja jinja2 j2 mustache twig liquid ejs pug mdx qml ui xaml swift kt dart`. Of `js mjs cjs ts mts cts`, the sole match was `feat2581-bun-preload.js`; the pinned blob instruments Bun test subprocesses and does not render UI. A supplemental scan of added Python and Markdown lines returned no inline UI markers.
- The pinned tree has neither a feature `DESIGN.md` nor a feature prototype. The brief describes package migration, CLI bytes, and gate diagnostics, not a visual surface.

Open questions: none.
