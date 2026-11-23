"""Génère le site statique dans docs/ à partir de src/.

    python build.py

- src/pages/*.html : contenu de chaque page (sans en-tête ni pied de page).
  Les premières lignes « clé: valeur » jusqu'à une ligne « --- » donnent
  title, description et nav (rubrique active).
- src/projets.json : les réalisations (une fiche projet générée par entrée).

Macros utilisables dans les pages :
  [[img:nom|texte alternatif|sizes|classe]]   image responsive (docs/img/nom.webp + nom-s.webp)
  [[card:slug|classe]]                        carte d’une réalisation
  [[gallery]]                                 filtres + grille de toutes les réalisations
  [[link:slug]]                               lien texte vers une fiche projet
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
]

E = html.escape


def img(name, alt="", sizes="100vw", cls="", eager=False):
    small = OUT / "img" / f"{name}-s.webp"
    srcset = f' srcset="img/{name}-s.webp 800w, img/{name}.webp 1800w" sizes="{sizes}"' if small.exists() else ""
    c = f' class="{cls}"' if cls else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="img/{name}.webp"{srcset} alt="{E(alt)}"{c} {load}>'


def alt_for(p, i=0):
    return f"{p['titre']} — {p['sous_titre'].lower()}" if i == 0 else f"{p['titre']}, vue {i + 1}"


def card(slug, cls="", image=None, sizes="(max-width: 880px) 100vw, 50vw"):
    p = BY_SLUG[slug]
    im = image or p["images"][0]
    return (
        f'<a class="card reveal {cls}" href="projet-{slug}.html" data-cat="{E(p["categorie"])}">'
        f'<div class="ph">{img(im, alt_for(p), sizes)}</div>'
        f'<div class="card-meta"><div class="card-tag">{E(p["categorie"])} · {E(p["annee"])}</div>'
        f'<div class="card-title">{E(p["titre"])}</div>'
        f'<div class="card-sub">{E(p["lieu"])}</div></div></a>'
    )


def gallery():
    cats = {}
    for p in PROJETS:
        cats[p["categorie"]] = cats.get(p["categorie"], 0) + 1
    order = ["Habitat", "Réhabilitation", "Bureaux", "Équipement", "Urbanisme", "Agriculture urbaine"]
    btns = [f'<button type="button" data-filter="tout" aria-pressed="true">Tout<span class="count">{len(PROJETS)}</span></button>']
    for c in order:
        if c in cats:
            btns.append(f'<button type="button" data-filter="{E(c)}" aria-pressed="false">{E(c)}<span class="count">{cats[c]}</span></button>')
    cards = []
    for i, p in enumerate(PROJETS):
        wide = "is-wide" if i in (0, 9) else ""
        sizes = "(max-width: 560px) 100vw, (max-width: 880px) 100vw, 66vw" if wide else "(max-width: 560px) 100vw, (max-width: 880px) 50vw, 33vw"
        cards.append(card(p["slug"], wide, sizes=sizes))
    return (
        f'<div class="filters" role="group" aria-label="Filtrer les réalisations">{"".join(btns)}</div>'
        f'<div class="gallery">{"".join(cards)}</div>'
    )


def macros(text):
    def rep(m):
        kind, _, arg = m.group(1).partition(":")
        parts = arg.split("|")
        if kind == "img":
            name, alt = parts[0], parts[1] if len(parts) > 1 else ""
            sizes = parts[2] if len(parts) > 2 and parts[2] else "100vw"
            cls = parts[3] if len(parts) > 3 else ""
            return img(name, alt, sizes, cls, eager="eager" in parts[4:] if len(parts) > 4 else False)
        if kind == "card":
            return card(parts[0], parts[1] if len(parts) > 1 else "", parts[2] if len(parts) > 2 and parts[2] else None)
        if kind == "gallery":
            return gallery()
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
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == nav_key else ""}>{label}</a>' for key, href, label in NAV
    )
    nav += f'<a class="nav-cta" href="contact.html"{" aria-current=\"page\"" if nav_key == "contact" else ""}>Contact</a>'
    og_img = meta.get("og", "img/home-11.webp")
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
<meta name="theme-color" content="#f3efe6">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300;1,6..72,400&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="{SITE}, accueil">
      <span class="wordmark">{WORDMARK}</span>
      <span class="brand-tag">agile · citoyenne · sobre · végétale</span>
    </a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav"><span class="lbl">Menu</span><span class="bars" aria-hidden="true"></span></button>
    <nav class="nav" id="nav" aria-label="Navigation principale">{nav}</nav>
  </div>
</header>
<main id="contenu">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-col">
        <p class="foot-title">Construire des lieux <em>vivants</em>,<br>qui évoluent avec ceux qui les habitent.</p>
        <a class="btn btn--light" href="contact.html">Parler de votre projet <span class="arrow">→</span></a>
      </div>
      <div class="foot-col">
        <p class="foot-h">Agence</p>
        <p>75 rue Victor Faugier<br>38200 Vienne</p>
        <p class="small" style="color:var(--on-dark-2);margin-top:10px">Tiers-lieu grünboX-Vienne</p>
      </div>
      <div class="foot-col">
        <p class="foot-h">Contact</p>
        <p><a href="tel:+33986572544">09 86 57 25 44</a><br><a href="mailto:contact@architecturefuture.fr">contact@architecturefuture.fr</a></p>
        <div class="social">
          <a href="https://www.instagram.com/archi4future/" aria-label="Instagram" rel="noopener" target="_blank">{ICON_IG}</a>
          <a href="https://fr.linkedin.com/in/patrick-stefan-rheinert-3ba51641" aria-label="LinkedIn" rel="noopener" target="_blank">{ICON_IN}</a>
        </div>
      </div>
      <div class="foot-col">
        <p class="foot-h">Plan du site</p>
        <ul>
          <li><a href="competences.html">Compétences</a></li>
          <li><a href="realisations.html">Réalisations</a></li>
          <li><a href="vegetal.html">Le végétal</a></li>
          <li><a href="agence.html">L’agence</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span class="wordmark">{WORDMARK}</span>
      <span>SAS d’architecture au capital de 4 444 € · SIRET 892 007 444 · Inscrite à l’Ordre des architectes</span>
      <a href="mentions-legales.html">Mentions légales</a>
    </div>
  </div>
</footer>
<script src="assets/site.js" defer></script>
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
        f'<button type="button" data-full="img/{n}.webp" aria-label="Agrandir la photo {k + 1}">{img(n, alt_for(p, k), "(max-width: 880px) 100vw, 60vw")}</button>'
        for k, n in enumerate(p["images"][1:], start=1)
    )
    body = f"""
