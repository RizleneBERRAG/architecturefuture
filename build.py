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
VERSION = "48"

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


def frame(slug, photo=None, label=None):
    """Vignette de pellicule pointant vers une fiche projet."""
    p = BY_SLUG[slug]
    return (
        f'<a class="frame" href="projet-{slug}.html"><div class="ph">{img(photo or p["images"][0], alt_for(p), "(max-width: 760px) 80vw, 40vw")}</div>'
        f'<div class="cap"><b>{E(label or p["titre"])}</b><span class="mono">{E(p["annee"])}</span></div></a>'
    )


def index_block():
    cats = {}
    for p in PROJETS:
        cats[p["categorie"]] = cats.get(p["categorie"], 0) + 1
    btns = [f'<button type="button" data-filter="tout" aria-pressed="true">Tout<sup>{len(PROJETS)}</sup></button>']
    btns += [f'<button type="button" data-filter="{E(c)}" aria-pressed="false">{E(c)}<sup>{cats[c]}</sup></button>' for c in ORDER if c in cats]
    tiles = []
    for i, p in enumerate(PROJETS, 1):
        tiles.append(
            f'<a class="tile rv" href="projet-{p["slug"]}.html" data-cat="{E(p["categorie"])}">'
            f'<div class="ph">{img(p["images"][0], alt_for(p), "(max-width: 760px) 100vw, (max-width: 960px) 50vw, 33vw")}'
            f'<span class="num mono">{i:02d}</span><span class="yr mono">{E(p["annee"])}</span></div>'
            f'<h3>{E(p["titre"])}</h3><p>{E(p["categorie"])} · {E(p["lieu"])}</p></a>'
        )
    return (
        f'<div class="filters" role="group" aria-label="Filtrer les réalisations">{"".join(btns)}</div>'
        '<p class="filter-live sr-only" aria-live="polite"></p>'
        f'<div class="frames">{"".join(tiles)}</div>'
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
        if kind == "frame":
            return frame(parts[0], parts[1] if len(parts) > 1 and parts[1] else None, parts[2] if len(parts) > 2 and parts[2] else None)
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
    links = NAV + [("contact", "contact.html", "Contact")]
    nav = "".join(f'<a href="{h}"{cur(k)}>{l}</a>' for k, h, l in links)
    menu = "".join(f'<a href="{h}"{cur(k)}><span class="mono">{i:02d}</span>{l}</a>' for i, (k, h, l) in enumerate([("index", "index.html", "Accueil")] + links, 1))
    og = meta.get("og", "img/gere-08.webp")
    home = ' class="home"' if nav_key == "index" else ""
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
<meta name="theme-color" content="#0f1510">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Work+Sans:wght@400;500;600&family=IBM+Plex+Mono&display=swap">
<link rel="stylesheet" href="assets/style.css?v={VERSION}">
</head>
<body{home}>
<a class="skiplink" href="#contenu">Aller au contenu</a>
<div class="cursor" aria-hidden="true"><span></span></div>
<div class="bars" aria-hidden="true"><i></i><i></i><div class="credit"><div><span class="a">{LOGO}</span></div></div></div>
<button class="intro-skip mono" type="button" hidden>Passer l’intro</button>
<header class="top">
  <a class="logo" href="index.html" aria-label="{SITE}, accueil">{LOGO}</a>
  <nav aria-label="Navigation principale">{nav}</nav>
  <button class="menu-btn mono" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
</header>
<div class="menu" id="menu">{menu}<p class="mono">grünboX-Vienne · 75 rue Victor Faugier · 09 86 57 25 44</p></div>
<main id="contenu">
{body}
</main>
<footer class="site-foot">
  <div class="sf-scene">
    <div class="sf-bg">{img("tiny-02", "Terrasse plantée et jardins verticaux", "100vw")}</div>
    <svg class="vine" viewBox="0 0 1200 300" preserveAspectRatio="none" aria-hidden="true"><path class="stem" pathLength="1" d="M-20,250 C140,250 200,140 340,150 C480,160 520,250 680,230 C840,210 880,90 1040,80 C1120,75 1180,95 1240,110"/><g class="leaf" style="--d:0.35s" transform="translate(120 236) rotate(-40)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:0.63s" transform="translate(248 178) rotate(35)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:0.91s" transform="translate(345 150) rotate(-30)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:1.19s" transform="translate(470 178) rotate(40)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:1.47s" transform="translate(605 236) rotate(-35)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:1.75s" transform="translate(760 216) rotate(30)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:2.03s" transform="translate(905 128) rotate(-45)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:2.31s" transform="translate(1040 82) rotate(25)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g><g class="leaf" style="--d:2.59s" transform="translate(1165 95) rotate(-30)"><path d="M0,0 C8,-14 26,-16 40,-4 C26,8 10,10 0,0Z"/><path class="rib" d="M2,0 L34,-4"/></g></svg>
    <div class="sf-in">
      <p class="mono sf-kick">Un bâtiment à transformer, un jardin à faire pousser ?</p>
      <a class="sf-mail" href="mailto:contact@architecturefuture.fr" data-cursor="Écrire">contact@architecturefuture.fr</a>
      <div class="sf-line">
        <a class="ul" href="tel:+33986572544">09 86 57 25 44</a>
        <span>grünboX-Vienne, 75 rue Victor Faugier</span>
        <span class="mono sf-clock">Vienne, <b data-clock>—</b></span>
      </div>
    </div>
  </div>
  <div class="sf-band" aria-hidden="true"><div class="sf-track">
    <span>agile</span><span>citoyenne</span><span>sobre</span><span>végétale</span><span>agile</span><span>citoyenne</span><span>sobre</span><span>végétale</span>
    <span>agile</span><span>citoyenne</span><span>sobre</span><span>végétale</span><span>agile</span><span>citoyenne</span><span>sobre</span><span>végétale</span>
  </div></div>
  <div class="sf-bottom mono">
    <span>architecture4future · SAS au capital de 4 444 € · SIRET 892 007 444 · Ordre des architectes</span>
    <span><a class="ul" href="https://www.instagram.com/archi4future/" rel="noopener" target="_blank">Instagram</a><a class="ul" href="https://fr.linkedin.com/in/patrick-stefan-rheinert-3ba51641" rel="noopener" target="_blank">LinkedIn</a><a class="ul" href="mentions-legales.html">Mentions légales</a><button class="to-top ul" type="button">Haut ↑</button></span>
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


def lines(text):
    """Coupe un titre en deux lignes équilibrées pour l’animation."""
    words = text.split(" ")
    if len(words) < 3:
        return f'<span class="l"><span>{E(text)}</span></span>'
    mid = (len(words) + 1) // 2
    return "".join(f'<span class="l"><span>{E(" ".join(w))}</span></span>' for w in (words[:mid], words[mid:]))


def project_page(i, p):
    prev_p, next_p = PROJETS[i - 1], PROJETS[(i + 1) % len(PROJETS)]
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in p["fiche"])
    if not any(k == "Lieu" for k, _ in p["fiche"]):
        facts = f"<div><dt>Lieu</dt><dd>{E(p['lieu'])}</dd></div>" + facts
    facts += f"<div><dt>Catégorie</dt><dd>{E(p['categorie'])}</dd></div>"
    texte = "".join(f"<p>{E(t)}</p>" for t in p["texte"])
    n = len(p["images"])
    shots = "".join(
        f'<button class="frame" type="button" data-full="img/{nm}.webp" aria-label="Agrandir la photo {k + 1}">'
        f'<div class="ph">{img(nm, alt_for(p, k), "(max-width: 760px) 80vw, 40vw")}</div>'
        f'<div class="cap"><b></b><span class="mono">{k + 1:02d} / {n:02d}</span></div></button>'
        for k, nm in enumerate(p["images"])
    )
    plural = "s" if n > 1 else ""
    body = f"""
<section class="shot short">
  <div class="bg">{img(p['images'][0], alt_for(p), '100vw', eager=True)}</div>
  <div class="title"><span class="kick mono">Réalisation {i + 1:02d} / {len(PROJETS):02d} — {E(p['categorie'])}</span><h1>{lines(p['titre'])}</h1></div>
  <p class="subtitle"><span>{E(p['sous_titre'])}. {E(p['lieu'])}, {E(p['annee'])}.</span></p>
  <span class="scroll mono">Défiler</span>
</section>
<section class="sec">
  <div class="w two">
    <div class="side rv"><p class="lab mono">Fiche technique</p><dl class="sheet">{facts}</dl></div>
    <div class="prose rv">{texte}</div>
  </div>
</section>
<section class="film">
  <div class="head rv"><div><p class="lab mono">Les images</p><h2>{n} image{plural}</h2></div><p>Cliquez sur une image pour l’agrandir.</p></div>
  <div class="reel-wrap"><div class="reel">{shots}</div></div>
</section>
<a class="prevlink" href="projet-{prev_p['slug']}.html"><span class="mono">← Réalisation précédente</span><b>{E(prev_p['titre'])}</b></a>
<a class="next" href="projet-{next_p['slug']}.html">
  <div class="bg">{img(next_p['images'][0], alt_for(next_p), '100vw')}</div>
  <div class="in"><span class="mono">Prochaine réalisation — {E(next_p['lieu'])}</span><b>{E(next_p['titre'])}</b></div>
</a>
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
