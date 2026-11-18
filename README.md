# Design Ébénisterie

Repo central pour le scriptage Fusion 360 de la gamme de meubles érotiques haut de gamme.

## Architecture en 3 couches

1. **parametres/** — vocabulaire partagé (dimensions, matériaux, fixations)
2. **catalogues/** — essences, cuirs, métaux, fixations (clés référencées par les scripts)
3. **scripts/** — grammaire par gamme, organisée en séries

## Gammes et séries

Chaque gamme = un langage visuel. Chaque série = un décor complet (meubles + accessoires assortis).

| Gamme | Style | Séries |
|-------|-------|--------|
| **Obsidienne** | Salles de jeux dédiées | Série 1 : Banc Feuille · Série 2 : Néogothique |
| **Opale** | Dissimulés / transformables (pièces de vie) | À définir |
| **Onyx** | Pliables, cachés sous le lit | À définir |
| **Magnétite** | Accessoires (liens, colliers, floggers) + Aboutissants | À définir |
| **Émeraude** | Tantra / bien-être | À définir |
| **Rangement** | Râteliers, armoires, coffres | À définir |

## Équipe d'agents

- **Orchestrateur Design Ébénisterie** — pilote, priorise, synchronise catalogues
- **Design** : Obsidienne, Opale, Onyx, Magnétite, Émeraude, Rangement
- **Script** : Obsidienne, Opale, Onyx, Magnétite, Émeraude, Rangement
- **Marché** : Étude de Marché, Benchmark Concurrentiel

## Règles

- Jamais de valeur en dur dans un script : tout passe par `parametres/` ou `catalogues/`
- Un changement de teinte ou d'essence se fait à un seul endroit
- Les jonctions : tourillons par défaut, mortaise-tenon pour les angles droits critiques
