# Paramètres de la gamme Rangement (généré)

Ne pas éditer : `python outils/generer_docs.py`.

#### Section `gamme`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `gamme.nom` | Nom de la gamme (prefixe des composants Fusion). | texte | — | Rangement | libre |  |
| `gamme.prefixe_fusion` | Prefixe des User Parameters crees dans Fusion. | texte | — | ran_ | **À VALIDER** | Aligne sur eq_ / neo_ / inc_ / abo_ / tan_ (Tantra) / gc_ (GammeCuir). |

#### Section `modules`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `modules.pas_trous` | Entraxe vertical des rangees de trous (taquets, charnieres) : trame de la gamme. | mm | 16 à 64 | 32 | **À VALIDER** | Systeme 32 (standard industriel europeen) ; absent des autres gammes. |
| `modules.recul_trous_avant` | Distance du chant avant a l'axe de la premiere rangee de trous. | mm | 20 à 100 | 37 | **À VALIDER** | Valeur usuelle du systeme 32 ; a confirmer avec les charnieres retenues. |
| `modules.diametre_trous_taquets` | Diametre des trous de taquets d'etageres. | mm | 3 à 8 | 5 | **À VALIDER** | Taquets O5 courants ; aucun taquet dans les autres gammes. |
| `modules.module_largeur` | Largeur d'un module (ratelier mural, travee d'armoire). | mm | 300 à 1200 | 600 | **À VALIDER** | 600 mm : 2 a 4 crochets ou 2 ports au pas de 200 par module ; portee de barre courte (flexion faible). Proposition. |
| `modules.module_hauteur` | Hauteur d'un module (multiple du pas de trous). | mm | 160 à 960 | 320 | **À VALIDER** | 10 x 32 mm : trame verticale commune aux rateliers et aux armoires. |
| `modules.hauteur_armoire` | Hauteur hors-tout des armoires. | mm | 900 à 2200 | 1800 | **À VALIDER** | Accessible sans escabeau ; au-dela de ~1600 mm fixation anti-basculement obligatoire (verifiee par regles). |
| `modules.profondeur_armoire` | Profondeur hors-tout des armoires. | mm | 300 à 650 | 450 | **À VALIDER** | Accepte des glissieres de 400 mm et des paddles a plat. Proposition. |
| `modules.profondeur_coffre` | Profondeur hors-tout des coffres. | mm | 300 à 700 | 450 | **À VALIDER** | Proposition (coffre-banc). |
| `modules.hauteur_coffre` | Hauteur hors-tout des coffres (peut servir d'assise). | mm | 300 à 600 | 440 | repris | equinox/equinox/parametres.py (OVERRIDES_TYPOLOGIE tabouret : dimensions.hauteur_assise 440) |

#### Section `panneaux`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `panneaux.epaisseur_caisson` | Epaisseur des cotes, dessus, dessous des caissons. | mm | 15 à 40 | 18 | repris | incognito/incognito/parametres.py (ParametresDiscretion.epaisseur_min_paroi_visible_mm = 18) |
| `panneaux.epaisseur_porte` | Epaisseur des portes et couvercles. | mm | 16 à 40 | 22 | repris | incognito/incognito/catalogues/fixations.py (CHARNIERE_SOSS : epaisseur_min_bois 22) |
| `panneaux.epaisseur_etagere` | Epaisseur des etageres massives. | mm | 15 à 40 | 22 | **À VALIDER** | Proposition ; la fleche est verifiee par regles. |
| `panneaux.epaisseur_fond` | Epaisseur des fonds (contreplaque en rainure). | mm | 4 à 18 | 8 | **À VALIDER** | Proposition. |
| `panneaux.epaisseur_panneau_mural` | Epaisseur du panneau dorsal des rateliers. | mm | 15 à 40 | 22 | **À VALIDER** | Recoit inserts M8 (20 mm), consoles tenonnees et douilles NPT. |
| `panneaux.epaisseur_support_garni` | Support contreplaque bouleau sous un fond garni de cuir. | mm | 9 à 30 | 18 | repris | equinox/equinox/parametres.py (garnissage.epaisseur_support = 18) |
| `panneaux.lamage_lecteur` | Amincissement local au dos de la porte au droit d'un lecteur RFID / verrou magnetique. | mm | 0 à 15 | 6 | **À VALIDER** | Permet de garder une porte de 22 mm (charnieres Soss) tout en restant sous l'epaisseur de lecture ; le bois restant doit garder le retrait de discretion de 10 mm (Incognito). |

#### Section `bois`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `bois.essence` | Cle de l'essence dans catalogues.bois. | texte | choix : `chene`, `chene_fume`, `contreplaque_bouleau`, `erable_dur`, `erable_sycomore`, `frene`, `frene_blanc`, `hetre`, `lamelle_hetre`, `merisier`, `noyer`, `noyer_noir` | chene | **À VALIDER** | incognito/incognito/parametres.py (ESSENCE_DEFAUT = CHENE) ; neogothique/neogothique/parametres.py — Chene : defaut d'Incognito, de Neogothique et de Tantra (essence de reference), defini dans les 5 gammes a meubles. Equinox est en frene. Choix a trancher par Fabien. |
| `bois.finition` | Cle de la finition dans catalogues.bois.FINITIONS_BOIS. | texte | choix : `cire_naturelle`, `fumage_ammoniac`, `huile_cire`, `huile_cire_noire`, `huile_teck`, `teinte_acetate_fer`, `vernis_pu_mat` | cire_naturelle | **À VALIDER** | neogothique/neogothique/catalogues/bois.py (FINITIONS_BOIS) — Compatible avec toutes les essences ; l'interieur des armoires peut passer en vernis_pu_mat (Tantra : nettoyabilite 5/5, lessivable). |
| `bois.humidite_cible` | Humidite du bois a la mise en oeuvre (interieur chauffe). | % | 6 à 15 | 10 | repris | equinox/equinox/parametres.py (bois.humidite_cible = 10) |

#### Section `cuir`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `cuir.famille` | Famille de cuir / garnissage (catalogues.garnissage). | texte | choix : `agneau_pleine_fleur`, `bouclette`, `cuir_classique_pleine_fleur`, `cuir_cognac`, `cuir_harnais_noir`, `cuir_harnais_vegetal`, `cuir_noir`, `cuir_pleine_fleur_noir`, `cuir_renforce_double_noir`, `cuir_sellier_fin_noir`, `cuir_sobre_facade`, `cuir_synthetique_hq`, `cuir_synthetique_pu_noir`, `cuir_vegan`, `doublure_agneau_noir`, `laine_bouclee`, `lin`, `simili_pu_medical`, `simili_vinyle_marine`, `tantra_cuir_cognac`, `tantra_cuir_noir`, `tissu_chine`, `tissu_krypton`, `tissu_technique_deperlant`, `tissu_technique_enduit`, `vachette_chrome_pleine_fleur`, `vachette_vegetale_pleine_fleur`, `veau_velours`, `velours`, `velours_deperlant` | cuir_classique_pleine_fleur | **À VALIDER** | equinox/equinox/catalogues/garnissage.py (GARNISSAGE_REFERENCE) — Cuir de reference Equinox (noir, cognac, havane, vert bouteille, bleu nuit), assorti a la vachette vegetale de GammeCuir (memes teintes + tan, bordeaux, brun fonce). |
| `cuir.teinte` | Teinte du cuir ; doit exister dans la famille (catalogues.garnissage.TEINTES_CUIR). | texte | choix : `blanc`, `bleu_nuit`, `bordeaux`, `brun_fonce`, `cognac`, `cognac_clair`, `gris`, `havane`, `noir`, `noir_mat`, `tan`, `vert_bouteille`, `vert_olive` | noir | **À VALIDER** | equinox/equinox/catalogues/garnissage.py ; neogothique/neogothique/catalogues/garnissage.py ; incognito/incognito/parametres.py ; tantra/tantra/parametres.py ; gamme_cuir/gamme_cuir/catalogues/cuirs.py — Noir : seule teinte presente dans les 5 gammes (Equinox, Neogothique, Incognito, Tantra, GammeCuir) ; cognac est dans 4 (pas Neogothique). |
| `cuir.epaisseur` | Epaisseur du cuir (derivee de la famille). | mm | 0,5 à 10 | 1,8 | dérivé | equinox/equinox/catalogues/garnissage.py (epaisseur_matiere) |

#### Section `quincaillerie`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `quincaillerie.metal` | Metal des crochets, barres, platines (catalogues.quincaillerie). | texte | choix : `fer_forge_mat`, `inox_304`, `inox_316`, `laiton_cw510l`, `laiton_cw614n`, `laiton_mat` | inox_316 | repris | equinox/equinox/parametres.py (inox.nuance = inox_316) ; aboutissants/catalogues/materiaux.py |
| `quincaillerie.finition_metal` | Finition des pieces metalliques. | texte | choix : `cire_noire`, `galvanisation_peinture_mate`, `huile_brunie`, `inox_brosse`, `inox_electropoli`, `laiton_brosse_vernis_mat`, `laiton_patine_vieilli`, `phosphatation_vernis_mat` | inox_electropoli | **À VALIDER** | aboutissants/catalogues/materiaux.py (inox_316.hygiene) — Electropolissage/passivation conseilles par Aboutissants pour l'hygiene. |
| `quincaillerie.filetage_insert` | Filetage des inserts (crochets, consoles, platines). | texte | choix : `M6`, `M8`, `M10` | M8 | repris | equinox/equinox/parametres.py (jonctions.filetage_insert) ; aboutissants/common/params_globaux.py |
| `quincaillerie.longueur_insert` | Longueur des inserts filetes (20 si densite >= 650 kg/m3, sinon 25). | mm | 10 à 40 | 20 | dérivé | equinox/equinox/catalogues/attaches.py (insert_filete_m8.dimensionnement) |

#### Section `charges`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `charges.charge_crochet` | Masse de service suspendue a un crochet. | kg | 0,5 à 20 | 3 | **À VALIDER** | Une paire de menottes acier ou un paddle : < 1,5 kg ; marge x2. Proposition. |
| `charges.charge_lineaire_barre` | Charge repartie de service sur une barre de suspension. | kg/m | 1 à 60 | 10 | **À VALIDER** | Martinets, cravaches, sangles serres sur la barre. Proposition. |
| `charges.charge_etagere` | Charge surfacique de service des etageres. | kg/m2 | 5 à 200 | 40 | **À VALIDER** | Accessoires et cordes, pas de livres. Proposition a recouper avec EN 16121 / EN 16122 (non consultees). |
| `charges.charge_tiroir` | Charge de service d'un tiroir. | kg | 2 à 60 | 15 | **À VALIDER** | Proposition ; a comparer a la fiche des glissieres. |
| `charges.effort_accidentel` | Traction accidentelle ponctuelle (on se retient a une barre ou un crochet). | N | 0 à 2000 | 300 | **À VALIDER** | ~30 kg : chute evitee de justesse. Verifiee en ALERTE (deformation), un ratelier n'est PAS un point d'ancrage de personne. |
| `charges.longueur_instrument_suspendu` | Longueur pendante typique sous une barre (martinet, sangle). | mm | 100 à 1200 | 500 | **À VALIDER** | Proposition ; sert a eviter que les instruments masquent les crochets. |

#### Section `securite`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `securite.coefficient_dynamique` | Majoration des charges de service (accrochage brusque, choc). | — | 1 à 4 | 2 | repris | equinox/equinox/parametres.py (securite.coefficient_dynamique = 2,0) |
| `securite.securite_metal` | Coefficient de securite sur la limite elastique des metaux. | — | 1,2 à 4 | 1,8 | repris | equinox/equinox/parametres.py (securite.securite_metal = 1,8) |
| `securite.fleche_admissible` | Fleche admissible = portee / ce nombre. | — | 100 à 1000 | 300 | repris | equinox/equinox/parametres.py (securite.fleche_admissible = 300) |
| `securite.securite_renversement` | Rapport mini moment stabilisant / renversant (armoires). | — | 1 à 3 | 1,5 | repris | equinox/equinox/parametres.py (securite.securite_renversement = 1,5) |

#### Section `discretion`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `discretion.niveau` | Niveau de discretion vise a l'etat ferme. | texte | choix : `apparent`, `discret`, `invisible` | discret | **À VALIDER** | 'invisible' applique les regles Incognito (zero cuir, zero ferrure visibles). |
| `discretion.retrait_min_ancre` | Bois mini entre une piece metallique noyee et une surface visible. | mm | 0 à 30 | 10 | repris | incognito/incognito/parametres.py (retrait_min_ancre_sous_surface_mm = 10) |
| `discretion.epaisseur_cache` | Epaisseur des caches bois affleurants (ports, inserts). | mm | 4 à 20 | 10 | repris | incognito/incognito/catalogues/fixations.py (CACHE_AFFLEURANT) ; aboutissants/common/params_globaux.py (vac_u_lock.cache_epaisseur) |
| `discretion.jeu_mecanique` | Jeu fonctionnel (portes, tiroirs, modules juxtaposes). | mm | 0,5 à 6 | 2 | repris | incognito/incognito/parametres.py (jeu_mecanique_mm = 2) |
| `discretion.recul_mortaise_charniere` | Distance mini mortaise de charniere invisible / chant visible. | mm | 3 à 20 | 8 | repris | incognito/incognito/parametres.py (mortaise_charniere_recul_bord_mm = 8) |
| `discretion.cuir_visible_ferme` | Le cuir est-il visible meuble ferme ? | bool | — | non | **À VALIDER** | incognito/incognito/parametres.py (regle « zero cuir visible ») — Incompatible avec niveau 'invisible' (regle Incognito). |

#### Section `ports`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `ports.vac_u_lock` | Prevoir des ports Vac-U-Lock (ergot) compatibles Aboutissants. | bool | — | oui | **À VALIDER** | aboutissants/common/params_globaux.py (cadre_modulaire.ports_vac_u_lock) — Exposer / ranger les accessoires Vac-U-Lock sur leur ergot. |
| `ports.npt` | Prevoir des douilles 1" NPT femelles compatibles Aboutissants / Incognito. | bool | — | oui | **À VALIDER** | aboutissants/common/params_globaux.py (cadre_modulaire.ports_npt) — La douille NPT recoit l'ergot Vac-U-Lock (arriere NPT male) ou un accessoire filete. |
| `ports.plug_longueur` | Longueur de l'ergot Vac-U-Lock (3 in). | mm | 50 à 100 | 76,2 | repris | aboutissants/common/params_globaux.py (vac_u_lock.plug_longueur, brevet US 5,127,396) |
| `ports.plug_diametre_tete` | Plus grand diametre de tete de l'ergot (1,25 in). | mm | 25 à 36 | 31,75 | repris | aboutissants/common/params_globaux.py (vac_u_lock.plug_diametre_tete_max ; a calibrer sur piece) |
| `ports.plug_diametre_tige` | Plus grand diametre de tige de l'ergot (0,75 in). | mm | 12 à 25 | 19,05 | repris | aboutissants/common/params_globaux.py (vac_u_lock.plug_diametre_tige_max) |
| `ports.epaulement_epaisseur` | Epaisseur de l'epaulement d'appui de l'ergot. | mm | 4 à 20 | 8 | repris | aboutissants/interfaces/port_vac_u_lock.py (EP_EPAULEMENT_ATELIER_MM = 8, hypothese d'atelier) |
| `ports.epaulement_diametre` | Diametre de l'epaulement = max(tete + 16, 50). | mm | 30 à 80 | 50 | dérivé | aboutissants/interfaces/port_vac_u_lock.py (calculer_port : d_col) |
| `ports.montage_arriere` | Interface arriere de l'ergot (choix Aboutissants). | texte | choix : `filete_machine`, `npt_1_femelle`, `npt_1_male`, `filete_et_npt`, `integré` | npt_1_male | **À VALIDER** | aboutissants/common/params_globaux.py (vac_u_lock.montage_arriere ; defaut Aboutissants filete_machine) — Sur un meuble, la douille femelle 1" NPT est dans le bois : l'ergot porte un arriere MALE et la douille reste utilisable par les accessoires NPT (Incognito / housses). Le defaut Aboutissants (ergot filete M8 cote machine) est disponible via le systeme port_vac_u_lock_m8. A TRANCHER. |
| `ports.filetage_ergot` | Filetage de l'ergot en montage filete (cote meuble). | texte | choix : `M6x1`, `M8x1`, `M8x1.25`, `M10x1`, `M10x1.5`, `M12x1.75`, `M16x2`, `3/8-16 UNC`, `3/4-10 UNC`, `5/16-18 UNC`, `1/4-20 UNC`, `G1/8` | M8x1.25 | repris | aboutissants/common/params_globaux.py (vac_u_lock.filetage_cote_machine) ; equinox/equinox/catalogues/attaches.py (insert_filete_m8) |
| `ports.filetage_ergot_longueur` | Longueur utile de la tige filetee de l'ergot. | mm | 6 à 40 | 16 | repris | aboutissants/common/params_globaux.py (vac_u_lock.filetage_cote_machine_longueur) |
| `ports.verrouillage_actif` | Collier de serrage anti-arrachement sur l'ergot. | bool | — | non | **À VALIDER** | aboutissants/common/params_globaux.py (vac_u_lock.verrouillage_actif) — Aboutissants : desactivable sur un port meuble peu charge (exposition). |
| `ports.npt_diametre_exterieur` | Diametre exterieur nominal du filetage 1" NPT. | mm | 33,3 à 33,5 | 33,401 | repris | aboutissants/common/params_globaux.py (npt_1.diametre_exterieur) ; incognito/incognito/catalogues/housses.py (NPT_1_OD_MM) |
| `ports.npt_longueur_utile` | Longueur utile de filet L2. | mm | 17,2 à 17,5 | 17,343 | repris | aboutissants/common/params_globaux.py (npt_1.longueur_utile_L2) ; incognito/incognito/catalogues/housses.py |
| `ports.npt_longueur_totale` | Longueur totale de filet L4 (filets imparfaits compris). | mm | 24,9 à 25,1 | 25,006 | repris | aboutissants/common/params_globaux.py (npt_1.longueur_totale_L4) |
| `ports.npt_depassement` | Depassement recommande d'un embout NPT pour le visser a la main. | mm | 18 à 40 | 25 | repris | incognito/incognito/catalogues/housses.py (NPT_1_DEPASSEMENT_RECOMMANDE_MM = 25) |
| `ports.npt_paroi_douille` | Paroi radiale de la douille inox autour du filetage. | mm | 2 à 10 | 4 | repris | aboutissants/interfaces/port_vac_u_lock.py (d_npt = diametre_exterieur + 8) |
| `ports.fond_mini_douille` | Bois mini sous le fond de la douille NPT. | mm | 3 à 20 | 6 | **À VALIDER** | Proposition : evite de deboucher au dos du plot. |
| `ports.paroi_bois_mini` | Bois mini autour de la douille NPT (fendage). | mm | 6 à 30 | 12 | **À VALIDER** | Proposition ; Aboutissants interdit de percer O33 dans une fibre tendue : plots rapportes. |
| `ports.pas_ports` | Entraxe des ports le long d'un module. | mm | 80 à 600 | 200 | repris | aboutissants/common/params_globaux.py (cadre_modulaire.pas_ports = 200) |
| `ports.degagement_accessoire` | Espace libre autour d'un ergot pour enfiler la base d'un accessoire. | mm | 60 à 300 | 120 | **À VALIDER** | Proposition : bases d'accessoires du marche non cotees (Aboutissants TODO). |

