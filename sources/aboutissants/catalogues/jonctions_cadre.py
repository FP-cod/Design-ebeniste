# -*- coding: utf-8 -*-
"""Couche 2 — jonctions des cadres modulaires (ébénisterie ou métal démontable).

Les règles d'ébénisterie sont *citées* des catalogues Equinox / Néogothique,
sans modifier ces dépôts. Les capacités de service sont des hypothèses de
catalogue, pas des CMU certifiées.
"""

from __future__ import annotations

# Règle Equinox : tenon = section/3 ; profondeur de mortaise = 0,8 × section receveuse.
REGLE_TENON_FRACTION = 1.0 / 3.0
REGLE_MORTAISE_FRACTION = 0.8

# Pente typique de queue d'aronde sur feuillu (règle d'atelier, pas une cote de meuble).
PENTE_QUEUE_D_ARONDE_FEUILLU = "1:6"

JONCTIONS = {
    "tenon_mortaise": {
        "nom": "Tenon-mortaise collé (éventuellement chevillé)",
        "famille": "ebenisterie",
        "demontable": False,
        "discretion": "haute",
        "modularite": "faible",
        "solidite": "haute",
        "capacite_service_N": 3000.0,
        "regle": "tenon = section/3 ; profondeur de mortaise = 0,8 × section receveuse ; cheville Ø8 décalée 1 mm (tire-fort).",
        "source": "equinox/equinox/catalogues/attaches.py (tenon_mortaise, capacite_service 3000 N)",
        "hypothese": "La capacité 3000 N est celle du catalogue Equinox, à confirmer par essai sur la section réelle.",
    },
    "queue_d_aronde": {
        "nom": "Queue d'aronde (collée, ou coulissante en variante)",
        "famille": "ebenisterie",
        "demontable": False,
        "discretion": "haute",
        "modularite": "faible",
        "solidite": "haute en traction dans le sens des queues",
        "capacite_service_N": None,  # non chiffrée dans les catalogues meubles
        "regle": "Pente 1:6 sur feuillu (hypothèse d'atelier). Variante coulissante plus démontable, moins rigide.",
        "source": "Pratique d'ébénisterie ; Néogothique mentionne des barres à queue d'aronde sous plateaux (catalogues/bois.py), sans CMU.",
        "hypothese": "Aucune CMU numérique dans les scripts de meubles : TODO essai. Ne pas inventer de charge.",
    },
    "tenon_clavete": {
        "nom": "Tenon traversant à clé (tusk tenon)",
        "famille": "ebenisterie",
        "demontable": True,
        "discretion": "moyenne (clé / bout de tenon visibles, chassés au nu possible)",
        "modularite": "moyenne",
        "solidite": "haute (cisaillement du bois en bout de tenon devant la clé)",
        "capacite_service_N": None,
        "regle": "Même fraction de tenon que le tenon-mortaise (tiers). Clé démontable, saillie à caler (Néogothique : saillie_tenon_clavete).",
        "source": "neogothique/neogothique/catalogues/attaches.py (tenon_traversant_clavete, demontable=True)",
        "hypothese": "Capacité non chiffrée en newtons dans le catalogue Néogothique : dimensionner par cisaillement du tenon et essayer.",
    },
    "raccord_metallique": {
        "nom": "Raccord métallique démontable (platine inox + barillet / vis M8)",
        "famille": "metal",
        "demontable": True,
        "discretion": "faible (sauf platine encastrée et bouchons affleurants)",
        "modularite": "haute",
        "solidite": "limitée par la vis et l'insert, pas par le bois massif",
        "capacite_service_N": 4000.0,
        "regle": "Barillet Ø10 à ≥ 2,5 d du bout, ou platine + insert M8. Filetage M8 aligné sur Equinox.",
        "source": "equinox/equinox/catalogues/attaches.py (vis_barillet_m8, capacite_service 4000 N ; insert_filete_m8, 2500 N)",
        "hypothese": "4000 N = capacité de service catalogue du barillet M8, pas une CMU certifiée. L'insert M8 Equinox est à 2500 N : le plus faible gouverne si on mixe.",
    },
}


def cotes_tenon(section_tenonnee_mm, section_receveuse_mm):
    """Cotes de tenon / mortaise selon la règle Equinox du tiers et de 0,8."""
    ep = float(section_tenonnee_mm) * REGLE_TENON_FRACTION
    profondeur = float(section_receveuse_mm) * REGLE_MORTAISE_FRACTION
    return {
        "tenon_epaisseur_mm": ep,
        "tenon_longueur_mm": profondeur,
        "mortaise_profondeur_mm": profondeur,
        "regle": "tiers / 0,8 (Equinox attaches.py)",
    }


def jonction(cle):
    if cle not in JONCTIONS:
        raise KeyError("Jonction de cadre inconnue : %s" % cle)
    return dict(JONCTIONS[cle])
