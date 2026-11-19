# Regles materiaux -> geometrie

Genere par `outils/generer_docs.py`. Chaque entree de catalogue porte un champ `regles` declaratif ; `equinox.regles.changer_materiau(params, categorie, cle)` les applique, recalcule en cascade les jonctions (tourillons, tenons, mortaises, inserts) et renvoie la liste des ajustements.

Statuts d'ajustement : `AJUSTE` (parametre libre/derive modifie), `AJUSTE (valeur imposee modifiee, a confirmer)` (une valeur donnee par Fabien a du changer), `BLOQUE` (option `forcer_imposes=False`, ou au lancement d'une grammaire : la valeur imposee est gardee et le conflit signale), `ALERTE` (information sans modification).

## Calculs du moteur

| Calcul | Formule / regle |
|---|---|
| `section_equivalente` | d = d_frene x max((E_frene/E)^1/4, (MOR_frene/MOR)^1/3, 1) arrondi au mm sup. (rigidite en flexion E.I ~ E.d^4, resistance M/W ~ MOR.d^3) ; jamais de reduction |
| `rayon_cintrage` | lamelle-colle : R >= ratio_lamelle x e_lamelle ; vapeur : R >= ratio_vapeur x section_noeud ; arrondi 10 mm ; le rayon n'est jamais diminue |
| `copier` | prend la valeur de la propriete du catalogue (rembourrage, fixation, rayon de bord) |
| `fixer` | impose une valeur (option `si_parmi`) |
| `tourillon` | d = section_noeud / 5 -> standard 6/8/10/12/14 |
| `longueur_tourillon` | L = 5 d |
| `tenon` | e = section_noeud / 3 |
| `mortaise` | p = 0,8 x section_noeud |
| `longueur_insert` | 20 mm si densite >= 650 kg/m3, sinon 25 mm |
| `section_metal_equivalente` | d = d_ref x (Re_ref/Re)^1/3 |
| `capacite_lest` | kg/m = (cote - 2 paroi)^2 x densite x taux_remplissage -> longueur de tube requise |
| `alerte` | message |

## Bois

### `frene` - Frene europeen

Proprietes : nom_latin = Fraxinus excelsior ; densite = 680.0 ; module_elasticite = 12310.0 ; resistance_flexion = 103.6 ; aptitude_cintrage = 5 ; ratio_vapeur = 6.0 ; ratio_lamelle = 80.0 ; tenue_vis = 3 ; teinte = clair, blond ; source = The Wood Database (wood-database.com), consulte le 18/11/2026

Notes : Essence de reference Equinox. Excellent au cintrage vapeur, resilient aux chocs. Vis : avant-trou obligatoire, cirer les vis.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

### `frene_blanc` - Frene blanc d'Amerique

Proprietes : nom_latin = Fraxinus americana ; densite = 675.0 ; module_elasticite = 12000.0 ; resistance_flexion = 103.5 ; aptitude_cintrage = 5 ; ratio_vapeur = 6.0 ; ratio_lamelle = 80.0 ; tenue_vis = 3 ; teinte = clair ; source = USDA FPL Wood Handbook FPL-GTR-282 (2021) tab. 5-3a, via The Wood Database

Notes : Equivalent americain ; espece menacee (agrile du frene) : verifier la provenance.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

### `chene` - Chene pedoncule

Proprietes : nom_latin = Quercus robur ; densite = 675.0 ; module_elasticite = 10600.0 ; resistance_flexion = 97.1 ; aptitude_cintrage = 4 ; ratio_vapeur = 7.0 ; ratio_lamelle = 90.0 ; tenue_vis = 4 ; teinte = blond a brun clair, maillure ; source = The Wood Database (wood-database.com), consulte le 18/11/2026

Notes : Tanins : tache au contact de l'acier non inox humide ; inox 316 ou laiton conseilles.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)
- `inox.nuance` <- `fixer` {'valeur': 'inox_316', 'si_parmi': ['inox_304', 'acier_s235']} : tanins du chene : eviter l'acier et l'inox 304 au contact (taches noires)

### `noyer` - Noyer commun

Proprietes : nom_latin = Juglans regia ; densite = 640.0 ; module_elasticite = 10810.0 ; resistance_flexion = 111.5 ; aptitude_cintrage = 4 ; ratio_vapeur = 7.0 ; ratio_lamelle = 90.0 ; tenue_vis = 4 ; teinte = brun, contraste fort avec cuir cognac ; source = The Wood Database (wood-database.com), consulte le 18/11/2026

