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

## Charte et mise en scène (version immersive)

- Papier chaud `#f2eee4`, forêt `#141c16`, mousse `#4d6a3f`, feuille `#9db27f`, terre cuite `#a4532f` (encadrés « à compléter »).
- Newsreader (titres, citations), Archivo (texte), IBM Plex Mono (annotations techniques), Google Fonts.
- Trame d’architecte en fond, photos plein écran sous un voile uni, rideau entre les pages, curseur personnalisé.
- Accueil : diaporama plein écran, manifeste qui s’allume mot à mot, 4 principes en séquence épinglée, réalisations en défilement horizontal, chiffres de la grünboX, bande végétale, défilant des distinctions.
- Index des réalisations : liste avec image qui suit la souris ou vue galerie, filtres par type. Fiches : héros plein écran, bande photo à glisser, visionneuse, projet suivant en plein écran.
- Animations : GSAP 3.12.5 + ScrollTrigger et Lenis 1.1.13, copiés dans `docs/assets/vendor/` (aucun appel externe). Tout reste lisible sans JavaScript et avec « réduire les animations ».
- Aucun dégradé, aucun halo, aucun bouton en gélule.

## Provenance du contenu

Tout le texte et toutes les photos viennent du site actuel (lu le 23/11/2026). Voir `CONTENU-SOURCE.md` pour le détail et la liste des emplacements à compléter avec l’agence.