<section class="proj-head">
  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d’Ariane"><a href="realisations.html">Réalisations</a><span>/</span><span>{E(p['categorie'])}</span></nav>
    <div class="grid">
      <h1 class="display">{E(p['titre'])}</h1>
      <p class="lede">{E(p['sous_titre'])}. <span class="small">{E(p['lieu'])} · {E(p['annee'])}</span></p>
    </div>
  </div>
</section>
<figure class="page-banner">{img(p['images'][0], alt_for(p), '100vw', eager=True)}</figure>
<div class="wrap">
  <div class="proj-body">
    <aside class="proj-facts"><p class="eyebrow">Fiche</p><dl>{facts}</dl></aside>
    <div class="proj-text">{texte}</div>
  </div>
  {'<div class="proj-gallery">' + shots + '</div>' if shots else ''}
  <nav class="proj-nav" aria-label="Autres réalisations">
    <a href="projet-{prev_p['slug']}.html"><span class="num">← Réalisation précédente</span><span class="card-title">{E(prev_p['titre'])}</span></a>
    <a href="projet-{next_p['slug']}.html"><span class="num">Réalisation suivante →</span><span class="card-title">{E(next_p['titre'])}</span></a>
  </nav>
</div>
<section class="section--tight"></section>
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
        out = layout(meta, macros(body), meta.get("nav", page.stem))
        (OUT / page.name).write_text(out, encoding="utf-8")
        n += 1
    for i, p in enumerate(PROJETS):
        (OUT / f"projet-{p['slug']}.html").write_text(project_page(i, p), encoding="utf-8")
        n += 1
    print(f"{n} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
