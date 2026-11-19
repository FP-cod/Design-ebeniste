# -*- coding: utf-8 -*-
"""Script Fusion 360 : crée/actualise tous les paramètres utilisateur ``tan_...``."""

from __future__ import annotations

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tantra_commun import fusion_assurer_parametre, parametres_typologie  # noqa: E402
from tantra import registre  # noqa: E402


def tous_les_parametres() -> dict:
    d = {}
    for nom in registre.REGISTRE:
        d.update(parametres_typologie(nom))
    return d


def run(context):  # noqa: ARG001 — signature imposée par Fusion
    import adsk.core
    import adsk.fusion

    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Ouvrir un document Fusion (environnement Design).")
            return
        d = tous_les_parametres()
        for nom, (val, unite, com) in d.items():
            fusion_assurer_parametre(design, nom, val, unite, com)
        ui.messageBox(f"{len(d)} paramètres Tantra créés ou actualisés (préfixe tan_, longueurs en mm).")
    except Exception:
        ui.messageBox(f"Échec :\n{traceback.format_exc()}")
