# -*- coding: utf-8 -*-
"""Couche 2 — compatibilité Vac-U-Lock, filetages côté machine, cales d'ajustement.

Le port usiné est l'ergot (plug) mâle, pour recevoir n'importe quel accessoire
du marché dont la base porte la cavité Vac-U-Lock. Côté machine, l'ergot est
fileté (marché des adaptateurs : vaculocks.com). Ce n'est pas un filetage
1 pouce NPT (interface distincte, optionnelle).
"""

from __future__ import annotations

import math

from catalogues.materiaux import METAUX, POLYMERES, JOINTS, HABILLAGE_HORS_ZONE_HUMIDE
from catalogues.visserie import CLASSES, charge_elastique_cisaillement, AS_M8_MM2
from common.params_globaux import effort_vide_theorique_tete

# Section résistante M4 (ISO 898-1 / ISO 3506), pas gros.
AS_M4_MM2 = 8.78
AS_M5_MM2 = 14.2
AS_VIS = {"M3": 5.03, "M4": AS_M4_MM2, "M5": AS_M5_MM2, "M6": 20.1}

SRC_VACULOCKS = "https://vaculocks.com (adaptateurs usinés alu ou inox, filetage côté machine)"
SRC_PATENT_PAGE = "https://vac-u-lock.com/vac-u-lock-patent.html"

# Filetages relevés sur vaculocks.com. Pas, Ø et As : normes ISO 261 / ISO 898-1
# (métrique) et ASME B1.1 (UNC) ; G1/8 : ISO 228-1. Les As sont des valeurs
# de table, pas des CMU d'adaptateur.
FILETAGES_COTE_MACHINE = {
    "M6x1": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique",
        "diametre_mm": 6.0, "pas_mm": 1.0, "As_mm2": 20.1,
        "source": SRC_VACULOCKS,
    },
    "M8x1": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique_fin",
        "diametre_mm": 8.0, "pas_mm": 1.0, "As_mm2": 39.2,
        "source": SRC_VACULOCKS,
    },
    "M8x1.25": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique",
        "diametre_mm": 8.0, "pas_mm": 1.25, "As_mm2": AS_M8_MM2,
        "defaut": True,
        "note": "Défaut Aboutissants : cohérent avec les inserts Equinox et interface_oeillet_m8.",
        "source": SRC_VACULOCKS + " ; equinox/equinox/catalogues/attaches.py (insert_filete_m8)",
    },
    "M10x1": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique_fin",
        "diametre_mm": 10.0, "pas_mm": 1.0, "As_mm2": 64.9,
        "source": SRC_VACULOCKS,
    },
    "M10x1.5": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique",
        "diametre_mm": 10.0, "pas_mm": 1.5, "As_mm2": 58.0,
        "source": SRC_VACULOCKS,
    },
    "M12x1.75": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique",
        "diametre_mm": 12.0, "pas_mm": 1.75, "As_mm2": 84.3,
        "source": SRC_VACULOCKS,
    },
    "M16x2": {
        "norme": "ISO 261 / ISO 898-1", "famille": "metrique",
        "diametre_mm": 16.0, "pas_mm": 2.0, "As_mm2": 157.0,
        "source": SRC_VACULOCKS,
        "note": "Même Ø que la tige de sortie de la machine (16 mm) : filetage débouchant possible.",
    },
    "3/8-16 UNC": {
        "norme": "ASME B1.1", "famille": "unc",
        "diametre_mm": 9.525, "tpi": 16, "pas_mm": 25.4 / 16.0, "As_mm2": 50.0,
        "source": SRC_VACULOCKS,
    },
    "3/4-10 UNC": {
        "norme": "ASME B1.1", "famille": "unc",
        "diametre_mm": 19.05, "tpi": 10, "pas_mm": 25.4 / 10.0, "As_mm2": 215.5,
        "source": SRC_VACULOCKS,
    },
    "5/16-18 UNC": {
        "norme": "ASME B1.1", "famille": "unc",
        "diametre_mm": 7.9375, "tpi": 18, "pas_mm": 25.4 / 18.0, "As_mm2": 33.8,
        "source": SRC_VACULOCKS,
    },
    "1/4-20 UNC": {
        "norme": "ASME B1.1", "famille": "unc",
        "diametre_mm": 6.35, "tpi": 20, "pas_mm": 25.4 / 20.0, "As_mm2": 20.5,
        "source": SRC_VACULOCKS,
    },
    "G1/8": {
        "norme": "ISO 228-1 (BSPP)", "famille": "gaz_cylindrique",
        "diametre_mm": 9.728, "tpi": 28, "pas_mm": 25.4 / 28.0, "As_mm2": None,
        "source": SRC_VACULOCKS,
        "note": "Filetage gaz cylindrique, pas un filetage de traction type vis. "
                "Pas de section résistante normalisée ici ; ne pas le dimensionner comme un M8 "
                "sans justification (TODO si usage en traction).",
    },
}

FILETAGES_COTE_MACHINE_DEFAUT = "M8x1.25"


