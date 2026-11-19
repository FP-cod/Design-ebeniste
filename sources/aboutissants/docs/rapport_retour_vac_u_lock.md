# Rapport court — retour Fabien sur le Vac-U-Lock

Les dépôts Equinox, Néogothique et Incognito n'ont **pas** été
modifiés. Tests hors Fusion : voir le résultat en fin de document.

## Changements

### 1. Deux diamètres de tête, plus des cales

Les diamètres **31,75 mm** (brevet, [vac-u-lock.com/vac-u-lock-patent.html](https://vac-u-lock.com/vac-u-lock-patent.html)) et **27,94 mm** (boutique officielle) sont des **variantes paramétrées** (`variante_tete` = `brevet` | `boutique`). On ne tranche plus. Le diamètre actif `plug_diametre_tete_max` suit la variante (défaut : brevet).

Un **jeu de cales d'ajustement** est documenté et géométrisé :

- épaisseurs radiales combinables : **0,25 / 0,5 / 1,0 / 2,0 mm** ;
- jeu typique à rattraper : (31,75 − 27,94) / 2 = **1,905 mm** ;
- matériau : **inox 316L** (défaut), **PP** ou **PE-HD** (polymères non poreux déjà au catalogue) ;
- les cales compensent le jeu d'un ergot plus petit dans une cavité plus grande ; elles ne font pas entrer un ergot 31,75 mm dans une cavité 27,94 mm (dans ce cas : variante boutique).

La forme étoilée, l'angle de cône et le diamètre intermédiaire restent **TODO**, non inventés.

### 2. Ergot fileté côté machine

Le marché visse le Vac-U-Lock plutôt qu'il ne le clipse. Catalogue `FILETAGES_COTE_MACHINE` (source [vaculocks.com](https://vaculocks.com), adaptateurs alu ou inox), avec pas / Ø / As de norme (ISO 261, ASME B1.1, ISO 228-1 pour G1/8) :

M6x1, M8x1, **M8x1.25** (défaut, cohérent Equinox et `interface_oeillet_m8`), M10x1, M10x1.5, M12x1.75, M16x2, 3/8-16 UNC, 3/4-10 UNC, 5/16-18 UNC, 1/4-20 UNC, G1/8 (filetage gaz, pas une section de traction — As = None).

L'ergot porte une tige filetée ; la tige Ø16 de la machine est taraudée en M8x1.25 par défaut (plus de raccord Ø 33 mm vers le NPT). Le montage arrière `filete_machine` remplace `npt_1_femelle` comme défaut ; le NPT reste une option (`filete_et_npt`, `npt_1_*`).

### 3. Poussée machine validée

La poussée nominale est **validée à 400 N** (décision Fabien). Dynamique : 400 × k_dyn 2 = **800 N**. Effort de calcul d'ancrage : 800 × CS 3 = **2400 N**. Toutes les mentions « en attente de validation » ont été retirées (paramètres, catalogues, machine, cadres, rapports). Ce n'est toujours pas une CMU certifiée : un essai de qualification reste obligatoire.

### 4. NPT 1" sur Equinox et Néogothique

**Aucune modification** de ces deux gammes. Le NPT 1" n'existe aujourd'hui que sur Incognito (housses / actionneur). L'ajouter rétroactivement pour une compatibilité Sybian partout est une **décision à prendre**, pas un changement déjà fait.

## Fichiers

- `common/params_globaux.py` — variantes, cales, filetage, poussée validée, synchro du Ø actif
- `catalogues/vac_u_lock.py` — `FILETAGES_COTE_MACHINE`, `COMPATIBILITE_CALES`
- `interfaces/port_vac_u_lock.py` — tige filetée, cales, NPT optionnel
- `mouvement/sex_machine_mecanique.py` — raccord taraudé M8 en bout de tige
- `cadres/cadre_modulaire.py` — libellés de charge
- `tests/test_port_vac_u_lock.py`, `tests/test_cadre_modulaire.py`
- `docs/rapport_vac_u_lock_collecteur_cadres.md`, `docs/rapport_couche1_mouvement.md` — mentions de charge et de variantes
- le présent `docs/rapport_retour_vac_u_lock.md`

## Tests

```bash
cd /workspace/aboutissants && /workspace/.venv/bin/python -m pytest
```

Résultat : **58 passed**.