Notes : Rompt avec le 'frene clair' de la gamme : variante sombre.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)
- `(alerte)` <- `alerte` {'message': "noyer : teinte foncee, l'identite 'frene clair' Equinox change ; valider le cuir"} : esthetique

### `hetre` - Hetre europeen

Proprietes : nom_latin = Fagus sylvatica ; densite = 710.0 ; module_elasticite = 14310.0 ; resistance_flexion = 110.1 ; aptitude_cintrage = 5 ; ratio_vapeur = 5.0 ; ratio_lamelle = 70.0 ; tenue_vis = 4 ; teinte = clair rosé ; source = The Wood Database (wood-database.com), consulte le 18/11/2026

Notes : Tres bon cintrage (chaises Thonet). Retrait important : sensible aux variations d'humidite.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

### `erable_sycomore` - Erable sycomore

Proprietes : nom_latin = Acer pseudoplatanus ; densite = 615.0 ; module_elasticite = 9920.0 ; resistance_flexion = 98.1 ; aptitude_cintrage = 3 ; ratio_vapeur = 10.0 ; ratio_lamelle = 100.0 ; tenue_vis = 4 ; teinte = tres clair, blanc creme ; source = The Wood Database (wood-database.com), consulte le 18/11/2026

Notes : Moins rigide que le frene (-19 % de MOE) : sections a augmenter.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

### `erable_dur` - Erable dur (a sucre)

Proprietes : nom_latin = Acer saccharum ; densite = 705.0 ; module_elasticite = 12620.0 ; resistance_flexion = 109.0 ; aptitude_cintrage = 3 ; ratio_vapeur = 10.0 ; ratio_lamelle = 100.0 ; tenue_vis = 5 ; teinte = tres clair ; source = USDA FPL Wood Handbook FPL-GTR-282 (2021) tab. 5-3a, via The Wood Database

Notes : Rigide et dur ; cintrage vapeur moyen, preferer le lamelle-colle.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

### `noyer_noir` - Noyer noir d'Amerique

Proprietes : nom_latin = Juglans nigra ; densite = 610.0 ; module_elasticite = 11590.0 ; resistance_flexion = 100.7 ; aptitude_cintrage = 4 ; ratio_vapeur = 7.0 ; ratio_lamelle = 90.0 ; tenue_vis = 4 ; teinte = brun chocolat ; source = USDA FPL Wood Handbook FPL-GTR-282 (2021) tab. 5-3a, via The Wood Database

Notes : Variante sombre.

- `bois.section_noeud` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 50.0} : conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud
- `bois.section_extremite` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 30.0} : conserver rigidite et resistance du frene de reference aux extremites
- `bois.section_entre_noeuds` <- `section_equivalente` {'reference': 'frene', 'valeur_reference': 40.0} : conserver rigidite et resistance du frene de reference entre noeuds
- `bois.rayon_courbure_min` <- `rayon_cintrage`  : rayon mini de cintrage propre a l'essence et a la methode
- `jonctions.longueur_insert` <- `longueur_insert`  : longueur d'insert filete selon la densite (arrachement)

## Garnissages

### `cuir_classique_pleine_fleur` - Cuir classique pleine fleur

Proprietes : famille = cuir ; coloris = ['noir', 'cognac', 'havane', 'vert_bouteille', 'bleu_nuit'] ; coloris_defaut = cognac ; epaisseur_matiere = 1.8 ; epaisseur_plage = (1.5, 2.0) ; abrasion = 8 ; abrasion_martindale = None ; abrasion_note = cuir : EN ISO 17076-1 / Veslic, pas de Martindale ; 'elevee' -> 8/10 ; cout_m2 = eleve ; entretien = patine avec le temps ; nettoyant doux pH neutre + nourrissant 2 a 4 fois/an ; eviter alcool et chlore ; desinfection = limitee (produits doux) ; finition semi-aniline protegee conseillee ; epaisseur_rembourrage_recommandee = 30.0 ; methode_fixation = agrafage_sous_plateau ; finition_bords = ourlets_cousus ; rayon_bord_min = 12.0

Notes : Revetement de reference Equinox (cognac). Valeur de rembourrage de reference des autres familles.

- `garnissage.couleur` <- `coloris_disponible`  : coloris non disponible dans cette famille : coloris par defaut de la famille
- `garnissage.epaisseur_rembourrage` <- `copier` {'propriete': 'epaisseur_rembourrage_recommandee'} : le cuir classique, epais et tenu, se tend sur 30 mm de mousse HR
- `garnissage.methode_fixation` <- `copier` {'propriete': 'methode_fixation'} : agrafage sous le plateau (support contreplaque)
- `garnissage.finition_bords` <- `copier` {'propriete': 'finition_bords'} : finition des bords propre a la famille
- `garnissage.rayon_bord` <- `copier` {'propriete': 'rayon_bord_min'} : rayon mini des aretes pour ne pas casser la fleur