#### Section `pose`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `pose.capacite_support_mur` | Capacite de calcul du support mural (chevilles, ossature). | N | — | — | **TODO** | aboutissants/common/params_globaux.py (cadre_modulaire.capacite_support_mur = TODO) — Support du batiment inconnu : releve sur place obligatoire. |
| `pose.anti_basculement` | Fixation murale anti-basculement des armoires hautes. | bool | — | oui | **À VALIDER** | Obligatoire au-dela de ~1600 mm de haut (verifie par regles) ; ne reprend que de l'effort horizontal. |

#### Section `jonctions`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `jonctions.type_caisson` | Jonction des panneaux de caisson (catalogues.jonctions). | texte | choix : `queue_d_aronde`, `tasseau_biseaute`, `tenon_clavete`, `tenon_mortaise`, `tourillons`, `vis_barillet_m8` | tourillons | **À VALIDER** | incognito/incognito/catalogues/fixations.py (TOURILLON_10 : caissons) — Invisible et economique ; queues d'aronde pour tiroirs et coffres. |
| `jonctions.diametre_tourillon` | Diametre des tourillons = standard <= 0,5 x epaisseur caisson. | mm | 6 à 14 | 8 | dérivé | neogothique/neogothique/catalogues/attaches.py (ratio_diametre_max 0,5) ; equinox/equinox/catalogues/attaches.py (diametres) |
| `jonctions.longueur_tourillon` | Longueur des tourillons = 5 d. | mm | 24 à 80 | 40 | dérivé | equinox/equinox/catalogues/attaches.py (L = 5 d) |
| `jonctions.alesage_chant` | Profondeur d'alesage cote chant = 2,5 d. | mm | 12 à 40 | 20 | dérivé | neogothique/neogothique/catalogues/attaches.py (ratio_profondeur 2,5) |
| `jonctions.epaisseur_tenon` | Tenon des consoles / cadres = 1/3 de la piece tenonnee (base : epaisseur_panneau_mural). | mm | 4 à 30 | 7 | dérivé | equinox/equinox/catalogues/attaches.py (tenon_mortaise : regle du tiers) |
| `jonctions.profondeur_mortaise` | Mortaise = 0,8 x piece receveuse (base : epaisseur_panneau_mural). | mm | 8 à 60 | 17,6 | dérivé | equinox/equinox/catalogues/attaches.py (tenon_mortaise : 0,8 x section) |

