# -*- coding: utf-8 -*-
"""Couche 1 — paramètres globaux partagés et utilitaires Fusion (sans import adsk)."""

from .params_globaux import Param, Parametres, SCHEMA, G, valider_parametres
from .fusion_utils import (
    MM_PAR_CM,
    mm_vers_cm,
    cm_vers_mm,
    cm,
    nom_fusion,
    fusion_disponible,
    parametres_exportables,
    exporter_user_parameters,
)

__all__ = [
    "Param",
    "Parametres",
    "SCHEMA",
    "G",
    "valider_parametres",
    "MM_PAR_CM",
    "mm_vers_cm",
    "cm_vers_mm",
    "cm",
    "nom_fusion",
    "fusion_disponible",
    "parametres_exportables",
    "exporter_user_parameters",
]
