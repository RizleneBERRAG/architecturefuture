"""Génère le site statique dans docs/ à partir de src/.

    python build.py

- src/pages/*.html : contenu de chaque page (sans en-tête ni pied de page).
  Les premières lignes « clé: valeur » jusqu'à une ligne « --- » donnent
  title, description, nav (rubrique active) et og (image de partage).
- src/projets.json : les réalisations (une fiche projet générée par entrée).
- docs/img/sizes.json : largeurs disponibles de chaque photo (800, 1400, native).

Macros utilisables dans les pages :
  [[img:nom|texte alternatif|sizes|classe|eager]]  image responsive
  [[mosaic:slug,slug,…]]                            mosaïque de projets (légendes en cartouche)
  [[index]]                                          filtres + mosaïque de toutes les réalisations
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
VERSION = "62"
# Compteur de visites sans cookie (GoatCounter) ; vide = pas de compteur
GOATCOUNTER = "a4f-apercu"

PROJETS = json.loads((SRC / "projets.json").read_text(encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PROJETS}
SIZES = json.loads((OUT / "img" / "sizes.json").read_text(encoding="utf-8"))

NAV_LEFT = [
    ("index", "index.html", "Accueil"),
    ("competences", "competences.html", "Compétences"),
    ("realisations", "realisations.html", "Réalisations"),
]
NAV_RIGHT = [
    ("vegetal", "vegetal.html", "Le végétal"),
    ("agence", "agence.html", "L’agence"),
    ("contact", "contact.html", "Contact"),
]
ORDER = ["Habitat", "Réhabilitation", "Bureaux", "Équipement", "Urbanisme", "Agriculture urbaine"]
E = html.escape

# Rangées de la mosaïque : (hauteur en rangs, largeurs sur 12 colonnes)
PATTERN = [(3, [4, 3, 5]), (4, [7, 5]), (3, [5, 3, 4]), (4, [5, 7])]


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


def spans(n):
    """Largeur et hauteur de chaque vignette pour que les rangées tombent juste."""
    out, k = [], 0
    while len(out) < n:
        h, ws = PATTERN[k % len(PATTERN)]
        left = n - len(out)
        if left < len(ws):
            ws = {1: [12], 2: [7, 5]}[left]
            h = 4
        out += [(w, h) for w in ws]
        k += 1
    return out


def tile(p, w, h, photo=None):
    pc = round(w / 12 * 100)
    return (
        f'<a class="tile" href="projet-{p["slug"]}.html" data-cat="{E(p["categorie"])}" style="--c:{w};--r:{h}">'
        f'<div class="ph">{img(photo or p["images"][0], alt_for(p), f"(max-width: 760px) 100vw, {pc}vw")}</div>'
        f'<div class="cap"><b>{E(p["titre"])}</b><span>{E(p["categorie"])} · {E(p["lieu"])}</span></div></a>'
    )


def mosaic(items):
    sz = spans(len(items))
    return '<div class="mosaic">' + "".join(tile(BY_SLUG[s], w, h, ph) for (s, ph), (w, h) in zip(items, sz)) + "</div>"


def index_block():
    cats = {}
    for p in PROJETS:
        cats[p["categorie"]] = cats.get(p["categorie"], 0) + 1
    btns = [f'<button type="button" data-filter="tout" aria-pressed="true">Tout<sup>{len(PROJETS)}</sup></button>']
    btns += [f'<button type="button" data-filter="{E(c)}" aria-pressed="false">{E(c)}<sup>{cats[c]}</sup></button>' for c in ORDER if c in cats]
    return (
        f'<div class="filters rv" role="group" aria-label="Filtrer les réalisations">{"".join(btns)}</div>'
        '<p class="filter-live sr-only" aria-live="polite"></p>'
        + mosaic([(p["slug"], None) for p in PROJETS])
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
        if kind == "mosaic":
            items = []
            for s in arg.split(","):
                slug, _, photo = s.strip().partition("=")
                items.append((slug, photo or None))
            return mosaic(items)
        if kind == "index":
            return index_block()
        if kind == "link":
            p = BY_SLUG[parts[0]]
            return f'<a href="projet-{p["slug"]}.html">{E(parts[1] if len(parts) > 1 else p["titre"])}</a>'
        raise ValueError(m.group(0))
    return re.sub(r"\[\[([a-z]+(?::[^\]]*)?)\]\]", rep, text)


ICON_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/></svg>'
LOGO = 'architecture<b>4</b>future'


def layout(meta, body, nav_key):
    title = meta.get("title", SITE)
    full_title = title if title.startswith(SITE) else f"{title} — {SITE}, architecte à Vienne"
    desc = meta.get("description", "")
    cur = lambda k: ' aria-current="page"' if k == nav_key else ""
    left = "".join(f'<a href="{h}"{cur(k)}>{l}</a>' for k, h, l in NAV_LEFT)
    right = "".join(f'<a href="{h}"{cur(k)}>{l}</a>' for k, h, l in NAV_RIGHT)
    ap = lambda t: t.replace("’", '<span class="ap">’</span>')
    left = "".join(f'<a href="{h}"{cur(k)}>{ap(l)}</a>' for k, h, l in NAV_LEFT)
    right = "".join(f'<a href="{h}"{cur(k)}>{ap(l)}</a>' for k, h, l in NAV_RIGHT)
    menu = "".join(f'<a href="{h}"{cur(k)}><span>{i:02d}</span><em>{ap(l)}</em></a>' for i, (k, h, l) in enumerate(NAV_LEFT + NAV_RIGHT, 1))
    og = meta.get("og", "img/gere-08.webp")
    cls = ["home"] if nav_key == "index" else []
    if '<section class="hero' in body:
        cls.append("has-hero")
    bcls = f' class="{" ".join(cls)}"' if cls else ""
    # La marque grünboX garde sa casse, même dans les titres en petites capitales
    body = re.sub(r">([^<]*)<", lambda m: ">" + m.group(1).replace("grünboX", '<span class="nc">grünboX</span>') + "<", body)
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
<meta name="theme-color" content="#f4f0e8">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Red+Hat+Mono:wght@300;400&display=swap">
<link rel="stylesheet" href="assets/style.css?v={VERSION}">
</head>
<body{bcls}>
<a class="skiplink" href="#contenu">Aller au contenu</a>
<div class="veil" aria-hidden="true"><span class="veil-logo">{LOGO}</span></div>
<div class="cursor" aria-hidden="true"><span></span></div>
<header class="top">
  <nav class="nav-l" aria-label="Navigation principale">{left}</nav>
  <a class="logo" href="index.html" aria-label="{SITE}, accueil">{LOGO}</a>
  <nav class="nav-r" aria-label="Navigation secondaire">{right}<a class="ig" href="https://www.instagram.com/archi4future/" rel="noopener" target="_blank" aria-label="Instagram">{ICON_IG}</a></nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span><i></i></button>
</header>
<div class="menu" id="menu"><nav aria-label="Menu">{menu}</nav><p>grünboX-Vienne · 75 rue Victor Faugier, Vienne<br><a href="tel:+33986572544">09 86 57 25 44</a></p></div>
<main id="contenu">
{body}
</main>
<footer class="foot">
  <div class="foot-in">
    <p class="eyebrow rv">Contact</p>
    <p class="display rv" data-type>Un projet&#8239;? Parlons-en.</p>
    <a class="foot-mail rv" href="mailto:contact@architecturefuture.fr" data-cursor="Écrire">contact@architecturefuture.fr</a>
    <p class="foot-line rv"><a href="tel:+33986572544">09 86 57 25 44</a><span>grünboX-Vienne, 75 rue Victor Faugier, 38200 Vienne</span><span>Vienne, <b data-clock>—</b></span></p>
  </div>
  <div class="foot-bottom">
    <span>architecture4future · SAS d’architecture au capital de 4 444 € · SIRET 892 007 444</span>
    <span><a href="https://www.instagram.com/archi4future/" rel="noopener" target="_blank">Instagram</a><a href="https://fr.linkedin.com/in/patrick-stefan-rheinert-3ba51641" rel="noopener" target="_blank">LinkedIn</a><a href="mentions-legales.html">Mentions légales</a><button class="to-top" type="button" aria-label="Revenir en haut de la page">Haut ↑</button></span>
  </div>
</footer>
<script src="assets/vendor/gsap.min.js" defer></script>
<script src="assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="assets/vendor/lenis.min.js" defer></script>
<script src="assets/site.js?v={VERSION}" defer></script>
{f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>' if GOATCOUNTER else ""}
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


def longest_word(text):
    plain = re.sub(r"<[^>]+>", " ", html.unescape(text))
    return max((len(w) for w in re.split(r"[\s\-]+", plain) if w), default=8)


def hero(image, alt, left, right, caption, short=True):
    """Ouverture d’une page : grande photo, titre coupé par un trait vertical."""
    L = max(8, longest_word(left))
    return f"""<section class="hero{' short' if short else ''}" style="--L:{L}">
  <div class="slides"><figure class="slide is-on" data-cap="{E(caption)}">{img(image, alt, '100vw', eager=True)}</figure></div>
  <div class="hero-title"><h1><span class="h-l" data-chars>{left}</span><span class="h-bar" aria-hidden="true"></span><span class="h-r">{right}</span></h1></div>
  <p class="hero-cap"><span data-cap-out>{E(caption)}</span></p>
  <a class="hero-down" href="#suite" aria-label="Descendre"><i></i></a>
