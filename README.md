# Design Ébénisterie

Repo central pour le scriptage Fusion 360 de la gamme de meubles érotiques haut de gamme.

## Architecture en 3 couches

1. **parametres/** — vocabulaire partagé (dimensions, matériaux, fixations)
2. **catalogues/** — essences, cuirs, métaux, fixations (clés référencées par les scripts)
3. **scripts/** — grammaire par gamme, organisée en séries

## Gammes et séries

Chaque gamme = un langage visuel. Chaque série = un décor complet (meubles + accessoires assortis).
Les séries sont ajoutées au fur et à mesure des itérations de design.

| Gamme | Style | Séries |
|-------|-------|--------|
| **Obsidienne** | Salles de jeux dédiées | Série 1 : Banc Équinox (typologies : banc_equinox — anciens identifiants banc_feuille, banc_flore —, croix de Saint-André, chaise trône, tabouret) · Série 2 : Néogothique (Entrave) |
| **Opale** | Dissimulés / transformables (pièces de vie) | À définir |
| **Onyx** | Pliables, cachés sous le lit | À définir |
| **Magnétite** | Accessoires (liens, colliers, floggers, menottes, harnais) | À définir |
| **Émeraude** | Tantra / bien-être | À définir |
| **Écrin** | Armoires, râteliers, coffres et supports d'accompagnement | À définir |
| **Aboutissants** | Ports Vac-U-Lock, NPT 1", machines, collecteurs, points d'ancrage | À définir |

## Équipe d'agents

- **Orchestrateur Design Ébénisterie** — pilote, priorise, synchronise catalogues
- **Design** : Obsidienne, Opale, Onyx, Magnétite, Émeraude, Écrin
- **Script** : Obsidienne, Opale, Onyx, Magnétite, Émeraude, Écrin
- **Marché** : Étude de Marché, Benchmark Concurrentiel

## Règles

- Jamais de valeur en dur dans un script : tout passe par `parametres/` ou `catalogues/`
- Un changement de teinte ou d'essence se fait à un seul endroit
- Les jonctions : tourillons par défaut, mortaise-tenon pour les angles droits critiques

## Sources récupérées et briefs

Les copies de travail locales (paramètres, catalogues de gamme, grammaires, scripts Fusion, tests, documentation et aperçus) sont sous [`sources/`](sources/README.md), rangées selon la nouvelle nomenclature. Voir ce README pour la correspondance des anciens noms (Equinox, Néogothique, Incognito, Tantra, Rangement, Gamme cuir, Aboutissants).

Les briefs Design, y compris le brief Émeraude et la récupération des propositions des anciens agents Design (propositions non validées), sont sous [`briefs/`](briefs/).

## Catalogue produits et circuit de preuves

Le catalogue commercial est [`catalogues/produits.json`](catalogues/produits.json). Le statut d'avancement est porté par chaque typologie (et plus tard par chaque référence commerciale) ; une série n'a pas de statut stocké. Le statut affiché d'une série est l'étape de sa typologie la moins avancée, ou `null` si l'une d'elles est `null`.

Le circuit compte 8 étapes. L'étape 1 (Benchmark) produit une preuve mais ne confère aucun statut. Les statuts des étapes 2 à 8 sont `design_valide`, `faisabilite_ok`, `normes_ok`, `script_ok`, `debit_ok`, `go_marche` et `produit`. Aucun statut sans preuve écrite correspondante. Le statut d'une typologie est celui de la plus haute étape 2 à 8 prouvée de façon contiguë. `design_valide` exige un visa écrit de Fabien (une cote dans le code ne compte pas) ; `produit` exige un dossier technique GPSR complet. À ce jour, toutes les typologies ont `"statut": null` et `"preuves": []`.

Le référentiel `circuit_etapes` et la règle courte `regle_statut` figurent à la racine de `catalogues/produits.json`. Le détail des conventions, le format d'une preuve et l'arborescence des fichiers sont dans [`preuves/README.md`](preuves/README.md).
