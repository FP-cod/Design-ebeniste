# Regles materiaux -> geometrie (couche 2 + moteur `neogothique/regles.py`)

Chaque entree de catalogue porte un champ `regles` **declaratif**. Quand on
change une selection avec `regles.changer_materiau(params, chemin, cle)`, le
moteur applique les regles de la **nouvelle** entree et renvoie une liste
d'`Ajustement` (chemin, avant, apres, unite, explication, regle, source,
statut). Les parametres d'origine ne sont jamais modifies (copie).

```python
from neogothique.parametres import Parametres
from neogothique import regles
p = Parametres.pour_typologie("entrave")
p2, ajustements = regles.changer_materiau(p, "ferrures.metal", "laiton_mat")
print(regles.rapport(ajustements))
```

## Selections pilotees

| Parametre de selection | Categorie | Exemple d'effet |
|---|---|---|
| `bois.essence` | bois | noyer -> chene : masse x1,11, platine 50 -> 48 mm, mortaises oblongues 2 -> 3 mm, alerte tanins/fer |
| `garnissage.cuir_manilles` | garnissage | renforce -> harnais : epaisseur 6,5 -> 4 mm, largeurs x1,2, alerte doublure |
| `ferrures.metal` | metal | fer -> laiton : pene, rivets, barre, axes, arbre, fers plats, module (serie), finition |
| `ferrures.finition` | finition | galvanisation : jeu des axes >= 0,5 mm |
| `entrave.manilles.pivot_cou` / `pivot_poignets` | pivot | rotule : hauteur 40 mm, col >= 20 mm |
| `jonctions.type_*` | attache | tenon a clef : saillie >= 40 mm ; tourillons porteurs : alerte |
| `ferrures.terminaison_pentures` | terminaison | fleur de lys : branche >= 150 mm, fer plat >= 24 mm |
| `cremaillere.habillage` | habillage | capot ajoure / plaque decoupee : signalement fabrication |
| `cremaillere.decor_barre` | decor_barre | festonnee / ajouree : section nette mini, largeur de barre recalculee |
| `garnissage.cuir_manilles` (sellerie) | garnissage | harnais : pas de point 4 mm, sans rembourrage ; PU : piqure machine |

## Operations

| Operation | Effet | Reversible |
|---|---|---|
| `echelle` | cible x (P_ancien / P_nouveau) ^ exposant, arrondi superieur (pas ou serie), bornes | oui (aux arrondis pres, <= 1 pas) |
| `fixer` | cible = valeur | via la regle de l'autre entree |
| `fixer_propriete` | cible = propriete de l'entree (ex. finition par defaut) | oui |
| `minimum` / `maximum` | borne la cible | non (volontairement conservateur) |
| `depuis_defaut` | cible = defaut gamme x facteur + ajout | oui (idempotent) |
| `recalcul` | signale une grandeur recalculee par la grammaire (masse...) | - |
| `signaler` | alerte lisible (precaution, incompatibilite) | - |
| `minimum_section_nette` | cible >= (somme des `bases` + `constante`) / (1 - `taux`), arrondi ; re-evaluee en cascade quand une base change (ex. pene en laiton) | non (minimum) |

## Lois physiques utilisees par `echelle`

| Sollicitation | Loi | Exposant sur (P_ancien/P_nouveau) |
|---|---|---|
| Flexion d'une plaque/poutre rectangulaire (epaisseur) | sigma = 6M/(b h^2) | 1/2 sur f_m |
| Rigidite d'une section carree (pieds) | I ~ a^4 | 1/4 sur E |
| Cisaillement / traction (pene, rivet, barre) | tau = F/A, A ~ d^2 | 1/2 sur Re |
| Flexion / torsion d'axe rond | sigma = 32M/(pi d^3) | 1/3 sur Re |
| Rigidite des fers plats | k ~ E e^3 | 1/3 sur E |
| Denture (Lewis) | sigma = F/(b m Y) | 1 sur Re, puis module normalise |
| Dilatation du plateau massif | dL = L . coef . dH | -1 sur le coefficient de retrait |

## Ajustements geometriques notables a connaitre

1. **Fer -> laiton mat** (v0.2, ferrures affinees) : pene 12 -> 14 mm, rivets 5 -> 6 (tete 8 -> 10),
   axe de pivot 18 -> 20, gond 8 -> 9, arbre 16 -> 18, fers plats 4 -> 5, platine de pivot 5 -> 7,
   module 3 -> 4, barre de calage 24x8 -> 30x10. **Pignons, cremailleres dentees et arbres restent en
   acier.** Sans les regles, l'axe passe mais avec une marge < 1,5 : alerte `marges_ferrures` (teste).
2. **Noyer -> chene** : platine 48 mm suffit (f_m,k 30 contre 27 MPa) mais masse +11 % et retrait +33 % :
   mortaises oblongues des tenons arriere portees a 3 mm. Chene + fer : taches noires (tanins).
3. **Chene fume** : la teinte ne penetre que 1 a 3 mm, tous les usinages et chanfreins avant fumage.
4. **Cuir harnais sans ame** : la traction est portee par le cuir seul -> largeurs x1,2 (cou 75 mm),
   diametre exterieur des manilles reduit (epaisseur 4 mm).
5. **Section octogonale** (parametre geometrique, pas materiau) : a cote de fut egale (100), le coulisseau
   passe de 61 a 46 mm (pans coupes) ; 120 mm sur plats redonne 60 mm.
6. **Decor de barre** : `festonnee` (20 % de section perdue) porte la barre a 30 mm, `ajouree` (30 %) a
   35 x 10 mm ; si le pene grossit ensuite (laiton), la largeur est recalculee en cascade.
7. **Terminaisons** : chaque terminaison impose une longueur de branche mini (fleur de lys 150, trilobe
   140, queue d'aronde 130 mm) ; `droite` est signalee comme « style v0.1 ».
