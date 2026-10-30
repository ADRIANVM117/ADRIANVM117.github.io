from pathlib import Path
from html import escape
from shutil import copy2
root=Path(__file__).parent
site_name='Adrián Vázquez'
pages=['index','research','projects','writing','about','cv']
# Research indexes and their individual publications are maintained directly in
# Quarto. Keep them out of this generator so future research pages are never
# overwritten when the existing site pages are rebuilt.
generated_pages=['index','projects','writing']
nav={'en':['Home','Research','Projects','Writing','About','CV & Contact'],'es':['Inicio','Investigación','Proyectos','Escritura','Sobre mí','CV y contacto']}
data={
'en':{
'hero_kicker':'RESEARCH / QUANTITATIVE LAB / PERSONAL CAPITAL MANAGEMENT','headline':'Quantitative research,<br><em>writing, and ideas.</em>',
'deck':'A personal space where I share research, develop models using real data, and document how they are applied to problems and decisions in financial markets.',
'cta1':'Explore research','cta2':'View projects','micro':'PORTFOLIO CONSTRUCTION & OPTIMIZATION · RISK MODELING · ALPHA RESEARCH',
'intro':'I study the intersection of financial markets, probability and computation. This is where I document the questions, experiments and work that shape my thinking.','home_intro':'My work combines empirical research, the development of quantitative strategies, and investment decision-making. Here I share experiments, results, and reflections on what works, what does not, and the questions that remain open.',
'selected':'Selected work','writing':'Notes & writing',
'abouthead':'A little about me','abouttext':'I have a background in actuarial science and quantitative modeling. My interests span systematic strategies, market microstructure, portfolio research, and financial machine learning. I value transparent experiments, careful validation, and ideas that survive scrutiny.','home_abouttext':"My background is in actuarial science and quantitative modeling. I'm interested in exploring what happens when academic ideas are put into practice: working with real data, building systems, facing practical constraints, and understanding why some strategies work while others fail. My goal is to bring research closer to concrete investment decisions, where results are measured not only by statistical metrics but also by their ability to generate returns and preserve capital.",
'contacthead':"I'm Adrián Vázquez, an actuary.",'contacttext':'Here I share part of my professional and academic background, the tools I work with, and the places where you can find my code, publications, and ways to get in touch.','cvbtn':'CV & contact','cvlabel':'MY BACKGROUND','footer':'Research, projects and notes in progress.',
'featured':('PORTFOLIO ENGINE / 03','Joint Resampling: Building Scenarios from Historical Returns','Scenario construction through joint resampling of historical returns. A comparison of one- and five-session horizons, exponential weighting, and the effect of Monte Carlo noise on simulated results.'),
'projects_empty':'Projects will appear here as they are ready to share.',
'writing_empty':'Writing is in preparation. Published notes will appear here as they are completed.',
'pageintro':{'research':('Research','Questions, experiments, methodologies, and findings—along with their limits.'),'projects':('Projects','Selected codebases and independent experiments, organized by research problem.'),'writing':('Writing','A space for essays, notes, and research diaries.'),'about':('About','A little about the background, interests and ideas behind the work.'),'cv':('CV',"My background is in actuarial science, with professional experience in credit risk modeling and machine learning. Alongside this work, I've developed my own research in quantitative finance, focusing on portfolio construction, systematic strategies, and financial markets.")},
'blurb':'Research is not only about finding a result; it is also about understanding why an idea fails.',
},
'es':{
'hero_kicker':'INVESTIGACIÓN / LABORATORIO CUANTITATIVO / GESTIÓN DE CAPITAL PROPIO','headline':'Investigación cuantitativa,<br><em>escritura e ideas.</em>',
'deck':'Un espacio personal donde comparto investigaciones, desarrollo modelos con datos reales y documento su aplicación a problemas y decisiones de los mercados financieros.',
'cta1':'Explorar investigaciones','cta2':'Ver proyectos','micro':'CONSTRUCCIÓN Y OPTIMIZACIÓN DE PORTAFOLIOS · MODELADO DE RIESGO · INVESTIGACIÓN DE ALPHA',
'intro':'Exploro la intersección entre los mercados financieros, la probabilidad y la computación. Aquí documento las preguntas, experimentos y trabajos que forman mi manera de pensar.','home_intro':'Mi trabajo combina investigación empírica, desarrollo de estrategias cuantitativas y toma de decisiones de inversión. Aquí comparto experimentos, resultados y reflexiones sobre lo que funciona, lo que no y las preguntas que siguen abiertas.',
'selected':'Proyectos destacados','writing':'Notas y artículos',
'abouthead':'Un poco sobre mí','abouttext':'Tengo formación en actuaría y modelación cuantitativa. Mis intereses abarcan estrategias sistemáticas, microestructura de mercados, investigación de portafolios y machine learning financiero. Valoro los experimentos transparentes, la validación cuidadosa y las ideas que resisten el escrutinio.','home_abouttext':'Tengo formación en actuaría y modelación cuantitativa. Me interesa explorar qué ocurre cuando las ideas académicas se llevan a la práctica: trabajar con datos reales, construir sistemas, enfrentar limitaciones y entender por qué algunas estrategias funcionan mientras otras fracasan. Mi objetivo es acercar la investigación a decisiones de inversión concretas, donde los resultados no se miden únicamente con métricas estadísticas, sino también por su capacidad de generar rendimientos y preservar capital.',
'contacthead':'Soy Adrián Vázquez, actuario.','contacttext':'Aquí comparto parte de mi trayectoria profesional y académica, las herramientas con las que trabajo y los distintos espacios donde puedes encontrar mi código, publicaciones y medios de contacto.','cvbtn':'CV y contacto','cvlabel':'SOBRE MI TRAYECTORIA','footer':'Investigaciones, proyectos y notas en desarrollo.',
'featured':('PORTFOLIO ENGINE / 03','Joint Resampling: construcción de escenarios a partir de retornos históricos','Construcción de escenarios mediante remuestreo conjunto de retornos históricos. Comparación de horizontes de una y cinco sesiones, ponderación exponencial y análisis del efecto del ruido Monte Carlo sobre los resultados simulados.'),
'projects_empty':'Los proyectos aparecerán aquí conforme estén listos para compartirse.',
'writing_empty':'La sección de escritura está en preparación. Las notas publicadas aparecerán aquí al completarse.',
'pageintro':{'research':('Investigación','Preguntas, experimentos, metodologías y hallazgos, junto con sus limitaciones.'),'projects':('Proyectos','Código y experimentos independientes organizados por pregunta de investigación.'),'writing':('Escritura','Un espacio para ensayos, notas y diarios de investigación.'),'about':('Sobre mí','Formación, intereses e ideas detrás de la investigación.'),'cv':('CV','Trayectoria profesional, formación académica y práctica técnica en ciencia de datos cuantitativa y servicios financieros.')},
'blurb':'Investigar no consiste solo en encontrar un resultado; también implica entender por qué una idea falla.'
}}

