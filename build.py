"""Génère le site statique dans docs/ à partir de src/.

    python build.py

- src/pages/*.html : contenu de chaque page (sans en-tête ni pied de page).
  Les premières lignes « clé: valeur » jusqu'à une ligne « --- » donnent
  title, description, nav (rubrique active) et og (image de partage).
- src/projets.json : les réalisations (une fiche projet générée par entrée).
- docs/img/sizes.json : largeurs disponibles de chaque photo (800, 1400, native).

Macros utilisables dans les pages :
  [[img:nom|texte alternatif|sizes|classe|eager]]  image responsive
  [[card:slug|photo facultative]]                    carte de projet (mosaïque)
  [[index]]                                          filtres + grille de toutes les réalisations
  [[link:slug|texte]]                                lien texte vers une fiche projet
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SITE = "architecture4future"
VERSION = "11"

PROJETS = json.loads((SRC / "projets.json").read_text(encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PROJETS}
SIZES = json.loads((OUT / "img" / "sizes.json").read_text(encoding="utf-8"))

NAV = [
    ("competences", "competences.html", "Compétences"),
    ("realisations", "realisations.html", "Réalisations"),
    ("vegetal", "vegetal.html", "Le végétal"),
    ("agence", "agence.html", "L’agence"),
]
ORDER = ["Habitat", "Réhabilitation", "Bureaux", "Équipement", "Urbanisme", "Agriculture urbaine"]
E = html.escape


def srcset(name):
    ws = SIZES.get(name, [])
    native = max(ws) if ws else 0
    return ", ".join(
        f"img/{name}.webp {w}w" if w == native else f"img/{name}-{'s' if w == 800 else 'm'}.webp {w}w" for w in ws
    )


def img(name, alt="", sizes="100vw", cls="", eager=False):
    ss = srcset(name)
    srcs = f' srcset="{ss}" sizes="{sizes}"' if "," in ss else ""
    c = f' class="{cls}"' if cls else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="img/{name}.webp"{srcs} alt="{E(alt)}"{c} {load}>'


def alt_for(p, i=0):
    return f"{p['titre']} — {p['sous_titre'].lower()}" if i == 0 else f"{p['titre']}, vue {i + 1}"


def card(slug, photo=None, sizes="(max-width: 860px) 100vw, 50vw"):
    p = BY_SLUG[slug]
    return (
        f'<a class="card" href="projet-{slug}.html">{img(photo or p["images"][0], alt_for(p), sizes)}'
        f'<span class="lbl"><b>{E(p["titre"])}</b><span>{E(p["categorie"])} · {E(p["lieu"])}</span></span></a>'
    )


def index_block():
    cats = {}
    for p in PROJETS:
        cats[p["categorie"]] = cats.get(p["categorie"], 0) + 1
    btns = [f'<button type="button" data-filter="tout" aria-pressed="true">Tout <span class="count">{len(PROJETS)}</span></button>']
    btns += [f'<button type="button" data-filter="{E(c)}" aria-pressed="false">{E(c)} <span class="count">{cats[c]}</span></button>' for c in ORDER if c in cats]
    tiles = []
    for p in PROJETS:
        tiles.append(
            f'<a class="tile" href="projet-{p["slug"]}.html" data-cat="{E(p["categorie"])}">'
            f'<div class="ph">{img(p["images"][0], alt_for(p), "(max-width: 560px) 100vw, (max-width: 1060px) 50vw, 33vw")}<span class="tag">{E(p["categorie"])}</span></div>'
            f'<h3>{E(p["titre"])}</h3><p>{E(p["lieu"])} · {E(p["annee"])}</p></a>'
        )
    return (
        f'<div class="filters" role="group" aria-label="Filtrer les réalisations">{"".join(btns)}</div>'
        '<p class="filter-live sr-only" aria-live="polite"></p>'
        f'<div class="grid rv-group">{"".join(tiles)}</div>'
    )


def macros(text):
    def rep(m):
        kind, _, arg = m.group(1).partition(":")
        parts = arg.split("|")
        if kind == "img":
            name, alt = parts[0], parts[1] if len(parts) > 1 else ""
            sizes = parts[2] if len(parts) > 2 and parts[2] else "100vw"
            cls = parts[3] if len(parts) > 3 else ""
            return img(name, alt, sizes, cls, len(parts) > 4 and parts[4] == "eager")
        if kind == "card":
            return card(parts[0], parts[1] if len(parts) > 1 and parts[1] else None,
                        parts[2] if len(parts) > 2 else "(max-width: 860px) 50vw, 25vw")
        if kind == "index":
            return index_block()
        if kind == "link":
            p = BY_SLUG[parts[0]]
            return f'<a href="projet-{p["slug"]}.html">{E(parts[1] if len(parts) > 1 else p["titre"])}</a>'
        raise ValueError(m.group(0))
    return re.sub(r"\[\[([a-z]+(?::[^\]]*)?)\]\]", rep, text)


ICON_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.1-1.1.1-1.7.2-2.1.4-.5.2-.9.4-1.2.8-.4.4-.6.7-.8 1.2-.2.4-.3 1-.4 2.1C2.7 9.8 2.7 10.2 2.7 12s0 2.2.1 3.4c.1 1.1.2 1.7.4 2.1.2.5.4.9.8 1.2.4.4.7.6 1.2.8.4.2 1 .3 2.1.4 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1.1-.1 1.7-.2 2.1-.4.5-.2.9-.4 1.2-.8.4-.4.6-.7.8-1.2.2-.4.3-1 .4-2.1.1-1.2.1-1.6.1-3.4s0-2.2-.1-3.4c-.1-1.1-.2-1.7-.4-2.1-.2-.5-.4-.9-.8-1.2-.4-.4-.7-.6-1.2-.8-.4-.2-1-.3-2.1-.4C15.5 4 15.1 4 12 4zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 1.8a3.1 3.1 0 1 0 0 6.2 3.1 3.1 0 0 0 0-6.2zm5.1-3.2a1.1 1.1 0 1 1 0 2.3 1.1 1.1 0 0 1 0-2.3z"/></svg>'
ICON_IN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3V9.5zm6.5 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4V9.5z"/></svg>'
LOGO = 'architecture<b>4</b>future'


def layout(meta, body, nav_key):
    title = meta.get("title", SITE)
    full_title = title if title.startswith(SITE) else f"{title} — {SITE}, architecte à Vienne"
    desc = meta.get("description", "")
    cur = lambda k: ' aria-current="page"' if k == nav_key else ""
    nav = "".join(f'<a href="{h}"{cur(k)}>{l}</a>' for k, h, l in NAV)
    nav += f'<a class="btn ocre" href="contact.html"{cur("contact")}>Contact</a>'
    og = meta.get("og", "img/home-06.webp")
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{og}">
<meta name="theme-color" content="#3f5a34">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Work+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/style.css?v={VERSION}">
<style>.sr-only{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}</style>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="site-header">
  <div class="w">
    <a class="logo" href="index.html" aria-label="{SITE}, accueil">{LOGO}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav"><span class="lbl">Menu</span><span class="bars" aria-hidden="true"></span></button>
    <nav class="nav" id="nav" aria-label="Navigation principale">{nav}</nav>
  </div>
</header>
<main id="contenu">
{body}
</main>
<footer class="site-footer">
  <div class="w">
    <div class="foot">
      <div><h2>Parlons de votre projet</h2><a class="btn ocre" href="contact.html">Écrire à l’agence <span class="arr">→</span></a></div>
      <div><small>Agence</small><p>grünboX-Vienne<br>75 rue Victor Faugier<br>38200 Vienne</p></div>
      <div><small>Contact</small><p><a href="tel:+33986572544">09 86 57 25 44</a><br><a href="mailto:contact@architecturefuture.fr">contact@architecturefuture.fr</a></p>
        <div class="social"><a href="https://www.instagram.com/archi4future/" aria-label="Instagram" rel="noopener" target="_blank">{ICON_IG}</a><a href="https://fr.linkedin.com/in/patrick-stefan-rheinert-3ba51641" aria-label="LinkedIn" rel="noopener" target="_blank">{ICON_IN}</a></div></div>
      <div><small>Le site</small><ul><li><a href="competences.html">Compétences</a></li><li><a href="realisations.html">Réalisations</a></li><li><a href="vegetal.html">Le végétal</a></li><li><a href="agence.html">L’agence</a></li><li><a href="contact.html">Contact</a></li></ul></div>
    </div>
    <div class="foot-bottom"><span class="logo">{LOGO}</span><span>SAS d’architecture au capital de 4 444 € · SIRET 892 007 444 · Inscrite à l’Ordre des architectes</span><a href="mentions-legales.html">Mentions légales</a></div>
  </div>
</footer>
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
    prev_p, next_p = PROJETS[i - 1], PROJETS[(i + 1) % len(PROJETS)]
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in p["fiche"])
    if not any(k == "Lieu" for k, _ in p["fiche"]):
        facts = f"<div><dt>Lieu</dt><dd>{E(p['lieu'])}</dd></div>" + facts
    facts += f"<div><dt>Catégorie</dt><dd>{E(p['categorie'])}</dd></div>"
    texte = "".join(f"<p>{E(t)}</p>" for t in p["texte"])
    n_img = len(p["images"])
    left = (n_img - 3) % 3 if n_img > 3 else 0

    def span(k):
        if k == n_img - 1 and n_img > 3 and left:
            return ' style="grid-column: span %d"' % (3 if left == 1 else 2)
        return ""
    shots = "".join(
        f'<button type="button"{span(k)} data-full="img/{n}.webp" aria-label="Agrandir la photo {k + 1}">'
        f'{img(n, alt_for(p, k), "(max-width: 860px) 100vw, 66vw" if k == 0 else "(max-width: 860px) 50vw, 33vw")}</button>'
        for k, n in enumerate(p["images"])
    )
    pn = lambda q, cls, lab: (
        f'<a class="{cls}" href="projet-{q["slug"]}.html"><div class="ph">{img(q["images"][0], "", "120px")}</div>'
        f'<div class="t"><small>{lab}</small><b>{E(q["titre"])}</b></div></a>'
    )
    body = f"""
