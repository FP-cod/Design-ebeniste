# -*- coding: utf-8 -*-
"""Catalogue des systemes de rangement.

Familles : ``tiroir``, ``porte``, ``etagere``, ``crochet``, ``barre``,
``serrure``, ``port``. Chaque entree contient :

- ``nom``, ``famille``, ``source`` (fichier d'une autre gamme ou « À VALIDER »),
  ``a_valider`` (True si cotes / capacite sans source) ;
- ``geometrie`` : cotes utilisees par les grammaires et ``rangement.regles`` [mm] ;
- ``capacite_service`` [N] ou ``None`` (= fiche fabricant a obtenir ; pour
  crochets et barres la capacite est CALCULEE par ``regles`` a partir de la
  section et du metal) ;
- ``compromis`` : notes 1 (faible) a 5 (excellent) sur ``capacite``,
  ``discretion``, ``solidite``, ``cout`` (5 = le moins cher) + ``texte`` ;
  ces notes sont des appreciations de conception, À VALIDER par Fabien ;
- ``contraintes`` : regles d'emploi lues par ``rangement.regles``.
"""

from .. import sources as S

V = S.A_VALIDER


def _c(capacite, discretion, solidite, cout, texte):
    return {"capacite": capacite, "discretion": discretion, "solidite": solidite, "cout": cout, "texte": texte}


