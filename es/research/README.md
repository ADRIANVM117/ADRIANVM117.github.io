# Esquema de contenido de investigación

Crea cada publicación como un archivo `.qmd` individual dentro de `projects/`, `notes/` o `journal/`. No la agregues a `build_content.py`: Quarto la descubre automáticamente desde `es/research.qmd`.

```yaml
---
title: "Título verificado"
description: "Descripción breve dirigida al lector."
date: 2026-01-01
updated: 2026-01-01
type: project # project | note | journal
topics: [tema-uno, tema-dos]
status: ongoing # ongoing | completed | archived
outcome: inconclusive # opcional: supported | rejected | inconclusive | not_applicable
lang: es
github_url: null # opcional
publication_url: null # opcional
translation_url: null # opcional; solo si existe una versión equivalente
---
```

`status` describe el ciclo de vida del trabajo; `outcome` describe el resultado de una hipótesis o experimento y es opcional. El índice público muestra únicamente metadatos útiles para el lector. `lang` es el campo nativo de idioma de Quarto; no se debe usar `language`, porque Quarto lo reserva para archivos de metadatos de idioma.

Cada artículo recibe automáticamente el header y footer de Research desde este directorio. Define `translation_url` con la URL relativa de una página equivalente existente (por ejemplo, `../../../en/research/projects/slug.html`). Si se omite, el control del otro idioma enlaza al índice Research correspondiente e indica discretamente que no hay traducción disponible.

## Presentación del artículo

Los artículos heredan un bloque de título orientado a la lectura, tabla de contenidos, soporte bibliográfico, control para copiar código y la navegación compartida de Research. Estos campos opcionales del front matter solo se muestran cuando contienen un valor:

```yaml
author: "Adrián Vázquez"
series: "Nombre de la serie"
series_number: "01"
github_url: https://github.com/…
previous_url: articulo-anterior.html
previous_title: "Título verificado anterior"
next_url: articulo-siguiente.html
next_title: "Título verificado siguiente"
```

`previous_url`, `next_url` y `github_url` deben apuntar a destinos reales. Usa Markdown estándar de Quarto para ecuaciones, celdas ejecutables de Python, figuras, tablas, referencias cruzadas, notas y citas; agrega entradas bibliográficas verificadas a `references.bib` solo cuando un artículo las necesite.