### `cuir_vegan` - Cuir vegan (sans cuir veritable)

Proprietes : famille = cuir_vegan ; coloris = ['noir', 'blanc', 'cognac', 'vert_olive', 'bordeaux'] ; coloris_defaut = cognac ; epaisseur_matiere = 1.35 ; epaisseur_plage = (1.2, 1.5) ; abrasion = 5 ; abrasion_martindale = 30000 ; abrasion_note = 'moyenne' -> 5/10 ; Martindale indicatif a valider ; cout_m2 = moyen ; entretien = entretien facile : chiffon humide + savon doux ; pas de nourrissant ; desinfection = desinfectants doux sans solvant ; epaisseur_rembourrage_recommandee = None ; ecart_rembourrage = 5.0 ; methode_fixation = agrafage_sous_plateau ; finition_bords = ourlets_cousus ; rayon_bord_min = 10.0

Notes : Aucun cuir veritable. Moins de tenue au molletonnage que le cuir : rembourrage +5 mm.

- `garnissage.couleur` <- `coloris_disponible`  : coloris non disponible dans cette famille : coloris par defaut de la famille
- `garnissage.epaisseur_rembourrage` <- `rembourrage_relatif` {'reference': 'cuir_classique_pleine_fleur', 'ecart': 5.0} : moins de tenue au molletonnage : rembourrage du cuir classique + 5 mm
- `garnissage.methode_fixation` <- `copier` {'propriete': 'methode_fixation'} : agrafage sous le plateau
- `garnissage.finition_bords` <- `copier` {'propriete': 'finition_bords'} : finition des bords propre a la famille
- `garnissage.rayon_bord` <- `copier` {'propriete': 'rayon_bord_min'} : matiere souple, aretes un peu plus vives possibles

### `tissu_krypton` - Tissu Krypton (tissu technique dense, type velours cotele renforce)

Proprietes : famille = tissu ; coloris = ['noir', 'gris_anthracite', 'bordeaux', 'bleu_marine'] ; coloris_defaut = noir ; epaisseur_matiere = 2.5 ; epaisseur_plage = (2.0, 3.0) ; abrasion = 8 ; abrasion_martindale = 60000 ; abrasion_note = 'elevee' -> 8/10 ; Martindale indicatif a valider ; cout_m2 = bas_moyen ; entretien = lavable ; brossage dans le sens des cotes ; detachage a l'eau savonneuse ; desinfection = absorbe les fluides : membrane PU sous le tissu recommandee ; epaisseur_rembourrage_recommandee = 40.0 ; methode_fixation = agrafage_ou_scratch ; finition_bords = rembordage_sans_couture ; rayon_bord_min = 20.0

Notes : Tissu technique dense type velours cotele renforce, utilise en ameublement et habillement technique. Cotes a orienter dans le sens de la longueur.

- `garnissage.couleur` <- `coloris_disponible`  : coloris non disponible dans cette famille : coloris par defaut de la famille
- `garnissage.epaisseur_rembourrage` <- `copier` {'propriete': 'epaisseur_rembourrage_recommandee'} : tissu dense : rembourrage plus epais (40 mm)
- `garnissage.methode_fixation` <- `copier` {'propriete': 'methode_fixation'} : fixation par agrafage ou par bande auto-agrippante (scratch)
- `garnissage.finition_bords` <- `copier` {'propriete': 'finition_bords'} : finition des bords propre a la famille
- `garnissage.rayon_bord` <- `copier` {'propriete': 'rayon_bord_min'} : le velours cotele s'ecrase et luit sur les aretes : rayon >= 20 mm
- `(alerte)` <- `alerte_si` {'parametre': 'garnissage.coutures_sur_courbes', 'valeur': True, 'message': 'tissu Krypton : pas de couture apparente recommandee sur les courbes'} : les coutures apparentes vrillent sur les courbes
- `(alerte)` <- `alerte` {'message': 'Recommandation : membrane PU impermeable sous le tissu Krypton'} : hygiene

### `cuir_synthetique_hq` - Cuir synthetique haute qualite (polyurethane haute densite)

