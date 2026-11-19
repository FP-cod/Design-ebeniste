# -*- coding: utf-8 -*-
"""Construction d'un ``Plan`` GammeCuir dans Autodesk Fusion (API Python).

SEUL module qui parle cm : l'API Fusion exprime les longueurs internes en
centimetres (``Point3D.create``, ``ValueInput.createByReal``) ; la gamme
raisonne en mm. ``cm(v_mm)`` fait la conversion.

Les imports ``adsk`` sont differes : le module s'importe hors Fusion et les
tests injectent un mock dans ``sys.modules`` (comme Equinox).

Apparences : pour chaque cle ('cuir', teinte) / ('metal', metal) /
('rembourrage', cle), on cherche d'abord un nom candidat dans les
bibliotheques d'apparences installees, sinon on copie la premiere apparence
trouvee et on la renomme / teinte avec le RVB indicatif du catalogue. Tout
echec est consigne dans ``Constructeur.erreurs`` sans interrompre la
construction.
"""

import os
import traceback

from .catalogues import cuirs, quincaillerie

MM_PAR_CM = 10.0
BIBLIOTHEQUES_APPARENCES = ("Fusion Appearance Library", "Fusion 360 Appearance Library")


def cm(v_mm):
    """mm -> cm (unite interne de l'API Fusion)."""
    return float(v_mm) / MM_PAR_CM


def _adsk():
    import adsk.core
    import adsk.fusion
    return adsk.core, adsk.fusion


def description_apparence(cle):
    """(nom a creer dans le design, rvb, noms candidats bibliotheque)."""
    famille, valeur = cle
    if famille == "cuir":
        t = cuirs.TEINTES[valeur]
        return "GammeCuir - cuir %s" % valeur, t["rgb"], t["apparences"]
    if famille == "metal":
        m = quincaillerie.METAUX[valeur]
        return "GammeCuir - %s" % valeur, m["rgb"], m["apparences"]
    return "GammeCuir - rembourrage %s" % valeur, (225, 215, 190), ["Foam", "Rubber - Soft"]


class Constructeur(object):
    """Construit les primitives d'un plan dans un design Fusion."""

    def __init__(self, design):
        self.core, self.fusion = _adsk()
        self.app = self.core.Application.get()
        self.design = design
        self.racine = design.rootComponent
        self.erreurs = []
        self.nb_corps = 0
        self.nb_percages = 0
        self.nb_points_couture = 0
        self._apparences = {}

    # -- outils -------------------------------------------------------------
    def pt(self, x, y, z=0.0):
        return self.core.Point3D.create(cm(x), cm(y), cm(z))

    def val(self, v_mm):
        return self.core.ValueInput.createByReal(cm(v_mm))

    def nouveau_composant(self, parent, nom):
        occ = parent.occurrences.addNewComponent(self.core.Matrix3D.create())
        occ.component.name = nom
        return occ.component

    def esquisse_z(self, comp, z_mm, nom=None):
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, self.val(z_mm))
        plan = comp.constructionPlanes.add(inp)
        sk = comp.sketches.add(plan)
        if nom:
            sk.name = nom
        return sk

    def dessiner(self, sketch, contour):
        """Dessine un contour (segments geometrie) dans l'esquisse (coordonnees XY ; z = plan)."""
        courbes = sketch.sketchCurves
        for s in contour:
            if s[0] == "ligne":
                courbes.sketchLines.addByTwoPoints(self.pt(*s[1]), self.pt(*s[2]))
            elif s[0] == "arc":
                _, c, r, a0, a1 = s
                from .geometrie import point_arc
                p0, pm, p1 = point_arc(c, r, a0), point_arc(c, r, (a0 + a1) / 2.0), point_arc(c, r, a1)
                courbes.sketchArcs.addByThreePoints(self.pt(*p0), self.pt(*pm), self.pt(*p1))
            elif s[0] == "cercle":
                courbes.sketchCircles.addByCenterRadius(self.pt(*s[1]), cm(s[2]))

    @staticmethod
    def profil(sketch, nb_boucles):
        """Profil ayant nb_boucles boucles (1 = plein, 2 = cadre avec jour), sinon le premier."""
        for i in range(sketch.profiles.count):
            prof = sketch.profiles.item(i)
            if prof.profileLoops.count == nb_boucles:
                return prof
        return sketch.profiles.item(0)

    def _nommer(self, feature, nom):
        try:
            corps = feature.bodies.item(0)
            corps.name = nom
            self.nb_corps += 1
            return corps
        except Exception:  # pragma: no cover - depend de Fusion
            return None

    # -- apparences -----------------------------------------------------------
    def apparence(self, cle):
        if cle in self._apparences:
            return self._apparences[cle]
        nom, rgb, candidats = description_apparence(cle)
        app_obj = None
        try:
            app_obj = self.design.appearances.itemByName(nom)
            if not app_obj:
                source = None
                for nom_bib in BIBLIOTHEQUES_APPARENCES:
                    bib = self.app.materialLibraries.itemByName(nom_bib)
                    if not bib:
                        continue
                    for cand in candidats:
                        source = bib.appearances.itemByName(cand)
                        if source:
                            break
                    if not source and bib.appearances.count:
                        source = bib.appearances.item(0)
                    if source:
                        break
                if source:
                    app_obj = self.design.appearances.addByCopy(source, nom)
                    self._teinter(app_obj, rgb)
        except Exception:
            self.erreurs.append("apparence %s : %s" % (nom, traceback.format_exc(limit=1)))
            app_obj = None
        self._apparences[cle] = app_obj
        return app_obj

    def _teinter(self, app_obj, rgb):
        try:
            props = app_obj.appearanceProperties
            for i in range(props.count):
                prop = self.core.ColorProperty.cast(props.item(i))
                if prop:
                    prop.value = self.core.Color.create(int(rgb[0]), int(rgb[1]), int(rgb[2]), 0)
                    return True
        except Exception:
            self.erreurs.append("teinte d'apparence non appliquee : %s" % traceback.format_exc(limit=1))
        return False

    def appliquer_apparence(self, corps, cle):
        a = self.apparence(cle)
        if corps is not None and a is not None:
            try:
                corps.appearance = a
            except Exception:  # pragma: no cover
                self.erreurs.append("apparence non appliquee sur %s" % getattr(corps, "name", "?"))

    # -- primitives -------------------------------------------------------------
    def plaque(self, comp, pr):
        sk = self.esquisse_z(comp, pr.z, pr.nom)
        self.dessiner(sk, pr.contour)
        for t in pr.trous:
            self.dessiner(sk, t)
        prof = self.profil(sk, 1 + len(pr.trous))
        ext = comp.features.extrudeFeatures.addSimple(prof, self.val(pr.epaisseur), self.fusion.FeatureOperations.NewBodyFeatureOperation)
        corps = self._nommer(ext, pr.nom)
        self.appliquer_apparence(corps, pr.apparence)

    def cylindre(self, comp, pr):
        sk = self.esquisse_z(comp, pr.z, pr.nom)
        sk.sketchCurves.sketchCircles.addByCenterRadius(self.pt(*pr.centre), cm(pr.diametre / 2.0))
        ext = comp.features.extrudeFeatures.addSimple(self.profil(sk, 1), self.val(pr.hauteur),
                                                      self.fusion.FeatureOperations.NewBodyFeatureOperation)
        self.appliquer_apparence(self._nommer(ext, pr.nom), pr.apparence)

    def percage(self, comp, pr):
        sk = self.esquisse_z(comp, pr.z, pr.nom)
        self.dessiner(sk, pr.contour)
        comp.features.extrudeFeatures.addSimple(self.profil(sk, 1), self.val(pr.hauteur),
                                                self.fusion.FeatureOperations.CutFeatureOperation)
        self.nb_percages += 1

    def couture(self, comp, pr):
        sk = self.esquisse_z(comp, pr.z, pr.nom)
        self.dessiner(sk, pr.contour)
        try:  # ligne de couture en construction : n'interfere pas avec les profils
            lignes = sk.sketchCurves
            for i in range(lignes.count):
                lignes.item(i).isConstruction = True
        except Exception:  # pragma: no cover
            pass
        for p in pr.points:
            sk.sketchPoints.add(self.pt(p[0], p[1]))
        self.nb_points_couture += len(pr.points)

    def primitive(self, comp, pr):
        getattr(self, pr.type)(comp, pr)

    def construire(self, plan):
        racine = self.nouveau_composant(self.racine, plan.nom)
        ordre = {"plaque": 0, "percage": 1, "cylindre": 2, "couture": 3}
        for compo in plan.composants:
            comp = self.nouveau_composant(racine, compo.nom)
            for pr in sorted(compo.primitives, key=lambda x: ordre[x.type]):
                try:
                    self.primitive(comp, pr)
                except Exception:
                    self.erreurs.append("%s/%s : %s" % (compo.nom, pr.nom, traceback.format_exc(limit=2)))
        return racine


