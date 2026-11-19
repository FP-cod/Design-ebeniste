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
| **Obsidienne** | Salles de jeux dédiées | Série 1 : Banc Feuille (typologies : banc_feuille — le code local utilise banc_flore —, croix de Saint-André, chaise trône, tabouret) · Série 2 : Néogothique (Entrave) |
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

