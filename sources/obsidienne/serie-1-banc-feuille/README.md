# Equinox : gamme de mobilier en ébénisterie organique (Fusion 360, API Python)

Frêne clair, courbes de nervures et de branches, cuir cognac, inox discret, jonctions d'ébénisterie.
Le code est organisé en trois couches :

```
equinox/                      projet (racine à mettre dans sys.path)
├── equinox/                  paquet Python
│   ├── parametres.py         COUCHE 1 : vocabulaire, accès par chemin, validation, overrides, export User Parameters
│   ├── parametres_equinox.json        overrides utilisateur (commun / typologies)
│   ├── parametres_equinox.defauts.json  copie des valeurs par défaut (référence)
│   ├── catalogues/           COUCHE 2 : bois, garnissage, metaux, attaches (+ champ `regles`)
│   ├── regles.py             moteur des règles matériaux → géométrie (liste des ajustements)
│   ├── geometrie.py          primitives (Fuseau, TubeSpline, Boite, PlaqueContour, Disque, TubeCarre), courbes
│   ├── calculs.py            stabilité, glissement, flexion, flambement, hélice (ressort)
│   ├── fusion_outils.py      construction dans Fusion (seul module en cm), run générique, rapport
│   ├── apercu.py             aperçu matplotlib 3D (PNG)
│   └── grammaires/           COUCHE 3 : banc_flore (complet), croix_saint_andre, tabouret, chaise_trone,
│                             ancrages (transversal), commun (briques partagées)
├── scripts_fusion/           un dossier de script Fusion par typologie (.py + .manifest)
├── docs/                     parametres.md, regles_materiaux.md, typologies.md, aperçus PNG, rapports
├── outils/generer_docs.py    régénère la doc, les aperçus et les rapports
└── tests/                    pytest + mock de l'API Fusion
```

## Installation dans Fusion

1. Copiez tout le dossier `equinox/`, celui qui contient `equinox/`, `scripts_fusion/`, etc., par
   exemple dans `Documents/Equinox/`.
2. Dans Fusion : **Utilitaires → Compléments → Scripts et compléments** (Maj+S), onglet **Scripts**,
   bouton **+** (« Ajouter un script existant »). Choisissez `scripts_fusion/EquinoxBancFlore`.
   Faites de même pour `EquinoxCroixSaintAndre`, `EquinoxTabouret` et `EquinoxChaiseTrone`.
   Vous pouvez aussi copier ces dossiers dans le dossier Scripts de Fusion :
   - Windows : `%appdata%\Autodesk\Autodesk Fusion 360\API\Scripts\`
   - macOS : `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/`

   Dans ce cas, définissez la variable d'environnement `EQUINOX_RACINE` vers le dossier du projet, ou
   modifiez `EQUINOX_RACINE` en tête du script.
3. Ouvrez un **nouveau design** (espace Design, mode paramétrique), sélectionnez le script, puis
   **Exécuter**.
4. Le script :
   - crée ou met à jour les **User Parameters** `eq_*` (Modifier → Modifier les paramètres), avec le
     chemin, le statut et le rôle en commentaire ;
   - crée un composant `Equinox_banc_flore` avec un sous-composant par pièce (pieds, hélices, traverse,
     etc.) et une esquisse `Jonctions` : un point par jonction, avec des attributs JSON `equinox` ;
   - affiche un résumé (échecs et alertes) et écrit `~/equinox_rapport_<typologie>.txt`.

Le script de lancement purge `equinox.*` de `sys.modules` : une modification du code est prise en
compte au lancement suivant, sans redémarrer Fusion.

Les User Parameters sont **exportés** pour être lus et documentés. La géométrie est recalculée en Python
à chaque lancement. Pour changer une cote, modifiez `parametres_equinox.json` (ou les overrides) et
relancez le script. Modifier le User Parameter dans Fusion ne régénère pas la géométrie.

## Changer une valeur ou un matériau

```json
// equinox/parametres_equinox.json
{"commun": {"garnissage": {"materiau": "tissu_krypton", "couleur": "gris_anthracite"}},
 "typologies": {"banc_flore": {"dimensions": {"mode_longueur": "bassin_epaules", "longueur_bassin_epaules": 520}}}}
```

```python
from equinox.parametres import Parametres
from equinox import regles
p = Parametres.pour_typologie("banc_flore")
p2, ajustements = regles.changer_materiau(p, "bois", "erable_sycomore")
print(regles.rapport(ajustements))   # sections, rayon, tenons, inserts recalculés + explications
```

Au lancement d'une grammaire, les règles des matériaux actifs sont appliquées **sans modifier les
valeurs imposées** : un conflit apparaît comme `BLOQUE` dans le rapport. `changer_materiau` les modifie
(statut « valeur imposée modifiée, à confirmer »), sauf avec `forcer_imposes=False`.

Revêtements : `garnissage.materiau` choisit la famille (`cuir_classique_pleine_fleur` par défaut, `cuir_vegan`,
`tissu_krypton`, `cuir_synthetique_hq`, `tissu_technique_enduit`) et `garnissage.couleur` le coloris, qui doit
exister dans la famille (validation). Quand le rembourrage change, `dimensions.hauteur_structure` est recalculée
pour que l'assise reste à 700 mm, et l'ajustement est signalé.

## Hors Fusion (tests, aperçus)

```bash
python -m venv .venv && . .venv/bin/activate && pip install pytest matplotlib
python -m pytest -q                       # 52 tests, mock de l'API Fusion
python outils/generer_docs.py             # docs + PNG + rapports
python -m equinox.apercu banc_flore docs/apercu_banc.png
```

## Unités

Tout le code raisonne en mm, kg, degrés, N et MPa. L'API Fusion travaille en **cm** et en radians :
la conversion se fait uniquement dans `fusion_outils.py` (`cm()`, `math.radians`). Les User Parameters
sont écrits sous forme d'expressions avec unité (`"700 mm"`, `"7 deg"`).

## Limites connues

- Le code **n'a pas été exécuté dans Fusion**. Il a été testé avec un mock de l'API qui vérifie la
  séquence d'appels et les conversions d'unités, pas le résultat géométrique. Les profils de
  balayage d'hélice et les lofts de fuseaux sont les points à vérifier en premier, ainsi que les
  congés (non bloquants, une erreur est simplement journalisée).
- Les calculs donnent des ordres de grandeur et ne remplacent pas une note de calcul (EN 1728 /
  EN 12520 pour l'assise, Eurocode 5 pour le bois). Valeurs bois : Wood Database / Wood Handbook ;
  cintrage et abrasion : ordres de grandeur à valider par essai et par les fiches fournisseur.
