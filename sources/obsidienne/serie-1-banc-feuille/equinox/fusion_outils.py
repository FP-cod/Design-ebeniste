# -*- coding: utf-8 -*-
"""Construction d'un ``Plan`` Equinox dans Autodesk Fusion (API Python).

C'est le SEUL module qui parle cm : l'API Fusion exprime toutes les
longueurs internes en centimetres (``ValueInput.createByReal``,
``Point3D.create``), alors que la gamme raisonne en mm. ``cm(v_mm)`` fait la
conversion. Les angles internes de l'API sont en radians.

Les imports ``adsk`` sont differes (fonction ``_adsk``) : le module
s'importe hors Fusion, et les tests injectent un mock dans ``sys.modules``.
"""

import json
import math
import os
import traceback

from .geometrie import Boite, Disque, Fuseau, PlaqueContour, TubeCarre, TubeSpline

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

    # -- outils -------------------------------------------------------------
    def pt(self, p):
        return self.core.Point3D.create(cm(p[0]), cm(p[1]), cm(p[2]))

    def val(self, v_mm):
        return self.core.ValueInput.createByReal(cm(v_mm))

    def plan_z(self, comp, z_mm):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, self.val(z_mm))
        return comp.constructionPlanes.add(inp)

    def plan_sur_chemin(self, comp, courbe, t):
        inp = comp.constructionPlanes.createInput()
        inp.setByDistanceOnPath(courbe, self.core.ValueInput.createByReal(t))
        return comp.constructionPlanes.add(inp)

    def nouveau_composant(self, parent, nom):
        occ = parent.occurrences.addNewComponent(self.core.Matrix3D.create())
        occ.component.name = nom
        return occ.component

    def _nouveau_corps(self):
        return self.fusion.FeatureOperations.NewBodyFeatureOperation

    def _nommer(self, feature, nom):
        try:
            corps = feature.bodies.item(0)
            corps.name = nom
            self.nb_corps += 1
            return corps
        except Exception:  # pragma: no cover - depend de Fusion
            return None

    def _tourner_y(self, comp, corps, pivot, angle_deg):
        if not angle_deg or corps is None:
            return
        coll = self.core.ObjectCollection.create()
        coll.add(corps)
        m = self.core.Matrix3D.create()
        m.setToRotation(math.radians(angle_deg), self.core.Vector3D.create(0, 1, 0), self.pt(pivot))
        moves = comp.features.moveFeatures
        try:
            inp = moves.createInput2(coll)
            inp.defineAsFreeMove(m)
        except AttributeError:  # API anterieure a 2022
            inp = moves.createInput(coll, m)
        moves.add(inp)

    def _profil_a_boucles(self, sketch, nb_boucles):
        for i in range(sketch.profiles.count):
            prof = sketch.profiles.item(i)
            if prof.profileLoops.count == nb_boucles:
                return prof
        return sketch.profiles.item(0)

    def _conge(self, comp, corps, rayon_mm):
        if not rayon_mm or corps is None:
            return
        try:
            coll = self.core.ObjectCollection.create()
            for i in range(corps.edges.count):
                coll.add(corps.edges.item(i))
            inp = comp.features.filletFeatures.createInput()
            try:
                inp.edgeSetInputs.addConstantRadiusEdgeSet(coll, self.val(rayon_mm), True)
            except AttributeError:
                inp.addConstantRadiusEdgeSet(coll, self.val(rayon_mm), True)
            comp.features.filletFeatures.add(inp)
        except Exception as e:  # conge non bloquant
            self.erreurs.append("conge %s : %s" % (corps.name, e))

    # -- primitives ------------------------------------------------------------
    def fuseau(self, comp, f):
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = f.nom + "_axe"
        ligne = sk.sketchCurves.sketchLines.addByTwoPoints(self.pt(f.p0), self.pt(f.p1))
        ligne.isConstruction = False
        profils = []
        for t, p, d in ((0.0, f.p0, f.d0), (1.0, f.p1, f.d1)):
            plan = self.plan_sur_chemin(comp, ligne, t)
            s = comp.sketches.add(plan)
            s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(self.pt(p)), cm(d / 2.0))
            profils.append(s.profiles.item(0))
        inp = comp.features.loftFeatures.createInput(self._nouveau_corps())
        for prof in profils:
            inp.loftSections.add(prof)
        return self._nommer(comp.features.loftFeatures.add(inp), f.nom)

    def tube_spline(self, comp, t):
        core = self.core
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = t.nom + "_trajectoire"
        coll = core.ObjectCollection.create()
        for p in t.points:
            coll.add(self.pt(p))
        spline = sk.sketchCurves.sketchFittedSplines.add(coll)
        if t.ferme:
            try:
                spline.isClosed = True
            except Exception:
                pass
        chemin = comp.features.createPath(spline, False)
        plan = self.plan_sur_chemin(comp, spline, 0.0)
        s = comp.sketches.add(plan)
        centre = s.modelToSketchSpace(self.pt(t.points[0]))
        s.sketchCurves.sketchCircles.addByCenterRadius(centre, cm(t.diametre / 2.0))
        if t.paroi:
            s.sketchCurves.sketchCircles.addByCenterRadius(centre, cm(t.diametre / 2.0 - t.paroi))
            prof = self._profil_a_boucles(s, 2)
        else:
            prof = s.profiles.item(0)
        inp = comp.features.sweepFeatures.createInput(prof, chemin, self._nouveau_corps())
        return self._nommer(comp.features.sweepFeatures.add(inp), t.nom)

    def boite(self, comp, b):
        z0 = b.centre[2] - b.dz / 2.0
        s = comp.sketches.add(self.plan_z(comp, z0))
        c = s.modelToSketchSpace(self.pt((b.centre[0], b.centre[1], z0)))
        coin = s.modelToSketchSpace(self.pt((b.centre[0] + b.dx / 2.0, b.centre[1] + b.dy / 2.0, z0)))
        s.sketchCurves.sketchLines.addCenterPointRectangle(c, coin)
        ext = comp.features.extrudeFeatures.addSimple(s.profiles.item(0), self.val(b.dz), self._nouveau_corps())
        corps = self._nommer(ext, b.nom)
        self._conge(comp, corps, b.rayon_bord)
        self._tourner_y(comp, corps, b.pivot, b.angle_y)
        return corps

    def plaque(self, comp, p):
        s = comp.sketches.add(self.plan_z(comp, p.z_bas))
        coll = self.core.ObjectCollection.create()
        for x, y in p.contour:
            coll.add(s.modelToSketchSpace(self.pt((x, y, p.z_bas))))
        spline = s.sketchCurves.sketchFittedSplines.add(coll)
        try:
            spline.isClosed = True
        except Exception:
            pass
        ext = comp.features.extrudeFeatures.addSimple(s.profiles.item(0), self.val(p.epaisseur), self._nouveau_corps())
        corps = self._nommer(ext, p.nom)
        self._tourner_y(comp, corps, p.pivot, p.angle_y)
        return corps

    def disque(self, comp, d):
        s = comp.sketches.add(self.plan_z(comp, d.centre[2]))
        s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(self.pt(d.centre)), cm(d.diametre / 2.0))
        ext = comp.features.extrudeFeatures.addSimple(s.profiles.item(0), self.val(d.epaisseur), self._nouveau_corps())
        return self._nommer(ext, d.nom)

    def tube_carre(self, comp, t):
        sk = comp.sketches.add(comp.xYConstructionPlane)
        ligne = sk.sketchCurves.sketchLines.addByTwoPoints(self.pt(t.p0), self.pt(t.p1))
        chemin = comp.features.createPath(ligne, False)
        s = comp.sketches.add(self.plan_sur_chemin(comp, ligne, 0.0))
        c = s.modelToSketchSpace(self.pt(t.p0))
        for demi in (t.cote / 2.0, t.cote / 2.0 - t.paroi):
            coin = self.core.Point3D.create(c.x + cm(demi), c.y + cm(demi), c.z)
            s.sketchCurves.sketchLines.addCenterPointRectangle(c, coin)
        prof = self._profil_a_boucles(s, 2)
        inp = comp.features.sweepFeatures.createInput(prof, chemin, self._nouveau_corps())
        return self._nommer(comp.features.sweepFeatures.add(inp), t.nom)

    def primitive(self, comp, prim):
        table = ((Fuseau, self.fuseau), (TubeSpline, self.tube_spline), (Boite, self.boite),
                 (PlaqueContour, self.plaque), (Disque, self.disque), (TubeCarre, self.tube_carre))
        for classe, fn in table:
            if isinstance(prim, classe):
                return fn(comp, prim)
        raise TypeError("Primitive non geree : %r" % prim)

    # -- plan --------------------------------------------------------------------
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
        """Esquisse 'Jonctions' : un point nomme par jonction + attributs JSON."""
        sk = parent.sketches.add(parent.xYConstructionPlane)
        sk.name = "Jonctions"
        for j in plan.jonctions:
            pt = sk.sketchPoints.add(self.pt(j.position))
            try:
                pt.attributes.add("equinox", j.nom, json.dumps({"type": j.type, "pieces": list(j.pieces),
                                                                 "details": j.details}, ensure_ascii=False))
            except Exception:
                pass


