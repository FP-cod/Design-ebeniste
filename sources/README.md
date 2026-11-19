# Correspondance des sources (anciens noms → nouvelle nomenclature)

Ce dossier rassemble les copies de travail locales des anciens projets, rangées selon la nomenclature officielle. Les sous-arborescences internes de chaque projet sont conservées telles quelles (tests, paquets Python, scripts Fusion, documentation, aperçus), afin que les tests restent exécutables depuis le dossier de la gamme.

Les catalogues JSON du référentiel (`catalogues/*.json`) ne sont pas modifiés ici.

| Ancien nom / dossier local | Nouvelle gamme | Chemin dans ce dépôt |
|---|---|---|
| Equinox (`/workspace/equinox`) | Obsidienne, Série 1 — Banc Feuille | `sources/obsidienne/serie-1-banc-feuille/` |
| Néogothique (`/workspace/neogothique`) | Obsidienne, Série 2 — Néogothique | `sources/obsidienne/serie-2-neogothique/` |
| Incognito (`/workspace/incognito`) | Opale | `sources/opale/` |
| Tantra (`/workspace/tantra`) | Émeraude (fixes / bien-être) ; les typologies camouflables de ce dossier sont orientées vers Opale (voir `briefs/brief_design_emeraude.md`) | `sources/emeraude/` |
| Rangement (`/workspace/rangement`) | Écrin | `sources/ecrin/` |
| Gamme cuir (`/workspace/gamme_cuir`) | Magnétite | `sources/magnetite/` |
| Aboutissants (`/workspace/aboutissants`) | Aboutissants | `sources/aboutissants/` |

Les briefs Design sont dans `briefs/` (y compris `briefs/recuperation/`, propositions des anciens agents Design, non validées par Fabien).

Le dossier `scripts/` conserve les README de ciblage des agents Script ; le code récupéré vit sous `sources/`.

Exclus de cette importation : caches Python (`__pycache__`, `.pytest_cache`, `*.pyc`), archives `.zip` / `.tar.gz`, le dossier immobilier `/workspace/veille`, les audits internes, et la branche locale non arbitrée `proposition/catalogue-materiaux`.