def rel(lang,page,preview=False): return f'../{lang}/{page}.html' if preview else f'../{lang}/{page}.qmd'
def header(lang,page,preview=False):
 d=data[lang]; links=''.join(f'<a class="navlink {"current" if page==p else ""}" href="{rel(lang,p,preview)}">{nav[lang][i]}</a>' for i,p in enumerate(pages))
 profiles='''<div class="platform-links" aria-label="Professional platforms"><a href="https://github.com/ADRIANVM117" target="_blank" rel="noopener noreferrer" aria-label="GitHub — Adrián Vázquez"><img src="../assets/brands/github.svg" alt=""></a><a href="https://www.linkedin.com/in/adrián-vazquez-1a90a01b6" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn — Adrián Vázquez"><img src="../assets/brands/linkedin.svg" alt=""></a><a href="https://substack.com/@radian117" target="_blank" rel="noopener noreferrer" aria-label="Substack — Adrián Vázquez"><img src="../assets/brands/substack.svg" alt=""></a><a href="https://medium.com/@doromenoharris0" target="_blank" rel="noopener noreferrer" aria-label="Medium — Adrián Vázquez"><img src="../assets/brands/medium.svg" alt=""></a></div>'''
 other='es' if lang=='en' else 'en'; switch=rel(other,page,preview)
 return f'''<div class="site-shell" data-language="{lang}" data-page="{page}"><style>.platform-links{{display:flex;align-items:center;gap:18px;margin-left:2px}}.platform-links a{{display:inline-flex;opacity:.78;transition:opacity .18s ease}}.platform-links a:hover{{opacity:1}}.platform-links a:focus-visible{{outline:2px solid var(--accent);outline-offset:4px}}.platform-links img{{width:19px;height:19px;display:block}}@media(max-width:720px){{.platform-links{{margin:5px 0 0;gap:20px}}.platform-links img{{width:20px;height:20px}}}}</style><header class="site-header"><a class="wordmark" href="{rel(lang,'index',preview)}">{site_name}<span class="wordmark-dot">.</span></a><button type="button" class="menu-toggle" aria-controls="main-nav" aria-expanded="false" aria-label="Toggle navigation">☰</button><nav id="main-nav" class="navigation" aria-label="Primary navigation">{links}{profiles}</nav><div class="language-switch" aria-label="Language"><a href="{rel('en',page,preview)}" lang="en" class="{'active' if lang=='en' else ''}">EN</a><span>/</span><a href="{rel('es',page,preview)}" lang="es" class="{'active' if lang=='es' else ''}">ES</a></div></header>'''