SYSTEMES = {
    # ------------------------------------------------------------------ tiroirs
    "glissiere_billes_sortie_totale": {
        "nom": "Glissieres a billes a sortie totale (paire laterale)", "famille": "tiroir",
        "geometrie": {"jeu_lateral": 12.7, "longueurs": [300, 350, 400, 450, 500]},
        "capacite_service": None, "source": V + " (standard commercial ; jeu 12,7 mm et charge = fiche fabricant)",
        "a_valider": True, "contraintes": {"profondeur_min_marge": 10.0},
        "compromis": _c(4, 3, 4, 3, "Tiroir entierement accessible, charge elevee ; glissieres visibles tiroir "
                                    "ouvert, bruit metallique sans amortisseur."),
    },
    "glissiere_invisible_amortie": {
        "nom": "Coulisses invisibles sous tiroir, amorties (push-to-open possible)", "famille": "tiroir",
        "geometrie": {"jeu_lateral": 5.0, "longueurs": [300, 350, 400, 450, 500]},
        "capacite_service": None, "source": V + " (standard commercial)", "a_valider": True,
        "contraintes": {"profondeur_min_marge": 10.0},
        "compromis": _c(4, 5, 4, 2, "Invisible et silencieuse (fermeture douce) : la plus discrete ; "
                                    "cout eleve, montage precis."),
    },
    "coulisse_bois": {
        "nom": "Coulisse bois traditionnelle (tiroir a l'anglaise, cires)", "famille": "tiroir",
        "geometrie": {"jeu_lateral": 1.0, "longueurs": []},
        "capacite_service": None, "source": V + " (pratique d'ebenisterie, pas de cote dans les autres gammes)",
        "a_valider": True, "contraintes": {"profondeur_min_marge": 0.0},
        "compromis": _c(3, 5, 4, 4, "Aucun metal, coherent avec l'ebenisterie de la gamme ; sortie 2/3, "
                                    "sensible a l'humidite (frottement)."),
    },
    "glissiere_inox_genou": {
        "nom": "Glissiere inox a billes + doigt d'indexage (reprise Equinox)", "famille": "tiroir",
        "geometrie": {"jeu_lateral": None, "course": 150.0, "pas_indexage": 25.0, "longueurs": []},
        "capacite_service": 1200.0, "source": S.EQ_ATT + " (glissiere_inox_genou)", "a_valider": False,
        "contraintes": {"profondeur_min_marge": 10.0},
        "compromis": _c(5, 2, 5, 2, "Tres robuste et indexable (tiroir-plateau d'exposition) ; course courte "
                                    "(150 mm), aspect technique."),
    },
    # ------------------------------------------------------------------ portes
    "battante_charniere_soss": {
        "nom": "Porte battante sur charnieres invisibles type Soss", "famille": "porte",
        "geometrie": {"epaisseur_min": 22.0, "nombre_charnieres": 3}, "capacite_service": None,
        "source": S.INC_FIX + " (CHARNIERE_SOSS : epaisseur mini 22 mm, 3 points)", "a_valider": False,
        "contraintes": {"epaisseur_min": 22.0},
        "compromis": _c(3, 5, 3, 2, "Totalement invisible ferme (exigence Incognito) ; mortaises qui affaiblissent "
                                    "le chant, reglage delicat."),
    },
    "battante_charniere_cuvette": {
        "nom": "Porte battante sur charnieres a cuvette O35", "famille": "porte",
        "geometrie": {"epaisseur_min": 16.0, "nombre_charnieres": 2}, "capacite_service": None,
        "source": V + " (standard commercial)", "a_valider": True, "contraintes": {"epaisseur_min": 16.0},
        "compromis": _c(3, 4, 3, 4, "Invisible de l'exterieur, reglable 3D, economique ; aspect "
                                    "« cuisine » a l'ouverture."),
    },
    "battante_pentures_forgees": {
        "nom": "Porte battante sur pentures forgees apparentes (style Neogothique)", "famille": "porte",
        "geometrie": {"epaisseur_min": 22.0}, "capacite_service": None,
        "source": S.NEO_FER + " (penture_angle)", "a_valider": True, "contraintes": {"epaisseur_min": 22.0},
        "compromis": _c(4, 1, 5, 2, "Tres solide et decoratif ; totalement apparent (pas discret)."),
    },
    "coulissante_rainure": {
        "nom": "Portes coulissantes en rainures (haut/bas)", "famille": "porte",
        "geometrie": {"epaisseur_min": 16.0, "profondeur_rainure": 10.0}, "capacite_service": None,
        "source": V, "a_valider": True, "contraintes": {"epaisseur_min": 16.0},
        "compromis": _c(3, 4, 3, 4, "Pas de debattement (piece etroite) ; on n'ouvre que la moitie a la fois."),
    },
    "abattant_compas": {
        "nom": "Abattant / couvercle retenu par compas ou verin", "famille": "porte",
        "geometrie": {"epaisseur_min": 18.0}, "capacite_service": None,
        "source": S.INC_FIX + " (VERIN_COMPAS)", "a_valider": False, "contraintes": {"epaisseur_min": 18.0},
        "compromis": _c(3, 4, 3, 3, "Coffres et vitrines basses ; le verin doit etre dimensionne sur la masse "
                                    "reelle du couvercle (Incognito)."),
    },
    # ---------------------------------------------------------------- etageres
    "taquets_systeme_32": {
        "nom": "Etageres reglables sur taquets O5 au pas de 32 mm", "famille": "etagere",
        "geometrie": {"diametre_taquet": 5.0, "pas": 32.0}, "capacite_service": None,
        "source": V + " (systeme 32 : standard industriel, absent des autres gammes)", "a_valider": True,
        "contraintes": {"porte_a_faux_max_ratio": 0.25},
        "compromis": _c(3, 3, 3, 5, "Reglage fin et peu couteux ; rangees de trous visibles a l'interieur."),
    },
    "cremaillere_encastree": {
        "nom": "Cremailleres metal encastrees + consoles", "famille": "etagere",
        "geometrie": {"pas": 32.0, "largeur_rainure": 16.0, "profondeur_rainure": 5.0}, "capacite_service": None,
        "source": V, "a_valider": True, "contraintes": {"porte_a_faux_max_ratio": 0.25},
        "compromis": _c(4, 2, 4, 3, "Charges plus fortes ; metal visible."),
    },
    "tasseaux_rainures": {
        "nom": "Etageres fixes en rainures (ou sur tasseaux colles)", "famille": "etagere",
        "geometrie": {"profondeur_rainure": 8.0}, "capacite_service": None, "source": V, "a_valider": True,
        "contraintes": {"porte_a_faux_max_ratio": 0.0},
        "compromis": _c(4, 5, 5, 4, "Contrevente le caisson, aucune quincaillerie ; non reglable."),
    },
    "etagere_invisible_tiges": {
        "nom": "Etagere murale « flottante » sur tiges noyees", "famille": "etagere",
        "geometrie": {"diametre_tige": 12.0}, "capacite_service": None, "source": V, "a_valider": True,
        "contraintes": {"porte_a_faux_max_ratio": 1.0},
        "compromis": _c(2, 5, 2, 4, "Aspect epure ; tout le moment repose sur les tiges et le mur (support inconnu)."),
    },
    # ---------------------------------------------------------------- crochets
    "crochet_inox_simple": {
        "nom": "Crochet inox 316 tige ronde O8 sur platine O40 (insert M8)", "famille": "crochet",
        "geometrie": {"metal": "inox_316", "diametre_tige": 8.0, "saillie": 60.0, "platine_diametre": 40.0,
                      "platine_epaisseur": 2.0, "branches": 1},
        "capacite_service": None,
        "source": S.EQ_PARAM + " (inox.diametre_oeillet 8, inox.epaisseur_plaque 2, laiton.diametre_capuchon 40) ; "
                  + S.EQ_ATT + " (insert_filete_m8)",
        "a_valider": False, "contraintes": {"fixation": "insert_filete_m8"},
        "compromis": _c(3, 3, 4, 4, "Hygienique (inox 316), sobre ; capacite calculee par la flexion de la tige."),
    },
    "crochet_inox_double": {
        "nom": "Crochet inox 316 double (deux branches O8)", "famille": "crochet",
        "geometrie": {"metal": "inox_316", "diametre_tige": 8.0, "saillie": 60.0, "platine_diametre": 40.0,
                      "platine_epaisseur": 2.0, "branches": 2},
        "capacite_service": None, "source": S.EQ_PARAM + " (memes cotes que crochet_inox_simple)",
        "a_valider": False, "contraintes": {"fixation": "insert_filete_m8"},
        "compromis": _c(4, 3, 4, 3, "Paire de menottes ou paddle a deux points ; un peu plus large."),
    },
    "patere_laiton": {
        "nom": "Patere laiton sans plomb O12", "famille": "crochet",
        "geometrie": {"metal": "laiton_cw510l", "diametre_tige": 12.0, "saillie": 50.0, "platine_diametre": 40.0,
                      "platine_epaisseur": 3.0, "branches": 1},
        "capacite_service": None,
        "source": S.EQ_PARAM + " (laiton.diametre_capuchon 40, epaisseur_capuchon 3) ; O12 : " + V,
        "a_valider": True, "contraintes": {"fixation": "insert_filete_m8"},
        "compromis": _c(3, 3, 4, 2, "Decoratif (Equinox / Neogothique) ; se raye et se ternit."),
    },
    "cheville_bois": {
        "nom": "Cheville bois tournee O20 (style shaker), essence du meuble", "famille": "crochet",
        "geometrie": {"metal": None, "diametre_tige": 20.0, "saillie": 70.0, "platine_diametre": None,
                      "platine_epaisseur": 0.0, "branches": 1},
        "capacite_service": None, "source": V, "a_valider": True,
        "contraintes": {"fixation": "collee_dans_percage", "profondeur_percage_ratio": 1.0},
        "compromis": _c(2, 4, 3, 5, "Aucun metal, discret et chaleureux ; capacite faible (bois)."),
    },
    "crochet_forge": {
        "nom": "Crochet forge rond 12 (style Neogothique)", "famille": "crochet",
        "geometrie": {"metal": "fer_forge_mat", "diametre_tige": 12.0, "saillie": 70.0, "platine_diametre": 50.0,
                      "platine_epaisseur": 5.0, "branches": 1},
        "capacite_service": None,
        "source": S.NEO_FER + " (fer_forge_mat : rond 12 dans sections_commerciales ; fer plat 5)",
        "a_valider": True, "contraintes": {"fixation": "insert_filete_m8"},
        "compromis": _c(5, 1, 5, 2, "Le plus robuste, totalement assume ; contact peau : finition cire noire."),
    },
    # ------------------------------------------------------------------ barres
    "tube_inox_20": {
        "nom": "Tube rond inox 316 O20 x 1,5", "famille": "barre",
        "geometrie": {"materiau": "inox_316", "diametre": 20.0, "paroi": 1.5}, "capacite_service": None,
        "source": V + " (dimension commerciale de tube, absente des autres gammes ; inox_316 : " + S.EQ_MET + ")",
        "a_valider": True, "contraintes": {},
        "compromis": _c(4, 3, 4, 3, "Leger, hygienique, glissement facile des boucles."),
    },
    "rond_inox_16": {
        "nom": "Rond plein inox 316 O16", "famille": "barre",
        "geometrie": {"materiau": "inox_316", "diametre": 16.0, "paroi": None}, "capacite_service": None,
        "source": S.EQ_PARAM + " (inox.diametre_axe_pivot 16) ; " + S.EQ_MET, "a_valider": False, "contraintes": {},
        "compromis": _c(4, 4, 5, 3, "Plus fin donc plus discret ; lourd."),
    },
    "rond_fer_forge_20": {
        "nom": "Rond fer forge O20 (cire noire)", "famille": "barre",
        "geometrie": {"materiau": "fer_forge_mat", "diametre": 20.0, "paroi": None}, "capacite_service": None,
        "source": S.NEO_FER + " (rond 20 dans sections_commerciales)", "a_valider": False, "contraintes": {},
        "compromis": _c(5, 1, 5, 3, "Tres solide et theatral ; tanins : pas au contact direct du chene humide."),
    },
    "rond_laiton_20": {
        "nom": "Rond laiton mat O20", "famille": "barre",
        "geometrie": {"materiau": "laiton_mat", "diametre": 20.0, "paroi": None}, "capacite_service": None,
        "source": S.NEO_FER + " (laiton_mat, rond 20)", "a_valider": False, "contraintes": {},
        "compromis": _c(4, 2, 4, 1, "Le plus decoratif et le plus cher ; laiton mat : contact peau a eviter."),
    },
    "rond_bois_30": {
        "nom": "Rond bois O30 dans l'essence du meuble", "famille": "barre",
        "geometrie": {"materiau": "bois", "diametre": 30.0, "paroi": None}, "capacite_service": None,
        "source": V + " (O30 propose ; sigma_adm de l'essence : " + S.INC_PARAM + ")", "a_valider": True,
        "contraintes": {},
        "compromis": _c(2, 5, 3, 5, "Tout bois, se fond dans le meuble ; plus epais, capacite limitee."),
    },
    # ---------------------------------------------------------------- serrures
    "serrure_came": {
        "nom": "Serrure a came et cle (barillet)", "famille": "serrure",
        "geometrie": {"diametre_percage": 19.0, "epaisseur_min": 16.0}, "capacite_service": None,
        "source": V, "a_valider": True, "contraintes": {"epaisseur_min": 16.0},
        "compromis": _c(3, 2, 3, 5, "Simple et fiable ; barillet visible en facade, cle a gerer."),
    },
    "serrure_code_mecanique": {
        "nom": "Serrure a code mecanique (molettes)", "famille": "serrure",
        "geometrie": {"epaisseur_min": 16.0}, "capacite_service": None, "source": V, "a_valider": True,
        "contraintes": {"epaisseur_min": 16.0},
        "compromis": _c(3, 1, 3, 4, "Pas de cle ; boitier tres visible."),
    },
    "serrure_electronique_rfid": {
        "nom": "Serrure electronique RFID invisible (montage interieur)", "famille": "serrure",
        "geometrie": {"epaisseur_max_lecture": 20.0, "epaisseur_min": 12.0}, "capacite_service": None,
        "source": V + " (portee de lecture a travers le bois = fiche fabricant)", "a_valider": True,
        "contraintes": {"epaisseur_max_lecture": 20.0, "epaisseur_min": 12.0, "secours_obligatoire": True},
        "compromis": _c(3, 5, 3, 2, "Aucune trace exterieure (badge) ; piles et ouverture de secours a prevoir."),
    },
    "verrou_magnetique_cache": {
        "nom": "Verrou magnetique cache (cle aimantee)", "famille": "serrure",
        "geometrie": {"epaisseur_max_lecture": 18.0, "epaisseur_min": 12.0}, "capacite_service": None,
        "source": V, "a_valider": True, "contraintes": {"epaisseur_max_lecture": 18.0, "epaisseur_min": 12.0},
        "compromis": _c(2, 5, 2, 4, "Invisible et sans pile ; securite faible (dissuasion vis-a-vis d'enfants "
                                    "ou de visiteurs, pas anti-effraction)."),
    },
    "loquet_pene_forge": {
        "nom": "Loquet a pene forge (reprise Neogothique)", "famille": "serrure",
        "geometrie": {"epaisseur_min": 22.0}, "capacite_service": None,
        "source": S.NEO_FER + " (loquet_pene)", "a_valider": False, "contraintes": {"epaisseur_min": 22.0},
        "compromis": _c(3, 1, 5, 3, "Fermeture sans cle (maintien) ; ajouter un cadenas pour verrouiller."),
    },
    "moraillon_cadenas": {
        "nom": "Moraillon forge + cadenas", "famille": "serrure",
        "geometrie": {"epaisseur_min": 22.0}, "capacite_service": None,
        "source": V + " (style " + S.NEO_FER + ", piece absente du catalogue)", "a_valider": True,
        "contraintes": {"epaisseur_min": 22.0},
        "compromis": _c(4, 1, 5, 3, "Tres dissuasif, esthetique « coffre » ; le moins discret."),
    },
    # -------------------------------------------------------------------- ports
    "port_vac_u_lock_npt": {
        "nom": "Port Vac-U-Lock (ergot inox 316L) visse dans une douille 1\" NPT femelle", "famille": "port",
        "geometrie": {"montage_arriere": "npt_1_male", "douille": "npt_1_femelle"}, "capacite_service": None,
        "source": S.ABO_PARAM + " (vac_u_lock.*, npt_1.*) ; " + S.ABO_PORT + " (calculer_port)", "a_valider": False,
        "contraintes": {"profondeur_npt": True, "pas_ports": True},
        "compromis": _c(4, 3, 4, 2, "Interchangeable : on devisse l'ergot pour liberer une douille NPT standard ; "
                                    "ergot visible quand il est monte."),
    },
    "port_vac_u_lock_m8": {
        "nom": "Port Vac-U-Lock (ergot inox) a tige M8 visse dans un insert M8 du panneau", "famille": "port",
        "geometrie": {"montage_arriere": "filete_machine", "insert": "insert_filete_m8"}, "capacite_service": 2500.0,
        "source": S.ABO_PARAM + " (vac_u_lock.montage_arriere = filete_machine, defaut Aboutissants ; "
                  "filetage_cote_machine M8x1.25 x 16) ; " + S.EQ_ATT + " (insert_filete_m8, 2500 N)",
        "a_valider": False, "contraintes": {"insert_m8": True, "pas_ports": True},
        "compromis": _c(3, 3, 4, 5, "Le plus simple et le moins cher : pas de plot ni de douille, l'insert tient dans "
                                    "un panneau de 22 ; n'accepte que les ergots filetes M8 (pas les accessoires NPT)."),
    },
    "port_npt_1_femelle": {
        "nom": "Douille 1\" NPT femelle seule (accessoires filetes)", "famille": "port",
        "geometrie": {"douille": "npt_1_femelle"}, "capacite_service": None,
        "source": S.ABO_PARAM + " (npt_1.*) ; " + S.INC_HOUSSES, "a_valider": False,
        "contraintes": {"profondeur_npt": True, "pas_ports": True},
        "compromis": _c(4, 4, 4, 4, "Simple et discret (trou affleurant) ; pas d'ergot Vac-U-Lock."),
    },
    "port_cache_affleurant": {
        "nom": "Douille NPT + cache bois affleurant 10 mm (etat ferme invisible)", "famille": "port",
        "geometrie": {"douille": "npt_1_femelle", "cache": True}, "capacite_service": None,
        "source": S.INC_FIX + " (CACHE_AFFLEURANT) ; " + S.ABO_PARAM + " (vac_u_lock.cache_epaisseur 10)",
        "a_valider": False, "contraintes": {"profondeur_npt": True, "cache": True, "pas_ports": True},
        "compromis": _c(4, 5, 4, 3, "Invisible ferme (regle Incognito) ; un geste de plus pour deployer."),
    },
}

FAMILLES = ("tiroir", "porte", "etagere", "crochet", "barre", "serrure", "port")


def par_famille(famille):
    """Cles des systemes d'une famille (ordre du catalogue)."""
    return [k for k, v in SYSTEMES.items() if v["famille"] == famille]