Proprietes : famille = cuir_synthetique ; coloris = ['noir', 'cognac', 'gris'] ; coloris_defaut = cognac ; epaisseur_matiere = 1.1 ; epaisseur_plage = (1.0, 1.2) ; abrasion = 9 ; abrasion_martindale = 100000 ; abrasion_note = 'tres elevee' -> 9/10 ; Martindale indicatif a valider ; cout_m2 = moyen ; entretien = resistant a l'eau ; nettoyage a l'eau savonneuse ; desinfection = resistant aux desinfectants usuels (ammoniums quaternaires, alcool dilue) ; epaisseur_rembourrage_recommandee = 30.0 ; methode_fixation = collage_et_agrafage ; finition_bords = rembordage_colle ; rayon_bord_min = 6.0 ; compatible_toutes_geometries = True

Notes : Compatible avec toutes les geometries (souple, colle sur les courbes).

- `garnissage.couleur` <- `coloris_disponible`  : coloris non disponible dans cette famille : coloris par defaut de la famille
- `garnissage.epaisseur_rembourrage` <- `copier` {'propriete': 'epaisseur_rembourrage_recommandee'} : PU haute densite : tenue proche du cuir, 30 mm
- `garnissage.methode_fixation` <- `copier` {'propriete': 'methode_fixation'} : collage + agrafage
- `garnissage.finition_bords` <- `copier` {'propriete': 'finition_bords'} : finition des bords propre a la famille
- `garnissage.rayon_bord` <- `copier` {'propriete': 'rayon_bord_min'} : compatible toutes geometries : aretes vives possibles

### `tissu_technique_enduit` - Tissu technique enduit PU (type medical)

Proprietes : famille = tissu_enduit ; coloris = ['noir', 'cognac'] ; coloris_defaut = noir ; epaisseur_matiere = 0.7 ; epaisseur_plage = (0.6, 0.9) ; abrasion = 9 ; abrasion_martindale = 100000 ; abrasion_note = 'tres elevee' -> 9/10 ; cout_m2 = moyen ; entretien = lessivable ; desinfection = desinfectants hospitaliers ; epaisseur_rembourrage_recommandee = 30.0 ; methode_fixation = agrafage_sous_plateau ; finition_bords = rembordage_sans_couture ; rayon_bord_min = 8.0

Notes : Le plus hygienique ; aspect moins noble.

- `garnissage.couleur` <- `coloris_disponible`  : coloris non disponible dans cette famille : coloris par defaut de la famille
- `garnissage.epaisseur_rembourrage` <- `copier` {'propriete': 'epaisseur_rembourrage_recommandee'} : enduit fin, tenue type cuir
- `garnissage.methode_fixation` <- `copier` {'propriete': 'methode_fixation'} : agrafage sous le plateau
- `garnissage.finition_bords` <- `copier` {'propriete': 'finition_bords'} : finition des bords propre a la famille
- `garnissage.rayon_bord` <- `copier` {'propriete': 'rayon_bord_min'} : aretes vives possibles

## Metaux et lests

### `inox_316` - Inox austenitique 316L (1.4404)

Proprietes : usage = structure ; densite = 8000.0 ; module_elasticite = 200000.0 ; limite_elastique = 200.0 ; sections_standards = {'rond_plein': [8, 10, 12, 14, 16, 20], 'tube_rond': ['12x1', '12x1.5', '12x2', '16x2', '20x2'], 'tube_carre': ['40x40x2', '40x40x3'], 'toles': [1.5, 2, 3, 4]} ; traitements = ['brosse grain 240', 'electropolissage', 'passivation', 'microbillage'] ; source = EN 10088-3 (barres, etat recuit)

Notes : Recommande : resiste aux desinfectants chlores et aux fluides corporels.

- (aucune regle propre)

### `inox_304` - Inox austenitique 304 (1.4301)

Proprietes : usage = structure ; densite = 7900.0 ; module_elasticite = 193000.0 ; limite_elastique = 190.0 ; sections_standards = {'rond_plein': [8, 10, 12, 14, 16, 20], 'tube_rond': ['12x1', '12x1.5', '16x1.5'], 'tube_carre': ['40x40x1.5', '40x40x2'], 'toles': [1.5, 2, 3]} ; traitements = ['brosse', 'electropolissage', 'passivation'] ; source = EN 10088-3 (barres, etat recuit)

Notes : Piqures possibles avec les desinfectants chlores.

- `(alerte)` <- `alerte` {'message': 'inox 304 : proscrire les desinfectants chlores, rincer ; 316L conseille'} : corrosion par piqures
- `inox.diametre_axe_pivot` <- `section_metal_equivalente` {'reference': 'inox_316', 'valeur_reference': 16.0} : limite elastique plus faible : axe de pivot a recalculer

### `acier_s235` - Acier S235 (zingue + peint)