def chart(lang):
 label='FIG. 01 / FROM RESEARCH TO PRACTICE' if lang=='en' else 'FIG. 01 / DE LA INVESTIGACIÓN A LA PRÁCTICA'
 return f'''<div class="graphic" role="img" aria-label="Abstract mathematical contours, a decorative research motif"><svg viewBox="0 0 540 430" aria-hidden="true" focusable="false"><defs><pattern id="dotgrid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".75" fill="#a8a29a" opacity=".55"/></pattern></defs><rect width="540" height="430" fill="url(#dotgrid)"/><g fill="none" stroke="#48473e" stroke-width="1.25" opacity=".65"><path d="M25 280 C95 250 92 370 160 320 S240 175 303 235 410 345 516 155"/><path d="M25 258 C95 228 96 347 160 295 S239 156 303 215 410 321 516 132"/><path d="M25 237 C95 204 99 325 162 272 S239 134 305 192 410 298 516 111"/><path d="M25 216 C95 185 101 306 165 250 S238 114 307 173 410 277 516 88"/><path d="M25 196 C95 166 103 284 168 228 S239 94 309 151 410 256 516 65"/></g><circle cx="303" cy="215" r="4" fill="#8A6853"/><path d="M303 215V397" stroke="#8A6853" stroke-dasharray="3 6"/><text x="28" y="42" fill="#766F65" font-family="monospace" font-size="12" letter-spacing="2">{label}</text></svg></div>'''

def projectcards(lang):
 d=data[lang]; shape=['contours','candles','curves','grid-art']; out='<div class="project-grid">'
 for i,(tag,title,desc) in enumerate(d['projects']):
  out+=f'<article class="project-card"><div class="card-art {shape[i]}"><span class="art-index">0{i+1}</span></div><div class="micro muted">{tag}</div><h3>{title}</h3><p>{desc}</p><span class="stub">{d["status"]} ↗</span></article>'
 return out+'</div>'

def writingcards(lang):
 d=data[lang];out='<div class="writing-grid">'
 for i,(cat,title,desc) in enumerate(d['posts']):
  out+=f'<article class="writing-item"><div class="micro muted">0{i+1} / {cat}</div><h3>{title}</h3><p>{desc}</p><span class="stub">{d["empty"]}</span></article>'
 return out+'</div>'

def featured_research(lang):
 label, title, description=data[lang]['featured']
 href=f'research/projects/03_joint_resampling.html'
 return f'''<article class="writing-item"><div class="micro muted">{label}</div><h3><a class="no-external" href="{href}">{title}</a></h3><p>{description}</p><a class="end-link" href="{href}">{data[lang]["cta1"]} ↗</a></article>'''

def foot(lang):
 d=data[lang];return f'''<footer class="site-footer"><div><span class="footer-name">{site_name}.</span><p class="micro">{d['footer']}</p></div><span class="footer-symbol">∴</span></footer></div>'''

def sectionhead(number,title,right):return f'<div class="section-heading"><span class="micro section-number">{number} / {title}</span><span class="section-rule"></span><span class="micro right-label">{right}</span></div>'