</section>
<span id="suite"></span>"""


def project_page(i, p):
    prev_p, next_p = PROJETS[i - 1], PROJETS[(i + 1) % len(PROJETS)]
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in p["fiche"])
    if not any(k == "Lieu" for k, _ in p["fiche"]):
        facts = f"<div><dt>Lieu</dt><dd>{E(p['lieu'])}</dd></div>" + facts
    facts += f"<div><dt>Catégorie</dt><dd>{E(p['categorie'])}</dd></div>"
    texte = "".join(f"<p>{E(t)}</p>" for t in p["texte"])
    n = len(p["images"])
    gal = []
    widths = {1: [12], 2: [7, 5], 3: [12, 6, 6], 4: [12, 7, 5, 12], 5: [12, 7, 5, 5, 7]}
    ws = widths.get(n) or ([12] + [7, 5, 5, 7] * 3)[:n]
    for k, nm in enumerate(p["images"]):
        w = ws[k] if k < len(ws) else 6
        gal.append(
            f'<button class="shot" type="button" data-full="img/{nm}.webp" style="--c:{w}" aria-label="Agrandir la photo {k + 1} sur {n}">'
            f'{img(nm, alt_for(p, k), f"(max-width: 760px) 100vw, {round(w / 12 * 100)}vw")}<span class="n">{k + 1:02d} / {n:02d}</span></button>'
        )
    left = E(p["titre"])
    right = f"{E(p['categorie'])}<br>{E(p['lieu'])}"
    body = f"""
{hero(p['images'][0], alt_for(p), left, right, f"{p['sous_titre']} — {p['annee']}")}
<section class="sec intro">
  <p class="eyebrow rv">Réalisation {i + 1:02d} / {len(PROJETS):02d}</p>
  <h2 class="display rv" data-type>— {E(p['sous_titre'])}.</h2>
  <div class="cols">
    <dl class="sheet rv">{facts}</dl>
    <div class="prose rv">{texte}</div>
  </div>
