# Research content schema

Create each publication as an individual `.qmd` file in `projects/`, `notes/`, or `journal/`. Do not add it to `build_content.py`: Quarto discovers it automatically from `en/research.qmd`.

```yaml
---
title: "Verified title"
description: "Brief reader-facing description."
date: 2026-01-01
updated: 2026-01-01
type: project # project | note | journal
topics: [topic-one, topic-two]
status: ongoing # ongoing | completed | archived
outcome: inconclusive # optional: supported | rejected | inconclusive | not_applicable
lang: en
github_url: null # optional
publication_url: null # optional
translation_url: null # optional; add only when a real equivalent exists
---
```

`status` describes the lifecycle of the work; `outcome` describes the result of a hypothesis or experiment and is optional. The public index shows only reader-facing metadata. `lang` is Quarto's native language field; do not use `language`, which Quarto reserves for language metadata files.

Every article automatically receives the Research header and footer from this directory. Set `translation_url` to the relative URL of an existing equivalent page (for example, `../../../es/research/projects/slug.html`). When it is omitted, the other-language control links to that language's Research index and indicates that no translation is available.

## Article presentation

Articles inherit a reader-focused title block, table of contents, bibliography support, code-copy control, and the shared Research navigation. These optional front-matter fields are shown only when they contain a value:

```yaml
author: "Adrián Vázquez"
series: "Series name"
series_number: "01"
github_url: https://github.com/…
previous_url: previous-article.html
previous_title: "Previous verified title"
next_url: next-article.html
next_title: "Next verified title"
```

`previous_url`, `next_url`, and `github_url` must point to real destinations. Use standard Quarto Markdown for equations, executable Python cells, figures, tables, cross-references, footnotes, and citations; add verified bibliography entries to `references.bib` only when an article needs them.
