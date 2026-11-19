# -*- coding: utf-8 -*-
"""Visserie M8 — hypothèses de charge admissible (traction / cisaillement).

Ces calculs sont des **ordres de grandeur de conception**. Ils ne remplacent
ni la CMU marquée du fabricant, ni un essai réel, ni une note d'ingénieur.

Hypothèses (à citer telles quelles dans tout rapport) :

- Filetage M8 × 1,25 (pas gros), section résistante As = 36,6 mm² (ISO 898-1
  / ISO 3506). Pas issu des scripts de meubles, valeur de norme.
- Traction : F_el = Rp0,2 × As  (limite élastique conventionnelle, pas Rm).
- Cisaillement sur la partie filetée, un plan : F_c = 0,6 × Rp0,2 × As.
  Le coefficient 0,6 est une hypothèse courante (Tresca / pratique boulonnerie),
  pas une valeur de norme de levage.
- Cisaillement sur fût lisse (si le plan de cisaillement est non fileté) :
  F_c_fut = 0,6 × Rp0,2 × (π d² / 4) avec d = 8 mm (A = 50,27 mm²).
- Charge admissible (CMU de calcul) = F / coefficient_securite.
- Classe A4-70 (inox, cohérente avec la quincaillerie « inox A4 » Equinox) :
  Rm = 700 MPa, Rp0,2 = 450 MPa (ISO 3506).
- Classe 8.8 (acier, donnée pour comparaison, à zinguer / ne pas laisser
  apparente en milieu humide) : Rm = 800 MPa, Rp0,2 = 640 MPa (ISO 898-1).
- Barre / tôle inox 316 recuit (catalogue Equinox, Re = 200 MPa) : ce n'est
  PAS une vis ; ne pas l'utiliser comme Rp0,2 de visserie.

Limite pratique côté meuble : la CMU catalogue de l'œillet Equinox est 2000 N,
celle de l'insert M8 2500 N — très inférieures à la capacité d'une vis M8 A4-70
avec CS 3. C'est le meuble, pas la vis, qui dimensionne l'accroche.
"""

import math

AS_M8_MM2 = 36.6
DIAMETRE_M8_MM = 8.0
PAS_M8_MM = 1.25
AIRE_FUT_M8_MM2 = math.pi * (DIAMETRE_M8_MM ** 2) / 4.0  # 50.27
COEF_CISAILLEMENT = 0.6

CLASSES = {
    "A4-70": {
        "nom": "Inox austénitique A4-70 (ISO 3506)",
        "Rm_mpa": 700.0,
        "Rp02_mpa": 450.0,
        "source": "ISO 3506 (classe 70). Cohérent avec la désignation « vis inox A4 » Equinox.",
        "usage": "visserie et tiges d'ancrage apparentes, environnement humide / nettoyage",
    },
    "A2-70": {
        "nom": "Inox austénitique A2-70 (ISO 3506)",
        "Rm_mpa": 700.0,
        "Rp02_mpa": 450.0,
        "source": "ISO 3506 (classe 70). Moins résistant à la chloration que A4.",
        "usage": "alternative A4, à éviter avec désinfectants chlorés",
    },
    "8.8": {
        "nom": "Acier classe 8.8 (ISO 898-1)",
        "Rm_mpa": 800.0,
        "Rp02_mpa": 640.0,
        "source": "ISO 898-1",
        "usage": "comparaison uniquement ; protection anticorrosion obligatoire, pas en pièces de contact",
    },
}

# Axe de bride Ø6 (petit œillet DI 12) — pas une vis M8.
AS_M6_MM2 = 20.1
DIAMETRE_AXE_PETIT_OEIL_MM = 6.0
AIRE_FUT_6_MM2 = math.pi * (DIAMETRE_AXE_PETIT_OEIL_MM ** 2) / 4.0


def charge_elastique_traction(rp02_mpa, as_mm2=AS_M8_MM2):
    """Effort à la limite élastique en traction [N]."""
    return rp02_mpa * as_mm2


def charge_elastique_cisaillement(rp02_mpa, aire_mm2=AS_M8_MM2, coef=COEF_CISAILLEMENT):
    """Effort à la limite conventionnelle en cisaillement, un plan [N]."""
    return coef * rp02_mpa * aire_mm2