#### Section `systemes`

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `systemes.tiroir` | Systeme de tiroir (catalogues.systemes). | texte | choix : `glissiere_billes_sortie_totale`, `glissiere_invisible_amortie`, `coulisse_bois`, `glissiere_inox_genou` | glissiere_invisible_amortie | **À VALIDER** | Discretion (silencieux, invisible) ; cout a arbitrer. |
| `systemes.porte` | Systeme de porte. | texte | choix : `battante_charniere_soss`, `battante_charniere_cuvette`, `battante_pentures_forgees`, `coulissante_rainure`, `abattant_compas` | battante_charniere_soss | **À VALIDER** | incognito/incognito/catalogues/fixations.py — Invisible ferme, coherent Incognito. |
| `systemes.etagere` | Systeme d'etagere. | texte | choix : `taquets_systeme_32`, `cremaillere_encastree`, `tasseaux_rainures`, `etagere_invisible_tiges` | taquets_systeme_32 | **À VALIDER** | Reglage au pas de 32. |
| `systemes.crochet` | Type de crochet. | texte | choix : `crochet_inox_simple`, `crochet_inox_double`, `patere_laiton`, `cheville_bois`, `crochet_forge` | crochet_inox_double | **À VALIDER** | equinox/equinox/parametres.py — Inox 316 O8 (cotes Equinox). |
| `systemes.barre` | Type de barre de suspension. | texte | choix : `tube_inox_20`, `rond_inox_16`, `rond_fer_forge_20`, `rond_laiton_20`, `rond_bois_30` | tube_inox_20 | **À VALIDER** | Leger et hygienique ; dimension de tube À VALIDER. |
| `systemes.serrure` | Systeme de verrouillage. | texte | choix : `serrure_came`, `serrure_code_mecanique`, `serrure_electronique_rfid`, `verrou_magnetique_cache`, `loquet_pene_forge`, `moraillon_cadenas` | serrure_came | **À VALIDER** | Decision prioritaire de Fabien (cle / code / RFID). |
| `systemes.port` | Type de port de fixation. | texte | choix : `port_vac_u_lock_npt`, `port_vac_u_lock_m8`, `port_npt_1_femelle`, `port_cache_affleurant` | port_vac_u_lock_npt | **À VALIDER** | aboutissants/common/params_globaux.py — Ergot + douille NPT interchangeables. |

