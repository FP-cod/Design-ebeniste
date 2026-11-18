# Design Ébéniste

Système de design paramétrique pour gammes de mobilier ébénisterie (Fusion 360).

## Architecture en 3 couches

1. **Paramètres globaux** (`parametres/`) — Vocabulaire partagé de la gamme (dimensions, essences, finitions, angles…).
2. **Catalogues** (`catalogues/`) — Matériaux, fixations, règles de recalcul automatique.
3. **Scripts de grammaire** (`scripts/`) — Un dossier par gamme / typologie de meuble. Chaque script importe les paramètres et catalogues.

## Nomenclature des gammes

| Gamme | Style | Usage |
|---|---|---|
| **Obsidienne** | Salles de jeux dédiées (reprend Equinox + Néogothique) | Bancs, entraves, piloris, meubles assumés |
| **Opale** | Meubles dissimulés / transformables (reprend Incognito) | Pièces de vie, canapés, banquettes, poufs vibrants |
| **Onyx** | Meubles entièrement pliables | Se cachent sous le lit |
| **Magnétite** | Accessoires (reprend Cuir + Aboutissants) | Liens, colliers, floggers, ports Vac-U-Lock / NPT, machines, collecteurs |
| **Émeraude** | Gamme tantra (reprise de Tantra) | Fauteuils tantriques fixes |
| **Rangement** | Armoires, râteliers, coffres | Salles de jeux |

## Organisation des agents

### Design (esthétique, ergonomie, proportions)
- [Ébénisterie] Design Obsidienne
- [Ébénisterie] Design Opale
- [Ébénisterie] Design Onyx
- [Ébénisterie] Design Magnétite
- [Ébénisterie] Design Émeraude
- [Ébénisterie] Design Rangement

### Script Fusion (code API Python Fusion 360)
- [Ébénisterie] Script Obsidienne
- [Ébénisterie] Script Opale
- [Ébénisterie] Script Onyx
- [Ébénisterie] Script Magnétite
- [Ébénisterie] Script Émeraude
- [Ébénisterie] Script Rangement

### Pilotage
- [Ébénisterie] Orchestrateur Design Ébénisterie

### Étude de marché
- [Ébénisterie] Étude de Marché
- [Ébénisterie] Benchmark Concurrentiel

## Jonctions ébénisterie

Tourillons et mortaises (pas de vis apparentes). Tolérances de jonction à définir dans `parametres/`.

## Repo

- `parametres/` — paramètres globaux partagés
- `catalogues/` — bois, cuirs, métaux, fixations
- `scripts/{gamme}/` — scripts Fusion par gamme
