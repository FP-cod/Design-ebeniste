# -*- coding: utf-8 -*-
"""Construction d'un ``Plan`` Rangement dans Autodesk Fusion (API Python).

C'est le SEUL module qui parle cm : l'API Fusion exprime les longueurs
internes en centimetres (``ValueInput.createByReal``, ``Point3D.create``),
alors que la gamme raisonne en mm. ``cm(v_mm)`` fait la conversion.

Strategie de construction (independante du sens des normales de plans) :
chaque primitive est esquissee sur un plan de construction decale passant
par son CENTRE, puis extrudee symetriquement sur toute sa longueur
(``setSymmetricExtent(..., isFullLength=True)``).

Les imports ``adsk`` sont differes (``_adsk``) : le module s'importe hors
Fusion et les tests injectent un mock dans ``sys.modules``.
"""

import json
import os
import traceback

from .geometrie import Boite, Cylindre

MM_PAR_CM = 10.0


def cm(v_mm):
    """mm -> cm (unite interne de l'API Fusion)."""
    return float(v_mm) / MM_PAR_CM


def _adsk():
    import adsk.core
    import adsk.fusion
    return adsk.core, adsk.fusion


def fusion_disponible():
    try:
        _adsk()
        return True
    except ImportError:
        return False


class Constructeur(object):
    """Construit les primitives d'un plan dans un design Fusion."""

    def __init__(self, design):
        self.core, self.fusion = _adsk()
        self.design = design
        self.racine = design.rootComponent
        self.erreurs = []
        self.nb_corps = 0

    # -- outils ---------------------------------------------------------------
    def pt(self, p):
        return self.core.Point3D.create(cm(p[0]), cm(p[1]), cm(p[2]))

    def val(self, v_mm):
        return self.core.ValueInput.createByReal(cm(v_mm))

    def plan_decale(self, comp, axe, decalage_mm):
        """Plan normal a ``axe`` ('x' -> YZ, 'y' -> XZ, 'z' -> XY) decale de ``decalage_mm``."""
        base = {"x": comp.yZConstructionPlane, "y": comp.xZConstructionPlane, "z": comp.xYConstructionPlane}[axe]
        # Securite : si la normale du plan d'origine pointe vers -axe, le decalage change de signe.
        try:
            composante = float(getattr(base.geometry.normal, axe))
            if composante < 0:
                decalage_mm = -decalage_mm
        except Exception:  # pragma: no cover - geometrie indisponible
            pass
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(base, self.val(decalage_mm))
        return comp.constructionPlanes.add(inp)

    def nouveau_composant(self, parent, nom):
        occ = parent.occurrences.addNewComponent(self.core.Matrix3D.create())
        occ.component.name = nom
        return occ.component

    def _profil(self, sketch, nb_boucles):
        for i in range(sketch.profiles.count):
            prof = sketch.profiles.item(i)
            if prof.profileLoops.count == nb_boucles:
                return prof
        return sketch.profiles.item(0)

    def _extruder_symetrique(self, comp, profil, longueur_mm, nom):
        feats = comp.features.extrudeFeatures
        inp = feats.createInput(profil, self.fusion.FeatureOperations.NewBodyFeatureOperation)
        inp.setSymmetricExtent(self.val(longueur_mm), True)
        feat = feats.add(inp)
        try:
            corps = feat.bodies.item(0)
            corps.name = nom
            self.nb_corps += 1
            return corps
        except Exception:  # pragma: no cover - depend de Fusion
            return None

    # -- primitives -------------------------------------------------------------
    def boite(self, comp, b):
        cx, cy, cz = b.centre
        s = comp.sketches.add(self.plan_decale(comp, "z", cz))
        s.name = b.nom
        c = s.modelToSketchSpace(self.pt((cx, cy, cz)))
        coin = s.modelToSketchSpace(self.pt((cx + b.dx / 2.0, cy + b.dy / 2.0, cz)))
        s.sketchCurves.sketchLines.addCenterPointRectangle(c, coin)
        return self._extruder_symetrique(comp, s.profiles.item(0), b.dz, b.nom)

    def cylindre(self, comp, c):
        centre = c.centre()
        i = "xyz".index(c.axe)
        s = comp.sketches.add(self.plan_decale(comp, c.axe, centre[i]))
        s.name = c.nom
        pc = s.modelToSketchSpace(self.pt(centre))
        cercles = s.sketchCurves.sketchCircles
        cercles.addByCenterRadius(pc, cm(c.diametre / 2.0))
        if c.paroi:
            cercles.addByCenterRadius(pc, cm(c.diametre / 2.0 - c.paroi))
            prof = self._profil(s, 2)
        else:
            prof = s.profiles.item(0)
        return self._extruder_symetrique(comp, prof, c.longueur, c.nom)

    def primitive(self, comp, prim):
        if isinstance(prim, Boite):
            return self.boite(comp, prim)
        if isinstance(prim, Cylindre):
            return self.cylindre(comp, prim)
        raise TypeError("Primitive non geree : %r" % prim)

    # -- plan ---------------------------------------------------------------------
    def construire(self, plan):
        parent = self.nouveau_composant(self.racine, "%s_%s" % (plan.params.get("gamme.nom"), plan.nom))
        for composant in plan.composants:
            comp = self.nouveau_composant(parent, composant.nom)
            for prim in composant.primitives:
                try:
                    self.primitive(comp, prim)
                except Exception:
                    self.erreurs.append("%s/%s : %s" % (composant.nom, prim.nom, traceback.format_exc(limit=1)))
        self.jonctions(parent, plan)
        return parent

    def jonctions(self, parent, plan):
        """Esquisse 'Jonctions' : un point par jonction + attributs JSON 'rangement'."""
        sk = parent.sketches.add(parent.xYConstructionPlane)
        sk.name = "Jonctions"
        for j in plan.jonctions:
            pt = sk.sketchPoints.add(self.pt(j.position))
            try:
                pt.attributes.add("rangement", j.nom, json.dumps({"type": j.type, "pieces": list(j.pieces),
                                                                   "details": j.details}, ensure_ascii=False))
            except Exception:  # pragma: no cover
                pass


