# -*- coding: utf-8 -*-
"""Couche 2 — matériaux, visserie, compatibilité Vac-U-Lock, jonctions de cadres, matrices de gammes."""

from .materiaux import METAUX, BOIS, POLYMERES, JOINTS, HABILLAGE_HORS_ZONE_HUMIDE, materiau
from .visserie import (
    VISSERIE,
    AS_M8_MM2,
    charge_admissible_traction,
    charge_admissible_cisaillement,
    rapport_m8,
)
from .vac_u_lock import (
    COMPATIBILITE_CONTACT, COMPATIBILITE_CALES, FILETAGES_COTE_MACHINE,
    compatible_ergot, compatible_cale, filetage_cote_machine, rapport_arrachement,
)
from .jonctions_cadre import JONCTIONS, cotes_tenon, jonction
from .compatibilite import (
    GAMMES, INTERFACES, STATUTS, LEGENDE, NOMS_GAMMES,
    matrice_interfaces_gammes, decisions_a_trancher, matrice_markdown as matrice_interfaces_markdown,
)

__all__ = [
    "METAUX",
    "BOIS",
    "POLYMERES",
    "JOINTS",
    "HABILLAGE_HORS_ZONE_HUMIDE",
    "materiau",
    "VISSERIE",
    "AS_M8_MM2",
    "charge_admissible_traction",
    "charge_admissible_cisaillement",
    "rapport_m8",
    "COMPATIBILITE_CONTACT",
    "COMPATIBILITE_CALES",
    "FILETAGES_COTE_MACHINE",
    "compatible_ergot",
    "compatible_cale",
    "filetage_cote_machine",
    "rapport_arrachement",
    "JONCTIONS",
    "cotes_tenon",
    "jonction",
    "GAMMES",
    "INTERFACES",
    "STATUTS",
    "LEGENDE",
    "NOMS_GAMMES",
    "matrice_interfaces_gammes",
    "decisions_a_trancher",
    "matrice_interfaces_markdown",
]

