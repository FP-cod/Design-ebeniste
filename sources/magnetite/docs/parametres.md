# Parametres globaux GammeCuir

Genere par `outils/generer_docs.py` depuis `gamme_cuir/parametres_gamme_cuir.defauts.json` (lui-meme produit par `outils/_generer_defauts_json.py`). Surcharges projet : `gamme_cuir/parametres_gamme_cuir.json`. Unites internes mm / N ; seul `fusion_outils` convertit en cm.

Statuts : `impose` (fixe par Fabien), `a_valider` (proposition a trancher), `derive`, `libre`. Une source = valeur reprise d'une autre gamme (chemin sous /workspace) ; pas de source = proposition GammeCuir.


## `gamme`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `gamme.nom` | GammeCuir | texte |  | impose | Nom de la gamme (prefixe des composants Fusion). | Convention Equinox (gamme.nom). |  |
| `gamme.prefixe_fusion` | gc_ | texte |  | impose | Prefixe des User Parameters Fusion. | Convention eq_ / neo_ / inc_ / abo_ des autres gammes. |  |

## `tailles`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `tailles.poignet_S` | 150 | mm | 130 - 165 | a_valider | Tour de poignet taille S (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.poignet_tour_S) |
| `tailles.poignet_M` | 170 | mm | 155 - 185 | a_valider | Tour de poignet taille M (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.poignet_tour_M) |
| `tailles.poignet_L` | 190 | mm | 175 - 205 | a_valider | Tour de poignet taille L (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.poignet_tour_L) |
| `tailles.poignet_XL` | 210 | mm | 195 - 240 | a_valider | Tour de poignet taille XL (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.poignet_tour_XL) |
| `tailles.cheville_S` | 200 | mm | 170 - 215 | a_valider | Tour de cheville taille S (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cheville_tour_S) |
| `tailles.cheville_M` | 220 | mm | 205 - 240 | a_valider | Tour de cheville taille M (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cheville_tour_M) |
| `tailles.cheville_L` | 245 | mm | 225 - 265 | a_valider | Tour de cheville taille L (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cheville_tour_L) |
| `tailles.cheville_XL` | 270 | mm | 250 - 310 | a_valider | Tour de cheville taille XL (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cheville_tour_XL) |
| `tailles.cou_S` | 330 | mm | 300 - 355 | a_valider | Tour de cou taille S (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cou_tour_S) |
| `tailles.cou_M` | 370 | mm | 345 - 395 | a_valider | Tour de cou taille M (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cou_tour_M) |
| `tailles.cou_L` | 410 | mm | 385 - 435 | a_valider | Tour de cou taille L (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cou_tour_L) |
| `tailles.cou_XL` | 450 | mm | 425 - 500 | a_valider | Tour de cou taille XL (mesure anatomique, sans jeu). | Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles). | aboutissants/common/params_globaux.py (anthropometrie.cou_tour_XL) |

## `produit`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `produit.membre` | poignet | texte | poignet, cheville | libre | Membre vise par la grammaire menottes (selectionne les tours et la largeur). | Une seule grammaire pour poignet et cheville. |  |
| `produit.taille` | M | texte | S, M, L, XL | libre | Taille S/M/L/XL : le trou central de la rangee d'ardillon tombe sur le tour de cette taille. | Taille centrale par defaut. |  |
| `produit.usage` | jeu_leger | texte | jeu_leger, contention | a_valider | Usage annonce : 'jeu_leger' (decoratif / contrainte symbolique) ou 'contention' (retenue reelle attachee a un meuble). Durcit les regles de securite. | Le scratch et les fermetures faibles ne sont acceptables qu'en jeu leger. |  |

