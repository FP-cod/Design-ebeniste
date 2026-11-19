# Gamme Neogothique : Entrave cou-poignets (Fusion 360, API Python)

Il s'agit de mobilier d'ebenisterie massive au style medieval / neogothique : chene ou noyer, cuir noir,
ferrures apparentes en fer forge ou laiton, sections carrees ou octogonales, tenons-mortaises,
chevilles et clefs. Aucune vis n'est apparente. La gamme est le contrepoint assume d'Equinox et reprend
son decoupage en trois couches et ses conventions (`Param`, `Parametres`, champ `regles`).

**v0.2 « raffine »** : angles francs et sections carrees conserves, mais proportions au nombre d'or,
pieds-colonnes (plinthe, fut fusele a chanfreins arretes, astragale, chapiteau), chants moulures reels
(conge, bec-de-corbin, quart-de-rond, cavet), ceintures ajourees d'ogives / trilobes / quadrilobes,
ferrures forgees plus fines a terminaisons (fleur de lys, queue d'aronde, trilobe), rivets goutte de
suif, barre de calage habillee, sellerie fine (point sellier double, tranches lustrees, coussin
matelasse). Pas de courbes organiques type Equinox : uniquement droites et arcs de cercle.
Voir `docs/style.md` (tous les parametres de style) et `docs/ajustements_v2.md` (avant -> apres).

## Arborescence

```
neogothique/
  README.md
  neogothique/                     # paquet Python (logique pure + pont Fusion)
    parametres.py                  # COUCHE 1 : schema documente, validation, overrides, export User Parameters
    parametres_neogothique.exemple.json
    catalogues/                    # COUCHE 2
      bois.py                      # chene, chene fume, noyer, noyer noir (sources citees)
      garnissage.py                # cuir renforce double, harnais, PU, pleine fleur, doublure
      ferrures.py                  # metaux, finitions, composants ferres, pivots
      attaches.py                  # tenons (borgne, a coins, cheville a tire, a clef), tourillons, chevilles, rivets
    regles.py                      # moteur de regles materiaux -> geometrie (dont minimum_section_nette)
    profils.py                     # geometrie pure : moulures, traces (d, z), ogives, lobes, terminaisons
    fusion_outils.py               # Solide, BlocProfile (moulures), Revolution, construction Fusion (mm -> cm ICI)
    grammaires/entrave.py          # COUCHE 3 : Entrave cou-poignets, run(context)
  scripts_fusion/Entrave/          # lanceur Fusion (Entrave.py + Entrave.manifest)
  outils/                          # generer_apercu.py, generer_docs.py
  docs/                            # style.md, ajustements_v2.md, parametres.md, regles_materiaux.md,
                                   # points_a_trancher.md, apercus PNG (3D, profil, details), rapport
  tests/                           # pytest + faux adsk (tests/fake_adsk.py)
```

## Installation dans Fusion 360

1. Dossier des scripts Fusion :
   - Windows : `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\`
   - macOS : `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts/`
2. Copier le dossier `scripts_fusion/Entrave` dans ce dossier Scripts.
3. Rendre le paquet `neogothique` accessible au lanceur. Au choix :
   - copier le dossier `neogothique/neogothique` **dans** `Scripts/Entrave/` (le plus simple) ;
   - ou ecrire le chemin du depot dans `Scripts/Entrave/chemin_neogothique.txt` ;
   - ou definir la variable d'environnement `NEOGOTHIQUE_CHEMIN`.
4. Dans Fusion : **Utilitaires > Complements > Scripts et complements (Maj+S)**, onglet Scripts,
   choisir `Entrave` puis **Executer**. Il faut un document ouvert dans l'espace Design ; le script le
   passe en conception parametrique.

### Ce que fait le script

- Il cree ou met a jour tous les User Parameters `neo_*`, numeriques et commentes, plus les parametres
  derives a expression liee :
  `neo_course_courante = neo_cremaillere_cran_courant * neo_cremaillere_pas`,
  `neo_hauteur_platine = neo_cremaillere_hauteur_mini + neo_course_courante`, etc.
- Les pieces moulurees (platine, pieds-colonnes, semelles, ceintures, cellules du coussin) sont des
  **BlocProfile** : une esquisse du profil de moulure par plan vertical (faces, et aretes a 45 deg pour
  les chanfreins arretes / l'octogone), extrudee symetriquement ; le premier extrude cree le corps, les
  suivants l'**intersectent** ; alesages, lumieres, logements et ajours sont ensuite **enleves** (Cut).
  Les tetes de rivets goutte de suif, boutons de capiton et la bague sont des **revolutions**.
- Il cree un composant `Entrave_Neogothique` avec deux sous-composants, `Fixe` et `Mobile`. Les corps
  mobiles (platine, coulisseaux, cremailleres, manilles, pentures) sont construits au cran 0, puis
  deplaces par une **MoveFeature dont la translation Z est l'expression `neo_course_courante`**.
- Pour changer de cran : **Modifier > Modifier les parametres**, puis saisir `neo_cremaillere_cran_courant`
  = 0 a 6. Le modele suit. Fusion n'impose pas un entier : garder une valeur entiere comprise dans les
  bornes. Si la MoveFeature parametrique n'est pas disponible dans ta version de l'API, le script
  construit les corps au cran courant, sans lien, et l'indique dans le message final.
- Si on relance le script, le cran deja regle dans Fusion est conserve. En revanche, un nouveau
  composant est cree : supprimer l'ancien.
- La geometrie qui depend des **autres** parametres (cotes, sections) est calculee en Python. Apres un
  changement de cote ou de materiau, il faut relancer le script. Seule la hauteur est liee en direct.

## Utilisation hors Fusion

```bash
python -m venv .venv && .venv/bin/pip install pytest matplotlib numpy
.venv/bin/python -m pytest -q                 # tests (mock de l'API Fusion)
.venv/bin/python outils/generer_apercu.py      # docs/apercu_entrave*.png (3D, profil, details de style)
.venv/bin/python outils/generer_docs.py        # docs/parametres.md, style.md, ajustements_v2.md, regles, rapport
```

```python
from neogothique.parametres import Parametres
from neogothique import regles
from neogothique.grammaires import entrave

p = Parametres.pour_typologie("entrave", {"ferrures.terminaison_pentures": "trilobe",
                                         "sellerie.matelassage_platine": "capitonne"})
p, ajustements = regles.changer_materiau(p, "ferrures.metal", "laiton_mat")
print(regles.rapport(ajustements))
print(entrave.rapport_texte(entrave.calculer_entrave(p, cran=6)))
```

## Repere et unites

X = longueur de la platine (800 mm), Y = profondeur (400 mm), Z = vertical, origine au sol au centre.
Unites internes : mm, kg, deg, N, MPa. Fusion travaille en cm en interne : la conversion est faite
uniquement dans `fusion_outils.mm_vers_cm`. Les expressions des User Parameters portent leur unite
(`25 mm`).

## Etat

- Couches 1 a 3 ecrites et documentees (v0.2). 128 tests passent (`pytest`), mais sur un **mock** de
  l'API Fusion : **rien n'a encore ete execute dans Fusion 360** (points sensibles : sens de
  `setByAngle`, extrusions Intersect/Cut multi-profils, temps de construction ≈ 190 corps).
- Les decisions a prendre sont dans `docs/points_a_trancher.md`.
