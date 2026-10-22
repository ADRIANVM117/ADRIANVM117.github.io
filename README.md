# Editorial & Warm — Bilingual Quarto personal site

An initial **working prototype**, with source `.qmd` pages, shared CSS, mobile navigation, language-equivalent EN/ES links, a static HTML preview, and a GitHub Actions Pages workflow.

## Preview without Quarto
Open `preview/index.html` in a browser, or run from the `preview/` directory:

```bash
python -m http.server 8000
```

Go to `http://localhost:8000`.

## Develop with Quarto
Install [Quarto](https://quarto.org/docs/get-started/) then run:

```bash
quarto preview
quarto render
```

The render goes into `docs/`. This environment did **not** have Quarto available, so the generated Quarto version has not been rendered/visually tested; the independent HTML preview uses the same page markup and stylesheet.

## Deploy
1. Create a new GitHub repository and push this folder to its `main` branch.
2. In GitHub **Settings → Pages**, choose **GitHub Actions** as the build/deployment source.
3. The supplied `.github/workflows/publish.yml` renders the Quarto site and publishes `docs` on push.
4. Your site will appear at the Pages URL that GitHub assigns. If using a *project repository* (`username.github.io/repository`), check relative asset links before launch.

## Editorial decisions
- Primary language English (`/en/`), Spanish equivalent (`/es/`)
- Manual editorial translations, **not** automatic translation
- Warm ivory `#F7F5EF`, charcoal `#252522`
- Placeholder project descriptions based on research topics only; article dates and actual publications are **not** fabricated
- Do **not** publish the site as a final CV until replacing `Personal Research`, adding verified GitHub/LinkedIn URLs, CV document, contact and real published links

## Structure
- `en/` and `es/`: 6 Quarto pages each
- `assets/site.css`: shared design system
- `assets/site.js`: responsive menu
- `build_content.py`: generates the current starter site pages; edit this when updating the starter content, or remove this generator and edit QMD directly later
- `preview/`: static HTML preview (no Quarto required)

## Known next iteration
- Replace placeholder name with the chosen public name
- Add verified case studies and articles as standalone QMD pages, with real status, dates and links
- Create real paired article translations, and show explicit translation availability
- Replace conceptual illustration with a real chart/graphic from your work if desired
- Test Quarto output and Pages URL after install/push
