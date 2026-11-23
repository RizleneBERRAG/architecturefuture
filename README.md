# architecture4future — refonte du site

Maquette complète de la refonte de https://www.architecturefuture.fr/ (agence de Patrick Stefan Rheinert, Vienne).
Site **statique** : aucune base de données, publiable tel quel depuis `docs/` (GitHub Pages ou n’importe quel hébergeur).

## Voir le site en local

- XAMPP : démarrer Apache puis ouvrir http://localhost/architecturefuture/ (redirige vers `docs/`).
- Sans XAMPP : `python -m http.server 8080 --directory docs` puis http://localhost:8080/

## Modifier le contenu

| Quoi | Où |
|---|---|
| Textes des pages | `src/pages/*.html` (en-tête « title / description / nav », puis `---`, puis le contenu) |
| Réalisations (fiches, chiffres, photos) | `src/projets.json` — une fiche `docs/projet-<slug>.html` est générée par entrée |
| En-tête, pied de page, menu | `build.py` (fonction `layout`) |
| Charte (couleurs, typographies, mises en page) | `docs/assets/style.css` |
| Menu mobile, filtres, visionneuse, formulaire | `docs/assets/site.js` |
| Photos | `docs/img/<nom>.webp` (1 800 px) et `<nom>-s.webp` (800 px) |

Après chaque modification de `src/` : `python build.py` (régénère `docs/*.html`).

## Charte « Jardin » (version retenue le 23/11/2026)

- Couleurs du végétal : crème `#f6f1e3`, sauge `#dde3cf`, olive `#7d8a3c`, ocre `#d99a3d`, mousse `#3f5a34`, encre `#22301e`.
- Young Serif (titres) et Work Sans (texte), Google Fonts.
- Grande photo avec encart crème à liseré ocre, les 4 principes en blocs de couleur, étiquettes à liseré, cartes de projets avec légende qui se déplie au survol.
- Interactions : en-tête qui se resserre au défilement, apparitions douces, filtres animés des réalisations (mémorisés dans l’adresse), accordéon des compétences, compteurs de chiffres, frise qui se remplit, visionneuse au clavier et au doigt, vérification du formulaire.
- JavaScript sans librairie (`docs/assets/site.js`). Tout reste lisible sans JavaScript et avec « réduire les animations ».
- Aucun dégradé, aucun halo, aucun bouton en gélule.
- Les trois pistes comparées avant ce choix sont gardées dans `docs/pistes/`.

## Provenance du contenu

Tout le texte et toutes les photos viennent du site actuel (lu le 23/11/2026). Voir `CONTENU-SOURCE.md` pour le détail et la liste des emplacements à compléter avec l’agence.
