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

## Charte « cinéma » (version en cours, 23/11/2026)

- Nuit vert sombre `#0f1510`, crème `#f6f1e3`, ocre `#d99a3d` ; sauge, olive et mousse pour les fondus de couleur.
- Young Serif (titres), Work Sans (texte), IBM Plex Mono (annotations).
- Ouverture en bandes noires (une fois par visite), plans plein écran avec sous-titres, scènes épinglées, principes en fondus de couleur, filmographie sur pellicule, générique de fin, transitions de page en bandes noires, léger grain.
- Animations : GSAP 3.12.5 + ScrollTrigger et Lenis 1.1.13 dans `docs/assets/vendor/`. Tout reste lisible sans JavaScript et avec « réduire les animations ».
- Aucun dégradé, aucun halo, aucun bouton en gélule.
- Les pistes comparées (A Lumière, B Jardin, C Galerie, prototype cinéma) restent dans `docs/pistes/`.

## Provenance du contenu

Tout le texte et toutes les photos viennent du site actuel (lu le 23/11/2026). Voir `CONTENU-SOURCE.md` pour le détail et la liste des emplacements à compléter avec l’agence.