Proprietes : usage = structure ; densite = 7850.0 ; module_elasticite = 210000.0 ; limite_elastique = 235.0 ; sections_standards = {'rond_plein': [10, 12, 16, 20], 'tube_carre': ['40x40x2', '40x40x3', '40x40x4']} ; traitements = ['zingage + thermolaquage', 'noircissage (interieur seulement)'] ; source = EN 10025-2

Notes : A reserver aux pieces cachees (ame de traverse).

- `(alerte)` <- `alerte` {'message': 'acier : traitement anticorrosion obligatoire, ne pas laisser apparent'} : corrosion

### `laiton_cw614n` - Laiton de decolletage CuZn39Pb3 (CW614N)

Proprietes : usage = decor ; densite = 8470.0 ; module_elasticite = 97000.0 ; limite_elastique = 250.0 ; sections_standards = {'rond_plein': [30, 40, 45, 50], 'toles': [1, 2, 3]} ; traitements = ['poli + vernis', 'brosse', 'patine naturelle', 'PVD'] ; source = EN 12164 (etat R430, ordre de grandeur)

Notes : Contient du plomb (decolletage) : CW510L sans plomb si contact cutane prolonge.

- (aucune regle propre)

### `laiton_cw510l` - Laiton sans plomb CuZn42 (CW510L)

Proprietes : usage = decor ; densite = 8400.0 ; module_elasticite = 100000.0 ; limite_elastique = 250.0 ; sections_standards = {'rond_plein': [30, 40, 50]} ; traitements = ['poli + vernis', 'brosse'] ; source = EN 12164 (ordre de grandeur)

Notes : Option contact cutane.

- (aucune regle propre)

### `plomb` - Plomb coule / barre

Proprietes : usage = lest ; densite = 11340.0 ; taux_remplissage = 1.0

Notes : Toxique a l'usinage ; enfermer hermetiquement (bouchons soudes).

- `(alerte)` <- `capacite_lest`  : capacite du tube selon densite

### `acier_plein` - Barre acier pleine 36x36 (dans tube 40x40x2)

Proprietes : usage = lest ; densite = 7850.0 ; taux_remplissage = 1.0

Notes : Sans toxicite.

- `(alerte)` <- `capacite_lest`  : capacite du tube selon densite

### `grenaille_acier` - Grenaille d'acier en vrac

Proprietes : usage = lest ; densite = 7850.0 ; taux_remplissage = 0.58

Notes : Masse apparente ~4,5 t/m3 ; bruit si mal tassee : noyer dans resine.

- `(alerte)` <- `capacite_lest`  : capacite du tube selon densite

## Attaches

### `tourillon_hetre` - Tourillon hetre cannele

Proprietes : famille = jonction_bois ; diametres = [6, 8, 10, 12, 14] ; capacite_service = 1500.0 ; dimensionnement = d ~ section/5 arrondi au standard ; longueur >= 5 d ; 2 tourillons mini par jonction

- `jonctions.diametre_tourillon` <- `tourillon`  : d = section_noeud / 5
- `jonctions.longueur_tourillon` <- `longueur_tourillon`  : L = 5 d

### `tenon_mortaise` - Tenon-mortaise colle (+ cheville)

Proprietes : famille = jonction_bois ; capacite_service = 3000.0 ; dimensionnement = tenon = section/3 ; profondeur = 0,8 x section ; cheville d 8 decalee 1 mm (tire-fort)

- `jonctions.epaisseur_tenon` <- `tenon`  : regle du tiers
- `jonctions.profondeur_mortaise` <- `mortaise`  : 0,8 x section au noeud

### `vis_bois_inox` - Vis bois inox A4 tete fraisee

Proprietes : famille = quincaillerie ; diametres = [4, 5, 6] ; capacite_service = 800.0 ; dimensionnement = avant-trou 70 % du d dans les feuillus durs ; ancrage >= 8 d ; jamais en bois de bout seul

- (aucune regle propre)

### `insert_filete_m8` - Insert filete inox M8 a visser (type Ensat)

Proprietes : famille = quincaillerie ; filetage = M8 ; capacite_service = 2500.0 ; dimensionnement = longueur 20 mm dans densite >= 650 kg/m3, 25 mm en dessous ; colle epoxy conseillee

- `jonctions.longueur_insert` <- `longueur_insert`  : selon densite

### `vis_barillet_m8` - Boulon + ecrou barillet M8 (cross-dowel)

Proprietes : famille = quincaillerie ; capacite_service = 4000.0 ; dimensionnement = barillet d 10 a >= 2,5 d du bout ; demontable (traverse / pieds)

- (aucune regle propre)

### `glissiere_inox_genou` - Glissiere inox a billes + doigt d'indexage