def home(lang):
 d=data[lang]
 return f'''<main><section class="hero"><div class="hero-copy"><div class="micro hero-kicker">{d['hero_kicker']}</div><h1>{d['headline']}</h1><p class="hero-deck">{d['deck']}</p><div class="hero-actions"><a class="button dark" href="{rel(lang,'research')}">{d['cta1']} <span>↗</span></a><a class="button light" href="{rel(lang,'projects')}">{d['cta2']} <span>↗</span></a></div><p class="micro intro-label">{d['micro']}</p><p class="hero-intro">{d['home_intro']}</p></div>{chart(lang)}</section>
<section class="content-section">{sectionhead('01',d['selected'],'PORTFOLIO ENGINE')}{featured_research(lang)}</section>
<section class="content-section closing">{sectionhead('02',d['cvbtn'],d['cvlabel'])}<div class="closing-columns"><div><h2>{d['contacthead']}</h2><p>{d['contacttext']}</p></div><a class="button dark" href="{rel(lang,'cv')}">{d['cvbtn']} ↗</a></div></section>
<section class="content-section about-strip">{sectionhead('03',d['abouthead'],'BACKGROUND / PROFILE')}<div class="about-columns"><h2>{d['blurb']}</h2><div><p>{d['home_abouttext']}</p><a class="text-link" href="{rel(lang,'about')}">{d['abouthead']} ↗</a></div></div></section></main>'''

# CV and About pages are maintained directly as approved Quarto source files.
# They are deliberately excluded from this generator so editorial revisions
# cannot be overwritten by legacy templates.

def inner(lang, page):
 d=data[lang]
 title, sub=d['pageintro'][page]
 intro=f'<main class="inner-main"><section class="page-intro"><div class="micro">{site_name.upper()} / {escape(page.upper())}</div><h1>{title}<span class="period">.</span></h1><p>{sub}</p></section>'
 if page=='projects':
  content=sectionhead('01',d['selected'],'PROJECTS')+f'<div class="two-column-prose"><h2>{d["projects_empty"]}</h2></div>'
 elif page=='writing':
  content=sectionhead('01',d['writing'],'WRITING')+f'<div class="two-column-prose"><h2>{d["writing_empty"]}</h2></div>'
 elif page=='about':
  content=f'''<div class="two-column-prose"><h2>{d['blurb']}</h2><div><p>{d['abouttext']}</p><p>{d['intro']}</p><div class="tag-row"><span>Actuarial science</span><span>Research</span><span>Python</span><span>Markets</span></div></div></div>'''
 else:
  raise ValueError(f'Unknown generated page: {page}')
 return intro+f'<section class="content-section">{content}</section></main>'

for lang in ['en','es']:
 (root/lang).mkdir(exist_ok=True)
 (root/'preview'/lang).mkdir(parents=True,exist_ok=True)
 for p in generated_pages:
  body=(home(lang) if p=='index' else inner(lang,p))
  # preview paths .html, Quarto paths .qmd for HTML output links auto converted by Quarto; render qmd links as html for preview
  htmlbody=header(lang,p,True)+body.replace('.qmd','.html')+foot(lang)
  quarto_body=htmlbody+'<script src="../assets/site.js"></script>'
  qmd=f'''---\ntitle: "{nav[lang][pages.index(p)]} | {site_name}"\nlang: {lang}\npage-layout: full\ntitle-block: false\ntoc: false\n---\n\n<style>#title-block-header{{display:none}}</style>\n\n```{{=html}}\n{quarto_body}\n```\n'''
  (root/lang/f'{p}.qmd').write_text(qmd,encoding='utf-8')
  static=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(nav[lang][pages.index(p)])} | {site_name}</title><link rel="stylesheet" href="../assets/site.css"></head><body>{htmlbody}<script src="../assets/site.js"></script></body></html>'''
  (root/'preview'/lang/f'{p}.html').write_text(static,encoding='utf-8')
preview_assets=root/'preview'/'assets'
preview_assets.mkdir(exist_ok=True)
for asset in ('site.css','site.js'):
 copy2(root/'assets'/asset,preview_assets/asset)
preview_backgrounds=preview_assets/'backgrounds'
preview_backgrounds.mkdir(exist_ok=True)
for asset in (root/'assets'/'backgrounds').glob('*.svg'):
 copy2(asset,preview_backgrounds/asset.name)
print('Created bilingual QMD and preview pages')
