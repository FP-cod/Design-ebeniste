# Parametres de la gamme Neogothique (couche 1)

Genere par `outils/generer_docs.py` depuis `neogothique/parametres.py` (source de verite).

Unites internes : mm, kg, deg, N, MPa. Valeurs affichees : typologie `entrave` (override : {'bois': {'essence': 'noyer'}}).

Statuts : **impose** (fixe par Fabien), **a_valider** (propose, voir points_a_trancher.md), **derive** (peut etre recalcule par les regles materiaux), **libre** (reference de gamme).

Nom Fusion : `neo_` + chemin avec `_` (ex. `cremaillere.pas` -> `neo_cremaillere_pas`). Les textes et booleens ne sont pas exportes (Fusion ne gere que des valeurs numeriques).

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `gamme.nom` | Neogothique | texte | Nom de la gamme. |  | libre | gamme |
| `gamme.version` | 0.2.0 | texte | Version du vocabulaire de parametres. |  | libre | gamme |
| `gamme.prefixe_fusion` | neo_ | texte | Prefixe des User Parameters crees dans Fusion. |  | libre | fusion_outils |
| `style.proportions` | nombre_or | texte | Regle de proportion des pieds (plinthe / fut / chapiteau) et des semelles : 'nombre_or' (H/phi^4, H/phi, H/phi^3 : 1/phi + 1/phi^3 + 1/phi^4 = 1), 'harmonique' (1:5:2 : octave plinthe/chapiteau, dixieme majeure chapiteau/fut), 'libre' (parts ci-dessous). | nombre_or, harmonique, libre | a_valider | entrave, gamme |
| `style.part_plinthe` | 0.1459 |  | Part de la hauteur visible du pied occupee par la plinthe (utilisee si proportions = 'libre'). | 0.08 - 0.3 | libre | entrave |
| `style.part_chapiteau` | 0.2361 |  | Part occupee par le chapiteau, astragale comprise (si proportions = 'libre'). | 0.12 - 0.35 | libre | entrave |
| `style.motif_ajours` | ogive | texte | Motif des ajours (ceinture) : arc brise, trilobe ou quadrilobe. | ogive, trilobe, quadrilobe | a_valider | entrave, gamme |
| `style.ratio_rayon_ogive` | 1 |  | Rayon des arcs brises / largeur de baie : 1 = ogive equilaterale, > 1 = lancette, < 1 = surbaissee. | 0.6 - 1.6 | libre | entrave, gamme |
| `style.montant_mini` | 14 | mm | Largeur mini de bois laissee entre deux ajours (section nette des montants de ceinture). | 8 - 40 | libre | entrave, regles |
| `bois.essence` | noyer | texte | Essence par defaut de la gamme (cle du catalogue bois). L'Entrave l'impose a 'noyer' (override de typologie). | chene, chene_fume, noyer, noyer_noir | impose | entrave, regles |
| `bois.finition` | huile_cire_noire | texte | Finition du bois. | cire_naturelle, fumage_ammoniac, huile_cire_noire, teinte_acetate_fer | libre | entrave, regles |
| `bois.humidite_cible` | 10 | % | Humidite d'equilibre visee a la fabrication (interieur chauffe). | 6 - 14 | libre | entrave |
| `bois.variation_humidite` | 3 | % | Variation saisonniere d'humidite a absorber (mortaises oblongues). | 1 - 6 | libre | entrave |
| `bois.chanfrein_aretes` | 1.5 | mm | Adoucissement des aretes NON moulurees (abaque, plinthe, traverses) : angles francs mais sans echarde. | 0.5 - 6 | libre | entrave, gamme |
| `bois.section_mini` | 40 | mm | Plus petite section admise pour une piece bois porteuse (coulisseau). | 30 - 80 | libre | entrave, gamme |
| `garnissage.cuir_manilles` | cuir_sellier_fin_noir | texte | Cuir des manilles (cle du catalogue). | cuir_harnais_noir, cuir_renforce_double_noir, cuir_sellier_fin_noir, cuir_synthetique_pu_noir | impose | entrave, regles |
| `garnissage.coloris` | noir | texte | Coloris impose de la gamme (verifie contre le catalogue). | noir | impose | entrave |
| `garnissage.epaisseur_manille` | 7.5 | mm | Epaisseur du complexe cuir des manilles (exterieur + ame + rembourrage + doublure). | 3 - 12 | derive | entrave, regles |
| `garnissage.largeur_manille_cou` | 60 | mm | Largeur (hauteur de bande) de la manille de cou. | 40 - 90 | derive | entrave, regles |
| `garnissage.largeur_manille_poignet` | 50 | mm | Largeur de bande des manilles de poignets. | 35 - 80 | derive | entrave, regles |
| `garnissage.diametre_int_cou` | 130 | mm | Diametre interieur nominal de la manille de cou (reglable par boucle +/-15 mm). | 100 - 170 | a_valider | entrave |
| `garnissage.diametre_int_poignet` | 75 | mm | Diametre interieur nominal des manilles de poignets. | 55 - 100 | a_valider | entrave |
| `garnissage.epaisseur_rembourrage` | 30 | mm | Rembourrage des coussinets (futures typologies). | 10 - 60 | libre | gamme, regles |
| `sellerie.point` | sellier_double | texte | Point de couture : sellier double a deux aiguilles (main, indecousable) ou piqure machine. | sellier_double, piqure_machine | a_valider | entrave, regles |
| `sellerie.pas_point` | 3.2 | mm | Pas du point (pricot) : 3,2 mm = 8 points / pouce, fin et regulier. | 2 - 6 | derive | entrave, regles |
| `sellerie.fil` | lin_cire | texte | Fil de couture. | lin_cire, polyester_cire | libre | entrave, regles |
| `sellerie.fil_diametre` | 0.55 | mm | Diametre du fil cire (0,55 mm : fin, visible sans etre grossier). | 0.35 - 1.2 | derive | entrave, regles |
| `sellerie.filet_bordure` | 3 | mm | Retrait de la couture et du filet d'embellissement (abattage) au bord de la sangle. | 2 - 6 | libre | entrave |
| `sellerie.tranches` | teintees_lustrees | texte | Finition des tranches : teintees noir puis lustrees (gomme adragante, os), ou simplement cirees. | teintees_lustrees, cirees | libre | entrave |
| `sellerie.rembourrage_manille` | 3 | mm | Rembourrage fin (mousse latex haute densite) entre exterieur et doublure des manilles. | 0 - 8 | derive | entrave, regles |
| `sellerie.coussin_avant` | True | bool | Coussin d'appui en cuir sur l'avant de la platine (devant les manilles). |  | a_valider | entrave |
| `sellerie.coussin_epaisseur` | 15 | mm | Epaisseur du coussin d'appui (cuir + mousse). | 8 - 40 | libre | entrave |
| `sellerie.matelassage_platine` | losange | texte | Matelassage du coussin : 'aucun', 'losange' (piqures en losange) ou 'capitonne' (losanges + boutons recouverts). | aucun, losange, capitonne | a_valider | entrave |
| `sellerie.matelassage_pas` | 50 | mm | Pas (diagonale) des losanges du matelassage. | 30 - 120 | libre | entrave |
| `sellerie.bouton_diametre` | 12 | mm | Diametre des boutons de capiton (cuir noir). | 8 - 20 | libre | entrave |
| `ferrures.metal` | fer_forge_mat | texte | Metal des ferrures apparentes. | fer_forge_mat, laiton_mat | a_valider | entrave, regles |
| `ferrures.finition` | cire_noire | texte | Finition des ferrures ('fer forge cire noir', 'bruni', 'laiton vieilli'...). | cire_noire, galvanisation_peinture_mate, huile_brunie, laiton_brosse_vernis_mat, laiton_patine_vieilli, phosphatation_vernis_mat | libre | entrave, regles |
| `ferrures.terminaison_pentures` | fleur_de_lys | texte | Terminaison forgee des pentures (cle du catalogue TERMINAISONS). | droite, fleur_de_lys, queue_d_aronde, trilobe | a_valider | entrave, regles |
| `ferrures.fer_plat_largeur` | 28 | mm | Largeur des fers plats (pentures, brides) : 28 mm, plus fin que la v1 (40) ; non porteur (decor + anti-fente). | 20 - 60 | libre | entrave |
| `ferrures.fer_plat_epaisseur` | 4 | mm | Epaisseur des fers plats. | 3 - 12 | derive | entrave, regles |
| `ferrures.rivet_diametre` | 5 | mm | Diametre de tige des rivets forges. | 3 - 12 | derive | entrave, regles |
| `ferrures.tete_rivet_diametre` | 8 | mm | Diametre de la tete goutte de suif des rivets (>= 1,5 x tige). | 5 - 18 | derive | entrave, regles |
| `ferrures.tete_rivet_hauteur` | 3 | mm | Hauteur de la calotte goutte de suif. | 1.5 - 8 | libre | entrave |
| `ferrures.axe_pivot_diametre` | 18 | mm | Diametre des axes de pivot des manilles. | 10 - 30 | derive | entrave, regles |
| `ferrures.gond_diametre` | 8 | mm | Diametre d'axe des gonds de manilles. | 6 - 20 | derive | entrave, regles |
| `ferrures.platine_pivot_cote` | 70 | mm | Cote de la platine forgee sous chaque pivot (coins abattus). | 50 - 140 | libre | entrave |
| `ferrures.platine_pivot_epaisseur` | 5 | mm | Epaisseur de la platine de pivot. | 4 - 12 | derive | entrave, regles |
| `cremaillere.hauteur_mini` | 300 | mm | Hauteur du DESSUS de platine au cran 0 (position basse). Interpretation de 'debattement 15 cm ... a 45 cm' : 450 - 150. | 150 - 600 | a_valider | entrave |
| `cremaillere.hauteur_maxi` | 450 | mm | Hauteur du dessus de platine au dernier cran. | 200 - 700 | impose | entrave |
| `cremaillere.nombre_crans` | 7 | entier | Nombre de crans = nombre de POSITIONS de calage (convention 'positions' : debattement = (n-1) x pas). | 2 - 20 | a_valider | entrave |
| `cremaillere.pas` | 25 | mm | Pas entre deux crans. | 10 - 60 | a_valider | entrave |
| `cremaillere.convention` | positions | texte | 'positions' : n crans = n hauteurs, debattement=(n-1).pas ; 'intervalles' : n intervalles, n+1 hauteurs, debattement=n.pas. | positions, intervalles | libre | entrave |
| `cremaillere.cran_courant` | 0 | entier | Cran courant (0 = position basse) : pilote la geometrie et le User Parameter Fusion. | 0 - 20 | libre | entrave |
| `cremaillere.barre_largeur` | 24 | mm | Largeur de la barre crantee de calage. | 16 - 50 | derive | entrave, regles |
| `cremaillere.barre_epaisseur` | 8 | mm | Epaisseur de la barre crantee de calage. | 6 - 20 | derive | entrave, regles |
| `cremaillere.module` | 3 | mm | Module de denture pignon / cremaillere de synchronisation. | 1.5 - 6 | derive | entrave, regles |
| `cremaillere.angle_pression` | 20 | deg | Angle de pression de la denture. | 14.5 - 25 | libre | entrave |
| `cremaillere.largeur_denture` | 20 | mm | Largeur de denture (pignon et cremaillere). | 10 - 40 | libre | entrave |
| `cremaillere.dents_mini` | 14 | entier | Nombre de dents mini du pignon (sous-coupe a 20 deg). | 12 - 30 | libre | entrave |
| `cremaillere.marge_engrenement` | 15 | mm | Marge de denture au-dela du point de contact en position haute. | 5 - 40 | libre | entrave |
| `cremaillere.habillage` | capot_ajoure | texte | Habillage de la barre de calage visible : aucun, capot ajoure de lancettes, plaque decoupee de quadrilobes (catalogue HABILLAGES). | aucun, capot_ajoure, plaque_decoupee | a_valider | entrave, regles |
| `cremaillere.decor_barre` | lisse | texte | Decor de la barre crantee : lisse, festonnee (rives en festons), ajouree (catalogue DECORS_BARRE). | ajouree, festonnee, lisse | a_valider | entrave, regles |
| `cremaillere.capot_epaisseur` | 2.5 | mm | Epaisseur de la tole du capot / de la plaque d'habillage. | 1.5 - 5 | libre | entrave |
| `loquet.pene_diametre` | 12 | mm | Diametre du pene rond du loquet. | 10 - 30 | derive | entrave, regles |
| `loquet.engagement` | 10 | mm | Profondeur d'entree du pene dans la gache au-dela de la barre. | 6 - 30 | libre | entrave |
| `loquet.course` | 20 | mm | Course du pene (retrait complet hors de la barre). | 10 - 50 | libre | entrave |
| `loquet.boitier_hauteur` | 32 | mm | Hauteur du boitier forge du loquet. | 30 - 80 | libre | entrave |
| `loquet.loquets_porteurs_min` | 2 | entier | Nombre de loquets supposes porteurs pour la verification (cas d'un oubli de verrouillage). | 1 - 4 | libre | entrave |
| `synchro.mode` | quatre_points | texte | 'deux_cotes' : un arbre transversal par extremite (avant/arriere) ; 'quatre_points' : + arbre longitudinal et renvois d'angle 1:1 (platine horizontale dans les deux directions). | deux_cotes, quatre_points | a_valider | entrave |
| `synchro.arbre_diametre` | 16 | mm | Diametre des arbres de transmission. | 12 - 40 | derive | entrave, regles |
| `synchro.carter_cote` | 60 | mm | Cote du carter forge des renvois d'angle. | 40 - 100 | libre | entrave |
| `jonctions.ratio_tenon` | 0.3333 |  | Epaisseur tenon / epaisseur piece (regle du tiers). | 0.25 - 0.45 | libre | entrave, regles |
| `jonctions.tolerance_ratio_tenon` | 0.05 |  | Ecart admis autour de 1/3 avant alerte. | 0 - 0.15 | libre | parametres |
| `jonctions.tourillon_diametre` | 6 | mm | Diametre des tourillons (<= 1/2 de la piece la plus fine). | 6 - 16 | libre | entrave, regles |
| `jonctions.cheville_diametre` | 10 | mm | Diametre des chevilles de chene. | 6 - 16 | libre | entrave, regles |
| `jonctions.decalage_drawbore` | 1.5 | mm | Decalage du chevillage a tire. | 0.5 - 3 | libre | entrave |
| `jonctions.saillie_tenon_clavete` | 45 | mm | Saillie des tenons a clef hors de la semelle. | 30 - 90 | libre | entrave, regles |
| `jonctions.type_coulisseau_platine` | tenon_traversant_cale | texte | Jonction coulisseau -> platine. | tenon_traversant_cale, tenon_traversant_cheville, tenon_mortaise_borgne | libre | entrave, regles |
| `jonctions.type_fourreau_semelle` | tenon_traversant_cheville | texte | Jonction fourreau -> semelle. | tenon_traversant_cheville, tenon_traversant_cale, tenon_mortaise_borgne | libre | entrave, regles |
| `jonctions.type_traverse_semelle` | tenon_traversant_clavete | texte | Jonction traverse basse -> semelles (demontable). | tenon_traversant_clavete, tenon_traversant_cheville | libre | entrave, regles |
| `jonctions.type_joues_fourreau` | tourillons | texte | Assemblage des deux demi-fourreaux rainures. | tourillons, chevillage | libre | entrave, regles |
| `tolerances.jeu_coulisseau` | 1.5 | mm | Jeu radial coulisseau / fourreau (mouvement du bois + glissement). | 0.5 - 4 | a_valider | entrave |
| `tolerances.jeu_mortaise` | 0.2 | mm | Jeu d'ajustement tenon / mortaise. | 0 - 0.6 | libre | entrave |
| `tolerances.jeu_mortaise_oblongue` | 2 | mm | Jeu mini des mortaises oblongues (dilatation du plateau). | 0.5 - 8 | derive | entrave, regles |
| `tolerances.jeu_axes` | 0.3 | mm | Jeu diametral axes / alesages des ferrures. | 0.1 - 1 | derive | entrave, regles |
| `tolerances.ecart_debattement` | 0.5 | mm | Ecart admis entre debattement demande et crans x pas. | 0 - 5 | libre | parametres |
| `charges.verticale_service` | 1500 | N | Charge verticale de service sur la platine (appui du corps). | 300 - 4000 | a_valider | entrave |
| `charges.traction_manille` | 500 | N | Traction laterale de verification sur une manille. | 100 - 3000 | a_valider | entrave |
| `charges.coef_dynamique` | 1.5 |  | Majoration dynamique des charges. | 1 - 3 | libre | entrave |
| `charges.gamma_m_bois` | 1.3 |  | Coefficient partiel bois massif (EC5). | 1 - 2 | libre | entrave |
| `charges.kmod_bois` | 0.8 |  | Coefficient de modification (classe de service 1, moyen terme). | 0.5 - 1.1 | libre | entrave |
| `charges.gamma_m_metal` | 1.1 |  | Coefficient partiel acier/laiton. | 1 - 1.5 | libre | entrave |
| `charges.gamma_cuir` | 4 |  | Coefficient de securite sur la traction du cuir / de l'ame. | 2 - 8 | libre | entrave |
| `charges.fleche_limite_ratio` | 300 |  | Fleche admissible = portee / ratio. | 150 - 600 | libre | entrave |
| `charges.coef_frottement_sol` | 0.3 |  | Frottement semelle bois / sol (glissement). | 0.1 - 0.8 | libre | entrave |
| `charges.recouvrement_ratio_mini` | 1.5 |  | Recouvrement mini coulisseau/fourreau en position haute, en multiple de la section du coulisseau. | 0.5 - 4 | libre | entrave |
| `charges.marge_mini_ferrures` | 1.5 |  | Marge mini (admissible / sollicitation) exigee des ferrures affinees : en dessous, alerte meme si la verification passe. | 1 - 3 | libre | entrave |
| `charges.g` | 9.81 |  | Acceleration de la pesanteur (m/s2). | 9.8 - 9.82 | libre | entrave |
| `securite.ouverture_rapide_cou` | True | bool | Manille de cou a ouverture rapide sans outil (obligatoire recommande : goupille a anneau ou boucle a degagement). |  | a_valider | entrave |
| `securite.arrondi_contact_peau` | 3 | mm | Rayon mini des tranches et aretes en contact peau. | 1 - 10 | libre | entrave |
| `ancrage.anneaux_sol` | True | bool | Anneaux d'ancrage au sol encastres sous les semelles. |  | a_valider | entrave |
| `ancrage.capacite_point` | 2000 | N | Effort admissible par point d'ancrage (cheville + anneau). | 200 - 10000 | libre | entrave |
| `ancrage.lest` | 0 | kg | Lest additionnel integre (barres d'acier dans la traverse), 0 = aucun. | 0 - 80 | libre | entrave |
| `entrave.platine.longueur` | 800 | mm | Longueur de la platine (axe X). | 600 - 1200 | impose | entrave |
| `entrave.platine.largeur` | 400 | mm | Largeur (profondeur) de la platine (axe Y). | 300 - 600 | impose | entrave |
| `entrave.platine.epaisseur` | 50 | mm | Epaisseur de la platine en noyer massif. | 35 - 80 | a_valider | entrave, regles |
| `entrave.platine.chant_dessus` | conge | texte | Profil du chant superieur (cote corps : doux au toucher). | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | a_valider | entrave |
| `entrave.platine.chant_dessus_taille` | 4 | mm | Rayon / cote du chant superieur. | 0 - 15 | libre | entrave |
| `entrave.platine.chant_dessous` | bec_de_corbin | texte | Profil du chant inferieur : bec-de-corbin (tore + gorge + listel) qui allege visuellement les 50 mm de noyer. | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | a_valider | entrave |
| `entrave.platine.chant_dessous_hauteur` | 31 | mm | Hauteur moulee du chant inferieur (e/phi = 30,9 mm). | 0 - 45 | libre | entrave |
| `entrave.platine.chant_dessous_profondeur` | 14 | mm | Profondeur (retrait) du chant inferieur. | 0 - 25 | libre | entrave |
| `entrave.pied.section` | carre | texte | Section des pieds (fourreaux). | carre, octogonal | a_valider | entrave |
| `entrave.pied.cote` | 100 | mm | Cote du FUT au pied de la colonne : cote du carre ou distance sur plats de l'octogone. | 70 - 180 | a_valider | entrave, regles |
| `entrave.pied.retrait_bord` | 30 | mm | Retrait du CHAPITEAU (partie la plus large) par rapport aux bords de la platine. | 0 - 120 | libre | entrave |
| `entrave.pied.debord_base` | 12 | mm | Debord de la plinthe et de l'abaque du chapiteau sur le fut, par face. | 0 - 30 | libre | entrave |
| `entrave.pied.fuselage` | 3 | mm | Retrait par face du haut du fut (fruit / leger fuselage, 1,5 deg). | 0 - 10 | libre | entrave |
| `entrave.pied.rayon_astragale` | 3 | mm | Rayon du boudin d'astragale sous le chapiteau. | 0 - 8 | libre | entrave |
| `entrave.pied.rayon_cavet` | 9 | mm | Rayon du cavet sous l'abaque du chapiteau. | 0 - 20 | libre | entrave |
| `entrave.pied.rayon_conge_plinthe` | 6 | mm | Rayon du conge de raccord fut / plinthe. | 0 - 15 | libre | entrave |
| `entrave.pied.part_abaque` | 0.35 |  | Part du chapiteau occupee par l'abaque (tailloir). | 0.15 - 0.6 | libre | entrave |
| `entrave.pied.chanfrein_arrete` | 8 | mm | Largeur (face vue) du chanfrein arrete des aretes du fut (section carree) ; 0 = arete vive. | 0 - 20 | a_valider | entrave |
| `entrave.pied.longueur_arret` | 18 | mm | Distance entre l'extremite du fut et le debut du chanfrein. | 5 - 60 | libre | entrave |
| `entrave.pied.type_arret` | droit | texte | Arret du chanfrein : 'droit' (biais a 45 deg) ou 'langue_de_boeuf' (cuilleron concave). | droit, langue_de_boeuf | a_valider | entrave |
| `entrave.fourreau.paroi` | 15 | mm | Epaisseur de paroi du fourreau sur les plats, mesuree au plus fin (haut du fut). | 12 - 40 | libre | entrave |
| `entrave.fourreau.paroi_diagonale_min` | 12 | mm | Paroi mini dans les pans coupes (section octogonale). | 8 - 30 | libre | entrave |
| `entrave.fourreau.jeu_haut` | 10 | mm | Jour entre le haut du fourreau et le dessous de platine au cran 0. | 3 - 30 | libre | entrave |
| `entrave.fourreau.frette_hauteur` | 12 | mm | Hauteur de la bague forgee au pied du fut, au-dessus du conge de plinthe (0 = sans). | 0 - 60 | libre | entrave |
| `entrave.semelle.longueur` | 566 | mm | Longueur des semelles (patins) le long de Y : W x racine(2) (trace ad quadratum, 566 mm) ; elargit le polygone de sustentation. | 400 - 900 | a_valider | entrave |
| `entrave.semelle.largeur` | 140 | mm | Largeur des semelles (axe X) : plinthe + 2 x chant (la plinthe ne deborde plus de la semelle). | 60 - 200 | libre | entrave |
| `entrave.semelle.hauteur` | 54 | mm | Hauteur des semelles = largeur / phi^2 (54 mm). | 40 - 120 | libre | entrave |
| `entrave.semelle.chant` | quart_de_rond | texte | Profil des aretes superieures longues de la semelle. | droit, chanfrein, conge, quart_de_rond, cavet, bec_de_corbin | libre | entrave |
| `entrave.semelle.chant_taille` | 8 | mm | Rayon du chant superieur de la semelle. | 0 - 20 | libre | entrave |
| `entrave.semelle.garde_cavet` | 12 | mm | Hauteur droite laissee sous le cavet des bouts de semelle (le cavet a pour rayon hauteur - garde). | 5 - 40 | libre | entrave |
| `entrave.semelle.profondeur_logement` | 36 | mm | Profondeur du logement ou descend le coulisseau en position basse. | 0 - 80 | libre | entrave |
| `entrave.coulisseau.garde_bas` | 5 | mm | Jour sous le coulisseau au fond du logement, cran 0. | 2 - 30 | libre | entrave |
| `entrave.traverse.largeur` | 60 | mm | Largeur (Y) de la traverse basse longitudinale. | 40 - 100 | libre | entrave |
| `entrave.traverse.hauteur` | 70 | mm | Hauteur (Z) de la traverse basse. | 40 - 120 | libre | entrave |
| `entrave.traverse.garde_sol` | 10 | mm | Jour sous la traverse basse. | 0 - 40 | libre | entrave |
| `entrave.ceinture.active` | True | bool | Ceintures ajourees (bandeaux avant et arriere sous la platine). |  | a_valider | entrave |
| `entrave.ceinture.hauteur` | 80 | mm | Hauteur de la ceinture (e x phi = 81 mm). | 40 - 140 | libre | entrave |
| `entrave.ceinture.epaisseur` | 20 | mm | Epaisseur de la ceinture. | 12 - 40 | libre | entrave |
| `entrave.ceinture.retrait` | 20 | mm | Retrait de la face de la ceinture sous le bord de platine. | 5 - 60 | libre | entrave |
| `entrave.ceinture.nombre_arcades` | 5 | entier | Nombre de baies ajourees par ceinture (impair : baie axiale). | 1 - 12 | libre | entrave |
| `entrave.ceinture.ratio_largeur` | 0.55 |  | Largeur de baie / entraxe des baies. | 0.3 - 0.8 | libre | entrave, regles |
| `entrave.ceinture.marge` | 10 | mm | Bois plein au-dessus et au-dessous des ajours. | 5 - 30 | libre | entrave |
| `entrave.ceinture.chanfrein_bas` | 4 | mm | Chanfrein des aretes inferieures de la ceinture. | 0 - 10 | libre | entrave |
| `entrave.manilles.ecartement_poignets` | 600 | mm | Entraxe des deux manilles de poignets (epaules ouvertes). | 450 - 760 | impose | entrave |
| `entrave.manilles.position_y` | 0 | mm | Decalage en Y de la ligne des manilles par rapport au milieu. | -150 - 150 | libre | entrave |
| `entrave.manilles.pivot_cou` | axe_vertical_chape | texte | Type de pivot de la manille de cou. | axe_vertical_chape, charniere_basculante, rotule | a_valider | entrave, regles |
| `entrave.manilles.pivot_poignets` | axe_vertical_chape | texte | Type de pivot des manilles de poignets. | axe_vertical_chape, charniere_basculante, rotule | libre | entrave, regles |
| `entrave.manilles.hauteur_pivot` | 30 | mm | Hauteur du pivot au-dessus de sa platine forgee. | 15 - 60 | derive | entrave, regles |
| `entrave.pentures.longueur` | 160 | mm | Longueur de chaque branche des pentures d'angle, terminaison comprise. | 60 - 250 | libre | entrave |
| `entrave.pentures.recul_bord` | 3 | mm | Jour entre la terminaison la plus large et le bord de platine. | 0 - 20 | libre | entrave |
| `entrave.pentures.rivets_par_branche` | 3 | entier | Rivets apparents par branche de penture. | 1 - 6 | libre | entrave |

## Grandeurs derivees (calculees par la grammaire Entrave, cran 0)

| Grandeur | Valeur | Unite | Role |
|---|---|---|---|
| `hauteur` | 300 | mm | Dessus de platine = hauteur_mini + cran x pas |
| `hauteurs_crans` | 300, 325, 350, 375, 400, 425, 450 | mm | Hauteurs des 7 positions |
| `coulisseau` | 61 | mm | Section du coulisseau (pied - 2 parois - 2 jeux ; octogone : limite par les pans) |
| `coulisseau_longueur` | 227 | mm | Longueur du coulisseau sous la platine |
| `fourreau_hauteur` | 186 | mm | Hauteur du fourreau (pied visible) |
| `recouvrement_haut` | 67 | mm | Recouvrement coulisseau/fourreau en position haute |
| `pignon_dents` | 16 |  | Dents du pignon = max(dents_mini, course/(pi.m)) |
| `pignon_d_primitif` | 48 | mm | m.z |
| `course_par_tour` | 150.796 | mm | pi.m.z |
| `z_arbre` | 188 | mm | Hauteur des arbres bas |
| `z_loquet` | 175 | mm | Hauteur des penes |
| `trous_crans` | 15, 40, 65, 90, 115, 140, 165 | mm | Trous de crans depuis le bas de la barre de calage |
| `barre_calage_longueur` | 236 | mm | Longueur des cremailleres laterales |
| `dilatation_platine` | 1.77552 | mm | Mouvement transversal calcule de la platine |
| `jeu_mortaise_oblongue` | 2 | mm | Jeu retenu (mortaises arriere) |
| `hauteur_mini_pour_recouvrement` | 315 | mm | hauteur_mini mini pour un recouvrement de 1,5 x section |
| `h_plinthe` | 27.137 | mm | Plinthe = H/phi^4 (style.proportions) |
| `h_fut` | 114.954 | mm | Fut = H/phi |
| `h_chapiteau` | 43.9086 | mm | Chapiteau + astragale = H/phi^3 |
| `a_max` | 124 | mm | Largeur de plinthe et d'abaque = cote + 2 x debord_base |
| `a_fut_haut` | 94 | mm | Largeur du haut du fut = cote - 2 x fuselage |
| `paroi_plats` | 15 | mm | Paroi du fourreau sur les plats (haut du fut) |
| `paroi_diagonale` | 17.2132 | mm | Paroi dans l'arete chanfreinee / le pan coupe |
| `ceinture_baie` | 53.68 | mm | Largeur des baies de la ceinture |
| `ceinture_montant` | 43.92 | mm | Montant de bois entre deux baies |
| `penture_inset` | 29.7298 | mm | Axe des pentures depuis le bord (terminaison + recul) |
| `penture_bande_droite` | 76 | mm | Partie droite des pentures (rivets) |
| `coussin_cellules` | 47 |  | Cellules du matelassage en losange |

User Parameters a expression liee crees en plus dans Fusion :

| Nom | Expression | Unite | Commentaire |
|---|---|---|---|
| `neo_course_courante` | `neo_cremaillere_cran_courant * neo_cremaillere_pas` | mm | Course au cran courant = cran x pas (pilote le deplacement des corps mobiles) |
| `neo_hauteur_platine` | `neo_cremaillere_hauteur_mini + neo_course_courante` | mm | Hauteur du dessus de platine = hauteur_mini + cran x pas |
| `neo_debattement` | `neo_cremaillere_hauteur_maxi - neo_cremaillere_hauteur_mini` | mm | Debattement total |
| `neo_pignon_dents` | `16` |  | Nombre de dents du pignon (calcule) |
| `neo_pignon_d_primitif` | `neo_cremaillere_module * neo_pignon_dents` | mm | Diametre primitif du pignon = m.z |
| `neo_coulisseau_section` | `61 mm` | mm | Section du coulisseau (calculee) |
| `neo_z_arbre` | `188 mm` | mm | Hauteur des arbres de synchronisation |
| `neo_pied_plinthe` | `27.14 mm` | mm | Hauteur de plinthe (nombre_or) |
| `neo_pied_fut` | `114.95 mm` | mm | Hauteur du fut (nombre_or) |
| `neo_pied_chapiteau` | `43.91 mm` | mm | Hauteur du chapiteau, astragale comprise (nombre_or) |

## Overrides

- Par typologie : `OVERRIDES_TYPOLOGIE` dans `parametres.py` (fusion profonde).
- Par fichier : copier `neogothique/parametres_neogothique.exemple.json` en `neogothique/parametres_neogothique.json` (charge automatiquement : `commun` puis `typologies.<nom>`).
- Par code : `Parametres.pour_typologie('entrave', {'cremaillere.pas': 30.0})` (cles pointees ou dict imbrique).