Proprietes : famille = mecanisme ; course = 150.0 ; capacite_service = 1200.0 ; pas_indexage = 25.0 ; dimensionnement = charge par glissiere >= charge genou x coef dynamique ; doigt d'indexage a ressort

- (aucune regle propre)

### `pivot_crans` - Pivot d'helice : axe inox + bague bronze + doigt d'indexage a ressort

Proprietes : famille = mecanisme ; capacite_service = 2000.0 ; dimensionnement = axe d >= 16 ; 1 trou d'indexage par cran ; bague bronze frettee dans le pied

- (aucune regle propre)

### `oeillet_inox_8` - Oeillet inox A4 fil 8 mm sur platine 2 mm (soude, teste)

Proprietes : famille = ancrage ; fil = 8.0 ; capacite_service = 2000.0 ; dimensionnement = platine vissee 4 x vis 5 + insert M8 traversant ; CMU fabricant >= effort calcule

- (aucune regle propre)

### `anneau_inox_8` - Anneau inox A4 fil 8 mm, di 40, sur pontet + tige filetee M8 traversante

Proprietes : famille = ancrage ; fil = 8.0 ; capacite_service = 2500.0 ; dimensionnement = tige traversant la traverse et le tube, ecrou borgne + rondelle cote oppose

- (aucune regle propre)

## Revetements : synthese

Echelle d'abrasion Equinox 1-10 : faible = 1-3 ; moyenne = 4-6 ; elevee = 7-8 ; tres_elevee = 9-10. Couts au m2 par categorie (sans prix) : bas, bas_moyen, moyen, eleve.

| Cle | Famille | Coloris | Epaisseur (plage) | Abrasion /10 (Martindale) | Cout m2 | Rembourrage | Fixation | Bords |
|---|---|---|---|---|---|---|---|---|
| `cuir_classique_pleine_fleur` | cuir | noir, cognac, havane, vert_bouteille, bleu_nuit | 1.8 (1.5-2) mm | 8 (n/a) | eleve | 30 mm | agrafage_sous_plateau | ourlets_cousus |
| `cuir_vegan` | cuir_vegan | noir, blanc, cognac, vert_olive, bordeaux | 1.35 (1.2-1.5) mm | 5 (30000) | moyen | 35 mm | agrafage_sous_plateau | ourlets_cousus |
| `tissu_krypton` | tissu | noir, gris_anthracite, bordeaux, bleu_marine | 2.5 (2-3) mm | 8 (60000) | bas_moyen | 40 mm | agrafage_ou_scratch | rembordage_sans_couture |
| `cuir_synthetique_hq` | cuir_synthetique | noir, cognac, gris | 1.1 (1-1.2) mm | 9 (100000) | moyen | 30 mm | collage_et_agrafage | rembordage_colle |
| `tissu_technique_enduit` | tissu_enduit | noir, cognac | 0.7 (0.6-0.9) mm | 9 (100000) | moyen | 30 mm | agrafage_sous_plateau | rembordage_sans_couture |

Alias conserves : `cuir_pleine_fleur` -> `cuir_classique_pleine_fleur`, `cuir_synthetique_pu` -> `cuir_synthetique_hq`

## Ajustements calcules sur le banc Flore (assise maintenue a 700 mm)

### garnissage -> `cuir_classique_pleine_fleur`

```
Aucun ajustement.
```

### garnissage -> `cuir_vegan`

```
- AJUSTE garnissage.materiau : cuir_classique_pleine_fleur -> cuir_vegan  [garnissage] changement de materiau demande
- AJUSTE garnissage.epaisseur_rembourrage : 30 mm -> 35 mm  [garnissage:cuir_vegan] moins de tenue au molletonnage : rembourrage du cuir classique + 5 mm (rembourrage cuir_classique_pleine_fleur 30 mm +5 mm)
- AJUSTE garnissage.rayon_bord : 12 mm -> 10 mm  [garnissage:cuir_vegan] matiere souple, aretes un peu plus vives possibles (valeur catalogue 'rayon_bord_min')
- AJUSTE dimensions.hauteur_structure : 652 mm -> 647 mm  [geometrie] hauteur de structure recalculee pour garder la hauteur d'assise (assise maintenue a 700 mm : 700 - 35 (rembourrage) - 18 (support))
```

### garnissage -> `tissu_krypton`

