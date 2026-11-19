# -*- coding: utf-8 -*-
"""Outils communs des scripts Fusion 360 Tantra.

Chaque script de typologie :

1. crée/actualise les paramètres utilisateur ``tan_...`` (dont
   ``tan_<clé>_etat`` pour les meubles à deux états) ;
2. lit l'état demandé, appelle la grammaire Python pure via
   ``tantra.registre`` ;
3. reconstruit, dans un conteneur idempotent (supprimé puis recréé), un
   composant par pièce : esquisse du profil plan sur un plan décalé
   parallèle au plan du profil, extrusion **symétrique** de l'épaisseur.

Changer ``tan_<clé>_etat`` puis relancer le script régénère le modèle dans
l'autre état (les deux états sont des géométries complètes calculées à
partir des mêmes paramètres).

Hypothèse : document Fusion configuré « Z vers le haut ». Les cotes sont en
mm dans Tantra ; la conversion en cm (unité interne de l'API) passe
uniquement par ``tantra.fusion_outils``.

La partie « plan » (``plan_piece``) est en Python pur et testée ; seules les
fonctions préfixées ``fusion_`` touchent à ``adsk``.
"""

from __future__ import annotations

import os
import sys
import traceback

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from tantra.fusion_outils import mm_vers_cm  # noqa: E402
from tantra.parametres import PARAMETRES_DEFAUT, vers_parametres_fusion  # noqa: E402
from tantra import registre  # noqa: E402

PLAN_DE_BASE = {"x": "yZConstructionPlane", "y": "xZConstructionPlane", "z": "xYConstructionPlane"}


def plan_piece(piece) -> tuple[str, float, list[tuple[float, float, float]]]:
    """(plan de base, décalage du plan médian en mm, sommets 3D du profil en mm).

    Le profil est posé sur le plan médian de la pièce ; l'extrusion
    symétrique de ``piece.epaisseur`` restitue [début, début + épaisseur].
    """
    milieu = piece.debut + piece.epaisseur / 2.0
    pts = [piece.vers_3d(u, v, milieu) for (u, v) in piece.profil]
    return PLAN_DE_BASE[piece.axe], milieu, pts


def composante_axe(point, axe: str) -> float:
    return {"x": point[0], "y": point[1], "z": point[2]}[axe]


def expression_fusion(valeur: float, unite: str) -> str:
    if unite:
        return f"{valeur} {unite}"
    if float(valeur) == int(valeur):
        return str(int(valeur))
    return repr(valeur)


def parametres_typologie(nom: str) -> dict:
    """Paramètres globaux + paramètres propres à la typologie (pur Python)."""
    d = vers_parametres_fusion(PARAMETRES_DEFAUT)
    d.update(registre.parametres_fusion(nom))
    return d


# ---------------------------------------------------------------------------
# Partie Fusion (adsk)
# ---------------------------------------------------------------------------

def fusion_assurer_parametre(design, nom, valeur, unite, commentaire):
    import adsk.core

    up = design.userParameters
    expr = expression_fusion(valeur, unite)
    p = up.itemByName(nom)
    if p:
        p.comment = commentaire
        return p  # on ne réécrit pas : l'utilisateur a peut-être changé la valeur
    return up.add(nom, adsk.core.ValueInput.createByString(expr), unite or "", commentaire)


def fusion_lire_etat(design, nom_param: str | None) -> int:
    if not nom_param:
        return 0
    p = design.userParameters.itemByName(nom_param)
    if p is None:
        return 0
    try:
        return 1 if int(round(p.value)) else 0
    except Exception:
        return 0


def fusion_conteneur(design, nom: str):
    """Occurrence racine idempotente : l'ancienne est supprimée puis recréée."""
    import adsk.core

    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        occ = root.occurrences.item(i)
        if occ.component.name == nom:
            occ.deleteMe()
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = nom
    return occ


def fusion_plan_decale(comp, piece):
    """Plan médian de la pièce ; vérifie le signe du décalage via ``geometry.origin``."""
    import adsk.core

    base_nom, milieu, _ = plan_piece(piece)
    base = getattr(comp, base_nom)
    plans = comp.constructionPlanes
    for signe in (1.0, -1.0):
        e = plans.createInput()
        e.setByOffset(base, adsk.core.ValueInput.createByReal(signe * mm_vers_cm(milieu)))
        plan = plans.add(e)
        o = plan.geometry.origin
        n = plan.geometry.normal
        # distance signée du plan à l'origine selon l'axe d'extrusion
        dist = o.x * n.x + o.y * n.y + o.z * n.z
        axe_n = {"x": n.x, "y": n.y, "z": n.z}[piece.axe]
        if abs(dist * (1 if axe_n >= 0 else -1) - mm_vers_cm(milieu)) < 1e-4:
            return plan
        plan.deleteMe()
    raise RuntimeError(f"Plan décalé introuvable pour {piece.nom}.")


def fusion_ajouter_piece(parent_occ, piece):
    import adsk.core
    import adsk.fusion

    occ = parent_occ.component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = piece.nom
    plan = fusion_plan_decale(comp, piece)
    sk = comp.sketches.add(plan)
    _, _, pts = plan_piece(piece)
    pts_sk = [sk.modelToSketchSpace(adsk.core.Point3D.create(*(mm_vers_cm(c) for c in p))) for p in pts]
    lignes = sk.sketchCurves.sketchLines
    for a, b in zip(pts_sk, pts_sk[1:] + pts_sk[:1]):
        if a.distanceTo(b) > 1e-6:
            lignes.addByTwoPoints(a, b)
    if sk.profiles.count < 1:
        return occ
    # Profil le plus grand (sécurité si l'esquisse a produit des îlots)
    prof = max((sk.profiles.item(i) for i in range(sk.profiles.count)),
               key=lambda pr: pr.areaProperties().area)
    ext = comp.features.extrudeFeatures
    e = ext.createInput(prof, adsk.fusion.FeatureOperations.NewBodyOperation)
    e.setSymmetricExtent(adsk.core.ValueInput.createByReal(mm_vers_cm(piece.epaisseur)), True)
    f = ext.add(e)
    if f.bodies.count:
        f.bodies.item(0).name = piece.nom
    return occ


def fusion_construire(nom_typologie: str):
    """Corps du ``run(context)`` des scripts de typologie."""
    import adsk.core
    import adsk.fusion

    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Ouvrir un document Fusion (environnement Design).")
            return
        for nom, (val, unite, com) in parametres_typologie(nom_typologie).items():
            fusion_assurer_parametre(design, nom, val, unite, com)
        code = fusion_lire_etat(design, registre.nom_parametre_etat(nom_typologie))
        geo = registre.geometrie(nom_typologie, code if registre.entree(nom_typologie).deux_etats else None)
        cont = fusion_conteneur(design, f"tantra_{nom_typologie}")
        for piece in geo.pieces:
            try:
                fusion_ajouter_piece(cont, piece)
            except Exception:
                ui.messageBox(f"Pièce {piece.nom} non construite :\n{traceback.format_exc()}")
        alertes = [v for v in geo.verifications if v.niveau in ("non_conforme", "avertissement")]
        ui.messageBox(
            f"{nom_typologie} — état {geo.etat} : {len(geo.pieces)} pièces.\n"
            f"Vérifications non conformes / avertissements : {len(alertes)}.\n"
            "Modèles simplifiés : visa d'ingénieur et essai de charge réel obligatoires."
        )
    except Exception:
        ui.messageBox(f"Échec :\n{traceback.format_exc()}")
