# -*- coding: utf-8 -*-
"""Script Fusion 360 : génère le pouf vibrant Incognito.

Point d'entrée ``run(context)``. Le script crée les paramètres
``inc_sybian_gamme`` (0 entrée / 1 haut), ``inc_pouf_etat`` (0 pouf /
1 module), ``inc_module_vibration``, ``inc_module_piston``,
``inc_module_rotation``, ``inc_masse_housse``, génère un composant par
pièce, et peut exporter les STL imprimables + le moule de selle
(2 parties) via ``incognito.export_fabrication``.

Unités internes de l'API : cm, conversion par ``mm_vers_cm``.
"""

from __future__ import annotations

import os
import sys
import traceback

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from incognito.export_fabrication import exporter_tout  # noqa: E402
from incognito.fusion_outils import mm_vers_cm  # noqa: E402
from incognito.grammaires.pouf_vibrant import (  # noqa: E402
    Etat,
    calculer,
    parametres_pouf_defaut,
)
from incognito.parametres import GAMME_SYBIAN_ENTREE, GAMME_SYBIAN_HAUT  # noqa: E402
from incognito_parametres_fusion import appliquer_parametres  # noqa: E402


def _lire_entier(design, nom, defaut=0) -> int:
    param = design.userParameters.itemByName(nom)
    if param is None:
        return defaut
    try:
        return int(round(param.value))
    except Exception:
        try:
            return int(round(float(str(param.expression).split()[0])))
        except Exception:
            return defaut


def _lire_reel(design, nom, defaut=0.0) -> float:
    param = design.userParameters.itemByName(nom)
    if param is None:
        return defaut
    try:
        return float(param.value)
    except Exception:
        try:
            return float(str(param.expression).split()[0])
        except Exception:
            return defaut


def _occurence_vide(parent, nom):
    import adsk.core
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = nom
    return occ


def ajouter_prisme(parent, nom, x, y, z, dx, dy, dz):
    import adsk.core
    import adsk.fusion
    occ = _occurence_vide(parent, nom)
    comp = occ.component
    if min(dx, dy, dz) <= 0:
        return occ
    plans = comp.constructionPlanes
    entree_p = plans.createInput()
    entree_p.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(mm_vers_cm(z)))
    plan = plans.add(entree_p)
    croquis = comp.sketches.add(plan)
    croquis.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm_vers_cm(x), mm_vers_cm(y), 0.0),
        adsk.core.Point3D.create(mm_vers_cm(x + dx), mm_vers_cm(y + dy), 0.0),
    )
    if croquis.profiles.count < 1:
        return occ
    ext = comp.features.extrudeFeatures
    entree = ext.createInput(croquis.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyOperation)
    entree.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm_vers_cm(dz)))
    corps = ext.add(entree)
    if corps.bodies.count > 0:
        corps.bodies.item(0).name = nom
    return occ


def generer_pouf(design):
    etat = Etat.MODULE if _lire_entier(design, "inc_pouf_etat", 0) else Etat.POUF
    gamme = GAMME_SYBIAN_HAUT if _lire_entier(design, "inc_sybian_gamme", 1) else GAMME_SYBIAN_ENTREE
    params = parametres_pouf_defaut(
        gamme=gamme,
        module_vibration=bool(_lire_entier(design, "inc_module_vibration", 1)),
        module_piston=bool(_lire_entier(design, "inc_module_piston", 1)),
        module_rotation=bool(_lire_entier(design, "inc_module_rotation", 1)),
        masse_housse_kg=_lire_reel(design, "inc_masse_housse", 0.75) or 0.75,
    )
    geo = calculer(etat, params)
    racine = design.rootComponent
    nom = "Incognito_Pouf_Vibrant"
    for i in range(racine.occurrences.count):
        occ = racine.occurrences.item(i)
        if occ.component.name == nom:
            occ.deleteMe()
            break
    import adsk.core
    conteneur = racine.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    conteneur.component.name = nom
    parent = conteneur.component
    for piece in geo.pieces:
        b = piece.boite
        ajouter_prisme(parent, piece.nom, b.x, b.y, b.z, b.dx, b.dy, b.dz)
    return geo


def run(context):  # noqa: ARG001
    import adsk.core
    import adsk.fusion

    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Ouvrir un document Design avant de lancer incognito_pouf_vibrant.")
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        appliquer_parametres(design, inclure_banquette=False, inclure_pouf=True)
        geo = generer_pouf(design)
        dossier_stl = os.path.join(_RACINE, "exports_impression", "pouf_vibrant")
        fichiers = exporter_tout(dossier_stl)
        etat = "MODULE" if geo.etat is Etat.MODULE else "POUF"
        signaux = [v.message for v in geo.verifications if v.niveau in ("non_conforme", "essai_requis", "avertissement")]
        msg = (
            f"Pouf vibrant généré, état {etat}, gamme {geo.parametres.gamme}.\n"
            f"Pièces : {len(geo.pieces)}.\n"
            f"STL/moule exportés dans {dossier_stl} ({len(fichiers)} fichiers).\n"
            "Modifier inc_sybian_gamme, inc_pouf_etat, inc_module_* puis relancer.\n"
            "Rappel : 24 V DC uniquement, essai réel et conformité obligatoires."
        )
        if signaux:
            msg += "\n\nSignalements :\n- " + "\n- ".join(signaux[:6])
        ui.messageBox(msg)
    except Exception:
        if ui:
            ui.messageBox(f"Échec du script pouf vibrant :\n{traceback.format_exc()}")
        else:
            raise