COMPATIBILITE_CONTACT = {
    "inox_316": {
        "role": "ergot, collier, cache métallique, raccord fileté, cales",
        "ok": True,
        "etat_surface": "Ra ≤ 0,8 µm sur l'ergot (emboîtement et nettoyage)",
        "note": METAUX["inox_316"].get("contact_silicone_pvc", ""),
    },
    "laiton_cw510l": {
        "role": "pièces sèches décoratives seulement, pas l'ergot de série",
        "ok": "limite",
        "note": "Contact cutané OK, mais le laiton se raye et se ternit ; l'ergot de travail reste en 316L.",
    },
    "alu_6082_t6": {
        "role": "platine / adaptateur, pas l'ergot de contact répété",
        "ok": "limite",
        "note": "Anodiser. Éviter le contact cyclique avec une cavité abrasive ou un désinfectant chloré. "
                "Les adaptateurs du marché (vaculocks.com) existent aussi en alu.",
    },
    "bois": {
        "role": "interdit pour l'ergot, la cavité et les cales",
        "ok": False,
        "note": "Poreux, non lavable, incompatible avec un emboîtement étanche et avec l'urine.",
    },
    "cuir": {
        "role": "habillage hors zone de l'ergot",
        "ok": False,
        "note": HABILLAGE_HORS_ZONE_HUMIDE["cuir"],
    },
    "sangle": {
        "role": "habillage / sanglage hors ergot",
        "ok": False,
        "note": HABILLAGE_HORS_ZONE_HUMIDE["sangle"],
    },
}

# Cales d'ajustement : mêmes familles que le contact fluide / ergot (316L ou polymère non poreux).
COMPATIBILITE_CALES = {
    "inox_316": {
        "ok": True,
        "role": "cales métalliques, rincables, répétables",
        "note": METAUX["inox_316"].get("contact_silicone_pvc", ""),
    },
    "pp_homopolymere": {
        "ok": True,
        "role": "cales polymère non poreuses, plus souples au contact d'une cavité silicone",
        "note": POLYMERES["pp_homopolymere"].get("notes", ""),
    },
    "pehd": {
        "ok": True,
        "role": "cales polymère non poreuses, un peu plus tendres que le PP",
        "note": POLYMERES["pehd"].get("notes", ""),
    },
}


def compatible_ergot(cle_materiau):
    """True si le matériau est admis pour l'ergot au contact silicone/PVC."""
    if cle_materiau in ("inox_316", "inox_316L", "inox_316l"):
        return True
    return False


def compatible_cale(cle_materiau):
    """True si le matériau est admis pour une cale d'ajustement."""
    return cle_materiau in COMPATIBILITE_CALES and COMPATIBILITE_CALES[cle_materiau]["ok"]


def filetage_cote_machine(cle):
    """Entrée de catalogue pour un filetage côté machine, ou KeyError."""
    if cle not in FILETAGES_COTE_MACHINE:
        raise KeyError("Filetage côté machine inconnu (hors catalogue vaculocks.com) : %s" % cle)
    return dict(FILETAGES_COTE_MACHINE[cle])


def rapport_arrachement(diametre_tete_mm, poussee_n=400.0, k_dyn=2.0,
                        verrouillage_type="collier_serrage", vis="M4",
                        nombre_vis=2, cs=3.0, classe="A4-70"):
    """Estime les efforts d'arrachement (hypothèses explicites).

    - Vide théorique max = patm × section de la tête (plafond, vide parfait).
    - Frottement cavité/ergot : non chiffré dans les sources (TODO) — ignoré
      par prudence, surtout en présence de lubrifiant ou de poudre.
    - Effort de calcul = poussée nominale validée × coefficient dynamique
      (400 N × 2 = 800 N). CS 3 pour l'ancrage / le collier.
    - Collier : cisaillement des vis (un plan), CMU = F_el / CS.
    - Durée de vie en cycles : aucune donnée fabricant trouvée (TODO).
    """
    vide = effort_vide_theorique_tete(diametre_tete_mm)
    f_calc = float(poussee_n) * float(k_dyn)
    as_mm2 = AS_VIS[vis]
    f_vis_el = charge_elastique_cisaillement(CLASSES[classe]["Rp02_mpa"], as_mm2)
    cmu_vis = (f_vis_el / cs) * int(nombre_vis)
    return {
        "vide_theorique_max_N": vide,
        "frottement_cavite_N": None,  # TODO, non publié
        "poussee_service_N": poussee_n,
        "coefficient_dynamique": k_dyn,
        "effort_calcul_N": f_calc,
        "verrouillage_type": verrouillage_type,
        "cmu_collier_vis_N": cmu_vis,
        "vis": "%s × %s %s, CS %g" % (nombre_vis, vis, classe, cs),
        "vide_suffisant": vide >= f_calc,
        "collier_suffisant": cmu_vis >= f_calc,
        "cycles_certifies": None,  # TODO
        "hypotheses": (
            "Vide parfait sur la section de tête (plafond). Frottement négligé. "
            "Poussée nominale validée %g N × k_dyn %g = %.0f N (CS 3 → effort d'ancrage %.0f N). "
            "Vis : 0,6 × Rp0,2 × As / CS, un plan. Cycles : pas de donnée publique."
            % (poussee_n, k_dyn, f_calc, f_calc * cs)
        ),
    }
