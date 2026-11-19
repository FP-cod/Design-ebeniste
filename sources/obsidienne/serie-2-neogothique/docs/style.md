# Style Neogothique « raffine » (v0.2) : vocabulaire et parametres

Le style reste medieval / neogothique : angles francs, sections carrees ou
octogonales, ferrures apparentes, assemblages chevilles, aucune vis visible.
L'elegance vient de la **finition** : proportions reglees, moulures sur les
chants, ferronnerie plus fine et forgee, sellerie de maroquinier. La regle
« zero courbe organique » de la v0.1 devient : **pas de courbes organiques type
Equinox (splines, galbes libres), mais des moulures et chanfreins travailles sur
les chants**. Toute la geometrie est faite de droites et d'arcs de cercle
(quarts de cercle des moulures, arcs brises des ogives, lobes), donc usinable a
la toupie / fraise de forme et dessinable exactement dans Fusion.

## 1. Proportions (`style.proportions`)

| Mode | Plinthe / fut / chapiteau (H = hauteur visible du pied) | Remarque |
|---|---|---|
| `nombre_or` (defaut) | H/phi^4, H/phi, H/phi^3 (14,6 % / 61,8 % / 23,6 %) | 1/phi + 1/phi^3 + 1/phi^4 = 1 exactement |
| `harmonique` | 1 : 5 : 2 (12,5 % / 62,5 % / 25 %) | plinthe/chapiteau = octave, chapiteau/fut = dixieme majeure |
| `libre` | `style.part_plinthe`, `style.part_chapiteau` | parts <= 0,7 au total (validation) |

Les autres rapports de la gamme : platine 800 x 400 (2:1, octave) ;
semelle 140 x 54 (largeur / phi^2) et 566 de long (400 x racine(2), trace
*ad quadratum*) ; ceinture 80 mm (≈ 50 x phi) ; chant inferieur de platine
31 mm (50 / phi) ; ogives equilaterales (`style.ratio_rayon_ogive` = 1).

**Contrainte mecanique** : le loquet doit tomber dans le fut, entre la bague et
l'astragale. La fenetre est etroite (≈ 172 a 177 mm) : un chapiteau ou une
plinthe plus hauts (mode libre, rapport 1:4:2...) la ferment, la grammaire leve
alors une `ErreurGeometrie` explicite.

## 2. Pied-colonne (`entrave.pied.*`)

De bas en haut : **plinthe** (abaque inferieur, debord `debord_base` par face,
conge `rayon_conge_plinthe` vers le fut) ; **bague forgee** au pied du fut
(`fourreau.frette_hauteur`) ; **fut** au fruit leger (`fuselage` par face, ≈ 1,5
deg) dont les aretes portent un **chanfrein arrete** (`chanfrein_arrete`,
s'arretant a `longueur_arret` des extremites par un arret `droit` a 45 deg ou en
`langue_de_boeuf`) ; **astragale** (boudin `rayon_astragale`) ; **chapiteau** :
cavet `rayon_cavet` sous un abaque (tailloir) occupant `part_abaque` du
chapiteau. `cote` est la cote du **fut** en bas ; plinthe et abaque font
`cote + 2 x debord_base` (124 mm). La paroi du fourreau est controlee sur les
plats (`fourreau.paroi`) et dans l'arete chanfreinee (`paroi_diagonale_min`).
En octogonal, les pans coupes remplacent le chanfrein arrete.

## 3. Chants moulures (`*.chant_*`)

