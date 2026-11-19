# -*- coding: utf-8 -*-
"""Script Fusion Equinox : chaise_trone.

Copier le dossier du projet Equinox (contenant le paquet 'equinox') a cote de
ce dossier, ou regler EQUINOX_RACINE ci-dessous. Fusion :
Utilitaires > Complements > Scripts et complements > + > ce dossier > Executer.
"""

import os
import sys
import importlib

# Racine du projet = dossier qui contient le paquet 'equinox'
EQUINOX_RACINE = os.environ.get("EQUINOX_RACINE") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))


def _charger():
    if EQUINOX_RACINE not in sys.path:
        sys.path.insert(0, EQUINOX_RACINE)
    # rechargement : prend en compte les modifications sans relancer Fusion
    for nom in [m for m in list(sys.modules) if m == "equinox" or m.startswith("equinox.")]:
        del sys.modules[nom]
    return importlib.import_module("equinox.grammaires.chaise_trone")


def run(context):
    try:
        _charger().run(context)
    except Exception:
        import traceback
        import adsk.core
        adsk.core.Application.get().userInterface.messageBox("Equinox : %s" % traceback.format_exc())


def stop(context):
    pass