```
- AJUSTE garnissage.materiau : cuir_classique_pleine_fleur -> tissu_krypton  [garnissage] changement de materiau demande
- AJUSTE (valeur imposee modifiee, a confirmer) garnissage.couleur : cognac -> noir  [garnissage:tissu_krypton] coloris non disponible dans cette famille : coloris par defaut de la famille ('cognac' indisponible (coloris : noir, gris_anthracite, bordeaux, bleu_marine))
- AJUSTE garnissage.epaisseur_rembourrage : 30 mm -> 40 mm  [garnissage:tissu_krypton] tissu dense : rembourrage plus epais (40 mm) (valeur catalogue 'epaisseur_rembourrage_recommandee')
- AJUSTE garnissage.methode_fixation : agrafage_sous_plateau -> agrafage_ou_scratch  [garnissage:tissu_krypton] fixation par agrafage ou par bande auto-agrippante (scratch) (valeur catalogue 'methode_fixation')
- AJUSTE garnissage.finition_bords : ourlets_cousus -> rembordage_sans_couture  [garnissage:tissu_krypton] finition des bords propre a la famille (valeur catalogue 'finition_bords')
- AJUSTE garnissage.rayon_bord : 12 mm -> 20 mm  [garnissage:tissu_krypton] le velours cotele s'ecrase et luit sur les aretes : rayon >= 20 mm (valeur catalogue 'rayon_bord_min')
- ALERTE [garnissage:tissu_krypton] tissu Krypton : pas de couture apparente recommandee sur les courbes
- ALERTE [garnissage:tissu_krypton] Recommandation : membrane PU impermeable sous le tissu Krypton
- AJUSTE dimensions.hauteur_structure : 652 mm -> 642 mm  [geometrie] hauteur de structure recalculee pour garder la hauteur d'assise (assise maintenue a 700 mm : 700 - 40 (rembourrage) - 18 (support))
```

### garnissage -> `cuir_synthetique_hq`

```
- AJUSTE garnissage.materiau : cuir_classique_pleine_fleur -> cuir_synthetique_hq  [garnissage] changement de materiau demande
- AJUSTE garnissage.methode_fixation : agrafage_sous_plateau -> collage_et_agrafage  [garnissage:cuir_synthetique_hq] collage + agrafage (valeur catalogue 'methode_fixation')
- AJUSTE garnissage.finition_bords : ourlets_cousus -> rembordage_colle  [garnissage:cuir_synthetique_hq] finition des bords propre a la famille (valeur catalogue 'finition_bords')
- AJUSTE garnissage.rayon_bord : 12 mm -> 6 mm  [garnissage:cuir_synthetique_hq] compatible toutes geometries : aretes vives possibles (valeur catalogue 'rayon_bord_min')
```

### garnissage -> `tissu_technique_enduit`

```
- AJUSTE garnissage.materiau : cuir_classique_pleine_fleur -> tissu_technique_enduit  [garnissage] changement de materiau demande
- AJUSTE garnissage.finition_bords : ourlets_cousus -> rembordage_sans_couture  [garnissage:tissu_technique_enduit] finition des bords propre a la famille (valeur catalogue 'finition_bords')
- AJUSTE garnissage.rayon_bord : 12 mm -> 8 mm  [garnissage:tissu_technique_enduit] aretes vives possibles (valeur catalogue 'rayon_bord_min')
```

## Autres changements de materiau sur le banc Flore

### bois -> `erable_sycomore`

```
- AJUSTE bois.essence : frene -> erable_sycomore  [bois] changement de materiau demande
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_noeud : 50 mm -> 53 mm  [bois:erable_sycomore] conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud (facteur rigidite 1.055, resistance 1.018 sur 50 mm (frene))
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_extremite : 30 mm -> 32 mm  [bois:erable_sycomore] conserver rigidite et resistance du frene de reference aux extremites (facteur rigidite 1.055, resistance 1.018 sur 30 mm (frene))
- AJUSTE bois.section_entre_noeuds : 40 mm -> 43 mm  [bois:erable_sycomore] conserver rigidite et resistance du frene de reference entre noeuds (facteur rigidite 1.055, resistance 1.018 sur 40 mm (frene))
- AJUSTE jonctions.longueur_insert : 20 mm -> 25 mm  [bois:erable_sycomore] longueur d'insert filete selon la densite (arrachement) (densite 615 kg/m3)
- AJUSTE jonctions.epaisseur_tenon : 17 mm -> 18 mm  [jonctions] regle du tiers (section_noeud / 3)
- AJUSTE jonctions.profondeur_mortaise : 40 mm -> 42 mm  [jonctions] 0,8 x section au noeud (0,8 x section_noeud)
```

### bois -> `chene`

