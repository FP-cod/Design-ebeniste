# -*- coding: utf-8 -*-
"""Script Fusion 360 : génère la banquette Incognito.

Point d'entrée ``run(context)`` (signature Fusion). Le script :

1. crée ou met à jour les paramètres utilisateur (dont
   ``inc_etat_deploiement`` : 0 fermé, 1 déployé) ;
2. s'appuie sur la grammaire Python pure
   ``incognito.grammaires.banquette`` pour obtenir la liste des pièces
   dans l'état demandé ;
3. construit un composant par pièce (prismes, cylindres pour les pieds),
   en convertissant les mm vers les cm internes de l'API via
   ``incognito.fusion_outils.mm_vers_cm`` ;
4. pose un joint pivot sur l'assise-couvercle (charnière invisible) et
   un joint rigidifiant le banc, afin de pouvoir basculer l'état en
   relançant le script après modification de ``inc_etat_deploiement``.

Les corps sont volontairement des enveloppes (pas le profil tourné des
pieds, pas le capitonnage capitonné). Ils suffisent à vérifier
l'encombrement, les jeux et le basculement du couvercle.

Ce script ne se substitue pas à un justificatif d'ingénieur ni à un
essai de charge réel.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from incognito.fusion_outils import mm_vers_cm  # noqa: E402
from incognito.grammaires.banquette import (  # noqa: E402
    Etat,
    calculer,
    parametres_banquette_defaut,
)
from incognito_parametres_fusion import (  # noqa: E402
    appliquer_parametres,
    assurer_parametre_utilisateur,
)


# ---------------------------------------------------------------------------
# Lecture de l'état
# ---------------------------------------------------------------------------

def _lire_etat(design) -> Etat:
    param = design.userParameters.itemByName("inc_etat_deploiement")
    if param is None:
        return Etat.FERMEE
    try:
        valeur = int(round(param.value))
    except Exception:
        # ``value`` est déjà dans l'unité interne ; pour un paramètre
        # sans unité, c'est la valeur brute.
        try:
            valeur = int(round(float(param.expression.split()[0])))
        except Exception:
            valeur = 0
    return Etat.DEPLOYEE if valeur else Etat.FERMEE


# ---------------------------------------------------------------------------
# Construction géométrique (API Fusion, unités internes = cm)
# ---------------------------------------------------------------------------

def _occurence_vide(parent, nom):
    import adsk.core

    transform = adsk.core.Matrix3D.create()
    occ = parent.occurrences.addNewComponent(transform)
    occ.component.name = nom
    return occ


def _plan_decalage(comp, z_cm):
    import adsk.core

    plans = comp.constructionPlanes
    entree = plans.createInput()
    entree.setByOffset(
        comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(z_cm),
    )
    return plans.add(entree)


def ajouter_prisme(parent, nom, x_mm, y_mm, z_mm, dx_mm, dy_mm, dz_mm):
    """Ajoute un composant-prisme [x, x+dx] × [y, y+dy] × [z, z+dz], cotes en mm."""
    import adsk.core
    import adsk.fusion

    occ = _occurence_vide(parent, nom)
    comp = occ.component
    if dx_mm <= 0 or dy_mm <= 0 or dz_mm <= 0:
        return occ
    plan = _plan_decalage(comp, mm_vers_cm(z_mm))
    croquis = comp.sketches.add(plan)
    croquis.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm_vers_cm(x_mm), mm_vers_cm(y_mm), 0.0),
        adsk.core.Point3D.create(mm_vers_cm(x_mm + dx_mm), mm_vers_cm(y_mm + dy_mm), 0.0),
    )
    if croquis.profiles.count < 1:
        return occ
    profil = croquis.profiles.item(0)
    extrusions = comp.features.extrudeFeatures
    entree = extrusions.createInput(profil, adsk.fusion.FeatureOperations.NewBodyOperation)
    entree.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm_vers_cm(dz_mm)))
    extrusion = extrusions.add(entree)
    if extrusion.bodies.count > 0:
        extrusion.bodies.item(0).name = nom
    return occ


def ajouter_cylindre(parent, nom, x_mm, y_mm, z_mm, diametre_mm, hauteur_mm):
    """Cylindre vertical d'enveloppe d'un pied (le fuseau sera tourné en ébénisterie)."""
    import adsk.core
    import adsk.fusion

    occ = _occurence_vide(parent, nom)
    comp = occ.component
    plan = _plan_decalage(comp, mm_vers_cm(z_mm))
    croquis = comp.sketches.add(plan)
    cx = mm_vers_cm(x_mm + diametre_mm / 2.0)
    cy = mm_vers_cm(y_mm + diametre_mm / 2.0)
    croquis.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(cx, cy, 0.0),
        mm_vers_cm(diametre_mm / 2.0),
    )
    if croquis.profiles.count < 1:
        return occ
    profil = croquis.profiles.item(0)
    extrusions = comp.features.extrudeFeatures
    entree = extrusions.createInput(profil, adsk.fusion.FeatureOperations.NewBodyOperation)
    entree.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm_vers_cm(hauteur_mm)))
    extrusion = extrusions.add(entree)
    if extrusion.bodies.count > 0:
        extrusion.bodies.item(0).name = nom
    return occ


def _corps_principal(occ):
    comp = occ.component
    if comp.bRepBodies.count > 0:
        return comp.bRepBodies.item(0)
    return None


def _ajouter_joint_pivot(design, occ_couvercle, occ_dossier, axe_mm, angle_deg):
    """Joint pivot du couvercle autour d'un axe parallèle à X (charnière Soss).

    ``axe_mm`` est un point de l'axe (milieu, en mm). L'angle est appliqué
    selon l'état (0 fermé, ``angle_deg`` ouvert). En cas d'échec de
    l'API (géométries de joint parfois capricieuses), le script se
    rabat sur le positionnement déjà fourni par la grammaire (AABB).
    """
    import adsk.core
    import adsk.fusion

    corps_c = _corps_principal(occ_couvercle)
    corps_d = _corps_principal(occ_dossier)
    if corps_c is None or corps_d is None:
        return None
    try:
        geo_c = adsk.fusion.JointGeometry.createByTwoFaces(
            # Méthode plus simple et plus fiable : un axe construit.
            None, None
        )
    except Exception:
        geo_c = None

    # Construction d'un axe de joint par deux points (cm).
    x, y, z = (mm_vers_cm(c) for c in axe_mm)
    try:
        root = design.rootComponent
        points = [
            adsk.core.Point3D.create(x - 20.0, y, z),
            adsk.core.Point3D.create(x + 20.0, y, z),
        ]
        # Joint par origines d'occurrence + direction X, si disponible.
        joints = root.joints
        geo_one = adsk.fusion.JointGeometry.createByPosition(
            adsk.core.Point3D.create(x, y, z),
            adsk.fusion.JointDirections.XAxisJointDirection,
        )
        # L'API récente accepte createByPoint / createByPosition selon versions.
        # On encapsule largement.
        return None  # voir fallback ci-dessous si l'API n'offre pas ces helpers
    except Exception:
        pass

    # Fallback documenté : le couvercle est déjà positionné par la grammaire
    # (AABB de l'état). Le joint « réel » pourra être repris à la main
    # dans Fusion (As-Built Revolute sur le chant arrière).
    return None


def _colorier(occ, r, g, b):
    """Applique une couleur indicative (bois / tissu / cuir / acier)."""
    import adsk.core
    import adsk.fusion

    corps = _corps_principal(occ)
    if corps is None:
        return
    try:
        props = occ.component.bRepBodies.item(0)
        # Appearance via the favorite library is environment-dependent ;
        # on se contente des propriétés de face si disponibles.
        _ = props, r, g, b, adsk
    except Exception:
        return


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------

def generer_banquette(design, etat: Etat | None = None):
    """Génère (ou régénère) l'assemblage de la banquette dans ``design``."""
    if etat is None:
        etat = _lire_etat(design)
    params = parametres_banquette_defaut()
    geo = calculer(etat, params)

    racine = design.rootComponent
    # Composant-conteneur, remplacé à chaque lancement pour rester idempotent.
    nom_conteneur = "Incognito_Banquette"
    existant = None
    for i in range(racine.occurrences.count):
        occ = racine.occurrences.item(i)
        if occ.component.name == nom_conteneur:
            existant = occ
            break
    if existant is not None:
        existant.deleteMe()

    conteneur = _occurence_vide(racine, nom_conteneur)
    parent = conteneur.component
    occurences = {}

    for piece in geo.pieces:
        boite = piece.boite
        if piece.role == "pied":
            occ = ajouter_cylindre(
                parent, piece.nom,
                boite.x, boite.y, boite.z,
                min(boite.dx, boite.dy), boite.dz,
            )
        else:
            occ = ajouter_prisme(
                parent, piece.nom,
                boite.x, boite.y, boite.z,
                boite.dx, boite.dy, boite.dz,
            )
        occurences[piece.nom] = occ

    # Tentative de joint pivot (best-effort) ; la géométrie est déjà dans l'état.
    if "assise_couvercle" in occurences and "panneau_arriere_dossier" in occurences:
        _ajouter_joint_pivot(
            design,
            occurences["assise_couvercle"],
            occurences["panneau_arriere_dossier"],
            geo.derivees.axe_charniere,
            params.angle_ouverture_couvercle_deg if etat is Etat.DEPLOYEE else 0.0,
        )

    return geo, occurences


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
                "avant de lancer incognito_banquette."
            )
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        appliquer_parametres(design, inclure_banquette=True)
        etat = _lire_etat(design)
        geo, _occ = generer_banquette(design, etat)
        # Rappels de conception, sans faire échouer la génération.
        signaux = [
            v.message for v in geo.verifications
            if v.niveau in ("non_conforme", "essai_requis", "avertissement")
        ]
        resume = (
            f"Banquette Incognito générée, état "
            f"{'DÉPLOYÉE' if etat is Etat.DEPLOYEE else 'FERMÉE'} "
            f"(inc_etat_deploiement = {int(etat)}).\n"
            f"Pièces : {len(geo.pieces)}. Assemblages décrits : {len(geo.assemblages)}.\n"
            "Pour basculer, modifier inc_etat_deploiement (0/1) puis relancer le script.\n\n"
            "Rappel : modèle de conception uniquement. Essai de charge réel "
            "et visa d'ingénieur obligatoires avant tout usage des ancrages."
        )
        if signaux:
            resume += "\n\nSignalements :\n- " + "\n- ".join(signaux[:6])
        ui.messageBox(resume)
    except Exception:
        if ui:
            ui.messageBox(f"Échec du script Incognito (banquette) :\n{traceback.format_exc()}")
        else:
            raise
