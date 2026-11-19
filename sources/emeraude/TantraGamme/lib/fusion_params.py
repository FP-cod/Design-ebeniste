# -*- coding: utf-8 -*-
"""Pont Fusion 360 : pousse la couche 1 dans les *User Parameters* du design.

``adsk`` n'est importé QU'À L'APPEL : ce module se compile et s'importe hors
Fusion, sans erreur, ce qui garde les couches 1-2 testables en pur Python.
"""
from __future__ import annotations

try:
    from . import params_globaux as pg
except ImportError:  # pragma: no cover
    import params_globaux as pg  # type: ignore


def creer_ou_mettre_a_jour_parametres(design, p: pg.ParametresGlobaux = pg.PARAMS) -> int:
    """Crée/actualise les paramètres utilisateur ``TG_*`` dans ``design``.

    Retourne le nombre de paramètres écrits. Les valeurs passent par
    ``ValueInput.createByString("<valeur> <unité>")`` : Fusion gère la
    conversion mm→cm interne.
    """
    import adsk.core  # import local : indisponible hors Fusion

    up = design.userParameters
    n = 0
    for nom, (valeur, unite, commentaire) in pg.parametres_fusion(p).items():
        expr = f"{valeur} {unite}"
        existant = up.itemByName(nom)
        if existant:
            existant.expression = expr
            existant.comment = commentaire
        else:
            up.add(nom, adsk.core.ValueInput.createByString(expr), unite, commentaire)
        n += 1
    return n
