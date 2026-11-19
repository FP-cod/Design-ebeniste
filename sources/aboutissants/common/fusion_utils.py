# -*- coding: utf-8 -*-
"""Outils d'interface avec Fusion 360 (couche 1).

Convention identique aux trois gammes de meubles :

- toutes les longueurs internes sont en millimètres ;
- l'API Fusion attend des centimètres pour ``Point3D`` et
  ``ValueInput.createByReal`` ;
- la conversion mm → cm se fait ICI ET SEULEMENT ICI ;
- les User Parameters s'écrivent en expressions munies de leur unité
  (``"80 mm"``, ``"2 deg"``) : Fusion convertit lui-même ;
- les imports ``adsk`` sont différés, le module s'importe hors Fusion.
"""

from __future__ import annotations

import re

MM_PAR_CM = 10.0

# Unités exportées telles quelles vers Fusion ; MPa, kg/m3, mm2 n'ont pas
# d'unité User Parameter fiable → expression numérique nue + commentaire.
UNITES_FUSION = {
    "mm": "mm",
    "deg": "deg",
    "kg": "kg",
    "": "",
    "%": "",
    "N": "N",
    "N.m": "",
    "MPa": "",
    "kg/m3": "",
    "mm2": "",
    "m/s2": "",
    "liste_mm": None,  # non exporté
    "texte": None,
    "bool": None,
}


def mm_vers_cm(v_mm):
    """Convertit une longueur interne (mm) vers l'unité interne Fusion (cm)."""
    return float(v_mm) / MM_PAR_CM


def cm_vers_mm(v_cm):
    """Convertit une longueur des cm internes Fusion vers les mm du projet."""
    return float(v_cm) * MM_PAR_CM


# Alias Equinox.
cm = mm_vers_cm


def fusion_disponible():
    """True si l'API ``adsk`` est importable (session Fusion ou mock)."""
    try:
        import adsk.core  # noqa: F401
        import adsk.fusion  # noqa: F401
        return True
    except ImportError:
        return False


def nom_fusion(chemin, prefixe="abo_"):
    """'mouvement.course' -> 'abo_mouvement_course' (identifiant Fusion valide)."""
    nom = prefixe + re.sub(r"[^A-Za-z0-9_]", "_", chemin.replace(".", "_"))
    if not nom or not nom[0].isalpha():
        nom = "p" + nom
    return nom


def parametres_exportables(params):
    """Liste ``(nom, expression, unite_fusion, commentaire)`` des numériques.

    Les booléens, textes, listes et valeurs ``None`` (TODO) sont exclus :
    Fusion ne gère que des User Parameters numériques.
    """
    prefixe = params.get("gamme.prefixe_fusion", "abo_")
    res = []
    for chemin, meta, val in params.feuilles():
        if val is None or isinstance(val, bool) or not isinstance(val, (int, float)):
            continue
        unite_f = UNITES_FUSION.get(meta.unite, "")
        if unite_f is None:
            continue
        expression = ("%g %s" % (val, unite_f)).strip()
        commentaire = "%s [%s%s] %s" % (
            chemin,
            meta.statut,
            (" " + meta.unite) if meta.unite else "",
            (meta.role + (" | " + meta.source if meta.source else ""))[:200],
        )
        res.append((nom_fusion(chemin, prefixe), expression, unite_f, commentaire[:250]))
    return res


def exporter_user_parameters(design, params):
    """Crée ou met à jour les User Parameters de ``design`` (Fusion uniquement).

    Fusion convertit lui-même les expressions ``'80 mm'`` en cm internes.
    Renvoie ``(crees, mis_a_jour)``.
    """
    import adsk.core  # import différé : uniquement dans Fusion (ou mock)

    crees, maj = [], []
    ups = design.userParameters
    for nom, expression, unite, commentaire in parametres_exportables(params):
        existant = ups.itemByName(nom)
        if existant:
            existant.expression = expression
            existant.comment = commentaire
            maj.append(nom)
        else:
            ups.add(nom, adsk.core.ValueInput.createByString(expression), unite, commentaire)
            crees.append(nom)
    return crees, maj


def point3d(core, p_mm):
    """``Point3D`` Fusion à partir d'un triplet (x, y, z) en mm."""
    return core.Point3D.create(mm_vers_cm(p_mm[0]), mm_vers_cm(p_mm[1]), mm_vers_cm(p_mm[2]))


def valeur_reelle(core, v_mm):
    """``ValueInput`` en cm internes à partir d'une longueur mm."""
    return core.ValueInput.createByReal(mm_vers_cm(v_mm))


def ajouter_boite(comp, core, fusion, nom, origin_mm, dx_mm, dy_mm, dz_mm):
    """Ajoute un pavé (origine = coin min, dimensions en mm) dans ``comp``.

    Construction minimale : esquisse XY décalée + extrusion. Renvoie le corps
    (ou None hors Fusion / en cas d'échec).
    """
    try:
        sketches = comp.sketches
        planes = comp.constructionPlanes
        inp = planes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, valeur_reelle(core, origin_mm[2]))
        plan = planes.add(inp)
        sk = sketches.add(plan)
        sk.name = "sk_" + nom
        p0 = core.Point3D.create(mm_vers_cm(origin_mm[0]), mm_vers_cm(origin_mm[1]), 0)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            p0,
            core.Point3D.create(
                mm_vers_cm(origin_mm[0] + dx_mm),
                mm_vers_cm(origin_mm[1] + dy_mm),
                0,
            ),
        )
        prof = sk.profiles.item(0)
        ext_inp = comp.features.extrudeFeatures.createInput(prof, fusion.FeatureOperations.NewBodyFeatureOperation)
        ext_inp.setDistanceExtent(False, valeur_reelle(core, dz_mm))
        feat = comp.features.extrudeFeatures.add(ext_inp)
        corps = feat.bodies.item(0)
        corps.name = nom
        return corps
    except Exception:
        return None


def nouveau_composant(core, parent, nom):
    occ = parent.occurrences.addNewComponent(core.Matrix3D.create())
    occ.component.name = nom
    return occ.component