```
- AJUSTE bois.essence : frene -> chene  [bois] changement de materiau demande
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_noeud : 50 mm -> 52 mm  [bois:chene] conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud (facteur rigidite 1.038, resistance 1.022 sur 50 mm (frene))
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_extremite : 30 mm -> 32 mm  [bois:chene] conserver rigidite et resistance du frene de reference aux extremites (facteur rigidite 1.038, resistance 1.022 sur 30 mm (frene))
- AJUSTE bois.section_entre_noeuds : 40 mm -> 42 mm  [bois:chene] conserver rigidite et resistance du frene de reference entre noeuds (facteur rigidite 1.038, resistance 1.022 sur 40 mm (frene))
- AJUSTE jonctions.profondeur_mortaise : 40 mm -> 42 mm  [jonctions] 0,8 x section au noeud (0,8 x section_noeud)
```

### bois -> `noyer`

```
- AJUSTE bois.essence : frene -> noyer  [bois] changement de materiau demande
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_noeud : 50 mm -> 52 mm  [bois:noyer] conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud (facteur rigidite 1.033, resistance 0.976 sur 50 mm (frene))
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_extremite : 30 mm -> 31 mm  [bois:noyer] conserver rigidite et resistance du frene de reference aux extremites (facteur rigidite 1.033, resistance 0.976 sur 30 mm (frene))
- AJUSTE bois.section_entre_noeuds : 40 mm -> 42 mm  [bois:noyer] conserver rigidite et resistance du frene de reference entre noeuds (facteur rigidite 1.033, resistance 0.976 sur 40 mm (frene))
- AJUSTE jonctions.longueur_insert : 20 mm -> 25 mm  [bois:noyer] longueur d'insert filete selon la densite (arrachement) (densite 640 kg/m3)
- ALERTE [bois:noyer] noyer : teinte foncee, l'identite 'frene clair' Equinox change ; valider le cuir
- AJUSTE jonctions.profondeur_mortaise : 40 mm -> 42 mm  [jonctions] 0,8 x section au noeud (0,8 x section_noeud)
```

### bois -> `hetre`

```
- AJUSTE bois.essence : frene -> hetre  [bois] changement de materiau demande
```

### inox -> `inox_304`

```
- AJUSTE inox.nuance : inox_316 -> inox_304  [inox] changement de materiau demande
- ALERTE [inox:inox_304] inox 304 : proscrire les desinfectants chlores, rincer ; 316L conseille
- AJUSTE inox.diametre_axe_pivot : 16 mm -> 17 mm  [inox:inox_304] limite elastique plus faible : axe de pivot a recalculer (Re 200 -> 190 MPa)
```

### lest -> `grenaille_acier`

```
- AJUSTE traverse.materiau_lest : plomb -> grenaille_acier  [lest] changement de materiau demande
- ALERTE [lest:grenaille_acier] lest grenaille_acier : 5.90 kg/m dans tube 40x40 ; 18 kg exigent 3050 mm de tube rempli
```

### lest -> `acier_plein`

```
- AJUSTE traverse.materiau_lest : plomb -> acier_plein  [lest] changement de materiau demande
- ALERTE [lest:acier_plein] lest acier_plein : 10.17 kg/m dans tube 40x40 ; 18 kg exigent 1769 mm de tube rempli
```

### bois -> `erable_sycomore` en cintrage vapeur

```
- AJUSTE bois.essence : frene -> erable_sycomore  [bois] changement de materiau demande
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_noeud : 50 mm -> 53 mm  [bois:erable_sycomore] conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud (facteur rigidite 1.055, resistance 1.018 sur 50 mm (frene))
- AJUSTE (valeur imposee modifiee, a confirmer) bois.section_extremite : 30 mm -> 32 mm  [bois:erable_sycomore] conserver rigidite et resistance du frene de reference aux extremites (facteur rigidite 1.055, resistance 1.018 sur 30 mm (frene))
- AJUSTE bois.section_entre_noeuds : 40 mm -> 43 mm  [bois:erable_sycomore] conserver rigidite et resistance du frene de reference entre noeuds (facteur rigidite 1.055, resistance 1.018 sur 40 mm (frene))
- AJUSTE bois.rayon_courbure_min : 300 mm -> 530 mm  [bois:erable_sycomore] rayon mini de cintrage propre a l'essence et a la methode (vapeur : 10 x section 53 mm = 530 mm (requis), actuel 300 mm)
- AJUSTE jonctions.longueur_insert : 20 mm -> 25 mm  [bois:erable_sycomore] longueur d'insert filete selon la densite (arrachement) (densite 615 kg/m3)
- AJUSTE jonctions.epaisseur_tenon : 17 mm -> 18 mm  [jonctions] regle du tiers (section_noeud / 3)
- AJUSTE jonctions.profondeur_mortaise : 40 mm -> 42 mm  [jonctions] 0,8 x section au noeud (0,8 x section_noeud)
```

