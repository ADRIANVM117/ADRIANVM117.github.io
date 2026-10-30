# Editorial & Warm — Bilingual Quarto personal site

An initial **working prototype**, with source `.qmd` pages, shared CSS, mobile navigation, language-equivalent EN/ES links, a static HTML preview, and a GitHub Actions Pages workflow.

## Preview without Quarto
Open `preview/index.html` in a browser, or run from the `preview/` directory:

```bash
python -m http.server 8000
```

Go to `http://localhost:8000`.

## Develop with Quarto

This project is validated with Quarto 1.10.19. Install
[Quarto](https://quarto.org/docs/get-started/) if needed, then run:

```bash
quarto preview
quarto render
```

The render goes into `docs/`. The Quarto output has been rendered and
validated locally. The independent HTML preview remains available for quick
static checks.

## Deploy
1. Create a new GitHub repository and push this folder to its `main` branch.
2. In GitHub **Settings → Pages**, choose **GitHub Actions** as the build/deployment source.
3. The supplied `.github/workflows/publish.yml` renders the Quarto site and publishes `docs` on push.
4. Your site will appear at the Pages URL that GitHub assigns. If using a *project repository* (`username.github.io/repository`), check relative asset links before launch.

## Editorial decisions
- Primary language English (`/en/`), Spanish equivalent (`/es/`)
- Manual editorial translations, **not** automatic translation
- Warm ivory `#F7F5EF`, charcoal `#252522`
- Project and writing placeholders are explicitly labeled as drafts or work in
  progress; article dates and actual publications are **not** fabricated
- Research articles are individual bilingual Quarto documents with manual
  translations only where a translation exists

## Structure
- `en/` and `es/`: core Quarto pages plus independent Research articles
- `assets/site.css`: shared design system
- `assets/site.js`: responsive menu
- `build_content.py`: regenerates the shared starter pages; approved CV and
  Research documents are maintained directly as `.qmd` source files and are
  not overwritten
- `preview/`: static HTML preview (no Quarto required)

## Known next iteration
- Review or replace draft cards before launch as editorial decisions are made
- Add future research as standalone paired or single-language QMD documents,
  with verified status, dates and links
- Test the final GitHub Pages URL after the repository is created and deployed