#### Sous-schéma `ratelier` (grammaire râtelier mural)

| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |
|---|---|---|---|---|---|---|
| `ratelier.nombre_modules` | Nombre de modules juxtaposes. | — | 1 à 6 | 2 | **À VALIDER** | Demonstration : 2 x 600 mm = 1,2 m. |
| `ratelier.modules_hauteur` | Hauteur du panneau en modules (x modules.module_hauteur). | — | 1 à 6 | 3 | **À VALIDER** | 3 x 320 = 960 mm. |
| `ratelier.hauteur_pose` | Hauteur du bas du panneau au sol. | mm | 300 à 1500 | 900 | **À VALIDER** | Haut a 1860 mm : barres atteignables debout. |
| `ratelier.tasseau_hauteur` | Hauteur de chaque demi-tasseau biseaute. | mm | 50 à 150 | 90 | **À VALIDER** | Proposition. |
| `ratelier.tasseau_epaisseur` | Epaisseur des tasseaux et de la cale basse (ecart mur / panneau). | mm | 15 à 30 | 22 | **À VALIDER** | Proposition. |
| `ratelier.recul_tasseau` | Distance du haut du panneau au haut du tasseau. | mm | 0 à 200 | 40 | **À VALIDER** | Proposition. |
| `ratelier.nombre_barres` | Nombre de barres de suspension par module. | — | 0 à 4 | 2 | **À VALIDER** | Proposition. |
| `ratelier.hauteur_premiere_barre` | Axe de la barre la plus basse depuis le bas du panneau. | mm | 100 à 1800 | 680 | **À VALIDER** | Proposition. |
| `ratelier.entraxe_barres` | Entraxe vertical des barres. | mm | 60 à 600 | 180 | **À VALIDER** | Proposition. |
| `ratelier.saillie_barre` | Distance axe de barre / face du panneau. | mm | 40 à 250 | 110 | **À VALIDER** | Les instruments suspendus passent devant les crochets (saillie crochet + 40 mm). |
| `ratelier.console_hauteur` | Hauteur des consoles de barre. | mm | 40 à 200 | 80 | **À VALIDER** | Proposition. |
| `ratelier.marge_console` | Recul des consoles par rapport au bord du module. | mm | 0 à 100 | 20 | **À VALIDER** | Proposition. |
| `ratelier.crochets_par_module` | Nombre de crochets par module. | — | 0 à 8 | 4 | **À VALIDER** | Proposition. |
| `ratelier.hauteur_crochets` | Axe de la rangee de crochets depuis le bas du panneau. | mm | 50 à 1800 | 400 | **À VALIDER** | Proposition. |
| `ratelier.ports_par_module` | Nombre de ports Aboutissants par module (au pas ports.pas_ports). | — | 0 à 4 | 2 | **À VALIDER** | Proposition. |
| `ratelier.hauteur_ports` | Axe de la rangee de ports depuis le bas du panneau. | mm | 40 à 1800 | 130 | **À VALIDER** | Proposition. |
| `ratelier.plot_largeur` | Largeur (X) et hauteur (Z) du plot bois porte-douille. | mm | 40 à 150 | 70 | **À VALIDER** | >= douille O41,4 + 2 x 12 mm (regles). |
| `ratelier.plot_profondeur` | Profondeur (Y) du plot porte-douille. | mm | 20 à 120 | 40 | **À VALIDER** | >= L4 25 + fond 6 mm (regles). |

#### Surcharges par typologie

| Typologie | Paramètre | Valeur |
|---|---|---|
| `ratelier_mural` | — | (défauts communs) |
| `armoire_accessoires` | — | (défauts communs) |
| `coffre` | `systemes.porte` | abattant_compas |
| `support_exposition` | `systemes.porte` | coulissante_rainure |
| `armoire_verrouillable` | `discretion.niveau` | invisible |
| `armoire_verrouillable` | `systemes.serrure` | serrure_electronique_rfid |
