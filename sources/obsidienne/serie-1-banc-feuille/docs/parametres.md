# Parametres Equinox (couche 1)

Genere par `outils/generer_docs.py` depuis `equinox/parametres.py` et les schemas specifiques des grammaires. Unites internes mm / kg / deg (l'export Fusion ecrit des expressions `700 mm`, `7 deg`, Fusion convertit en cm internes).

Statuts : **impose** = valeur donnee par Fabien ; *a valider* = proposition a trancher ; *derive* = recalcule par les regles materiaux (`equinox/regles.py`).

Overrides : `equinox/parametres_equinox.json` (`commun` et `typologies.<nom>`), `OVERRIDES_TYPOLOGIE` dans `parametres.py`, ou `concevoir(overrides={'bois.section_noeud': 52})`.

Nom Fusion d'un parametre : `eq_` + chemin avec `_` (ex. `eq_bois_section_noeud`).

## Vocabulaire commun

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `gamme.nom` | `Equinox` | texte | Nom de la gamme (prefixe des composants Fusion). |  | libre | - |
| `gamme.prefixe_fusion` | `eq_` | texte | Prefixe des User Parameters crees dans Fusion. |  | libre | - |
| `dimensions.hauteur_assise` | 700 | mm | Hauteur du dessus de garnissage (plateau / assise) au sol, point haut. | 350 - 950 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `dimensions.hauteur_structure` | 652 | mm | Dessous du support garni = hauteur_assise - rembourrage - support : recalculee quand le rembourrage change pour garder l'assise. | 200 - 950 | derive | banc_flore |
| `dimensions.longueur_plateau` | 1150 | mm | Longueur nominale du plateau garni (mode 'complet'). | 500 - 1600 | **impose** | banc_flore, cheval_arcon |
| `dimensions.mode_longueur` | `complet` | texte | 'complet' = longueur_plateau ; 'bassin_epaules' = plateau raccourci a longueur_bassin_epaules + marges. | complet, bassin_epaules | a valider | banc_flore |
| `dimensions.longueur_bassin_epaules` | 540 | mm | Distance bassin (grand trochanter) - epaules (acromion) de l'utilisateur, a mesurer sur la personne. | 380 - 700 | a valider | banc_flore |
| `dimensions.marge_bassin` | 80 | mm | Debord du plateau cote bassin (arriere) au-dela du trochanter. | 0 - 200 | a valider | banc_flore |
| `dimensions.marge_epaules` | 60 | mm | Debord du plateau cote epaules (avant), degage la poitrine. | 0 - 200 | a valider | banc_flore |
| `dimensions.largeur_plateau` | 340 | mm | Largeur du plateau garni (buste). | 220 - 600 | a valider | banc_flore, cheval_arcon, tabouret |
| `dimensions.porte_a_faux` | 110 | mm | Retrait longitudinal du noeud de pied par rapport au bout du plateau. | 40 - 250 | a valider | banc_flore, cheval_arcon |
| `dimensions.retrait_lateral_pieds` | 40 | mm | Retrait lateral du noeud de pied par rapport au chant du plateau. | 0 - 120 | a valider | banc_flore, cheval_arcon |
| `dimensions.hauteur_appui_genoux` | 430 | mm | Hauteur du dessus des repose-genoux (position levrette). | 250 - 600 | a valider | banc_flore |
| `dimensions.entraxe_genoux` | 480 | mm | Entraxe lateral des deux repose-genoux (genoux de part et d'autre du plateau, cuisses le long des chants). | 250 - 600 | a valider | banc_flore |
| `dimensions.recul_genoux` | 100 | mm | Position longitudinale du centre genou depuis le bout arriere du plateau (positif = sous le plateau). | -100 - 300 | a valider | banc_flore |
| `dimensions.hauteur_appui_coudes` | 570 | mm | Hauteur du dessus des repose-coudes. | 400 - 750 | a valider | banc_flore |
| `dimensions.entraxe_coudes` | 480 | mm | Entraxe lateral des repose-coudes (plus large que le plateau). | 300 - 800 | a valider | banc_flore |
| `dimensions.avance_coudes` | 60 | mm | Avance des repose-coudes par rapport au bout avant du plateau (negatif = en retrait sous le plateau). | -200 - 200 | a valider | banc_flore |
| `bois.essence` | `frene` | texte | Cle de l'essence dans catalogues.bois. |  | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.section_noeud` | 50 | mm | Diametre des sections bois au noeud (jonction, zone la plus sollicitee). | 30 - 90 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.section_extremite` | 30 | mm | Diametre des sections bois aux extremites (pieds, bouts de branches). | 20 - 70 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.section_entre_noeuds` | 40 | mm | Diametre au plus fin entre deux noeuds d'une meme piece (galbe 'branche' : noeud 50 -> 40 -> noeud 50). | 25 - 70 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.rayon_courbure_min` | 300 | mm | Rayon de courbure minimal des pieces cintrees (verifie par les regles selon essence et methode de cintrage). | 100 - 2000 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.methode_cintrage` | `lamelle_colle` | texte | Methode de cintrage des courbes. | lamelle_colle, vapeur, massif_debite | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.epaisseur_lamelle` | 3 | mm | Epaisseur des lamelles en lamelle-colle cintre. | 1 - 8 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.angle_splay` | 7 | deg | Angle d'ecartement (splay) des pieds vers l'exterieur, par rapport a la verticale. | 0 - 20 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `bois.section_traverse` | 60 | mm | Cote de l'enveloppe bois carree de la traverse lestee (tube 40x40 + 2 x 10 mm de bois). | 50 - 120 | a valider | banc_flore, cheval_arcon, croix_saint_andre |
| `bois.longeron_largeur` | 40 | mm | Largeur des longerons sous plateau (ceinture). | 25 - 80 | a valider | banc_flore, cheval_arcon |
| `bois.longeron_hauteur` | 70 | mm | Hauteur des longerons sous plateau. | 40 - 140 | a valider | banc_flore, cheval_arcon |
| `bois.humidite_cible` | 10 | % | Humidite du bois a la mise en oeuvre (interieur chauffe). | 6 - 15 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.materiau` | `cuir_classique_pleine_fleur` | texte | Famille de revetement : cle dans catalogues.garnissage (cuir_classique_pleine_fleur, cuir_vegan, tissu_krypton, cuir_synthetique_hq, tissu_technique_enduit ; anciennes cles acceptees). |  | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.couleur` | `cognac` | texte | Coloris ; doit exister dans la famille choisie (valide). |  | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.epaisseur_rembourrage` | 30 | mm | Epaisseur de mousse sous le revetement : 30 mm pour le cuir classique (valeur de reference), recalculee par famille (vegan +5, Krypton 40...). | 10 - 80 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.inclinaison_plateau` | 2 | deg | Inclinaison du plateau (sens donne par flore.sens_inclinaison ; defaut : bassin haut, epaules basses). | 0 - 15 | **impose** | banc_flore, cheval_arcon |
| `garnissage.epaisseur_support` | 18 | mm | Epaisseur du support contreplaque bouleau sous la mousse. | 9 - 30 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.densite_mousse` | 50 | kg/m3 | Masse volumique de la mousse HR (portance). | 25 - 80 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.methode_fixation` | `agrafage_sous_plateau` | texte | Mode de fixation du revetement (derive de la famille). | agrafage_sous_plateau, agrafage_ou_scratch, collage_et_agrafage | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.finition_bords` | `ourlets_cousus` | texte | Finition des bords (derivee de la famille). | ourlets_cousus, rembordage_sans_couture, rembordage_colle | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.coutures_sur_courbes` | False | bool | La grammaire prevoit des coutures apparentes (surpiqures, passepoil) sur des bords courbes ; declenche l'avertissement du tissu Krypton. |  | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `garnissage.rayon_bord` | 12 | mm | Rayon des aretes du coussin (derive de la famille). | 3 - 40 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `inox.nuance` | `inox_316` | texte | Cle de la nuance dans catalogues.metaux. |  | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `inox.diametre_tube_helice` | 12 | mm | Diametre exterieur du tube / rond de l'helice. | 8 - 30 | **impose** | banc_flore |
| `inox.section_helice` | `plein` | texte | 'plein' (rond plein) ou 'tube' (tube, voir epaisseur_paroi_helice). | plein, tube | a valider | banc_flore |
| `inox.epaisseur_paroi_helice` | 2 | mm | Paroi si section_helice = 'tube'. | 1 - 4 | a valider | banc_flore |
| `inox.nombre_tours_helice` | 2 |  | Nombre de tours de l'helice. | 0.5 - 5 | **impose** | banc_flore |
| `inox.crans_verrouillage` | 2 |  | Nombre de crans de verrouillage du pivot d'helice. | 1 - 6 | **impose** | banc_flore |
| `inox.angle_entre_crans` | 35 | deg | Angle de pivotement entre deux crans (position usage / rangee). | 10 - 180 | a valider | banc_flore |
| `inox.diametre_axe_pivot` | 16 | mm | Diametre de l'axe de pivot d'helice dans le pied arriere. | 10 - 30 | a valider | banc_flore |
| `inox.hauteur_pivot` | 300 | mm | Hauteur du pivot d'helice sur le pied arriere. | 100 - 600 | a valider | banc_flore |
| `inox.diametre_oeillet` | 8 | mm | Diametre du fil des oeillets d'ancrage. | 5 - 16 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `inox.epaisseur_plaque` | 2 | mm | Epaisseur des plaques inox (platines, semelles d'oeillet). | 1.5 - 6 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `laiton.nuance` | `laiton_cw614n` | texte | Cle du laiton dans catalogues.metaux. |  | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `laiton.diametre_capuchon` | 40 | mm | Diametre des capuchons / embouts laiton. | 20 - 80 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `laiton.epaisseur_capuchon` | 3 | mm | Epaisseur du fond des capuchons laiton. | 1 - 8 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `laiton.hauteur_jupe` | 12 | mm | Hauteur de la jupe du capuchon remontant sur le bois. | 0 - 40 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `traverse.cote_tube` | 40 | mm | Cote du tube carre inox de la traverse lestee. | 20 - 80 | **impose** | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.epaisseur_paroi` | 2 | mm | Paroi du tube carre 40x40. | 1.5 - 5 | a valider | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.lest_min` | 15 | kg | Lest integre minimal. | 0 - 60 | **impose** | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.lest_max` | 20 | kg | Lest integre maximal. | 0 - 80 | **impose** | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.lest_nominal` | 18 | kg | Lest vise (entre lest_min et lest_max). | 0 - 80 | a valider | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.materiau_lest` | `plomb` | texte | Cle du materiau de lest dans catalogues.metaux. | plomb, acier_plein, grenaille_acier | a valider | banc_flore, cheval_arcon, croix_saint_andre |
| `traverse.hauteur_axe` | 130 | mm | Hauteur de l'axe de la traverse arriere au sol (bas = CG bas). | 60 - 400 | a valider | banc_flore, cheval_arcon |
| `ancrage.oeillets_bas` | True | bool | Oeillets bas encastres sous les semelles des pieds arriere. |  | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `ancrage.profondeur_encastrement` | 10 | mm | Profondeur de la feuillure sous semelle recevant la platine d'oeillet. | 3 - 25 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `ancrage.saillie_oeillet` | 18 | mm | Saillie de l'oeil hors de l'empreinte du pied (accessible). | 8 - 40 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `ancrage.anneau_arriere` | True | bool | Anneau arriere a mi-hauteur de traverse. |  | **impose** | banc_flore, cheval_arcon |
| `ancrage.position_anneau` | `mi_hauteur_traverse` | texte | Position de l'anneau arriere. | mi_hauteur_traverse | **impose** | banc_flore |
| `ancrage.diametre_interieur_anneau` | 40 | mm | Diametre interieur de l'anneau arriere. | 20 - 80 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `ancrage.attache_oeillet` | `oeillet_inox_8` | texte | Cle de l'oeillet dans catalogues.attaches. |  | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `ancrage.attache_anneau` | `anneau_inox_8` | texte | Cle de l'anneau dans catalogues.attaches. |  | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.charge_utilisateur` | 120 | kg | Masse de l'utilisateur prise en compte. | 40 - 200 | **impose** | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.coefficient_dynamique` | 2 |  | Majoration des efforts verticaux (mouvements, impacts). | 1 - 4 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.coefficient_horizontal_long` | 0.3 |  | Effort horizontal longitudinal = coef x poids utilisateur (poussee du partenaire en levrette). | 0 - 1 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.coefficient_horizontal_lat` | 0.15 |  | Effort horizontal lateral = coef x poids utilisateur. | 0 - 1 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.securite_bois` | 3 |  | Coefficient de securite sur la resistance en flexion du bois (MOR). | 1.5 - 6 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.securite_metal` | 1.8 |  | Coefficient de securite sur la limite elastique des metaux. | 1.2 - 4 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.securite_renversement` | 1.5 |  | Rapport mini moment stabilisant / moment renversant. | 1 - 3 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.fleche_admissible` | 300 |  | Fleche admissible = portee / ce nombre. | 100 - 1000 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `securite.frottement_sol` | 0.3 |  | Coefficient de frottement embout laiton / sol (parquet vitrifie). | 0.1 - 0.8 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.diametre_tourillon` | 10 | mm | Diametre des tourillons (derive de la section). | 6 - 16 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.longueur_tourillon` | 50 | mm | Longueur des tourillons (>= 5 x diametre). | 30 - 100 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.epaisseur_tenon` | 17 | mm | Epaisseur des tenons (~ 1/3 de la section au noeud). | 8 - 40 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.profondeur_mortaise` | 40 | mm | Profondeur des mortaises. | 20 - 80 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.filetage_insert` | `M8` | texte | Filetage des inserts / taraudages (pivots, glissieres, ancrages). | M6, M8, M10 | a valider | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |
| `jonctions.longueur_insert` | 20 | mm | Longueur des inserts filetes (derivee de la densite du bois). | 10 - 40 | derive | banc_flore, croix_saint_andre, tabouret, chaise_trone, cheval_arcon |

## Banc Flore (`flore.*`)

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `flore.sens_inclinaison` | `avant_bas` | texte | 'avant_bas' : bassin haut, epaules basses (classique) ; 'avant_haut' : l'inverse. | avant_bas, avant_haut | a valider | banc_flore |
| `flore.splay_double` | True | bool | Splay de 7 deg aussi dans le sens longitudinal (pieds AR vers l'arriere, AV vers l'avant) : meilleure tenue a la poussee. |  | a valider | banc_flore |
| `flore.cambrure_pieds` | 15 | mm | Fleche du galbe 'branche' des pieds (vers l'exterieur). | 0 - 60 | a valider | banc_flore |
| `flore.exposant_contour` | 4 |  | Exposant de la superellipse du contour de plateau (2 = ellipse, grand = rectangle). | 2 - 10 | a valider | banc_flore |
| `flore.genou_longueur` | 200 | mm | Longueur du coussin de genou. | 120 - 300 | a valider | banc_flore |
| `flore.genou_largeur` | 110 | mm | Largeur du coussin de genou. | 80 - 180 | a valider | banc_flore |
| `flore.course_glissiere` | 150 | mm | Course des glissieres de genou. | 50 - 300 | a valider | banc_flore |
| `flore.hauteur_glissiere` | 20 | mm | Hauteur de la glissiere sous coussin. | 10 - 40 | a valider | banc_flore |
| `flore.coude_longueur` | 220 | mm | Longueur du coussin de coude. | 120 - 320 | a valider | banc_flore |
| `flore.coude_largeur` | 90 | mm | Largeur du coussin de coude. | 60 - 150 | a valider | banc_flore |
| `flore.hauteur_noeud_branche` | 380 | mm | Hauteur du noeud de depart des branches de coude sur les pieds avant. | 150 - 600 | a valider | banc_flore |
| `flore.fleche_branche` | 15 | mm | Fleche (arc) des branches de coude, vers le haut. | 0 - 120 | a valider | banc_flore |
| `flore.helice_demi_axe_x` | 120 | mm | Demi-axe longitudinal de l'ellipse d'appui genou. | 60 - 200 | a valider | banc_flore |
| `flore.helice_demi_axe_y` | 110 | mm | Demi-axe lateral de l'ellipse d'appui genou. | 40 - 160 | a valider | banc_flore |
| `flore.jeu_helice_pied` | 6 | mm | Jeu radial entre helice et pied (collier). | 2 - 20 | a valider | banc_flore |
| `flore.part_plateau` | 0.55 |  | Part du poids utilisateur sur le plateau (levrette). | 0.2 - 0.9 | a valider | banc_flore |
| `flore.part_genoux` | 0.3 |  | Part du poids sur les deux genoux. | 0.05 - 0.6 | a valider | banc_flore |
| `flore.part_coudes` | 0.15 |  | Part du poids sur les deux coudes. | 0 - 0.5 | a valider | banc_flore |

## Croix de Saint-Andre (`croix.*`)

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `croix.hauteur` | 2100 | mm | Hauteur hors tout des branches. | 1600 - 2500 | a valider | - |
| `croix.largeur_haut` | 1250 | mm | Ecart des extremites hautes (poignets). | 800 - 1600 | a valider | - |
| `croix.largeur_bas` | 950 | mm | Ecart des extremites basses (chevilles). | 500 - 1300 | a valider | - |
| `croix.inclinaison` | 6 | deg | Inclinaison de la croix vers l'arriere (la personne s'appuie). | 0 - 20 | a valider | - |
| `croix.fleche_branches` | 30 | mm | Fleche du cintrage des branches (vers l'exterieur). | 0 - 120 | a valider | - |
| `croix.profondeur_base` | 750 | mm | Recul du pied de la jambe de force derriere le plan de la croix. | 400 - 1200 | a valider | - |
| `croix.hauteur_attache_jambe` | 0 | mm | Hauteur d'attache de la jambe de force (0 = au noeud). | 0 - 2000 | a valider | - |
| `croix.profondeur_plateforme` | 550 | mm | Plateforme frene (lattes) devant la croix sur laquelle se tient la personne : son poids stabilise et ses tractions deviennent des efforts internes. 0 = pas de plateforme. | 0 - 900 | a valider | - |
| `croix.section_branches` | 60 | mm | Section des branches au noeud (>= section_noeud : grande portee). | 40 - 100 | a valider | - |

## Tabouret (`tabouret.*`)

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `tabouret.longueur_assise` | 400 | mm | Longueur (X) de l'assise. | 300 - 600 | a valider | - |
| `tabouret.echancrure` | 0 | mm | Profondeur de l'echancrure avant de queening (0 = tabouret plein). | 0 - 200 | a valider | - |
| `tabouret.hauteur_ceinture` | 160 | mm | Hauteur de la ceinture basse (noeuds) portant les anneaux. | 80 - 300 | a valider | - |
| `tabouret.retrait_pieds` | 50 | mm | Retrait des noeuds de pied sous l'assise. | 20 - 120 | a valider | - |
| `tabouret.fleche_ceinture` | 18 | mm | Fleche des branches de ceinture (vers l'exterieur). | 0 - 60 | a valider | - |

## Chaise / trone (`chaise.*`)

| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |
|---|---|---|---|---|---|---|
| `chaise.profondeur_assise` | 460 | mm | Profondeur d'assise. | 380 - 600 | a valider | - |
| `chaise.hauteur_dossier` | 1250 | mm | Hauteur du haut du dossier (trone) au sol. | 800 - 1800 | a valider | - |
| `chaise.inclinaison_dossier` | 12 | deg | Inclinaison du dossier vers l'arriere. | 0 - 30 | a valider | - |
| `chaise.nervures` | 5 |  | Nombre de nervures du dossier (impair). | 3 - 9 | a valider | - |
| `chaise.recul_pieds_arriere` | 220 | mm | Recul supplementaire des pieds arriere (pieds 'sabre') contre le basculement arriere du trone. | 0 - 400 | a valider | - |
| `chaise.hauteur_accoudoirs` | 670 | mm | Hauteur des accoudoirs au sol. | 550 - 800 | a valider | - |

## Overrides par typologie

- `banc_flore` : {'garnissage': {'coutures_sur_courbes': True}}
- `cheval_arcon` : {'dimensions': {'hauteur_assise': 760.0, 'longueur_plateau': 700.0, 'largeur_plateau': 260.0}}
- `tabouret` : {'dimensions': {'hauteur_assise': 440.0, 'largeur_plateau': 380.0}}
- `chaise_trone` : {'dimensions': {'hauteur_assise': 460.0, 'largeur_plateau': 480.0}, 'garnissage': {'inclinaison_plateau': 4.0}}
- `croix_saint_andre` : {'securite': {'coefficient_horizontal_long': 0.25}}
