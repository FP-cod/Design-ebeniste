# Preuves du circuit produit

Ce dossier rassemble les preuves écrites qui permettent d'attribuer un statut d'avancement aux typologies (et, plus tard, aux références commerciales) du catalogue [`catalogues/produits.json`](../catalogues/produits.json).

Aucune typologie n'a aujourd'hui de visa : toutes portent `"statut": null` et `"preuves": []`. Aucun fichier de preuve n'est déposé pour l'instant, hors le présent README.

## Circuit à 8 étapes

| Numéro | Étape | Statut conféré |
|---:|---|---|
| 1 | Benchmark | aucun (`null`) — la preuve s'enregistre sans changer le statut |
| 2 | Design validé | `design_valide` |
| 3 | Faisabilité OK | `faisabilite_ok` |
| 4 | Normes OK | `normes_ok` |
| 5 | Script OK | `script_ok` |
| 6 | Débit OK | `debit_ok` |
| 7 | Go marché | `go_marche` |
| 8 | Produit | `produit` |

L'identifiant technique d'étape (`etape` dans le JSON) est : `benchmark`, `design_valide`, `faisabilite_ok`, `normes_ok`, `script_ok`, `debit_ok`, `go_marche`, `produit`. Le référentiel officiel est le tableau `circuit_etapes` à la racine de `catalogues/produits.json`.

## Règles d'attribution

- **Aucun statut sans preuve.** Une entrée du catalogue ne prend un statut que si la preuve écrite correspondante existe et est pointée depuis son tableau `preuves`.
- **Étape 1 (Benchmark).** Elle produit une preuve, enregistrée dans `preuves`, mais **ne confère aucun statut**.
- **`design_valide` (étape 2)** exige un **visa écrit de Fabien**. Une cote, un identifiant ou un script déjà présents dans le code ne comptent pas comme visa.
- **`produit` (étape 8)** exige un **dossier technique GPSR complet**.
- **Calcul du statut d'une typologie** (et, plus tard, d'une référence commerciale) : plus haute étape **2 à 8** prouvée de façon **contiguë**. L'étape *n* n'est acquise que si les étapes 2 à *n* le sont aussi. L'étape 1 n'entre pas dans ce calcul. S'il n'y a aucune preuve d'étape 2 à 8, le statut reste `null`.
- **Niveau de stockage.** Le statut est porté par chaque typologie, et plus tard par chaque référence commerciale. **Une série n'a pas de statut stocké.**
- **Statut affiché d'une série** = étape de sa typologie la moins avancée. Si l'une des typologies a le statut `null`, le statut affiché de la série est `null`.

Ces règles sont aussi résumées par la clé `regle_statut` de `catalogues/produits.json` et dans le README racine.

## Format d'une entrée `preuves`

Dans `catalogues/produits.json`, chaque typologie a un tableau `preuves`. Une entrée a la forme suivante :

```json
{
  "numero_etape": 1,
  "etape": "benchmark",
  "preuve": "preuves/obsidienne/banc_equinox/1_benchmark_2026-11-23.md",
  "date": "2026-11-23",
  "valide_par": "Fabien Petrot"
}
```

- `numero_etape` : entier de 1 à 8.
- `etape` : identifiant de l'étape (voir le tableau ci-dessus).
- `preuve` : **lien relatif** depuis la racine du dépôt vers un fichier sous `preuves/`.
- `date` : jour de la preuve, format `AAAA-MM-JJ`.
- `valide_par` : auteur du visa ou de la validation écrite.

L'exemple de chemin ci-dessus est illustratif : ce fichier n'existe pas encore.

## Arborescence proposée

```
preuves/
  README.md
  <gamme>/
    <typologie>/
      <numero>_<etape>_<date>.md
```

- `<gamme>` et `<typologie>` reprennent les identifiants du catalogue (`obsidienne`, `banc_equinox`, `entrave`, etc.).
- `<numero>` est le numéro d'étape, sans zéro forcé ou avec deux chiffres, mais de façon homogène : recommandation `1` … `8` telle quelle, ou `01` … `08` si l'on préfère le tri lexicographique ; une fois le premier fichier déposé, on conserve le même schéma.
- `<etape>` est l'identifiant technique (`benchmark`, `design_valide`, …).
- `<date>` est au format `AAAA-MM-JJ`.

Exemples (fichiers non créés à ce jour) :

```
preuves/obsidienne/banc_equinox/1_benchmark_2026-11-23.md
preuves/obsidienne/banc_equinox/2_design_valide_2026-12-01.md
preuves/obsidienne/entrave/2_design_valide_2026-12-01.md
```

Pour une référence commerciale, lorsqu'elle existera, on pourra ajouter un niveau `<reference>/` sous la typologie, sans changer le reste de la convention.