## `sangles`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `sangles.largeur_menotte_poignet` | 50 | mm | 30 - 80 | a_valider | Largeur de bande des menottes de poignet. | Meme largeur que les manilles de poignet de l'Entrave : assortiment visuel et repartition de pression. | neogothique/neogothique/parametres.py (garnissage.largeur_manille_poignet = 50) |
| `sangles.largeur_menotte_cheville` | 60 | mm | 40 - 90 | a_valider | Largeur de bande des menottes de cheville. | Cheville plus forte et plus osseuse (malleoles) : bande plus large. Proposition a valider. |  |
| `sangles.largeur_collier` | 40 | mm | 20 - 70 | a_valider | Largeur de bande des colliers (grammaire future). | Compromis confort de la nuque / maintien. Neogothique utilise 60 mm pour une manille de cou fixe. |  |
| `sangles.largeur_sangle_contention` | 38 | mm | 25 - 60 | a_valider | Largeur des sangles de contention (grammaire future). | Largeur courante de boucle de harnachement ; a confirmer selon boucles retenues. |  |
| `sangles.largeur_passant` | 12 | mm | 8 - 20 | a_valider | Largeur du passant (bride qui maintient la pointe). | Assez large pour ne pas couper le cuir, assez etroit pour rester discret. |  |
| `sangles.epaisseur_passant` | 2 | mm | 1,5 - 3,5 | a_valider | Epaisseur du cuir du passant (refendu). | Un passant a 3,5 mm fait une surepaisseur disgracieuse : refendre a ~2 mm. |  |
| `sangles.jeu_passant` | 2 | mm | 0,5 - 5 | a_valider | Jeu ajoute a la largeur de bande pour le perimetre interieur du passant. | Le passant doit glisser sur deux epaisseurs de bande sans forcer. |  |

