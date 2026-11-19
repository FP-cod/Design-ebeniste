# Ajustements v0.1 -> v0.2 : Neogothique « raffine »

Genere par `outils/generer_docs.py` (comparaison automatique de
`docs/parametres_entrave_defauts_v1.json` et `docs/resultats_entrave_v1.json`,
instantanes de la v0.1, avec les defauts et resultats actuels).

Direction : toujours medieval / neogothique (angles francs, sections carrees,
ferrures apparentes, zero vis) mais finition elegante : proportions au nombre
d'or, moulures reelles sur les chants (conge, bec-de-corbin, quart-de-rond,
cavet), colonnes a plinthe / fut a chanfreins arretes / astragale / chapiteau,
ceintures ajourees d'une arcature, ferrures forgees plus fines a terminaisons,
rivets goutte de suif, sellerie fine. La regle « zero courbe organique »
devient : *pas de courbes organiques type Equinox, mais des moulures et
chanfreins travailles sur les chants* (arcs de cercle et droites uniquement).

## Parametres modifies (avant -> apres)

| Chemin | v0.1 | v0.2 | Unite | Role |
|---|---|---|---|---|
| `bois.chanfrein_aretes` | 2 | **1.5** | mm | Adoucissement des aretes NON moulurees (abaque, plinthe, traverses) : angles francs mais sans echarde. |
| `cremaillere.barre_epaisseur` | 10 | **8** | mm | Epaisseur de la barre crantee de calage. |
| `cremaillere.barre_largeur` | 30 | **24** | mm | Largeur de la barre crantee de calage. |
| `entrave.fourreau.frette_hauteur` | 30 | **12** | mm | Hauteur de la bague forgee au pied du fut, au-dessus du conge de plinthe (0 = sans). |
| `entrave.fourreau.paroi` | 22 | **15** | mm | Epaisseur de paroi du fourreau sur les plats, mesuree au plus fin (haut du fut). |
| `entrave.pentures.longueur` | 140 | **160** | mm | Longueur de chaque branche des pentures d'angle, terminaison comprise. |
| `entrave.pied.cote` | 110 | **100** | mm | Cote du FUT au pied de la colonne : cote du carre ou distance sur plats de l'octogone. |
| `entrave.semelle.hauteur` | 60 | **54** | mm | Hauteur des semelles = largeur / phi^2 (54 mm). |
| `entrave.semelle.largeur` | 90 | **140** | mm | Largeur des semelles (axe X) : plinthe + 2 x chant (la plinthe ne deborde plus de la semelle). |
| `entrave.semelle.longueur` | 560 | **566** | mm | Longueur des semelles (patins) le long de Y : W x racine(2) (trace ad quadratum, 566 mm) ; elargit le polygone de sustentation. |
| `entrave.semelle.profondeur_logement` | 40 | **36** | mm | Profondeur du logement ou descend le coulisseau en position basse. |
| `ferrures.axe_pivot_diametre` | 16 | **18** | mm | Diametre des axes de pivot des manilles. |
| `ferrures.fer_plat_epaisseur` | 5 | **4** | mm | Epaisseur des fers plats. |
| `ferrures.fer_plat_largeur` | 40 | **28** | mm | Largeur des fers plats (pentures, brides) : 28 mm, plus fin que la v1 (40) ; non porteur (decor + anti-fente). |
| `ferrures.gond_diametre` | 10 | **8** | mm | Diametre d'axe des gonds de manilles. |
| `ferrures.platine_pivot_cote` | 80 | **70** | mm | Cote de la platine forgee sous chaque pivot (coins abattus). |
| `ferrures.platine_pivot_epaisseur` | 6 | **5** | mm | Epaisseur de la platine de pivot. |
| `ferrures.rivet_diametre` | 6 | **5** | mm | Diametre de tige des rivets forges. |
| `gamme.version` | 0.1.0 | **0.2.0** | texte | Version du vocabulaire de parametres. |
| `garnissage.cuir_manilles` | cuir_renforce_double_noir | **cuir_sellier_fin_noir** | texte | Cuir des manilles (cle du catalogue). |
| `garnissage.epaisseur_manille` | 6.5 | **7.5** | mm | Epaisseur du complexe cuir des manilles (exterieur + ame + rembourrage + doublure). |
| `jonctions.tourillon_diametre` | 10 | **6** | mm | Diametre des tourillons (<= 1/2 de la piece la plus fine). |
| `loquet.boitier_hauteur` | 50 | **32** | mm | Hauteur du boitier forge du loquet. |
| `loquet.course` | 25 | **20** | mm | Course du pene (retrait complet hors de la barre). |
| `loquet.engagement` | 12 | **10** | mm | Profondeur d'entree du pene dans la gache au-dela de la barre. |
| `loquet.pene_diametre` | 16 | **12** | mm | Diametre du pene rond du loquet. |
| `synchro.arbre_diametre` | 20 | **16** | mm | Diametre des arbres de transmission. |

## Parametres ajoutes

