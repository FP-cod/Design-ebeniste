# -*- coding: utf-8 -*-
"""Add-in Fusion 360 « TantraGamme » — point d'entrée.

Première passe : charge les couches 1-2 et crée les paramètres utilisateur
``TG_*`` dans le design actif. Les scripts de grammaire par typologie
(couche 3) seront ajoutés dans ``lib/typologies/`` après choix.
"""
import importlib
import os
import sys
import traceback

import adsk.core
import adsk.fusion

_DOSSIER = os.path.dirname(os.path.abspath(__file__))
if _DOSSIER not in sys.path:
    sys.path.insert(0, _DOSSIER)

from lib import params_globaux, catalogues, fusion_params  # noqa: E402

_app = None
_ui = None


def run(context):
    """Appelé par Fusion au démarrage de l'add-in."""
    global _app, _ui
    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        # Rechargement pour itérer sans redémarrer Fusion.
        for mod in (params_globaux, catalogues, fusion_params):
            importlib.reload(mod)
        design = adsk.fusion.Design.cast(_app.activeProduct)
        if not design:
            _ui.messageBox("Ouvrez un design Fusion avant de lancer TantraGamme.")
            return
        n = fusion_params.creer_ou_mettre_a_jour_parametres(design)
        p = params_globaux.PARAMS
        _ui.messageBox(
            f"TantraGamme : {n} paramètres TG_* créés/mis à jour.\n"
            f"Essence par défaut : {p.essence().nom}\n"
            f"Charge de conception : {p.charges.charge_verticale_N():.0f} N"
        )
    except Exception:  # pragma: no cover - affichage dans Fusion
        if _ui:
            _ui.messageBox("Échec TantraGamme :\n{}".format(traceback.format_exc()))


def stop(context):
    """Appelé par Fusion à l'arrêt de l'add-in."""
    pass
