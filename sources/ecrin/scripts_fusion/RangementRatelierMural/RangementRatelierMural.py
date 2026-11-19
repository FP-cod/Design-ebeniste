# -*- coding: utf-8 -*-
"""Script Fusion Rangement : ratelier mural modulaire.

Copier le dossier du projet Rangement (contenant le paquet 'rangement') a cote
de ce dossier, ou regler RANGEMENT_RACINE ci-dessous. Fusion :
Utilitaires > Complements > Scripts et complements > + > ce dossier > Executer.
"""

import os
import sys
import importlib

# Racine du projet = dossier qui contient le paquet 'rangement'
RANGEMENT_RACINE = os.environ.get("RANGEMENT_RACINE") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))


def _charger():
    if RANGEMENT_RACINE not in sys.path:
        sys.path.insert(0, RANGEMENT_RACINE)
    # rechargement : prend en compte les modifications sans relancer Fusion
    for nom in [m for m in list(sys.modules) if m == "rangement" or m.startswith("rangement.")]:
        del sys.modules[nom]
    return importlib.import_module("rangement.grammaires.ratelier_mural")


def run(context):
    try:
        _charger().run(context)
    except Exception:
        import traceback
        import adsk.core
        adsk.core.Application.get().userInterface.messageBox("Rangement : %s" % traceback.format_exc())


def stop(context):
    pass