## `cuir`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `cuir.epaisseur_exterieure` | 3,5 | mm | 2 - 5 | a_valider | Epaisseur du cuir exterieur (fleur visible). | Classe 'moyenne' 3-3,5 mm : tenue de bande et trous d'ardillon durables, se cintre encore sur un poignet S. |  |
| `cuir.classes_epaisseur` | fine 2-2,5 ; moyenne 3-3,5 ; forte 4-5 | mm |  | impose | Classes d'epaisseur fournisseur (mini, maxi). | Classes demandees par Fabien (2-2,5 / 3-3,5 / 4-5 mm). |  |
| `cuir.nb_couches` | 3 | - | 1 - 3 | a_valider | Nombre de couches : 1 = exterieur seul, 2 = exterieur + doublure, 3 = exterieur + rembourrage + doublure. | 3 couches = confort maximal pour la contention. |  |
| `cuir.epaisseur_doublure` | 1,2 | mm | 0,8 - 2 | a_valider | Epaisseur de la doublure cote peau. | Doublure agneau 1,2 mm comme Neogothique. | neogothique/neogothique/catalogues/garnissage.py (doublure_agneau_noir.epaisseur_mm = 1.2) |
| `cuir.rembourrage` | oui | bool |  | a_valider | Rembourrage entre exterieur et doublure (zone de contact du membre uniquement). | Confort et repartition de pression ; exige au moins 2 couches (doublure qui l'enferme). |  |
| `cuir.rembourrage_materiau` | mousse_latex | texte | mousse_latex, feutre_laine, neoprene | a_valider | Cle du rembourrage dans catalogues.cuirs.REMBOURRAGES. | Latex HD comme les manilles sellier fin Neogothique. |  |
| `cuir.epaisseur_rembourrage` | 4 | mm | 0 - 12 | a_valider | Epaisseur du rembourrage avant compression. | Neogothique : 3 mm (sellier fin). 4 mm propose pour une menotte de contention : confort accru. | neogothique/neogothique/catalogues/garnissage.py (cuir_sellier_fin_noir : rembourrage 3 mm) |
| `cuir.retrait_rembourrage` | 2 | mm | 0,5 - 6 | a_valider | Retrait du rembourrage par rapport a la ligne de couture (de chaque cote). | La couture doit passer dans le cuir seul, pas dans la mousse. |  |
| `cuir.marge_rembourrage` | 6 | mm | 2 - 20 | a_valider | Marge longitudinale entre le rembourrage et les zones percees (rivets, trous). | Evite que les rivets ecrasent la mousse et que la mousse bourre sous l'ardillon. |  |
| `cuir.matiere` | vachette_vegetale_pleine_fleur | texte | vachette_vegetale_pleine_fleur, cuir_harnais_vegetal, vachette_chrome_pleine_fleur | a_valider | Cle du cuir exterieur dans catalogues.cuirs.CUIRS. | Tannage vegetal : tranches lissables, se teinte, se patine comme le cuir Equinox. |  |
| `cuir.doublure_matiere` | agneau_pleine_fleur | texte | agneau_pleine_fleur, veau_velours | a_valider | Cle de la doublure dans catalogues.cuirs.DOUBLURES. | Agneau : doux et fin, comme Neogothique. |  |

## `tolerances`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `tolerances.decoupe` | 0,3 | mm | 0,05 - 1,5 | a_valider | Tolerance de decoupe (+/-) des pieces de cuir. | Decoupe laser / emporte-piece ; a la main compter 0,5-1 mm. Estimation d'atelier. |  |
| `tolerances.jeu_trou_ardillon` | 0,5 | mm | 0,2 - 2 | a_valider | Jeu diametral mini entre ardillon et trou. | Le cuir se referme apres poinconnage ; sans jeu l'ardillon force et deforme le trou. |  |
| `tolerances.jeu_passage_boucle` | 1 | mm | 0 - 4 | a_valider | Jeu mini entre largeur de bande et passage interieur de boucle / anneau. | La tranche lissee ne doit pas frotter sur la quincaillerie. |  |

## `couture`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `couture.pas_point` | 3,2 | mm | 2 - 6 | a_valider | Pas du point sellier (distance entre deux trous de griffe). | Pas sellerie fine de l'Entrave (8 points/pouce, ~3,1 points/cm). 4 mm pour du cuir de harnais. | neogothique/neogothique/catalogues/garnissage.py (_SELLERIE_FINE : sellier_pas = 3.2) |
| `couture.retrait_bord` | 3 | mm | 2 - 8 | a_valider | Retrait de la ligne de couture par rapport a la tranche (filet d'abattage). | Filet d'abattage a 3 mm comme Neogothique. | neogothique/neogothique/catalogues/garnissage.py (docstring : filet a 3 mm du bord) |
| `couture.fil` | lin_cire_055 | texte | lin_cire_055, polyester_cire_080, polyester_tresse_060 | a_valider | Cle du fil dans catalogues.finitions.FILS. | Lin cire 0,55 mm comme la sellerie fine Neogothique. | neogothique/neogothique/catalogues/garnissage.py (sellier_fil = 0.55) |
| `couture.facteur_fil` | 4 | - | 2,5 - 6 | a_valider | Longueur de fil = facteur x longueur de couture (point sellier a deux aiguilles). | Regle d'atelier courante (estimation non sourcee) ; a recaler sur un echantillon. |  |
| `couture.marge_couture_percages` | 2 | mm | 1 - 6 | a_valider | Distance mini entre la ligne de couture et un percage (trou, rivet, fente). | Evite de fragiliser le pont de cuir entre couture et trou. |  |

## `jonctions`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `jonctions.repli_boucle` | 30 | mm | 20 - 60 | a_valider | Longueur de cuir repliee autour de la barre de boucle (cote boucle). | Assez pour deux rivets ou une couture et loger le passant dans le repli. |  |
| `jonctions.fixation_repli` | rivets | texte | rivets, couture, rivets_et_couture | a_valider | Fixation du repli de boucle. | Rivets : demontable par un sellier et tres solide ; couture : plus fine. Voir docs/compromis.md. |  |
| `jonctions.rivet` | rivet_double_calotte_12 | texte | rivet_double_calotte_9, rivet_double_calotte_12, rivet_cuivre_contre_rivet | a_valider | Cle du rivet dans catalogues.quincaillerie.RIVETS. | Double calotte : tete lisse des deux cotes (pas d'arete cote peau) ; tete 12 mm = tiges jusqu'a 14 mm pour la patte (empilement ~11,7 mm). |  |
| `jonctions.diametre_trou_rivet` | 3 | mm | 2 - 5 | a_valider | Diametre de poinconnage pour la tige de rivet. | Tige ~2,5-3 mm des rivets double calotte courants : a verifier sur la reference fournisseur. |  |
| `jonctions.oeillet_diametre_interieur` | 5 | mm | 3 - 12 | a_valider | Diametre interieur des oeillets (grammaires futures : harnais, laçages). | Proposition a valider selon oeillets du fournisseur. |  |

## `ardillon`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `ardillon.nb_trous` | 5 | - | 3 - 9 | a_valider | Nombre de trous d'ardillon (impair : le trou central = tour de la taille). | 5 trous x 15 mm = +/-30 mm de reglage, couvre la plage d'une taille. |  |
| `ardillon.entraxe_trous` | 15 | mm | 10 - 25 | a_valider | Entraxe des trous d'ardillon. | Pas plus fin qu'une ceinture (~25 mm) : un poignet a besoin d'un reglage fin. |  |
| `ardillon.diametre_trou` | 4,5 | mm | 3 - 7 | a_valider | Diametre des trous d'ardillon. | Ardillon de boucle 50 mm ~3,5-4 mm + jeu : a verifier sur la boucle retenue. |  |
| `ardillon.bout_apres_dernier_trou` | 30 | mm | 15 - 60 | a_valider | Longueur de pointe au-dela du dernier trou. | Assez long pour rester engage dans le passant au trou le plus serre. |  |
| `ardillon.longueur_fente` | 14 | mm | 8 - 25 | a_valider | Longueur de la fente d'ardillon au pli de boucle. | Laisse pivoter l'ardillon sans couper le pli. |  |

## `extremites`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `extremites.rayon_ratio` | 0,5 | - | 0,1 - 0,5 | a_valider | Rayon des extremites = ratio x largeur (0,5 = bout demi-rond). | Bout demi-rond : aucune pointe ni coin vif. |  |
| `extremites.rayon_tranche` | 0,8 | mm | 0,3 - 2 | a_valider | Rayon d'adoucissement des aretes de tranche (abat-carre / bisautage). | Supprime l'arete vive ; donne par l'abat-carre n 1-2. Estimation d'atelier. |  |

## `anneau_d`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `anneau_d.present` | oui | bool |  | a_valider | Ajoute un anneau D sur patte rivetee. | Point d'attache (mousqueton, chaine). |  |
| `anneau_d.reference` | anneau_d_laiton_massif_6x30 | texte | anneau_d_inox_soude_5x25, anneau_d_inox_soude_6x30, anneau_d_laiton_massif_6x30, anneau_o_inox_soude_6x30 | a_valider | Cle de l'anneau dans catalogues.quincaillerie.ANNEAUX. | Laiton pour l'assortiment cognac ; charge estimee plus faible que l'inox soude (voir docs/compromis.md) : a valider. |  |
| `anneau_d.position` | oppose_boucle | texte | oppose_boucle | a_valider | Position de la patte sur la bande. | A l'oppose de la boucle : la traction ne passe pas par l'ardillon. |  |
| `anneau_d.largeur_patte` | 25 | mm | 12 - 40 | a_valider | Largeur de la patte qui tient l'anneau. | Doit passer dans l'anneau (passage interieur) avec le jeu de tolerance. |  |
| `anneau_d.longueur_patte` | 70 | mm | 40 - 110 | a_valider | Longueur developpee de la patte (avant repli autour de l'anneau). | Repliee en deux : 35 mm = fil de l'anneau + deux rivets en ligne avec leurs marges. |  |
| `anneau_d.fixation_patte` | rivets_et_couture | texte | rivets, rivets_et_couture | a_valider | Fixation de la patte d'anneau sur la bande. | Deux rivets seuls cisaillent sous la traction de retenue : couture sellier autour de la patte en plus. |  |
| `anneau_d.entraxe_rivets_patte` | 18 | mm | 10 - 35 | a_valider | Entraxe longitudinal des deux rivets de la patte. | Deux rivets en ligne : la patte ne pivote pas. |  |

## `securite`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `securite.jeu_doigt` | 20 | mm | 15 - 40 | a_valider | Surplus de circonference interieure par rapport au tour mesure (un doigt doit passer a plat). | Un doigt a plat (~12-18 mm) sous la bande : surplus ~1,5-2 fois son epaisseur. Plancher 15 mm = pas d'effet garrot. Proche du jeu Aboutissants (20 mm). | aboutissants/common/params_globaux.py (anthropometrie.jeu_circonference_manille = 20) |
| `securite.deverrouillage_rapide` | oui | bool |  | a_valider | Une attache a ouverture rapide (mousqueton panique) est prevue entre l'anneau et le point d'ancrage. | Recommandation de securite : liberer la personne en quelques secondes sans cle. |  |
| `securite.effort_service` | 500 | N | 100 - 3000 | a_valider | Traction de service sur une menotte attachee. | Traction laterale de verification de l'Entrave, reprise telle quelle (a valider). | neogothique/neogothique/parametres.py (charges.traction_manille = 500 N, a_valider) |
| `securite.coefficient_dynamique` | 1,5 | - | 1 - 4 | a_valider | Majoration a-coups. | Valeur Neogothique. | neogothique/neogothique/parametres.py (charges.coef_dynamique = 1.5) |
| `securite.coefficient_securite` | 4 | - | 2 - 8 | a_valider | Coefficient de securite sur la rupture du cuir et de la quincaillerie. | gamma_cuir Neogothique. | neogothique/neogothique/parametres.py (charges.gamma_cuir = 4) |
| `securite.rayon_mini_extremite` | 5 | mm | 2 - 20 | a_valider | Rayon mini des coins d'extremite (aucun coin vif). | Un coin de cuir de 3,5 mm peut griffer ; 5 mm mini. Proposition. |  |

## `finition`

| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |
|---|---|---|---|---|---|---|---|
| `finition.teinte` | cognac | texte | cognac, noir, tan, havane, brun_fonce, bordeaux, vert_bouteille, bleu_nuit | a_valider | Teinte du cuir (cle de catalogues.cuirs.TEINTES). | Cognac = cuir de reference Equinox. |  |
| `finition.quincaillerie` | laiton_massif_cw510l | texte | inox_316, inox_316_pvd_noir, laiton_massif_cw510l, laiton_patine, acier_nickele | a_valider | Metal de la quincaillerie (cle de catalogues.quincaillerie.METAUX). | Laiton avec cognac (regle d'assortiment) ; laiton sans plomb pour le contact peau (Equinox). |  |
| `finition.tranche` | teintee_lissee_cire | texte | brute, teintee_lissee_cire, peinte_edge_paint, rembordee | a_valider | Finition de tranche (cle de catalogues.finitions.TRANCHES). | Tranches teintees et lustrees comme la sellerie fine Neogothique. |  |
| `finition.fermeture` | boucle_ardillon | texte | boucle_ardillon, boucle_ardillon_cadenas, mousqueton, scratch | a_valider | Systeme de fermeture (cle de catalogues.fermetures.FERMETURES). | Boucle a ardillon : reglable, fiable, ouverture rapide sans cle. |  |
| `finition.boucle` | boucle_rouleau_50_laiton | texte | boucle_rouleau_50_laiton, boucle_rouleau_50_inox, boucle_rouleau_60_laiton, boucle_rouleau_60_inox, boucle_verrouillable_50_inox | a_valider | Cle de la boucle (catalogues.quincaillerie.BOUCLES). | Passage 50 mm = largeur de bande poignet. |  |

## Grandeurs derivees (defauts)

- epaisseur totale (doublure + rembourrage + exterieur) : 8,7 mm
- epaisseur cuir seul (zones percees) : 4,7 mm
- classe d'epaisseur exterieure : moyenne
- points de couture par cm : 3.12
