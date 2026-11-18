# Design Ébéniste

Système de design paramétrique pour gammes de mobilier ébénisterie (Fusion 360).

## Architecture en 3 couches

1. **Paramètres globaux** (`parametres/`) — Vocabulaire partagé de la gamme (dimensions, essences, finitions, angles…).
2. **Catalogues** (`catalogues/`) — Matériaux, fixations, règles de recalcul automatique.
3. **Scripts de grammaire** (`scripts/`) — Un dossier par gamme / typologie de meuble. Chaque script importe les paramètres et catalogues.

### Gammes prévues
- **Equinox** : organique, aérien, courbes (banc Feuille, etc.)
- **Néogothique** : angles francs, bois sombre, cuir noir, ferrures
- **Incognito** : meubles de salon discrets avec fonction cachée
- **Tantra** : fauteuils tantriques fixes
- **Cuir** : accessoires (menottes, sangles, impact) assortis aux meubles
- **Rangement** : armoires, râteliers
- **Aboutissants** : ports Vac-U-Lock, NPT, machines, collecteurs

Jonctions ébénisterie : tourillons et mortaises (pas de vis apparentes).

Les scripts sont destinés à l’API Python de Fusion 360.
