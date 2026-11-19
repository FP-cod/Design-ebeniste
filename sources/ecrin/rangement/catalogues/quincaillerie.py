# -*- coding: utf-8 -*-
"""Catalogue quincaillerie : metaux, finitions, visserie, charnieres, verins.

Metaux et visserie repris d'Equinox / Neogothique / Aboutissants (sources
citees). Les composants du commerce absents des autres gammes (taquets,
charnieres a cuvette, glissieres) portent ``a_valider=True`` : leur capacite
doit venir de la fiche du fabricant retenu, rien n'est invente.

Unites : densite [kg/m3], module_elasticite et limite_elastique [MPa],
capacite_service [N].
"""

from .. import sources as S

METAUX = {
    "inox_316": {"nom": "Inox austenitique 316L (1.4404)", "densite": 8000.0, "module_elasticite": 200000.0,
                 "limite_elastique": 200.0, "contact_peau": True, "desinfectants_chlores": True,
                 "source": S.EQ_MET + " ; " + S.ABO_MAT + " (inox_316, etat recuit EN 10088-3)"},
    "inox_304": {"nom": "Inox austenitique 304 (1.4301)", "densite": 7900.0, "module_elasticite": 193000.0,
                 "limite_elastique": 190.0, "contact_peau": True, "desinfectants_chlores": False,
                 "source": S.EQ_MET + " ; " + S.ABO_MAT + " (inox_304)"},
    "laiton_cw614n": {"nom": "Laiton de decolletage CuZn39Pb3 (CW614N)", "densite": 8470.0,
                      "module_elasticite": 97000.0, "limite_elastique": 250.0, "contact_peau": False,
                      "desinfectants_chlores": False,
                      "source": S.EQ_MET + " ; " + S.ABO_MAT + " (contient du plomb : pas de contact prolonge)"},
    "laiton_cw510l": {"nom": "Laiton sans plomb CuZn42 (CW510L)", "densite": 8400.0, "module_elasticite": 100000.0,
                      "limite_elastique": 250.0, "contact_peau": True, "desinfectants_chlores": False,
                      "source": S.EQ_MET + " ; " + S.ABO_MAT + " (laiton_cw510l)"},
    "fer_forge_mat": {"nom": "Fer forge mat (acier S235JR forge a chaud)", "densite": 7850.0,
                      "module_elasticite": 210000.0, "limite_elastique": 235.0, "contact_peau": True,
                      "desinfectants_chlores": False, "source": S.NEO_FER + " (fer_forge_mat)"},
    "laiton_mat": {"nom": "Laiton mat (CuZn37 / CuZn39Pb3, brosse ou patine)", "densite": 8440.0,
                   "module_elasticite": 110000.0, "limite_elastique": 180.0, "contact_peau": False,
                   "desinfectants_chlores": False, "source": S.NEO_FER + " (laiton_mat)"},
}

#: Finitions des metaux : six reprises de Neogothique (fer / laiton) + deux
#: finitions inox (electropolissage repris de l'hygiene Aboutissants ; brossage
#: sans source -> À VALIDER).
FINITIONS_METAL = {
    "cire_noire": {"metaux": ("fer_forge_mat",), "source": S.NEO_FER, "a_valider": False},
    "huile_brunie": {"metaux": ("fer_forge_mat",), "source": S.NEO_FER, "a_valider": False},
    "phosphatation_vernis_mat": {"metaux": ("fer_forge_mat",), "source": S.NEO_FER, "a_valider": False},
    "galvanisation_peinture_mate": {"metaux": ("fer_forge_mat",), "source": S.NEO_FER, "a_valider": False},
    "laiton_brosse_vernis_mat": {"metaux": ("laiton_mat", "laiton_cw614n", "laiton_cw510l"),
                                 "source": S.NEO_FER, "a_valider": False},
    "laiton_patine_vieilli": {"metaux": ("laiton_mat", "laiton_cw614n", "laiton_cw510l"),
                              "source": S.NEO_FER, "a_valider": False},
    "inox_electropoli": {"metaux": ("inox_316", "inox_304"),
                         "source": S.ABO_MAT + " (inox_316, champ hygiene : electropolissage / passivation)",
                         "a_valider": False},
    "inox_brosse": {"metaux": ("inox_316", "inox_304"), "source": S.A_VALIDER, "a_valider": True},
}

#: Visserie et inserts.
VISSERIE = {
    "vis_bois_inox": {"nom": "Vis bois inox A4 tete fraisee", "diametres": [4, 5, 6], "capacite_service": 800.0,
                      "regle": "avant-trou 70 % du d dans les feuillus durs ; ancrage >= 8 d ; jamais en bois de bout seul",
                      "source": S.EQ_ATT + " (vis_bois_inox)", "a_valider": False},
    "insert_filete_m8": {"nom": "Insert filete inox M8 a visser (type Ensat)", "filetage": "M8",
                         "capacite_service": 2500.0,
                         "regle": "longueur 20 mm si densite >= 650 kg/m3, 25 mm en dessous ; colle epoxy conseillee",
                         "source": S.EQ_ATT + " (insert_filete_m8)", "a_valider": False},
    "vis_barillet_m8": {"nom": "Boulon + ecrou barillet M8 (cross-dowel)", "capacite_service": 4000.0,
                        "regle": "barillet d 10 a >= 2,5 d du bout ; demontable",
                        "source": S.EQ_ATT + " (vis_barillet_m8)", "a_valider": False},
    "taquet_5": {"nom": "Taquet d'etagere O5 (douille + pion)", "diametre": 5.0, "capacite_service": None,
                 "regle": "4 taquets par etagere ; percage O5 profondeur 10-12 au pas du systeme 32",
                 "source": S.A_VALIDER + " (absent des autres gammes ; capacite = fiche fabricant)",
                 "a_valider": True},
}

CHARNIERES = {
    "charniere_soss": {"nom": "Charniere invisible type Soss", "visible_ferme": False,
                       "cotes": {"longueur_boitier": 118.0, "largeur_boitier": 18.0, "profondeur_mortaise": 19.0,
                                 "epaisseur_min_bois": 22.0, "nombre_recommande": 3},
                       "capacite_service": None, "source": S.INC_FIX + " (CHARNIERE_SOSS)", "a_valider": False},
    "charniere_cuvette_35": {"nom": "Charniere a cuvette O35 (invisible, reglable 3D)", "visible_ferme": False,
                             "cotes": {"diametre_cuvette": 35.0, "epaisseur_min_bois": 16.0},
                             "capacite_service": None,
                             "source": S.A_VALIDER + " (standard commercial, absent des autres gammes)",
                             "a_valider": True},
    "penture_angle": {"nom": "Penture d'angle a terminaisons forgees", "visible_ferme": True, "cotes": {},
                      "capacite_service": None, "source": S.NEO_FER + " (penture_angle, sans cotes)",
                      "a_valider": True},
    "charniere_piano": {"nom": "Charniere piano inox (abattants, couvercles)", "visible_ferme": True, "cotes": {},
                        "capacite_service": None, "source": S.A_VALIDER, "a_valider": True},
}

VERINS = {
    "verin_compas": {"nom": "Verin ou compas de maintien (couvercles, abattants)", "visible_ferme": False,
                     "cotes": {"course": 150.0, "longueur_pliee": 200.0},
                     "source": S.INC_FIX + " (VERIN_COMPAS : a dimensionner selon la masse du couvercle)",
                     "a_valider": False},
}


def finition_metal_compatible(metal, finition):
    ent = FINITIONS_METAL.get(finition)
    return ent is not None and metal in ent["metaux"]