| Chemin | Valeur | Unite | Role |
|---|---|---|---|
| `charges.marge_mini_ferrures` | 1.5 |  | Marge mini (admissible / sollicitation) exigee des ferrures affinees : en dessous, alerte meme si la verification passe. |
| `cremaillere.capot_epaisseur` | 2.5 | mm | Epaisseur de la tole du capot / de la plaque d'habillage. |
| `cremaillere.decor_barre` | lisse | texte | Decor de la barre crantee : lisse, festonnee (rives en festons), ajouree (catalogue DECORS_BARRE). |
| `cremaillere.habillage` | capot_ajoure | texte | Habillage de la barre de calage visible : aucun, capot ajoure de lancettes, plaque decoupee de quadrilobes (catalogue HABILLAGES). |
| `entrave.ceinture.active` | True | bool | Ceintures ajourees (bandeaux avant et arriere sous la platine). |
| `entrave.ceinture.chanfrein_bas` | 4 | mm | Chanfrein des aretes inferieures de la ceinture. |
| `entrave.ceinture.epaisseur` | 20 | mm | Epaisseur de la ceinture. |
| `entrave.ceinture.hauteur` | 80 | mm | Hauteur de la ceinture (e x phi = 81 mm). |
| `entrave.ceinture.marge` | 10 | mm | Bois plein au-dessus et au-dessous des ajours. |
| `entrave.ceinture.nombre_arcades` | 5 | entier | Nombre de baies ajourees par ceinture (impair : baie axiale). |
| `entrave.ceinture.ratio_largeur` | 0.55 |  | Largeur de baie / entraxe des baies. |
| `entrave.ceinture.retrait` | 20 | mm | Retrait de la face de la ceinture sous le bord de platine. |
| `entrave.pentures.recul_bord` | 3 | mm | Jour entre la terminaison la plus large et le bord de platine. |
| `entrave.pied.chanfrein_arrete` | 8 | mm | Largeur (face vue) du chanfrein arrete des aretes du fut (section carree) ; 0 = arete vive. |
| `entrave.pied.debord_base` | 12 | mm | Debord de la plinthe et de l'abaque du chapiteau sur le fut, par face. |
| `entrave.pied.fuselage` | 3 | mm | Retrait par face du haut du fut (fruit / leger fuselage, 1,5 deg). |
| `entrave.pied.longueur_arret` | 18 | mm | Distance entre l'extremite du fut et le debut du chanfrein. |
| `entrave.pied.part_abaque` | 0.35 |  | Part du chapiteau occupee par l'abaque (tailloir). |
| `entrave.pied.rayon_astragale` | 3 | mm | Rayon du boudin d'astragale sous le chapiteau. |
| `entrave.pied.rayon_cavet` | 9 | mm | Rayon du cavet sous l'abaque du chapiteau. |
| `entrave.pied.rayon_conge_plinthe` | 6 | mm | Rayon du conge de raccord fut / plinthe. |
| `entrave.pied.type_arret` | droit | texte | Arret du chanfrein : 'droit' (biais a 45 deg) ou 'langue_de_boeuf' (cuilleron concave). |
| `entrave.platine.chant_dessous` | bec_de_corbin | texte | Profil du chant inferieur : bec-de-corbin (tore + gorge + listel) qui allege visuellement les 50 mm de noyer. |
| `entrave.platine.chant_dessous_hauteur` | 31 | mm | Hauteur moulee du chant inferieur (e/phi = 30,9 mm). |
| `entrave.platine.chant_dessous_profondeur` | 14 | mm | Profondeur (retrait) du chant inferieur. |
| `entrave.platine.chant_dessus` | conge | texte | Profil du chant superieur (cote corps : doux au toucher). |
| `entrave.platine.chant_dessus_taille` | 4 | mm | Rayon / cote du chant superieur. |
| `entrave.semelle.chant` | quart_de_rond | texte | Profil des aretes superieures longues de la semelle. |
| `entrave.semelle.chant_taille` | 8 | mm | Rayon du chant superieur de la semelle. |
| `entrave.semelle.garde_cavet` | 12 | mm | Hauteur droite laissee sous le cavet des bouts de semelle (le cavet a pour rayon hauteur - garde). |
| `ferrures.terminaison_pentures` | fleur_de_lys | texte | Terminaison forgee des pentures (cle du catalogue TERMINAISONS). |
| `ferrures.tete_rivet_diametre` | 8 | mm | Diametre de la tete goutte de suif des rivets (>= 1,5 x tige). |
| `ferrures.tete_rivet_hauteur` | 3 | mm | Hauteur de la calotte goutte de suif. |
| `sellerie.bouton_diametre` | 12 | mm | Diametre des boutons de capiton (cuir noir). |
| `sellerie.coussin_avant` | True | bool | Coussin d'appui en cuir sur l'avant de la platine (devant les manilles). |
| `sellerie.coussin_epaisseur` | 15 | mm | Epaisseur du coussin d'appui (cuir + mousse). |
| `sellerie.fil` | lin_cire | texte | Fil de couture. |
| `sellerie.fil_diametre` | 0.55 | mm | Diametre du fil cire (0,55 mm : fin, visible sans etre grossier). |
| `sellerie.filet_bordure` | 3 | mm | Retrait de la couture et du filet d'embellissement (abattage) au bord de la sangle. |
| `sellerie.matelassage_pas` | 50 | mm | Pas (diagonale) des losanges du matelassage. |
| `sellerie.matelassage_platine` | losange | texte | Matelassage du coussin : 'aucun', 'losange' (piqures en losange) ou 'capitonne' (losanges + boutons recouverts). |
| `sellerie.pas_point` | 3.2 | mm | Pas du point (pricot) : 3,2 mm = 8 points / pouce, fin et regulier. |
| `sellerie.point` | sellier_double | texte | Point de couture : sellier double a deux aiguilles (main, indecousable) ou piqure machine. |
| `sellerie.rembourrage_manille` | 3 | mm | Rembourrage fin (mousse latex haute densite) entre exterieur et doublure des manilles. |
| `sellerie.tranches` | teintees_lustrees | texte | Finition des tranches : teintees noir puis lustrees (gomme adragante, os), ou simplement cirees. |
| `style.montant_mini` | 14 | mm | Largeur mini de bois laissee entre deux ajours (section nette des montants de ceinture). |
| `style.motif_ajours` | ogive | texte | Motif des ajours (ceinture) : arc brise, trilobe ou quadrilobe. |
| `style.part_chapiteau` | 0.2361 |  | Part occupee par le chapiteau, astragale comprise (si proportions = 'libre'). |
| `style.part_plinthe` | 0.1459 |  | Part de la hauteur visible du pied occupee par la plinthe (utilisee si proportions = 'libre'). |
| `style.proportions` | nombre_or | texte | Regle de proportion des pieds (plinthe / fut / chapiteau) et des semelles : 'nombre_or' (H/phi^4, H/phi, H/phi^3 : 1/phi + 1/phi^3 + 1/phi^4 = 1), 'harmonique' (1:5:2 : octave plinthe/chapiteau, dixieme majeure chapiteau/fut), 'libre' (parts ci-dessous). |
| `style.ratio_rayon_ogive` | 1 |  | Rayon des arcs brises / largeur de baie : 1 = ogive equilaterale, > 1 = lancette, < 1 = surbaissee. |