Types disponibles (`profils.TYPES_CHANT`) : `droit`, `chanfrein`, `conge`
(quart-de-rond creux vers l'exterieur, doux au toucher), `quart_de_rond`
(convexe), `cavet` (creux), `bec_de_corbin` (tore + gorge + listel). Defauts :
platine dessus `conge` 4 mm, dessous `bec_de_corbin` 31 x 14 mm (allege
visuellement les 50 mm de noyer, -5,3 % de module de section seulement, flexion
recalculee) ; semelle `quart_de_rond` 8 mm, bouts en cavet (`garde_cavet`) ;
ceinture chanfrein bas 4 mm. Les aretes non moulurees gardent un adoucissement
`bois.chanfrein_aretes` de 1,5 mm (non modelise).

## 4. Ceintures ajourees (`entrave.ceinture.*`)

Bandeaux avant et arriere sous la platine (mobiles avec elle), en retrait de
`retrait` sous le bord, ajoures de `nombre_arcades` baies au motif
`style.motif_ajours` : `ogive` (arc brise, rayon `ratio_rayon_ogive` x baie),
`trilobe`, `quadrilobe`. Largeur de baie = `ratio_largeur` x entraxe ; bois
plein `marge` dessus et dessous ; les montants doivent garder au moins
`style.montant_mini` (verification `montants_ceinture`). Les ceintures
s'arretent avant les chapiteaux.

## 5. Ferronnerie (`ferrures.*`, `entrave.pentures.*`, `cremaillere.*`)

- Fer plat 28 x 4 (au lieu de 40 x 5) : non porteur, decor + anti-fente ;
  terminaisons forgees `ferrures.terminaison_pentures` : `fleur_de_lys`,
  `queue_d_aronde`, `trilobe`, `droite` (catalogue `TERMINAISONS`, qui impose
  une longueur de branche mini).
- Rivets **goutte de suif** : tige `rivet_diametre`, calotte
  `tete_rivet_diametre` x `tete_rivet_hauteur` (tete >= 1,5 x tige).
- Pieces porteuses affinees mais justifiees : chaque verification de ferrure
  affinee doit garder une marge >= `charges.marge_mini_ferrures` (1,5), sinon
  alerte (synthese `marges_ferrures`). Axe de pivot porte a 18 mm pour cela.
- Barre de calage 24 x 8 ; `cremaillere.decor_barre` (`lisse`, `festonnee`,
  `ajouree`) avec regle de **section nette mini** (le decor elargit la barre
  automatiquement) ; `cremaillere.habillage` : `capot_ajoure` (tole
  `capot_epaisseur` en U, lancettes), `plaque_decoupee` (quadrilobes), `aucun`.
- Finitions : « fer forge cire noir », « bruni », « laiton vieilli ».

## 6. Sellerie (`sellerie.*`, `garnissage.*`)

Cuir par defaut `cuir_sellier_fin_noir` (veau tannage vegetal, ame
synthetique, doublure) ; point sellier double main au pas de 3,2 mm (8
points/pouce), fil de lin cire 0,55 mm, filet d'embellissement a 3 mm du bord,
tranches teintees et lustrees, rembourrage fin 3 mm. Coussin d'appui avant
(`coussin_avant`, 15 mm) matelasse `losange` (pas 50) ou `capitonne` (boutons
recouverts de 12 mm aux noeuds) ou `aucun`. Le catalogue garnissage porte les
regles sellerie de chaque cuir (ex. harnais : pas 4 mm, pas de rembourrage ;
PU : piqure machine).

## Reference : tous les parametres de style (genere)

| Chemin | Defaut | Unite | Plage / choix | Statut | Role |
|---|---|---|---|---|---|
| `bois.chanfrein_aretes` | 1.5 | mm | 0.5 - 6 | libre | Adoucissement des aretes NON moulurees (abaque, plinthe, traverses) : angles francs mais sans echarde. |
| `charges.marge_mini_ferrures` | 1.5 |  | 1 - 3 | libre | Marge mini (admissible / sollicitation) exigee des ferrures affinees : en dessous, alerte meme si la verification passe. |
| `cremaillere.barre_epaisseur` | 8 | mm | 6 - 20 | derive | Epaisseur de la barre crantee de calage. |
| `cremaillere.barre_largeur` | 24 | mm | 16 - 50 | derive | Largeur de la barre crantee de calage. |
| `cremaillere.capot_epaisseur` | 2.5 | mm | 1.5 - 5 | libre | Epaisseur de la tole du capot / de la plaque d'habillage. |
| `cremaillere.decor_barre` | lisse | texte | ajouree, festonnee, lisse | a_valider | Decor de la barre crantee : lisse, festonnee (rives en festons), ajouree (catalogue DECORS_BARRE). |
| `cremaillere.habillage` | capot_ajoure | texte | aucun, capot_ajoure, plaque_decoupee | a_valider | Habillage de la barre de calage visible : aucun, capot ajoure de lancettes, plaque decoupee de quadrilobes (catalogue HABILLAGES). |
| `entrave.ceinture.active` | True | bool |  | a_valider | Ceintures ajourees (bandeaux avant et arriere sous la platine). |
| `entrave.ceinture.chanfrein_bas` | 4 | mm | 0 - 10 | libre | Chanfrein des aretes inferieures de la ceinture. |
| `entrave.ceinture.epaisseur` | 20 | mm | 12 - 40 | libre | Epaisseur de la ceinture. |
| `entrave.ceinture.hauteur` | 80 | mm | 40 - 140 | libre | Hauteur de la ceinture (e x phi = 81 mm). |
| `entrave.ceinture.marge` | 10 | mm | 5 - 30 | libre | Bois plein au-dessus et au-dessous des ajours. |
| `entrave.ceinture.nombre_arcades` | 5 | entier | 1 - 12 | libre | Nombre de baies ajourees par ceinture (impair : baie axiale). |
| `entrave.ceinture.ratio_largeur` | 0.55 |  | 0.3 - 0.8 | libre | Largeur de baie / entraxe des baies. |
| `entrave.ceinture.retrait` | 20 | mm | 5 - 60 | libre | Retrait de la face de la ceinture sous le bord de platine. |
| `entrave.fourreau.frette_hauteur` | 12 | mm | 0 - 60 | libre | Hauteur de la bague forgee au pied du fut, au-dessus du conge de plinthe (0 = sans). |
| `entrave.fourreau.jeu_haut` | 10 | mm | 3 - 30 | libre | Jour entre le haut du fourreau et le dessous de platine au cran 0. |
| `entrave.fourreau.paroi` | 15 | mm | 12 - 40 | libre | Epaisseur de paroi du fourreau sur les plats, mesuree au plus fin (haut du fut). |
| `entrave.fourreau.paroi_diagonale_min` | 12 | mm | 8 - 30 | libre | Paroi mini dans les pans coupes (section octogonale). |
| `entrave.pentures.longueur` | 160 | mm | 60 - 250 | libre | Longueur de chaque branche des pentures d'angle, terminaison comprise. |
| `entrave.pentures.recul_bord` | 3 | mm | 0 - 20 | libre | Jour entre la terminaison la plus large et le bord de platine. |
| `entrave.pentures.rivets_par_branche` | 3 | entier | 1 - 6 | libre | Rivets apparents par branche de penture. |
| `entrave.pied.chanfrein_arrete` | 8 | mm | 0 - 20 | a_valider | Largeur (face vue) du chanfrein arrete des aretes du fut (section carree) ; 0 = arete vive. |
| `entrave.pied.cote` | 100 | mm | 70 - 180 | a_valider | Cote du FUT au pied de la colonne : cote du carre ou distance sur plats de l'octogone. |
| `entrave.pied.debord_base` | 12 | mm | 0 - 30 | libre | Debord de la plinthe et de l'abaque du chapiteau sur le fut, par face. |
| `entrave.pied.fuselage` | 3 | mm | 0 - 10 | libre | Retrait par face du haut du fut (fruit / leger fuselage, 1,5 deg). |
| `entrave.pied.longueur_arret` | 18 | mm | 5 - 60 | libre | Distance entre l'extremite du fut et le debut du chanfrein. |
| `entrave.pied.part_abaque` | 0.35 |  | 0.15 - 0.6 | libre | Part du chapiteau occupee par l'abaque (tailloir). |
| `entrave.pied.rayon_astragale` | 3 | mm | 0 - 8 | libre | Rayon du boudin d'astragale sous le chapiteau. |
| `entrave.pied.rayon_cavet` | 9 | mm | 0 - 20 | libre | Rayon du cavet sous l'abaque du chapiteau. |
| `entrave.pied.rayon_conge_plinthe` | 6 | mm | 0 - 15 | libre | Rayon du conge de raccord fut / plinthe. |
| `entrave.pied.retrait_bord` | 30 | mm | 0 - 120 | libre | Retrait du CHAPITEAU (partie la plus large) par rapport aux bords de la platine. |
| `entrave.pied.section` | carre | texte | carre, octogonal | a_valider | Section des pieds (fourreaux). |
| `entrave.pied.type_arret` | droit | texte | droit, langue_de_boeuf | a_valider | Arret du chanfrein : 'droit' (biais a 45 deg) ou 'langue_de_boeuf' (cuilleron concave). |
| `entrave.platine.chant_dessous` | bec_de_corbin | texte | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | a_valider | Profil du chant inferieur : bec-de-corbin (tore + gorge + listel) qui allege visuellement les 50 mm de noyer. |
| `entrave.platine.chant_dessous_hauteur` | 31 | mm | 0 - 45 | libre | Hauteur moulee du chant inferieur (e/phi = 30,9 mm). |
| `entrave.platine.chant_dessous_profondeur` | 14 | mm | 0 - 25 | libre | Profondeur (retrait) du chant inferieur. |
| `entrave.platine.chant_dessus` | conge | texte | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | a_valider | Profil du chant superieur (cote corps : doux au toucher). |
| `entrave.platine.chant_dessus_taille` | 4 | mm | 0 - 15 | libre | Rayon / cote du chant superieur. |
| `entrave.semelle.chant` | quart_de_rond | texte | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | libre | Profil des aretes superieures longues de la semelle. |
| `entrave.semelle.chant_taille` | 8 | mm | 0 - 20 | libre | Rayon du chant superieur de la semelle. |
| `entrave.semelle.garde_cavet` | 12 | mm | 5 - 40 | libre | Hauteur droite laissee sous le cavet des bouts de semelle (le cavet a pour rayon hauteur - garde). |
| `entrave.semelle.hauteur` | 54 | mm | 40 - 120 | libre | Hauteur des semelles = largeur / phi^2 (54 mm). |
| `entrave.semelle.largeur` | 140 | mm | 60 - 200 | libre | Largeur des semelles (axe X) : plinthe + 2 x chant (la plinthe ne deborde plus de la semelle). |
| `entrave.semelle.longueur` | 566 | mm | 400 - 900 | a_valider | Longueur des semelles (patins) le long de Y : W x racine(2) (trace ad quadratum, 566 mm) ; elargit le polygone de sustentation. |
| `entrave.semelle.profondeur_logement` | 36 | mm | 0 - 80 | libre | Profondeur du logement ou descend le coulisseau en position basse. |
| `ferrures.axe_pivot_diametre` | 18 | mm | 10 - 30 | derive | Diametre des axes de pivot des manilles. |
| `ferrures.fer_plat_epaisseur` | 4 | mm | 3 - 12 | derive | Epaisseur des fers plats. |
| `ferrures.fer_plat_largeur` | 28 | mm | 20 - 60 | libre | Largeur des fers plats (pentures, brides) : 28 mm, plus fin que la v1 (40) ; non porteur (decor + anti-fente). |
| `ferrures.finition` | cire_noire | texte | cire_noire, galvanisation_peinture_mate, huile_brunie, laiton_brosse_vernis_mat, laiton_patine_vieilli, phosphatation_vernis_mat | libre | Finition des ferrures ('fer forge cire noir', 'bruni', 'laiton vieilli'...). |
| `ferrures.gond_diametre` | 8 | mm | 6 - 20 | derive | Diametre d'axe des gonds de manilles. |
| `ferrures.metal` | fer_forge_mat | texte | fer_forge_mat, laiton_mat | a_valider | Metal des ferrures apparentes. |
| `ferrures.platine_pivot_cote` | 70 | mm | 50 - 140 | libre | Cote de la platine forgee sous chaque pivot (coins abattus). |
| `ferrures.platine_pivot_epaisseur` | 5 | mm | 4 - 12 | derive | Epaisseur de la platine de pivot. |
| `ferrures.rivet_diametre` | 5 | mm | 3 - 12 | derive | Diametre de tige des rivets forges. |
| `ferrures.terminaison_pentures` | fleur_de_lys | texte | droite, fleur_de_lys, queue_d_aronde, trilobe | a_valider | Terminaison forgee des pentures (cle du catalogue TERMINAISONS). |
| `ferrures.tete_rivet_diametre` | 8 | mm | 5 - 18 | derive | Diametre de la tete goutte de suif des rivets (>= 1,5 x tige). |
| `ferrures.tete_rivet_hauteur` | 3 | mm | 1.5 - 8 | libre | Hauteur de la calotte goutte de suif. |
| `garnissage.coloris` | noir | texte | noir | impose | Coloris impose de la gamme (verifie contre le catalogue). |
| `garnissage.cuir_manilles` | cuir_sellier_fin_noir | texte | cuir_harnais_noir, cuir_renforce_double_noir, cuir_sellier_fin_noir, cuir_synthetique_pu_noir | impose | Cuir des manilles (cle du catalogue). |
| `garnissage.diametre_int_cou` | 130 | mm | 100 - 170 | a_valider | Diametre interieur nominal de la manille de cou (reglable par boucle +/-15 mm). |
| `garnissage.diametre_int_poignet` | 75 | mm | 55 - 100 | a_valider | Diametre interieur nominal des manilles de poignets. |
| `garnissage.epaisseur_manille` | 7.5 | mm | 3 - 12 | derive | Epaisseur du complexe cuir des manilles (exterieur + ame + rembourrage + doublure). |
| `garnissage.epaisseur_rembourrage` | 30 | mm | 10 - 60 | libre | Rembourrage des coussinets (futures typologies). |
| `garnissage.largeur_manille_cou` | 60 | mm | 40 - 90 | derive | Largeur (hauteur de bande) de la manille de cou. |
| `garnissage.largeur_manille_poignet` | 50 | mm | 35 - 80 | derive | Largeur de bande des manilles de poignets. |
| `sellerie.bouton_diametre` | 12 | mm | 8 - 20 | libre | Diametre des boutons de capiton (cuir noir). |
| `sellerie.coussin_avant` | True | bool |  | a_valider | Coussin d'appui en cuir sur l'avant de la platine (devant les manilles). |
| `sellerie.coussin_epaisseur` | 15 | mm | 8 - 40 | libre | Epaisseur du coussin d'appui (cuir + mousse). |
| `sellerie.fil` | lin_cire | texte | lin_cire, polyester_cire | libre | Fil de couture. |
| `sellerie.fil_diametre` | 0.55 | mm | 0.35 - 1.2 | derive | Diametre du fil cire (0,55 mm : fin, visible sans etre grossier). |
| `sellerie.filet_bordure` | 3 | mm | 2 - 6 | libre | Retrait de la couture et du filet d'embellissement (abattage) au bord de la sangle. |
| `sellerie.matelassage_pas` | 50 | mm | 30 - 120 | libre | Pas (diagonale) des losanges du matelassage. |
| `sellerie.matelassage_platine` | losange | texte | aucun, losange, capitonne | a_valider | Matelassage du coussin : 'aucun', 'losange' (piqures en losange) ou 'capitonne' (losanges + boutons recouverts). |
| `sellerie.pas_point` | 3.2 | mm | 2 - 6 | derive | Pas du point (pricot) : 3,2 mm = 8 points / pouce, fin et regulier. |
| `sellerie.point` | sellier_double | texte | sellier_double, piqure_machine | a_valider | Point de couture : sellier double a deux aiguilles (main, indecousable) ou piqure machine. |
| `sellerie.rembourrage_manille` | 3 | mm | 0 - 8 | derive | Rembourrage fin (mousse latex haute densite) entre exterieur et doublure des manilles. |
| `sellerie.tranches` | teintees_lustrees | texte | teintees_lustrees, cirees | libre | Finition des tranches : teintees noir puis lustrees (gomme adragante, os), ou simplement cirees. |
| `style.montant_mini` | 14 | mm | 8 - 40 | libre | Largeur mini de bois laissee entre deux ajours (section nette des montants de ceinture). |
| `style.motif_ajours` | ogive | texte | ogive, trilobe, quadrilobe | a_valider | Motif des ajours (ceinture) : arc brise, trilobe ou quadrilobe. |
| `style.part_chapiteau` | 0.2361 |  | 0.12 - 0.35 | libre | Part occupee par le chapiteau, astragale comprise (si proportions = 'libre'). |
| `style.part_plinthe` | 0.1459 |  | 0.08 - 0.3 | libre | Part de la hauteur visible du pied occupee par la plinthe (utilisee si proportions = 'libre'). |
| `style.proportions` | nombre_or | texte | nombre_or, harmonique, libre | a_valider | Regle de proportion des pieds (plinthe / fut / chapiteau) et des semelles : 'nombre_or' (H/phi^4, H/phi, H/phi^3 : 1/phi + 1/phi^3 + 1/phi^4 = 1), 'harmonique' (1:5:2 : octave plinthe/chapiteau, dixieme majeure chapiteau/fut), 'libre' (parts ci-dessous). |
| `style.ratio_rayon_ogive` | 1 |  | 0.6 - 1.6 | libre | Rayon des arcs brises / largeur de baie : 1 = ogive equilaterale, > 1 = lancette, < 1 = surbaissee. |
