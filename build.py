"""Génère le site statique dans docs/ à partir de src/.

    python build.py

- src/pages/*.html : contenu de chaque page (sans en-tête ni pied de page).
  Les premières lignes « clé: valeur » jusqu'à une ligne « --- » donnent
  title, description, nav (rubrique active), hero (dark = en-tête clair sur photo), og.
- src/projets.json : les réalisations (une fiche projet générée par entrée).

Macros utilisables dans les pages :
  [[img:nom|texte alternatif|sizes|classe|eager]]  image responsive (docs/img/nom.webp + nom-s.webp)
  [[index]]                                        index des réalisations (filtres, liste, grille)
  [[hpanels]]                                      panneaux du défilement horizontal de l’accueil
  [[link:slug|texte]]                              lien texte vers une fiche projet
  [[src:nom]]                                      chemin de la petite image (pour data-img)
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SITE = "architecture4future"

PROJETS = json.loads((SRC / "projets.json").read_text(encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PROJETS}

NAV = [
    ("index", "index.html", "Accueil"),
    ("competences", "competences.html", "Compétences"),
    ("realisations", "realisations.html", "Réalisations"),
    ("vegetal", "vegetal.html", "Le végétal"),
    ("agence", "agence.html", "L’agence"),
    ("contact", "contact.html", "Contact"),
]

E = html.escape
VERSION = "8"


SIZES = json.loads((OUT / "img" / "sizes.json").read_text(encoding="utf-8"))


def srcset(name):
    """Toutes les tailles réellement disponibles d’une photo (800, 1400, native jusqu’à 2400)."""
    ws = SIZES.get(name, [])
    native = max(ws) if ws else 0
    parts = []
    for w in ws:
        f = f"img/{name}.webp" if w == native else f"img/{name}-{'s' if w == 800 else 'm'}.webp"
        parts.append(f"{f} {w}w")
    return ", ".join(parts)


def img(name, alt="", sizes="100vw", cls="", eager=False, attrs=""):
    ss = srcset(name)
    srcs = f' srcset="{ss}" sizes="{sizes}"' if ss.count("w,") >= 1 else ""
    c = f' class="{cls}"' if cls else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="img/{name}.webp"{srcs} alt="{E(alt)}"{c} {load}{attrs}>'


def alt_for(p, i=0):
    return f"{p['titre']} — {p['sous_titre'].lower()}" if i == 0 else f"{p['titre']}, vue {i + 1}"


ORDER = ["Habitat", "Réhabilitation", "Bureaux", "Équipement", "Urbanisme", "Agriculture urbaine"]


def index_block():
    cats = {}
    for p in PROJETS:
        cats[p["categorie"]] = cats.get(p["categorie"], 0) + 1
    btns = [f'<button type="button" data-filter="tout" aria-pressed="true">Tout<sup>{len(PROJETS)}</sup></button>']
    btns += [f'<button type="button" data-filter="{E(c)}" aria-pressed="false">{E(c)}<sup>{cats[c]}</sup></button>' for c in ORDER if c in cats]
    rows, cards = [], []
    for i, p in enumerate(PROJETS, 1):
        cover = p["images"][0]
        rows.append(
            f'<li class="p-row" data-cat="{E(p["categorie"])}"><a href="projet-{p["slug"]}.html" data-img="img/{cover}-s.webp">'
            f'<span class="thumb">{img(cover, alt_for(p), "96px")}</span>'
            f'<span class="mono num">{i:02d}</span><span class="t">{E(p["titre"])}</span>'
            f'<span class="mono loc">{E(p["lieu"])}</span><span class="mono cat">{E(p["categorie"])}</span>'
            f'<span class="mono yr">{E(p["annee"])}</span></a></li>'
        )
        cards.append(
            f'<a class="g-card reveal" href="projet-{p["slug"]}.html" data-cat="{E(p["categorie"])}" data-cursor="Voir">'
            f'<div class="ph">{img(cover, alt_for(p), "(max-width: 760px) 100vw, 33vw")}</div>'
            f'<div class="meta"><span class="mono" style="color:var(--ink-3)">{i:02d} — {E(p["categorie"])} · {E(p["annee"])}</span>'
            f'<div class="h3">{E(p["titre"])}</div><div class="small">{E(p["lieu"])}</div></div></a>'
        )
    return (
        '<div class="p-wrap">'
        '<div class="idx-bar">'
        f'<div class="filters" role="group" aria-label="Filtrer les réalisations">{"".join(btns)}</div>'
        '<div class="view-toggle" role="group" aria-label="Affichage"><button type="button" data-view="list" aria-pressed="true">Liste</button><button type="button" data-view="grid" aria-pressed="false">Galerie</button></div>'
        '</div>'
        f'<ol class="p-index">{"".join(rows)}</ol>'
        f'<div class="gallery">{"".join(cards)}</div>'
        '</div>'
    )


HPANELS = ["grunbox-vienne", "tiny-house-urbaine", "logements-caluire", "maison-jarret", "residence-intergenerationnelle-decines",
           "judo-club-lyon-6", "logements-vienne", "couzon-au-mont-d-or"]


def hpanels():
    out = []
    for i, slug in enumerate(HPANELS, 1):
        p = BY_SLUG[slug]
        out.append(
            f'<a class="hs-panel" href="projet-{slug}.html" data-cursor="Voir">'
            f'<div class="ph">{img(p["images"][0], alt_for(p), "(max-width: 760px) 82vw, 46vw")}</div>'
            f'<div class="hs-meta"><span class="mono">{i:02d}</span><span class="h3">{E(p["titre"])}</span>'
            f'<span class="mono" style="color:var(--ink-3)">{E(p["annee"])}</span></div>'
            f'<div class="small" style="margin:6px 0 0 64px">{E(p["lieu"])} — {E(p["sous_titre"])}</div></a>'
        )
    return "".join(out)


def macros(text):
    def rep(m):
        kind, _, arg = m.group(1).partition(":")
        parts = arg.split("|")
        if kind == "img":
            name, alt = parts[0], parts[1] if len(parts) > 1 else ""
            sizes = parts[2] if len(parts) > 2 and parts[2] else "100vw"
            cls = parts[3] if len(parts) > 3 else ""
            eager = len(parts) > 4 and parts[4] == "eager"
            return img(name, alt, sizes, cls, eager)
        if kind == "index":
            return index_block()
        if kind == "hpanels":
            return hpanels()
        if kind == "src":
            return f"img/{parts[0]}-s.webp"
        if kind == "link":
            p = BY_SLUG[parts[0]]
            return f'<a href="projet-{p["slug"]}.html">{E(parts[1] if len(parts) > 1 else p["titre"])}</a>'
        raise ValueError(m.group(0))
    return re.sub(r"\[\[([a-z]+(?::[^\]]*)?)\]\]", rep, text)


ICON_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.1-1.1.1-1.7.2-2.1.4-.5.2-.9.4-1.2.8-.4.4-.6.7-.8 1.2-.2.4-.3 1-.4 2.1C2.7 9.8 2.7 10.2 2.7 12s0 2.2.1 3.4c.1 1.1.2 1.7.4 2.1.2.5.4.9.8 1.2.4.4.7.6 1.2.8.4.2 1 .3 2.1.4 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1.1-.1 1.7-.2 2.1-.4.5-.2.9-.4 1.2-.8.4-.4.6-.7.8-1.2.2-.4.3-1 .4-2.1.1-1.2.1-1.6.1-3.4s0-2.2-.1-3.4c-.1-1.1-.2-1.7-.4-2.1-.2-.5-.4-.9-.8-1.2-.4-.4-.7-.6-1.2-.8-.4-.2-1-.3-2.1-.4C15.5 4 15.1 4 12 4zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 1.8a3.1 3.1 0 1 0 0 6.2 3.1 3.1 0 0 0 0-6.2zm5.1-3.2a1.1 1.1 0 1 1 0 2.3 1.1 1.1 0 0 1 0-2.3z"/></svg>'
ICON_IN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3V9.5zm6.5 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4V9.5z"/></svg>'
WORDMARK = 'architecture<sub>4</sub>future'


def layout(meta, body, nav_key):
    title = meta.get("title", SITE)
    full_title = title if title.startswith(SITE) else f"{title} — {SITE}, architecte à Vienne"
    desc = meta.get("description", "")
    cur = lambda key: ' aria-current="page"' if key == nav_key else ""
    head_nav = "".join(f'<a href="{h}"{cur(k)}>{l}</a>' for k, h, l in NAV[1:])
    menu_nav = "".join(
        f'<a href="{h}"{cur(k)}><span class="mono">{i:02d}</span><span>{l}</span></a>' for i, (k, h, l) in enumerate(NAV, 1)
    )
    body_cls = " ".join(c for c in ("hero-dark" if meta.get("hero") == "dark" else "", "head-solid" if meta.get("head") == "solid" else "") if c)
    og_img = meta.get("og", "img/home-11.webp")
    trame = "<span></span>" * 12
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{og_img}">
<meta name="theme-color" content="#141c16">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300;1,6..72,400&display=swap">
<link rel="stylesheet" href="assets/style.css?v={VERSION}">
</head>
<body class="{body_cls}">
<div class="curtain" aria-hidden="true"><span class="wordmark">{WORDMARK}</span></div>
<div class="trame" aria-hidden="true">{trame}</div>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="site-header">
  <div class="bar">
    <a class="brand" href="index.html" aria-label="{SITE}, accueil">
      <span class="wordmark">{WORDMARK}</span>
      <span class="mono">agile · citoyenne · sobre · végétale</span>
    </a>
    <div class="head-meta">
      <span class="mono">Vienne — 45°31′N 4°52′E</span>
      <nav class="head-nav" aria-label="Navigation principale">{head_nav}</nav>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="lbl">Menu</span><span class="bars" aria-hidden="true"></span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu">
  <nav class="js-stagger" aria-label="Menu">{menu_nav}</nav>
  <aside>
    <figure>{img("home-11", "Terrasse plantée", "30vw")}</figure>
    <p class="mono">Agence</p>
    <p>grünboX-Vienne<br>75 rue Victor Faugier, 38200 Vienne</p>
    <p><a href="tel:+33986572544">09 86 57 25 44</a><br><a href="mailto:contact@architecturefuture.fr">contact@architecturefuture.fr</a></p>
  </aside>
</div>
<div class="cursor" aria-hidden="true"><span class="lbl"></span></div>
<div class="hover-img" aria-hidden="true"><img alt=""></div>
<main id="contenu">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div><p class="mono">Agence</p><p>grünboX-Vienne<br>75 rue Victor Faugier<br>38200 Vienne</p></div>
      <div><p class="mono">Contact</p><p><a href="tel:+33986572544">09 86 57 25 44</a><br><a href="mailto:contact@architecturefuture.fr">contact@architecturefuture.fr</a></p>
        <div class="social"><a href="https://www.instagram.com/archi4future/" aria-label="Instagram" rel="noopener" target="_blank">{ICON_IG}</a><a href="https://fr.linkedin.com/in/patrick-stefan-rheinert-3ba51641" aria-label="LinkedIn" rel="noopener" target="_blank">{ICON_IN}</a></div></div>
      <div><p class="mono">Explorer</p><ul><li><a href="competences.html">Compétences</a></li><li><a href="realisations.html">Réalisations</a></li><li><a href="vegetal.html">Le végétal</a></li><li><a href="agence.html">L’agence</a></li></ul></div>
      <div><p class="mono">Principes</p><ul><li>Agile</li><li>Citoyenne</li><li>Sobre</li><li>Végétale</li></ul></div>
    </div>
    <div class="foot-word" aria-hidden="true">{WORDMARK}</div>
    <div class="foot-bottom mono"><span>SAS d’architecture au capital de 4 444 € · SIRET 892 007 444</span><span>Inscrite à l’Ordre des architectes</span><a href="mentions-legales.html">Mentions légales</a></div>
  </div>
</footer>
<script src="assets/vendor/gsap.min.js" defer></script>
<script src="assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="assets/vendor/lenis.min.js" defer></script>
<script src="assets/site.js?v={VERSION}" defer></script>
</body>
</html>
"""


