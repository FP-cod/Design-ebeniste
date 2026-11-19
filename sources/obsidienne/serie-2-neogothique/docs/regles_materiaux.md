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

## Catalogue des regles (genere)

### Categorie `bois` (selection : `bois.essence`)

**`chene`** - Chene massif (chene sessile / pedoncule) : 5 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| bois_masse | recalcul | - | densite_kg_m3 | Masse des pieces bois recalculee par la grammaire (densite {ancien_val:g} -> {nouveau_val:g} kg/m3, x{ratio_brut:.3f}) ; la stabilite au renversement est reverifiee. |
| bois_epaisseur_platine | echelle | *.platine.epaisseur | resistance_flexion_calcul_mpa ^ 0.5 | Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}). |
| bois_cote_pieds | echelle | *.pied.cote | module_elasticite_mpa ^ 0.25 | Rigidite des pieds courts (flambement/flexion) : I ~ a^4 => cote proportionnelle a E^-1/4 (E {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}), arrondi 5 mm. |
| bois_mortaise_oblongue | echelle | tolerances.jeu_mortaise_oblongue | retrait_tangentiel_coef ^ -1 | Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel ({ancien_val:g} -> {nouveau_val:g} %/%, facteur {ratio:.3f}). |
| chene_tanins | signaler | - |  | Chene + fer : risque de taches noires (tanins). Finition cire/vernis sur ferrures et bois avant montage, ou ferrures laiton. |

**`chene_fume`** - Chene massif fume (fumage ammoniacal) : 6 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| bois_masse | recalcul | - | densite_kg_m3 | Masse des pieces bois recalculee par la grammaire (densite {ancien_val:g} -> {nouveau_val:g} kg/m3, x{ratio_brut:.3f}) ; la stabilite au renversement est reverifiee. |
| bois_epaisseur_platine | echelle | *.platine.epaisseur | resistance_flexion_calcul_mpa ^ 0.5 | Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}). |
| bois_cote_pieds | echelle | *.pied.cote | module_elasticite_mpa ^ 0.25 | Rigidite des pieds courts (flambement/flexion) : I ~ a^4 => cote proportionnelle a E^-1/4 (E {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}), arrondi 5 mm. |
| bois_mortaise_oblongue | echelle | tolerances.jeu_mortaise_oblongue | retrait_tangentiel_coef ^ -1 | Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel ({ancien_val:g} -> {nouveau_val:g} %/%, facteur {ratio:.3f}). |
| fume_finition | fixer | bois.finition | fumage_ammoniac | Chene fume : la finition devient 'fumage_ammoniac'. |
| fume_usinage | signaler | - |  | Le fumage ne penetre que 1-3 mm : tous les usinages (mortaises, chanfreins de {bois.chanfrein_aretes} mm) doivent etre faits avant fumage. |

**`noyer`** - Noyer europeen massif : 4 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| bois_masse | recalcul | - | densite_kg_m3 | Masse des pieces bois recalculee par la grammaire (densite {ancien_val:g} -> {nouveau_val:g} kg/m3, x{ratio_brut:.3f}) ; la stabilite au renversement est reverifiee. |
| bois_epaisseur_platine | echelle | *.platine.epaisseur | resistance_flexion_calcul_mpa ^ 0.5 | Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}). |
| bois_cote_pieds | echelle | *.pied.cote | module_elasticite_mpa ^ 0.25 | Rigidite des pieds courts (flambement/flexion) : I ~ a^4 => cote proportionnelle a E^-1/4 (E {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}), arrondi 5 mm. |
| bois_mortaise_oblongue | echelle | tolerances.jeu_mortaise_oblongue | retrait_tangentiel_coef ^ -1 | Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel ({ancien_val:g} -> {nouveau_val:g} %/%, facteur {ratio:.3f}). |