def charge_admissible_traction(classe="A4-70", coefficient_securite=3.0, as_mm2=AS_M8_MM2):
    """CMU de calcul en traction = (Rp0,2 × As) / CS [N]."""
    rp = CLASSES[classe]["Rp02_mpa"]
    if coefficient_securite <= 0:
        raise ValueError("coefficient_securite doit être > 0")
    return charge_elastique_traction(rp, as_mm2) / coefficient_securite


def charge_admissible_cisaillement(
    classe="A4-70",
    coefficient_securite=3.0,
    sur_fut_lisse=False,
    diametre_mm=DIAMETRE_M8_MM,
    as_mm2=AS_M8_MM2,
):
    """CMU de calcul en cisaillement, un plan [N]."""
    rp = CLASSES[classe]["Rp02_mpa"]
    aire = (math.pi * diametre_mm ** 2 / 4.0) if sur_fut_lisse else as_mm2
    if coefficient_securite <= 0:
        raise ValueError("coefficient_securite doit être > 0")
    return charge_elastique_cisaillement(rp, aire) / coefficient_securite


def rapport_m8(coefficient_securite=3.0, classe="A4-70"):
    """Dict de synthèse pour le rapport « points critiques »."""
    rp = CLASSES[classe]["Rp02_mpa"]
    f_t = charge_elastique_traction(rp)
    f_c = charge_elastique_cisaillement(rp, AS_M8_MM2)
    f_c_fut = charge_elastique_cisaillement(rp, AIRE_FUT_M8_MM2)
    # Axe Ø6 A4-70, cisaillement sur fût (goupille lisse dans l'œillet bas).
    f_c6 = charge_elastique_cisaillement(CLASSES["A4-70"]["Rp02_mpa"], AIRE_FUT_6_MM2)
    return {
        "classe": classe,
        "Rp02_mpa": rp,
        "As_mm2": AS_M8_MM2,
        "coefficient_securite": coefficient_securite,
        "hypotheses": (
            "Traction : Rp0,2 × As. Cisaillement un plan : 0,6 × Rp0,2 × aire. "
            "CMU = F / CS. Pas une CMU fabricant."
        ),
        "traction_elastique_N": f_t,
        "cisaillement_filete_elastique_N": f_c,
        "cisaillement_fut_elastique_N": f_c_fut,
        "traction_admissible_N": f_t / coefficient_securite,
        "cisaillement_filete_admissible_N": f_c / coefficient_securite,
        "cisaillement_fut_admissible_N": f_c_fut / coefficient_securite,
        "axe6_cisaillement_fut_elastique_N": f_c6,
        "axe6_cisaillement_fut_admissible_N": f_c6 / coefficient_securite,
        "limite_meuble_oeillet_equinox_N": 2000.0,
        "limite_meuble_insert_m8_equinox_N": 2500.0,
        "limite_meuble_anneau_equinox_N": 2500.0,
    }


VISSERIE = {
    "m8_a4_70": {
        "nom": "Vis / tige filetée M8 inox A4-70",
        "filetage": "M8",
        "pas": PAS_M8_MM,
        "As": AS_M8_MM2,
        "classe": "A4-70",
        "famille": "visserie",
        "usage": "brides, chapes, inserts côté accessoire, tige d'anneau (côté machine)",
    },
    "m8_ecrou_a4": {
        "nom": "Écrou M8 inox A4 (éventuellement Nylstop / frein filet)",
        "filetage": "M8",
        "classe": "A4-70",
        "famille": "visserie",
        "usage": "serrage de chape ; prévoir un frein (frein-filet ou écrou à insert)",
    },
    "m8_rondelle_a4": {
        "nom": "Rondelle plate M8 inox A4",
        "filetage": "M8",
        "famille": "visserie",
        "usage": "sous tête et sous écrou, notamment sur bois ou laiton",
    },
    "goupille_arbre_12": {
        "nom": "Goupille fendue ou clip de débrayage sur arbre Ø12",
        "famille": "securite",
        "usage": "débrayage rapide manivelle / accouplement (arrêt d'urgence mécanique)",
    },
}