<section class="hero small">
  <div class="ph">{img(p['images'][0], alt_for(p), '100vw', eager=True)}</div>
  <div class="panel">
    <p class="crumbs"><a href="realisations.html">Réalisations</a> · {E(p['categorie'])}</p>
    <h1>{E(p['titre'])}</h1>
    <p class="lede" style="margin:0">{E(p['sous_titre'])}. <span class="small">{E(p['lieu'])} · {E(p['annee'])}</span></p>
  </div>
</section>
<section class="sec" style="padding-top:0">
  <div class="w proj">
    <aside class="facts rv"><dl>{facts}</dl></aside>
    <div class="txt rv">{texte}</div>
  </div>
</section>
<section class="sec cream2">
  <div class="w">
    <div class="sec-head"><h2>Images du projet</h2><p class="small" style="margin:0">{len(p['images'])} images · cliquer pour agrandir</p></div>
    <div class="gal rv-group">{shots}</div>
  </div>
</section>
<section class="sec">
  <div class="w pn">{pn(prev_p, "prev", "← Réalisation précédente")}{pn(next_p, "next", "Réalisation suivante →")}</div>
</section>
"""
    meta = {
        "title": p["titre"],
        "description": f"{p['titre']}, {p['lieu']} — {p['sous_titre']}. {p['texte'][0][:120]}…",
        "og": f"img/{p['images'][0]}.webp",
    }
    return layout(meta, body, "realisations")


def main():
    n = 0
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_page(page)
        (OUT / page.name).write_text(layout(meta, macros(body), meta.get("nav", page.stem)), encoding="utf-8")
        n += 1
    for i, p in enumerate(PROJETS):
        (OUT / f"projet-{p['slug']}.html").write_text(project_page(i, p), encoding="utf-8")
        n += 1
    print(f"{n} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
