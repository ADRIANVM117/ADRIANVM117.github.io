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