## Parametres retires

- `ferrures.tete_rivet_cote` (v0.1 : 10)

## Resultats de la grammaire (cran 0, defauts)

| Grandeur | v0.1 | v0.2 |
|---|---|---|
| Masse totale | 47.4 kg | 43.3 kg |
| Masse mobile / fixe | 24.6 / 22.8 kg | 23.8 / 19.4 kg |
| Corps Fusion | 113 | 190 (dont 56 blocs moulures, 40 revolutions) |
| Coulisseau | 63 mm | 61 mm |
| Recouvrement en position haute | 65 mm | 67 mm |
| Barre de calage / loquet | 235 mm, z=194 | 236 mm, z=175 |

| Verification | v0.1 (valeur / limite, niveau) | v0.2 (valeur / limite, marge, niveau) |
|---|---|---|
| renversement_y | 0.3113 / 1, alerte | 0.2867 / 1, x0.29, alerte |
| renversement_x | 0.4001 / 1, alerte | 0.3835 / 1, x0.38, alerte |
| glissement | 750 / 139.5, alerte | 750 / 127.3, x0.17, alerte |
| flexion_platine | 2.126 / 16.62, ok | 2.197 / 16.62, x7.56, ok |
| fleche_platine | 0.2605 / 2.1, ok | 0.2528 / 2.053, x8.12, ok |
| cisaillement_pene | 3.098 / 123.3, ok | 5.49 / 123.3, x22.47, ok |
| matage_cran | 7.786 / 427.3, ok | 12.94 / 427.3, x33.03, ok |
| ligament_crans | 6.921 / 123.3, ok | 5.97 / 123.3, x20.66, ok |
| traction_barre_cran | (nouvelle) | 12.94 / 213.6, x16.51, ok |
| dent_lewis | 10.2 / 142.4, ok | 9.87 / 142.4, x14.43, ok |
| torsion_arbre | 2.769 / 123.3, ok | 5.231 / 123.3, x23.58, ok |
| recouvrement | 1.032 / 1.5, alerte | 1.098 / 1.5, x0.73, alerte |
| paroi_diagonale | (nouvelle) | 17.21 / 12, x1.43, ok |
| montants_ceinture | (nouvelle) | 43.92 / 14, x3.14, ok |
| manille_cou | 750 / 1500, ok | 750 / 1500, x2.00, ok |
| manille_poignet | 750 / 1500, ok | 750 / 1500, x2.00, ok |
| axe_pivot | 189.3 / 213.6, ok | 134.3 / 213.6, x1.59, ok |
| rivets_pivot | 24.04 / 213.6, ok | 39.95 / 213.6, x5.35, ok |
| gond | (nouvelle) | 7.46 / 123.3, x16.53, ok |
| chevilles_pied | 909 / 1692, ok | 967.9 / 1658, x1.71, ok |
| marges_ferrures | (nouvelle) | 1.591 / 1.5, x1.06, ok |