def parse_page(path):
    raw = path.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n---\n")
    meta = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        if k.strip():
            meta[k.strip()] = v.strip()
    return meta, body


def project_page(i, p):
    prev_p = PROJETS[i - 1]
    next_p = PROJETS[(i + 1) % len(PROJETS)]
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in p["fiche"])
    if not any(k == "Lieu" for k, _ in p["fiche"]):
        facts = f"<div><dt>Lieu</dt><dd>{E(p['lieu'])}</dd></div>" + facts
    facts += f"<div><dt>Catégorie</dt><dd>{E(p['categorie'])}</dd></div>"
    texte = "".join(f"<p>{E(t)}</p>" for t in p["texte"])
    shots = "".join(
        f'<button type="button" data-full="img/{n}.webp" aria-label="Agrandir la photo {k + 1}" data-cursor="Agrandir">{img(n, alt_for(p, k), "(max-width: 760px) 100vw, 70vw")}</button>'
        for k, n in enumerate(p["images"])
    )
    words = p["titre"].split(" ")
    if len(words) > 2:
        mid = (len(words) + 1) // 2
        title_lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        title_lines = [p["titre"]]
    title_html = "".join(f'<span class="line"><span>{E(t)}</span></span>' for t in title_lines)
    body = f"""
<section class="page-hero">
  <div class="bg" data-speed="5">{img(p['images'][0], alt_for(p), '100vw', eager=True)}</div>
  <div class="content">
    <p class="eyebrow light">Réalisation {i + 1:02d} / {len(PROJETS):02d} — {E(p['categorie'])}</p>
    <h1 class="display split">{title_html}</h1>
    <div class="foot">
      <span class="mono">{E(p['lieu'])}</span>
      <span class="mono">{E(p['annee'])}</span>
      <p class="lede">{E(p['sous_titre'])}.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap proj-intro">
    <aside class="proj-facts reveal"><p class="eyebrow">Fiche technique</p><dl>{facts}</dl></aside>
    <div class="proj-text reveal">{texte}</div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap strip-head"><p class="eyebrow" style="margin:0">Images du projet — {len(p['images']):02d}</p><span class="mono" style="color:var(--ink-3)">Glisser →</span></div>
  <div class="strip">{shots}</div>
  <div class="wrap"><a class="prev-link" href="projet-{prev_p['slug']}.html"><span class="mono">← Précédent</span><span class="h3">{E(prev_p['titre'])}</span></a></div>
</section>
<a class="next-proj" href="projet-{next_p['slug']}.html" data-cursor="Suivant">
  <div class="bg" data-speed="5">{img(next_p['images'][0], alt_for(next_p), '100vw')}</div>
  <div class="content"><span class="mono">Réalisation suivante — {E(next_p['lieu'])}</span><span class="display" style="display:block">{E(next_p['titre'])}</span></div>
</a>
"""
    meta = {
        "title": p["titre"],
        "description": f"{p['titre']}, {p['lieu']} — {p['sous_titre']}. {p['texte'][0][:120]}…",
        "og": f"img/{p['images'][0]}.webp",
        "hero": "dark",
    }
    return layout(meta, body, "realisations")


def main():
    n = 0
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_page(page)
        out = layout(meta, macros(body), meta.get("nav", page.stem))
        (OUT / page.name).write_text(out, encoding="utf-8")
        n += 1
    for i, p in enumerate(PROJETS):
        (OUT / f"projet-{p['slug']}.html").write_text(project_page(i, p), encoding="utf-8")
        n += 1
    print(f"{n} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