**`noyer_noir`** - Noyer noir d'Amerique massif : 4 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| bois_masse | recalcul | - | densite_kg_m3 | Masse des pieces bois recalculee par la grammaire (densite {ancien_val:g} -> {nouveau_val:g} kg/m3, x{ratio_brut:.3f}) ; la stabilite au renversement est reverifiee. |
| bois_epaisseur_platine | echelle | *.platine.epaisseur | resistance_flexion_calcul_mpa ^ 0.5 | Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}). |
| bois_cote_pieds | echelle | *.pied.cote | module_elasticite_mpa ^ 0.25 | Rigidite des pieds courts (flambement/flexion) : I ~ a^4 => cote proportionnelle a E^-1/4 (E {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}), arrondi 5 mm. |
| bois_mortaise_oblongue | echelle | tolerances.jeu_mortaise_oblongue | retrait_tangentiel_coef ^ -1 | Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel ({ancien_val:g} -> {nouveau_val:g} %/%, facteur {ratio:.3f}). |

### Categorie `garnissage` (selection : `garnissage.cuir_manilles`)

**`cuir_sellier_fin_noir`** - Cuir sellier fin noir (vachette pleine fleur + ame + rembourrage + doublure agneau) : 6 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| sellier_fin_epaisseur | fixer | garnissage.epaisseur_manille | 7.5 | Vachette 3 + ame ~0,5 + rembourrage 3 + doublure 1 = 7,5 mm : le diametre exterieur des manilles est recalcule. |
| sellier_fin_rembourrage | fixer | sellerie.rembourrage_manille | 3.0 | Rembourrage fin 3 mm (latex haute densite). |
| sellier_fin_largeurs | depuis_defaut | garnissage.largeur_manille_cou, garnissage.largeur_manille_poignet | defaut x 1 + 0 | Ame porteuse : largeurs de reference (cou 60, poignets 50 mm). |
| sellier_point | fixer | sellerie.point | sellier_double | Point sellier double a la main (indecousable : si un fil casse, l'autre tient). |
| sellier_pas | fixer | sellerie.pas_point | 3.2 | Pas 3,2 mm (8 points/pouce) : couture fine et reguliere. |
| sellier_fil | fixer | sellerie.fil_diametre | 0.55 | Fil de lin cire 0,55 mm. |

**`cuir_renforce_double_noir`** - Cuir renforce double pour manilles (harnais + doublure + ame) : 5 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| renforce_epaisseur | fixer | garnissage.epaisseur_manille | 6.5 | Complexe harnais 4 + doublure 1,5 + ame ~1 = 6,5 mm : le diametre exterieur des manilles est recalcule. |
| renforce_largeurs | depuis_defaut | garnissage.largeur_manille_cou, garnissage.largeur_manille_poignet | defaut x 1 + 0 | Ame porteuse : largeurs de reference de la gamme (cou 60, poignets 50 mm). |
| renforce_pas | fixer | sellerie.pas_point | 4.0 | Harnais 4 mm : pas 4 mm (6 points/pouce), fil 0,8 mm - plus robuste, moins fin. |
| renforce_fil | fixer | sellerie.fil_diametre | 0.8 | Fil polyester cire 0,8 mm. |
| renforce_rembourrage | fixer | sellerie.rembourrage_manille | 0.0 | Pas de rembourrage (la doublure 1,5 mm suffit). |

**`cuir_harnais_noir`** - Cuir de harnais tannage vegetal noir (simple epaisseur) : 5 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| harnais_epaisseur | fixer | garnissage.epaisseur_manille | 4.0 | Simple epaisseur 4 mm, sans doublure. |
| harnais_largeur | depuis_defaut | garnissage.largeur_manille_cou, garnissage.largeur_manille_poignet | defaut x 1.2 + 0 | Sans ame porteuse : largeur des manilles x1,2 (le cuir seul porte la traction et la pression de contact augmente sans doublure). |
| harnais_doublure | signaler | - |  | Pas de doublure : contact direct cuir tannage vegetal / peau ; arrondir et lisser les tranches (rayon >= {securite.arrondi_contact_peau} mm). |
| harnais_pas | fixer | sellerie.pas_point | 4.0 | Cuir de harnais epais : pas 4 mm (le pas 3,2 fendrait le cuir). |
| harnais_rembourrage | fixer | sellerie.rembourrage_manille | 0.0 | Simple epaisseur : pas de rembourrage. |

**`cuir_synthetique_pu_noir`** - Cuir synthetique PU haute densite noir (sur ame sangle) : 5 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| pu_epaisseur | fixer | garnissage.epaisseur_manille | 5.0 | Complexe PU 2 x 1,2 mm + mousse 2,5 mm = 5 mm. |
| pu_largeur | depuis_defaut | garnissage.largeur_manille_cou, garnissage.largeur_manille_poignet | defaut x 1 + 5 | PU plus souple : +5 mm de largeur pour garder la meme tenue sur l'ame. |
| pu_point | fixer | sellerie.point | piqure_machine | PU : piqure machine (le point sellier main n'apporte rien sur un synthetique). |
| pu_pas | fixer | sellerie.pas_point | 3.5 | PU : pas 3,5 mm (au-dessous, la ligne de piqure se dechire). |
| pu_hygiene | signaler | - |  | Option hygiene : supporte les desinfectants ; contraste visuel moindre avec le cuir veritable (pas de patine). |

**`cuir_pleine_fleur_noir`** - Cuir pleine fleur noir d'ameublement (coussinets, garnitures) : 2 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| pf_rembourrage | fixer | garnissage.epaisseur_rembourrage | 30.0 | Cuir pleine fleur : rembourrage de reference 30 mm. |
| pf_usage | signaler | - |  | Usage coussin uniquement : ne pas l'utiliser seul pour des manilles. |

**`doublure_agneau_noir`** - Doublure cuir d'agneau noir : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| doublure_seule | signaler | - |  | Une doublure n'est pas une manille : a associer a un cuir exterieur. |

### Categorie `metal` (selection : `ferrures.metal`)

**`fer_forge_mat`** - Fer forge mat (acier doux S235JR forge a chaud) : 11 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| metal_pene | echelle | loquet.pene_diametre | limite_elastique_mpa ^ 0.5 | Pene en cisaillement : aire ~ 1/Re (Re {ancien_val:g} -> {nouveau_val:g} MPa), diametre x{ratio:.3f}. |
| metal_rivet | echelle | ferrures.rivet_diametre | limite_elastique_mpa ^ 0.5 | Rivets en cisaillement : diametre x{ratio:.3f}. |
| metal_tete_rivet | echelle | ferrures.tete_rivet_diametre | limite_elastique_mpa ^ 0.5 | Tete goutte de suif : suit la tige (tete >= 1,5 x tige), x{ratio:.3f}. |
| metal_barre_cremaillere | echelle | cremaillere.barre_epaisseur | limite_elastique_mpa ^ 0.5 | Barre de calage (matage du cran par le pene) : epaisseur x{ratio:.3f}. |
| metal_largeur_barre | echelle | cremaillere.barre_largeur | limite_elastique_mpa ^ 0.5 | Barre de calage : la largeur suit le diametre du pene (joues >= 6 mm), x{ratio:.3f}. |
| metal_axes | echelle | ferrures.axe_pivot_diametre, ferrures.gond_diametre | limite_elastique_mpa ^ 0.333 | Axes en flexion : d^3 ~ 1/Re, diametre x{ratio:.3f}. |
| metal_arbre | echelle | synchro.arbre_diametre | limite_elastique_mpa ^ 0.333 | Arbre de synchronisation en torsion : d^3 ~ 1/tau, diametre x{ratio:.3f}. |
| metal_fer_plat | echelle | ferrures.fer_plat_epaisseur, ferrures.platine_pivot_epaisseur | module_elasticite_mpa ^ 0.333 | Fers plats (pentures, platines) : rigidite ~ E.e^3, epaisseur x{ratio:.3f} (E {ancien_val:g} -> {nouveau_val:g} MPa). |
| metal_module | echelle | cremaillere.module | limite_elastique_mpa ^ 1 | Denture (Lewis) : module ~ 1/Re, x{ratio:.3f} puis module normalise superieur. |
| metal_finition | fixer_propriete | ferrures.finition | finition_defaut | Finition par defaut du nouveau metal. |
| metal_masse | recalcul | - | densite_kg_m3 | Masse des ferrures recalculee (densite {ancien_val:g} -> {nouveau_val:g} kg/m3). |

**`laiton_mat`** - Laiton mat (CuZn37 / CuZn39Pb3, brosse ou patine) : 13 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| metal_pene | echelle | loquet.pene_diametre | limite_elastique_mpa ^ 0.5 | Pene en cisaillement : aire ~ 1/Re (Re {ancien_val:g} -> {nouveau_val:g} MPa), diametre x{ratio:.3f}. |
| metal_rivet | echelle | ferrures.rivet_diametre | limite_elastique_mpa ^ 0.5 | Rivets en cisaillement : diametre x{ratio:.3f}. |
| metal_tete_rivet | echelle | ferrures.tete_rivet_diametre | limite_elastique_mpa ^ 0.5 | Tete goutte de suif : suit la tige (tete >= 1,5 x tige), x{ratio:.3f}. |
| metal_barre_cremaillere | echelle | cremaillere.barre_epaisseur | limite_elastique_mpa ^ 0.5 | Barre de calage (matage du cran par le pene) : epaisseur x{ratio:.3f}. |
| metal_largeur_barre | echelle | cremaillere.barre_largeur | limite_elastique_mpa ^ 0.5 | Barre de calage : la largeur suit le diametre du pene (joues >= 6 mm), x{ratio:.3f}. |
| metal_axes | echelle | ferrures.axe_pivot_diametre, ferrures.gond_diametre | limite_elastique_mpa ^ 0.333 | Axes en flexion : d^3 ~ 1/Re, diametre x{ratio:.3f}. |
| metal_arbre | echelle | synchro.arbre_diametre | limite_elastique_mpa ^ 0.333 | Arbre de synchronisation en torsion : d^3 ~ 1/tau, diametre x{ratio:.3f}. |
| metal_fer_plat | echelle | ferrures.fer_plat_epaisseur, ferrures.platine_pivot_epaisseur | module_elasticite_mpa ^ 0.333 | Fers plats (pentures, platines) : rigidite ~ E.e^3, epaisseur x{ratio:.3f} (E {ancien_val:g} -> {nouveau_val:g} MPa). |
| metal_module | echelle | cremaillere.module | limite_elastique_mpa ^ 1 | Denture (Lewis) : module ~ 1/Re, x{ratio:.3f} puis module normalise superieur. |
| metal_finition | fixer_propriete | ferrures.finition | finition_defaut | Finition par defaut du nouveau metal. |
| metal_masse | recalcul | - | densite_kg_m3 | Masse des ferrures recalculee (densite {ancien_val:g} -> {nouveau_val:g} kg/m3). |
| laiton_engrenages | signaler | - |  | Laiton deconseille pour pignons, cremaillere dentee et arbres de synchronisation (usure, grippage laiton/laiton) : garder ces pieces en acier et reserver le laiton aux pieces vues (pentures, frettes, boitiers, pivots). |
| laiton_tanins | signaler | - |  | Le laiton ne tache pas le chene (pas de reaction tanin-fer). |

### Categorie `finition` (selection : `ferrures.finition`)

**`cire_noire`** - Fer forge cire noir (cire d'abeille + noir de fumee a chaud) : 0 regle(s)

**`huile_brunie`** - Bruni (huile de lin cuite a chaud, reflets bleu-brun) : 0 regle(s)

**`phosphatation_vernis_mat`** - Phosphatation + vernis mat (fer) : 0 regle(s)

**`galvanisation_peinture_mate`** - Galvanisation a chaud + peinture noire mate (fer) : 2 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| galva_jeu | minimum | tolerances.jeu_axes | 0.5 | Galvanisation (~80 um par face) : jeu des axes et alesages porte a >= 0,5 mm. |
| galva_aspect | signaler | - |  | La galvanisation efface une partie des traces de forge : marteler fort avant. |

**`laiton_brosse_vernis_mat`** - Laiton brosse + vernis mat : 0 regle(s)

**`laiton_patine_vieilli`** - Laiton vieilli (patine chimique brun-noir, reliefs eclaircis, cire) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| patine_contact | signaler | - |  | Patine chimique : eviter le contact prolonge avec la peau (manilles) ; vernir les zones de contact. |

### Categorie `pivot` (selection : `entrave.manilles.pivot_cou`, `entrave.manilles.pivot_poignets`)

**`axe_vertical_chape`** - Axe vertical a chape (rotation dans le plan de la platine) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| pivot_axe_hauteur | fixer | entrave.manilles.hauteur_pivot | 30.0 | Chape + axe vertical : hauteur de pivot 30 mm. |

**`rotule`** - Rotule (boule forgee dans coquille) : 3 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| pivot_rotule_hauteur | fixer | entrave.manilles.hauteur_pivot | 40.0 | Rotule : coquille plus haute, hauteur de pivot 40 mm. |
| pivot_rotule_axe | minimum | ferrures.axe_pivot_diametre | 20.0 | Col de rotule : diametre >= 20 mm (flexion au col). |
| pivot_rotule_jeu | signaler | - |  | Rotule : prevoir un frein (ecrou de serrage cache ou ressort) pour limiter le ballant ; verifier l'usure de la coquille. |

**`charniere_basculante`** - Charniere basculante (axe horizontal) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| pivot_charniere_hauteur | fixer | entrave.manilles.hauteur_pivot | 25.0 | Charniere : noeuds de gond, hauteur de pivot 25 mm. |

### Categorie `attache` (selection : `jonctions.type_coulisseau_platine`, `jonctions.type_fourreau_semelle`, `jonctions.type_traverse_semelle`, `jonctions.type_joues_fourreau`)

**`tenon_mortaise_borgne`** - Tenon-mortaise borgne colle : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| borgne_dilatation | signaler | - |  | Tenon borgne colle : ne pas l'utiliser en travers du fil d'un plateau large sans mortaise oblongue (jeu {tolerances.jeu_mortaise_oblongue} mm). |

**`tenon_traversant_cale`** - Tenon traversant a coins (wedged through tenon) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| cale_aspect | signaler | - |  | Bout de tenon visible sur le dessus : affleurer et chanfreiner {bois.chanfrein_aretes} mm. |

**`tenon_traversant_cheville`** - Tenon traversant cheville a tire (drawbore) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| drawbore_decalage | minimum | jonctions.decalage_drawbore | 1.0 | Chevillage a tire : decalage >= 1 mm (1,5 mm conseille en chene). |

**`tenon_traversant_clavete`** - Tenon traversant a clef (tusk tenon, demontable) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| clef_saillie | minimum | jonctions.saillie_tenon_clavete | 40.0 | Tenon a clef : saillie >= 40 mm pour ne pas faire eclater le bout du tenon devant la clef. |

**`tourillons`** - Tourillons cannelés (hetre ou chene) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| tourillon_porteur | signaler | - |  | Tourillons choisis pour une jonction porteuse : prevoir au moins 4 tourillons de {jonctions.tourillon_diametre} mm et verifier l'arrachement ; preferer un tenon. |

**`chevillage`** - Chevillage (cheville de chene fendue, section octogonale) : 0 regle(s)

**`rivet_forge`** - Rivet forge traversant a contre-plaque : 0 regle(s)

### Categorie `terminaison` (selection : `ferrures.terminaison_pentures`)

**`fleur_de_lys`** - Fleur de lys (petale central en ogive, deux crosses laterales, bague) : 2 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| lys_longueur | minimum | entrave.pentures.longueur | 150.0 | Fleur de lys : terminaison de 2 largeurs de bande ; branche >= 150 mm pour garder 3 rivets dans la partie droite. |
| lys_largeur | minimum | ferrures.fer_plat_largeur | 24.0 | Fleur de lys : bande >= 24 mm pour que les crosses gardent >= 5 mm de matiere. |

**`queue_d_aronde`** - Queue d'aronde (bout fendu en V) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| aronde_longueur | minimum | entrave.pentures.longueur | 130.0 | Queue d'aronde : terminaison courte, branche >= 130 mm. |

**`trilobe`** - Trilobe (trefle forge) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| trilobe_longueur | minimum | entrave.pentures.longueur | 140.0 | Trilobe : branche >= 140 mm. |

**`droite`** - Bout droit a coins abattus (sobre) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| droite_sobre | signaler | - |  | Terminaison droite : retour vers le style brut de la v1. |

### Categorie `habillage` (selection : `cremaillere.habillage`)

**`capot_ajoure`** - Capot en U ajoure de lancettes (arcs brises) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| capot_jeu | signaler | - |  | Capot : garder >= 2 mm de jour devant la barre (graisse, poussiere) ; les lancettes laissent lire le cran engage. |

**`plaque_decoupee`** - Plaque decoupee de quadrilobes : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| plaque_decoupe | signaler | - |  | Plaque decoupee : decoupe laser ou jet d'eau puis reprise a la lime et martelage des rives (sinon aspect industriel). |

**`aucun`** - Barre apparente sans habillage : 0 regle(s)

### Categorie `decor_barre` (selection : `cremaillere.decor_barre`)

**`lisse`** - Barre lisse a rives adoucies : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| barre_lisse | minimum_section_nette | cremaillere.barre_largeur | (loquet.pene_diametre + 12) / (1 - 0) | Barre lisse : largeur >= pene + 2 x 6 mm = {mini:g} mm. |

**`festonnee`** - Barre festonnee (rives en festons entre les crans) : 1 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| barre_festons | minimum_section_nette | cremaillere.barre_largeur | (loquet.pene_diametre + 12) / (1 - 0.2) | Festons (-20 % de section) : largeur >= (pene + 12) / 0,8 = {mini:g} mm pour garder 6 mm de joue nette. |

**`ajouree`** - Barre ajouree (quadrilobes entre les crans, partie haute) : 2 regle(s)

| id | operation | cibles | propriete / valeur | explication |
|---|---|---|---|---|
| barre_ajours | minimum_section_nette | cremaillere.barre_largeur | (loquet.pene_diametre + 12) / (1 - 0.3) | Ajours (-30 % de section) : largeur >= (pene + 12) / 0,7 = {mini:g} mm. |
| barre_ajours_epaisseur | minimum | cremaillere.barre_epaisseur | 10.0 | Ajours : epaisseur >= 10 mm (raideur de la barre percee). |

## Exemples executes (typologie entrave)

### `bois.essence` -> `chene`

```
- AJUSTE bois.essence : noyer -> chene [chene] Selection bois : noyer -> chene
- RECALCUL [chene] Masse des pieces bois recalculee par la grammaire (densite 640 -> 710 kg/m3, x1.109) ; la stabilite au renversement est reverifiee.
- AJUSTE entrave.platine.epaisseur : 50 mm -> 48 mm [chene] Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k 27 -> 30 MPa, facteur 0.949).
- AJUSTE tolerances.jeu_mortaise_oblongue : 2 mm -> 3 mm [chene] Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel (0.274 -> 0.365 %/%, facteur 1.332).
- ALERTE [chene] Chene + fer : risque de taches noires (tanins). Finition cire/vernis sur ferrures et bois avant montage, ou ferrures laiton.
```

### `ferrures.metal` -> `laiton_mat`

```
- AJUSTE ferrures.metal : fer_forge_mat -> laiton_mat [laiton_mat] Selection metal : fer_forge_mat -> laiton_mat
- AJUSTE loquet.pene_diametre : 12 mm -> 14 mm [laiton_mat] Pene en cisaillement : aire ~ 1/Re (Re 235 -> 180 MPa), diametre x1.143.
- AJUSTE ferrures.rivet_diametre : 5 mm -> 6 mm [laiton_mat] Rivets en cisaillement : diametre x1.143.
- AJUSTE ferrures.tete_rivet_diametre : 8 mm -> 10 mm [laiton_mat] Tete goutte de suif : suit la tige (tete >= 1,5 x tige), x1.143.
- AJUSTE cremaillere.barre_epaisseur : 8 mm -> 10 mm [laiton_mat] Barre de calage (matage du cran par le pene) : epaisseur x1.143.
- AJUSTE cremaillere.barre_largeur : 24 mm -> 30 mm [laiton_mat] Barre de calage : la largeur suit le diametre du pene (joues >= 6 mm), x1.143.
- AJUSTE ferrures.axe_pivot_diametre : 18 mm -> 20 mm [laiton_mat] Axes en flexion : d^3 ~ 1/Re, diametre x1.093.
- AJUSTE ferrures.gond_diametre : 8 mm -> 9 mm [laiton_mat] Axes en flexion : d^3 ~ 1/Re, diametre x1.093.
- AJUSTE synchro.arbre_diametre : 16 mm -> 18 mm [laiton_mat] Arbre de synchronisation en torsion : d^3 ~ 1/tau, diametre x1.093.
- AJUSTE ferrures.fer_plat_epaisseur : 4 mm -> 5 mm [laiton_mat] Fers plats (pentures, platines) : rigidite ~ E.e^3, epaisseur x1.241 (E 210000 -> 110000 MPa).
- AJUSTE ferrures.platine_pivot_epaisseur : 5 mm -> 7 mm [laiton_mat] Fers plats (pentures, platines) : rigidite ~ E.e^3, epaisseur x1.241 (E 210000 -> 110000 MPa).
- AJUSTE cremaillere.module : 3 mm -> 4 mm [laiton_mat] Denture (Lewis) : module ~ 1/Re, x1.306 puis module normalise superieur.
- AJUSTE ferrures.finition : cire_noire -> laiton_brosse_vernis_mat [laiton_mat] Finition par defaut du nouveau metal.
- RECALCUL [laiton_mat] Masse des ferrures recalculee (densite 7850 -> 8440 kg/m3).
- ALERTE [laiton_mat] Laiton deconseille pour pignons, cremaillere dentee et arbres de synchronisation (usure, grippage laiton/laiton) : garder ces pieces en acier et reserver le laiton aux pieces vues (pentures, frettes, boitiers, pivots).
- ALERTE [laiton_mat] Le laiton ne tache pas le chene (pas de reaction tanin-fer).
```

### `garnissage.cuir_manilles` -> `cuir_harnais_noir`

```
- AJUSTE garnissage.cuir_manilles : cuir_sellier_fin_noir -> cuir_harnais_noir [cuir_harnais_noir] Selection garnissage : cuir_sellier_fin_noir -> cuir_harnais_noir
- AJUSTE garnissage.epaisseur_manille : 7.5 mm -> 4 mm [cuir_harnais_noir] Simple epaisseur 4 mm, sans doublure.
- AJUSTE garnissage.largeur_manille_cou : 60 mm -> 75 mm [cuir_harnais_noir] Sans ame porteuse : largeur des manilles x1,2 (le cuir seul porte la traction et la pression de contact augmente sans doublure).
- AJUSTE garnissage.largeur_manille_poignet : 50 mm -> 60 mm [cuir_harnais_noir] Sans ame porteuse : largeur des manilles x1,2 (le cuir seul porte la traction et la pression de contact augmente sans doublure).
- ALERTE [cuir_harnais_noir] Pas de doublure : contact direct cuir tannage vegetal / peau ; arrondir et lisser les tranches (rayon >= 3 mm).
- AJUSTE sellerie.pas_point : 3.2 mm -> 4 mm [cuir_harnais_noir] Cuir de harnais epais : pas 4 mm (le pas 3,2 fendrait le cuir).
- AJUSTE sellerie.rembourrage_manille : 3 mm -> 0 mm [cuir_harnais_noir] Simple epaisseur : pas de rembourrage.
```

### `entrave.manilles.pivot_cou` -> `rotule`

```
- AJUSTE entrave.manilles.pivot_cou : axe_vertical_chape -> rotule [rotule] Selection pivot : axe_vertical_chape -> rotule
- AJUSTE entrave.manilles.hauteur_pivot : 30 mm -> 40 mm [rotule] Rotule : coquille plus haute, hauteur de pivot 40 mm.
- AJUSTE ferrures.axe_pivot_diametre : 18 mm -> 20 mm [rotule] Col de rotule : diametre >= 20 mm (flexion au col).
- ALERTE [rotule] Rotule : prevoir un frein (ecrou de serrage cache ou ressort) pour limiter le ballant ; verifier l'usure de la coquille.
```

### `bois.essence` -> `chene_fume`

```
- AJUSTE bois.essence : noyer -> chene_fume [chene_fume] Selection bois : noyer -> chene_fume
- RECALCUL [chene_fume] Masse des pieces bois recalculee par la grammaire (densite 640 -> 710 kg/m3, x1.109) ; la stabilite au renversement est reverifiee.
- AJUSTE entrave.platine.epaisseur : 50 mm -> 48 mm [chene_fume] Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 (f_m,k 27 -> 30 MPa, facteur 0.949).
- AJUSTE tolerances.jeu_mortaise_oblongue : 2 mm -> 3 mm [chene_fume] Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel (0.274 -> 0.365 %/%, facteur 1.332).
- AJUSTE bois.finition : huile_cire_noire -> fumage_ammoniac [chene_fume] Chene fume : la finition devient 'fumage_ammoniac'.
- ALERTE [chene_fume] Le fumage ne penetre que 1-3 mm : tous les usinages (mortaises, chanfreins de 1.5 mm) doivent etre faits avant fumage.
```

### `ferrures.finition` -> `galvanisation_peinture_mate`

```
- AJUSTE ferrures.finition : cire_noire -> galvanisation_peinture_mate [galvanisation_peinture_mate] Selection finition : cire_noire -> galvanisation_peinture_mate
- AJUSTE tolerances.jeu_axes : 0.3 mm -> 0.5 mm [galvanisation_peinture_mate] Galvanisation (~80 um par face) : jeu des axes et alesages porte a >= 0,5 mm.
- ALERTE [galvanisation_peinture_mate] La galvanisation efface une partie des traces de forge : marteler fort avant.
```

### `cremaillere.decor_barre` -> `festonnee`

```
- AJUSTE cremaillere.decor_barre : lisse -> festonnee [festonnee] Selection decor_barre : lisse -> festonnee
- AJUSTE cremaillere.barre_largeur : 24 mm -> 30 mm [festonnee] Festons (-20 % de section) : largeur >= (pene + 12) / 0,8 = 30 mm pour garder 6 mm de joue nette.
```

### `cremaillere.decor_barre` -> `ajouree`

```
- AJUSTE cremaillere.decor_barre : lisse -> ajouree [ajouree] Selection decor_barre : lisse -> ajouree
- AJUSTE cremaillere.barre_largeur : 24 mm -> 35 mm [ajouree] Ajours (-30 % de section) : largeur >= (pene + 12) / 0,7 = 35 mm.
- AJUSTE cremaillere.barre_epaisseur : 8 mm -> 10 mm [ajouree] Ajours : epaisseur >= 10 mm (raideur de la barre percee).
```

### `ferrures.terminaison_pentures` -> `queue_d_aronde`

```
- AJUSTE ferrures.terminaison_pentures : fleur_de_lys -> queue_d_aronde [queue_d_aronde] Selection terminaison : fleur_de_lys -> queue_d_aronde
```

### `garnissage.cuir_manilles` -> `cuir_synthetique_pu_noir`

```
- AJUSTE garnissage.cuir_manilles : cuir_sellier_fin_noir -> cuir_synthetique_pu_noir [cuir_synthetique_pu_noir] Selection garnissage : cuir_sellier_fin_noir -> cuir_synthetique_pu_noir
- AJUSTE garnissage.epaisseur_manille : 7.5 mm -> 5 mm [cuir_synthetique_pu_noir] Complexe PU 2 x 1,2 mm + mousse 2,5 mm = 5 mm.
- AJUSTE garnissage.largeur_manille_cou : 60 mm -> 65 mm [cuir_synthetique_pu_noir] PU plus souple : +5 mm de largeur pour garder la meme tenue sur l'ame.
- AJUSTE garnissage.largeur_manille_poignet : 50 mm -> 55 mm [cuir_synthetique_pu_noir] PU plus souple : +5 mm de largeur pour garder la meme tenue sur l'ame.
- AJUSTE sellerie.point : sellier_double -> piqure_machine [cuir_synthetique_pu_noir] PU : piqure machine (le point sellier main n'apporte rien sur un synthetique).
- AJUSTE sellerie.pas_point : 3.2 mm -> 3.5 mm [cuir_synthetique_pu_noir] PU : pas 3,5 mm (au-dessous, la ligne de piqure se dechire).
- ALERTE [cuir_synthetique_pu_noir] Option hygiene : supporte les desinfectants ; contraste visuel moindre avec le cuir veritable (pas de patine).
```