def rapport_texte(plan):
    c = plan.cotes
    lignes = ["GammeCuir - %s" % plan.nom, "",
              "Cotes principales (mm) :"]
    for k in ("tour", "jeu_doigt", "epaisseur_totale", "circonference_interieure", "circonference_neutre",
              "recouvrement", "longueur_developpee", "largeur", "longueur_passant", "longueur_couture",
              "nb_points_couture", "longueur_fil", "points_par_cm", "tour_mini_reglable", "tour_maxi_reglable"):
        if k in c:
            v = c[k]
            lignes.append("  - %s : %s" % (k, ("%.1f" % v) if isinstance(v, float) else v))
    lignes.append("  - trous d'ardillon (x) : %s" % ", ".join("%.1f" % x for x in c.get("x_trous", [])))
    lignes.append("\nConstats des regles :")
    lignes += ["  - %r" % k for k in plan.constats]
    if plan.notes:
        lignes.append("\nNotes :")
        lignes += ["  - %s" % n for n in plan.notes]
    return "\n".join(lignes)


def executer(context, concevoir, nom_script):
    """Point d'entree generique ``run(context)`` des grammaires (meme schema qu'Equinox)."""
    core, fusion = _adsk()
    app = core.Application.get()
    ui = app.userInterface
    try:
        design = fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("GammeCuir : ouvrir un design (espace Design) avant de lancer %s." % nom_script)
            return None
        plan = concevoir()
        crees, maj = plan.params.exporter_user_parameters(design)
        constructeur = Constructeur(design)
        constructeur.construire(plan)
        texte = rapport_texte(plan)
        try:
            chemin = os.path.join(os.path.expanduser("~"), "gamme_cuir_rapport_%s.txt" % plan.nom)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        except Exception:
            chemin = "(non ecrit)"
        resume = ("%s construit : %d corps, %d percages, %d points de couture, %d User Parameters crees, "
                  "%d mis a jour.\nEchecs : %d, alertes : %d, erreurs de construction : %d.\nRapport : %s"
                  % (plan.nom, constructeur.nb_corps, constructeur.nb_percages, constructeur.nb_points_couture,
                     len(crees), len(maj), len(plan.echecs()), len(plan.alertes()), len(constructeur.erreurs), chemin))
        ui.messageBox(resume + "\n\n" + "\n".join(repr(v) for v in plan.echecs() + plan.alertes())[:1500])
        return plan, constructeur
    except Exception:
        ui.messageBox("GammeCuir - erreur :\n%s" % traceback.format_exc())
        return None
