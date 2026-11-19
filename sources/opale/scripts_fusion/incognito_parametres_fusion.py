# -*- coding: utf-8 -*-
"""Script Fusion 360 : crée ou met à jour les paramètres utilisateur Incognito.

Usage : ouvrir un document Design dans Fusion, puis lancer ce script.
Les valeurs restent exprimées en mm (unité utilisateur). La conversion
vers les cm internes de l'API n'est nécessaire que pour construire de
la géométrie (voir ``incognito.fusion_outils`` et
``incognito_banquette.py``).

Ce module gère l'existant : un paramètre déjà présent est mis à jour
(expression + commentaire), un paramètre absent est créé.

Le fichier est exécutable aussi bien depuis Fusion que (partiellement)
hors Fusion : sans ``adsk``, seules les fonctions pures restent
importables pour les tests.
"""

from __future__ import annotations

import os
import sys
import traceback

# Rendre le package incognito importable lorsque le script est lancé
# depuis le dossier scripts de Fusion.
_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from incognito.parametres import (  # noqa: E402
    PARAMETRES_DEFAUT,
    ParametresGlobaux,
    vers_parametres_fusion,
)
from incognito.grammaires.banquette import (  # noqa: E402
    vers_parametres_fusion_banquette,
)
from incognito.grammaires.pouf_vibrant import (  # noqa: E402
    vers_parametres_fusion_pouf,
)


def expression_fusion(valeur: float, unite: str) -> str:
    """Construit l'expression utilisateur Fusion (« 430 mm », ou « 3 » si sans unité)."""
    if unite:
        return f"{valeur} {unite}"
    # Les entiers « propres » s'écrivent sans décimale, plus lisible pour un état 0/1.
    if float(valeur) == int(valeur):
        return str(int(valeur))
    return repr(valeur)


def assurer_parametre_utilisateur(design, nom, valeur, unite, commentaire):
    """Crée ou met à jour un paramètre utilisateur Fusion.

    ``design`` est un ``adsk.fusion.Design``. Retourne le paramètre.
    """
    import adsk.core

    user_params = design.userParameters
    expression = expression_fusion(valeur, unite)
    existant = user_params.itemByName(nom)
    if existant:
        try:
            existant.expression = expression
        except Exception:
            # Certains paramètres liés peuvent refuser l'écriture : on conserve
            # alors la valeur existante et on met à jour le commentaire.
            pass
        existant.comment = commentaire
        return existant
    return user_params.add(
        nom,
        adsk.core.ValueInput.createByString(expression),
        unite or "",
        commentaire,
    )


def appliquer_parametres(design, parametres: ParametresGlobaux | None = None, inclure_banquette: bool = True, inclure_pouf: bool = True):
    """Applique le vocabulaire Incognito (et, par défaut, les cotes de banquette)."""
    dico = vers_parametres_fusion(parametres or PARAMETRES_DEFAUT)
    if inclure_banquette:
        dico.update(vers_parametres_fusion_banquette())
    if inclure_pouf:
        dico.update(vers_parametres_fusion_pouf())
    crees, mis_a_jour = 0, 0
    for nom, (valeur, unite, commentaire) in dico.items():
        existait = design.userParameters.itemByName(nom) is not None
        assurer_parametre_utilisateur(design, nom, valeur, unite, commentaire)
        if existait:
            mis_a_jour += 1
        else:
            crees += 1
    return crees, mis_a_jour


def run(context):  # noqa: ARG001 — signature imposée par Fusion
    """Point d'entrée Fusion 360."""
    import adsk.core
    import adsk.fusion

    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox(
                "Ouvrir un document Fusion (environnement Design) "
                "avant de lancer incognito_parametres_fusion."
            )
            return
        crees, mis_a_jour = appliquer_parametres(design)
        ui.messageBox(
            "Paramètres Incognito appliqués.\n"
            f"Créés : {crees}. Mis à jour : {mis_a_jour}.\n"
            "Les longueurs sont en mm. L'état de la banquette "
            "(inc_etat_deploiement) vaut 0 (fermée) par défaut."
        )
    except Exception:
        if ui:
            ui.messageBox(f"Échec du script Incognito (paramètres) :\n{traceback.format_exc()}")
        else:
            raise