def rapport_texte(plan, ajustements_params=()):
    """Rapport lisible d'un plan (verifications, ajustements, jonctions)."""
    lignes = ["Equinox - %s" % plan.nom, "=" * 40]
    cg, m = plan.cg_structure()
    lignes.append("Masse structure : %.1f kg ; CG (%.0f, %.0f, %.0f) mm" % ((m,) + cg))
    lignes.append("\nVerifications :")
    lignes += ["  %s" % v for v in plan.verifications]
    if plan.ajustements:
        lignes.append("\nAjustements materiaux -> geometrie :")
        lignes += ["  - %s" % a for a in plan.ajustements]
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
            ui.messageBox("Equinox : ouvrir un design (espace Design) avant de lancer %s." % nom_script)
            return None
        plan = concevoir()
        crees, maj = plan.params.exporter_user_parameters(design)
        constructeur = Constructeur(design)
        constructeur.construire(plan)
        texte = rapport_texte(plan)
        try:
            chemin = os.path.join(os.path.expanduser("~"), "equinox_rapport_%s.txt" % plan.nom)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        except Exception:
            chemin = "(non ecrit)"
        resume = ("%s construit : %d corps, %d User Parameters crees, %d mis a jour.\n"
                  "Echecs : %d, alertes : %d, erreurs de construction : %d.\nRapport : %s"
                  % (plan.nom, constructeur.nb_corps, len(crees), len(maj), len(plan.echecs()),
                     len(plan.alertes()), len(constructeur.erreurs), chemin))
        ui.messageBox(resume + "\n\n" + "\n".join(str(v) for v in plan.echecs() + plan.alertes())[:1500])
        return plan, constructeur
    except Exception:
        ui.messageBox("Equinox - erreur :\n%s" % traceback.format_exc())
        return None
