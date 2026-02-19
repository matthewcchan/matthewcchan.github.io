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
- **Static CSS/JS**: `static/css/custom.css` and `static/js/custom.js` — shared styles (scroll-to-top button, download button, publication list spacing) and scroll behavior, registered via `customCSS`/`customJS` in `hugo.toml`
- **Static assets**: `static/` — CV PDF, images (publication covers, background image), custom CSS/JS

## Deployment

Pushes to `main` trigger the GitHub Actions workflow (`.github/workflows/gh-pages.yml`) which uses `peaceiris/actions-hugo@v3` to install Hugo and deploys to GitHub Pages via `actions/deploy-pages`.

## Key Notes

- Content pages use Markdown with inline raw HTML (no shortcodes needed)
- The theme submodule must be initialized: `git submodule update --init --recursive`
- Generated SCSS cache (`resources/_gen/`) is gitignored
