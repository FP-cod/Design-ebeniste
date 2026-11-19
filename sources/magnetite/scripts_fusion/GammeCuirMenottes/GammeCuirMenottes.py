# -*- coding: utf-8 -*-
"""Script Fusion GammeCuir : menottes / bracelets (poignet ou cheville).

Le dossier du projet (contenant le paquet 'gamme_cuir') doit etre deux niveaux
au-dessus de ce fichier (arborescence livree), ou indique par la variable
d'environnement GAMME_CUIR_RACINE. Fusion :
Utilitaires > Complements > Scripts et complements > + > ce dossier > Executer.

Reglages : editer gamme_cuir/parametres_gamme_cuir.json (cle "surcharges"),
par ex. {"produit.membre": "cheville", "finition.teinte": "noir",
"finition.quincaillerie": "inox_316", "finition.boucle": "boucle_rouleau_60_inox"}.
"""

import importlib
import os
import sys

GAMME_CUIR_RACINE = os.environ.get("GAMME_CUIR_RACINE") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))


def _charger():
    if GAMME_CUIR_RACINE not in sys.path:
        sys.path.insert(0, GAMME_CUIR_RACINE)
    # rechargement : prend en compte les modifications sans relancer Fusion
    for nom in [m for m in list(sys.modules) if m == "gamme_cuir" or m.startswith("gamme_cuir.")]:
        del sys.modules[nom]
    return importlib.import_module("gamme_cuir.grammaires.menottes")


def run(context):
    try:
        _charger().run(context)
    except Exception:
        import traceback
        import adsk.core
        adsk.core.Application.get().userInterface.messageBox("GammeCuir : %s" % traceback.format_exc())


def stop(context):
    pass