def rapport_texte(plan):
    """Rapport lisible d'un plan (verifications, jonctions, notes)."""
    lignes = ["Rangement - %s" % plan.nom, "=" * 40]
    cg, m = plan.cg_structure()
    lignes.append("Masse structure : %.1f kg ; CG (%.0f, %.0f, %.0f) mm" % ((m,) + cg))
    if "charges_service" in plan.repere:
        lignes.append("Charges de service : %.1f kg" % plan.repere["charges_service"])
    lignes.append("\nVerifications :")
    lignes += ["  %s" % v for v in plan.verifications]
    lignes.append("\nJonctions (%d) :" % len(plan.jonctions))
    lignes += ["  - %s [%s] %s" % (j.nom, j.type, j.details) for j in plan.jonctions]
    if plan.notes:
        lignes.append("\nNotes :")
        lignes += ["  - %s" % n for n in plan.notes]
    return "\n".join(lignes)


def executer(context, concevoir, nom_script):
    """Point d'entree generique ``run(context)`` des grammaires."""
    core, fusion = _adsk()
    app = core.Application.get()
    ui = app.userInterface
    try:
        design = fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Rangement : ouvrir un design (espace Design) avant de lancer %s." % nom_script)
            return None
        plan = concevoir()
        crees, maj = plan.params.exporter_user_parameters(design)
        constructeur = Constructeur(design)
        constructeur.construire(plan)
        texte = rapport_texte(plan)
        try:
            chemin = os.path.join(os.path.expanduser("~"), "rangement_rapport_%s.txt" % plan.nom)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        except Exception:
            chemin = "(non ecrit)"
        resume = ("%s construit : %d corps, %d User Parameters crees, %d mis a jour.\n"
                  "Echecs : %d, alertes : %d, a relever (TODO) : %d, erreurs de construction : %d.\nRapport : %s"
                  % (plan.nom, constructeur.nb_corps, len(crees), len(maj), len(plan.echecs()), len(plan.alertes()),
                     len(plan.todos()), len(constructeur.erreurs), chemin))
        details = "\n".join(str(v) for v in plan.echecs() + plan.alertes() + plan.todos())
        ui.messageBox(resume + "\n\n" + details[:1500])
        return plan, constructeur
    except Exception:
        ui.messageBox("Rangement - erreur :\n%s" % traceback.format_exc())
        return None
