# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal academic website for Matthew C. Chan, built with Hugo and deployed to GitHub Pages at https://matthewcchan.github.io.

## Build & Development

```bash
# Local development server
hugo server

# Build for production
hugo --gc --minify
```

Hugo version: **0.156.0** (extended edition). This is set in `.github/workflows/gh-pages.yml`.

## Architecture

- **Static site generator**: Hugo
- **Theme**: `hello-friend-ng` (included as a git submodule from `matthewcchan/hugo-theme-hello-friend-ng`)
- **Config**: `hugo.toml` — site settings, menu items, social links, theme params, Goldmark unsafe rendering
- **Content pages**: `content/` — written as `.md` files with YAML front matter (`---`), using raw HTML inline where needed (enabled by `markup.goldmark.renderer.unsafe = true`)
- **Content sections**: Top-level pages (`about.md`, `cv.md`, `publications.md`) and `abstracts/` for individual publication detail pages
- **Static CSS/JS**: `static/css/custom.css` and `static/js/custom.js` — shared styles and behavior (scroll-to-top button, download button, publication card layout, filter animation, about page profile layout), registered via `customCSS`/`customJS` in `hugo.toml`
- **Static assets**: `static/` — CV PDF, images (publication TOC figures, background image, profile photo at `static/img/profile.jpg`), custom CSS/JS

## Publications Page

Publications are data-driven. The source of truth is `publications.bib`; a Python script converts it to `data/publications.yaml`, which Hugo renders via a shortcode.

**Data pipeline:**
```
publications.bib  →  scripts/bib_to_data.py  →  data/publications.yaml  →  Hugo shortcode
```

To regenerate after editing the `.bib`:
```bash
python scripts/bib_to_data.py   # requires: pip install bibtexparser PyYAML
```

CI (`.github/workflows/gh-pages.yml`) runs this automatically before every Hugo build.

**`publications.bib` custom fields** (non-standard BibTeX, parsed by the script):
- `image` / `image_alt` — thumbnail path and alt text
- `abstract_url` — relative URL to the abstract page
- `tags` — comma-separated filter keys (see tag table below)
- `badge` — optional label (e.g. `Cover Article`)
- `note` — optional HTML string shown below the tags
- `cofirst` — 1-indexed positions of co-first authors (e.g. `1, 2`)
- `preprint` — preprint URL

**Entry types:**
- `@article` — published journal article (uses journal/volume/number/pages/year/doi)
- `@unpublished` — preprint/in-review (renders as "In review" with preprint link)
- `@incollection` — book chapter (uses booktitle/editor/publisher/year/doi)

**Shortcode** — `layouts/shortcodes/pub-cards.html` renders all entries of a given type from `site.Data.publications`. Used in `content/publications.md` as:
```
{{< pub-cards type="article" >}}
{{< pub-cards type="book" >}}
```

**Tag system** — `tags` in BibTeX is a comma-separated list of filter keys. The script splits these into `filter_tags` (used on `data-tags` for JS filtering) and `display_tags` (shown as `pub-tag` chips — institution tags like `uiuc` are filter-only with no chip). The mapping lives in `TAG_DISPLAY` in `scripts/bib_to_data.py`.

Current topic tags: `transporter`, `molecular-dynamics`, `cryo-em`, `machine-learning`, `covid`, `catalysis`, `review`. Institution tags (filter-only): `uiuc`, `fred-hutch`.

**Filter logic** — `custom.js` reads `.filter-btn[data-filter]` clicks, compares against each card's `data-tags`, and animates cards in/out using `opacity` + `translateY` transitions (double `requestAnimationFrame` for show, `setTimeout(300ms)` for hide). The `#book-chapter-section` div is shown/hidden as a whole based on whether any child card matches.

**Styling** — all publication card styles are in `custom.css` under the `pub-*` namespace: `.pub-card`, `.pub-thumb`, `.pub-content`, `.pub-meta`, `.pub-tags`, `.pub-tag`, `.pub-badge`, `.pub-note`, `.pub-filters`, `.filter-btn`.

## About Page

The about page (`content/about.md`) uses a single-scroll profile layout built entirely with inline HTML and CSS classes defined in `custom.css` under the `profile-*` namespace.

**Structure:**
- All content is wrapped in `.about-content` (constrains width to `700px`, centered) — this class is only used on the about page
- `.profile-hero` — centered hero section: circular avatar, name, title, 2-sentence bio, social icon links
- `.profile-section` — repeated section wrapper with an uppercase `.profile-section-title` label and a rule
- Research Interests — `.profile-interests` unordered list with blue `○` bullets
- Experience / Education — `.profile-timeline` with a vertical blue line (`::before` pseudo-element) and individual `.profile-entry` rows each consisting of a `.profile-entry-dot` and a `.profile-entry-card`

**Profile photo:** place headshot at `static/img/profile.jpg` (referenced by the `<img>` tag in `about.md`).

**Timeline card anatomy:**
```
.profile-entry
  ├── .profile-entry-dot        (blue circle, z-index above the timeline line)
  └── .profile-entry-card       (bordered card matching pub-card style)
        ├── .profile-entry-header   (flex row: role left, date right)
        │     ├── .profile-entry-role
        │     └── .profile-entry-date
        ├── .profile-entry-org
        └── .profile-entry-meta
```

**Key notes:**
- Do not add a `title` in the front matter (set to `""`) — the page name is rendered inside `.profile-name` instead
- Social icon SVGs are inlined directly from the theme's `partials/svg.html`; update URLs in `about.md` if contact info changes (do not rely on `hugo.toml` social params — those only affect the homepage footer)

## Deployment

Pushes to `main` trigger the GitHub Actions workflow (`.github/workflows/gh-pages.yml`) which uses `peaceiris/actions-hugo@v3` to install Hugo and deploys to GitHub Pages via `actions/deploy-pages`.

## Key Notes

- Content pages use Markdown with inline raw HTML (enabled by `markup.goldmark.renderer.unsafe = true`)
- The publications page uses the `{{< pub-cards >}}` shortcode — do not add inline HTML cards to `publications.md`; edit `publications.bib` instead
- The theme submodule must be initialized: `git submodule update --init --recursive`
- Generated SCSS cache (`resources/_gen/`) is gitignored
- `data/publications.yaml` is committed (so `hugo server` works locally without running the script) but is also regenerated by CI on every push