</section>
<section class="sec gallery-sec">
  <div class="gallery">{''.join(gal)}</div>
</section>
<nav class="pn" aria-label="Autres réalisations">
  <a class="pn-a" href="projet-{prev_p['slug']}.html">{img(prev_p['images'][0], alt_for(prev_p), '(max-width: 760px) 100vw, 50vw')}<span class="pn-t"><span>← Réalisation précédente</span><b>{E(prev_p['titre'])}</b></span></a>
  <a class="pn-a" href="projet-{next_p['slug']}.html">{img(next_p['images'][0], alt_for(next_p), '(max-width: 760px) 100vw, 50vw')}<span class="pn-t"><span>Réalisation suivante →</span><b>{E(next_p['titre'])}</b></span></a>
</nav>
<p class="back rv"><a class="btn line" href="realisations.html">Toutes les réalisations</a></p>
"""
    meta = {
        "title": p["titre"],
        "description": f"{p['titre']}, {p['lieu']} — {p['sous_titre']}. {p['texte'][0][:120]}…",
        "og": f"img/{p['images'][0]}.webp",
    }
    return layout(meta, body, "realisations")


def hero_macro(text):
    """[[hero:image|alt|gauche|droite|légende]] → ouverture de page."""
    def rep(m):
        a = m.group(1).split("|")
        return hero(a[0], a[1], a[2], a[3], a[4])
    return re.sub(r"\[\[hero:([^\]]*)\]\]", rep, text)


def main():
    n = 0
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_page(page)
        (OUT / page.name).write_text(layout(meta, macros(hero_macro(body)), meta.get("nav", page.stem)), encoding="utf-8")
        n += 1
    for i, p in enumerate(PROJETS):
        (OUT / f"projet-{p['slug']}.html").write_text(project_page(i, p), encoding="utf-8")
        n += 1
    print(f"{n} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
