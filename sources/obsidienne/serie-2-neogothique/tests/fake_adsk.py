# -*- coding: utf-8 -*-
"""Faux modules ``adsk.core`` / ``adsk.fusion`` pour tester hors Fusion.

Ce mock n'imite que la surface d'API utilisee par le paquet et AJOUTE des
controles : noms de User Parameters valides, points d'esquisse situes dans le
plan d'esquisse, courbes chainees (lignes ET arcs), profils fermes,
intersections/enlevements avec corps participants, plans tournes a sens
inverse, plan XZ a normale inversee (comme on peut le
rencontrer dans Fusion selon l'orientation) pour tester la correction de sens.
"""

import re
import types

NOM_VALIDE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class Point3D(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    @staticmethod
    def create(x=0.0, y=0.0, z=0.0):
        return Point3D(x, y, z)

    def tup(self):
        return (self.x, self.y, self.z)


class ValueInput(object):
    def __init__(self, reel=None, texte=None):
        self.reel, self.texte = reel, texte

    @staticmethod
    def createByReal(v):
        return ValueInput(reel=float(v))

    @staticmethod
    def createByString(s):
        return ValueInput(texte=str(s))


class ObjectCollection(list):
    @staticmethod
    def create():
        return ObjectCollection()

    def add(self, o):
        self.append(o)

    @property
    def count(self):
        return len(self)


class Matrix3D(object):
    @staticmethod
    def create():
        return Matrix3D()


class UserParameter(object):
    def __init__(self, nom, expression, unite, commentaire):
        self.name, self.expression, self.unit, self.comment = nom, expression, unite, commentaire

    @property
    def value(self):
        try:
            v = float(self.expression.split()[0])
        except ValueError:
            return 0.0
        return v / 10.0 if self.unit == "mm" else v


class UserParameters(object):
    def __init__(self):
        self.items = {}

    def itemByName(self, nom):
        return self.items.get(nom)

    def add(self, nom, vi, unite, commentaire):
        if not NOM_VALIDE.match(nom):
            raise ValueError("Nom de parametre invalide : %r" % nom)
        if nom in self.items:
            raise ValueError("Parametre deja existant : %r" % nom)
        if vi.texte is None:
            raise ValueError("expression texte attendue")
        p = UserParameter(nom, vi.texte, unite, commentaire)
        self.items[nom] = p
        return p

    @property
    def count(self):
        return len(self.items)


class Vecteur(object):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def _rot_z(v, deg):
    import math
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


class Plan(object):
    """Plan n.p = d (n unitaire, d en cm). Les plans d'origine ont une normale imposee."""

    def __init__(self, n, d_cm=0.0, comp=None):
        self.n, self.d = tuple(float(c) for c in n), float(d_cm)
        self.supprime = False
        self.comp = comp

    @property
    def geometry(self):
        return types.SimpleNamespace(origin=Point3D(*[c * self.d for c in self.n]), normal=Vecteur(*self.n))

    @property
    def ia(self):
        return max(range(3), key=lambda i: abs(self.n[i]))

    def coordonnee(self):
        """Coordonnee (cm) du plan sur son axe dominant (plans paralleles aux plans d'origine)."""
        return self.n[self.ia] * self.d

    def distance(self, p):
        return sum(a * b for a, b in zip(self.n, p)) - self.d

    def deleteMe(self):
        self.supprime = True
        self.comp.constructionPlanes.liste.remove(self)


class PlanInput(object):
    def __init__(self):
        self.mode = None

    def setByOffset(self, base, vi):
        if vi.reel is None:
            raise AssertionError("decalage numerique attendu")
        self.mode, self.base, self.vi = "decalage", base, vi

    def setByAngle(self, axe, vi, base):
        if axe != "axe_Z":
            raise AssertionError("axe Z de construction attendu")
        if vi.texte is None or not vi.texte.endswith("deg"):
            raise AssertionError("angle en texte 'xx deg' attendu")
        self.mode, self.base, self.angle = "angle", base, float(vi.texte.split()[0])


class ConstructionPlanes(object):
    def __init__(self, comp):
        self.comp, self.liste = comp, []

    def createInput(self):
        return PlanInput()

    def add(self, entree):
        base = entree.base
        if getattr(base, "supprime", False):
            raise AssertionError("plan de base supprime")
        if entree.mode == "decalage":
            p = Plan(base.n, base.d + entree.vi.reel, self.comp)
        elif entree.mode == "angle":
            # rotation de -angle : sens volontairement « inverse » pour tester la correction
            p = Plan(_rot_z(base.n, -entree.angle), 0.0, self.comp)
        else:
            raise AssertionError("PlanInput non defini")
        self.liste.append(p)
        return p


class Profil(object):
    def __init__(self, n_boucles):
        self.profileLoops = types.SimpleNamespace(count=n_boucles)


class Collection(object):
    def __init__(self, liste):
        self.liste = liste

    @property
    def count(self):
        return len(self.liste)

    def item(self, i):
        return self.liste[i]

    def __iter__(self):
        return iter(list(self.liste))


def _egal(a, b, tol=1e-9):
    return all(abs(u - v) < tol for u, v in zip(a, b))


class LigneEsquisse(object):
    def __init__(self, a, b):
        self.a, self.b = a, b


class Lignes(object):
    def __init__(self, esq):
        self.esq = esq

    def addByTwoPoints(self, a, b):
        self.esq._verifier(a)
        self.esq._verifier(b)
        if _egal(a.tup(), b.tup(), 1e-7):
            raise AssertionError("ligne de longueur nulle")
        self.esq._chainer(a.tup(), b.tup())
        l = LigneEsquisse(a.tup(), b.tup())
        self.esq.lignes.append(l)
        return l


class Arcs(object):
    def __init__(self, esq):
        self.esq = esq

    def addByThreePoints(self, a, m, b):
        for p in (a, m, b):
            self.esq._verifier(p)
        u = [m.tup()[i] - a.tup()[i] for i in range(3)]
        v = [b.tup()[i] - a.tup()[i] for i in range(3)]
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        if sum(c * c for c in cr) ** 0.5 < 1e-10:
            raise AssertionError("arc a trois points alignes")
        self.esq._chainer(a.tup(), b.tup())
        self.esq.arcs.append((a.tup(), m.tup(), b.tup()))
        return self.esq.arcs[-1]


class Cercles(object):
    def __init__(self, esq):
        self.esq = esq

    def addByCenterRadius(self, c, r):
        self.esq._verifier(c)
        if r <= 0:
            raise ValueError("rayon nul")
        if self.esq._debut is not None:
            raise AssertionError("cercle dessine au milieu d'une boucle ouverte")
        self.esq.cercles.append((c.tup(), r))
        self.esq.boucles += 1


class Esquisse(object):
    def __init__(self, plan):
        self.plan, self.name = plan, ""
        self.lignes, self.arcs, self.cercles, self.boucles = [], [], [], 0
        self._debut = self._fin = None
        self.sketchCurves = types.SimpleNamespace(sketchLines=Lignes(self), sketchCircles=Cercles(self),
                                                  sketchArcs=Arcs(self))

    def modelToSketchSpace(self, p):
        return p

    def _verifier(self, p):
        if abs(self.plan.distance(p.tup())) > 1e-6:
            raise AssertionError("point %s hors du plan d'esquisse (n=%s, d=%g)" % (p.tup(), self.plan.n, self.plan.d))

    def _chainer(self, a, b):
        """Controle le chainage des courbes d'une boucle et compte les boucles fermees."""
        if self._debut is None:
            self._debut = a
        elif not _egal(a, self._fin, 1e-7):
            raise AssertionError("courbe non chainee : %s apres %s" % (a, self._fin))
        self._fin = b
        if _egal(b, self._debut, 1e-7):
            self.boucles += 1
            self._debut = self._fin = None

    @property
    def profiles(self):
        if self._debut is not None or self.boucles == 0:
            return Collection([])  # boucle non fermee
        if self.boucles == 1:
            return Collection([Profil(1)])
        # profil exterieur a n boucles + un profil par boucle interieure
        return Collection([Profil(1) for _ in range(self.boucles - 1)] + [Profil(self.boucles)])


class Sketches(object):
    def __init__(self):
        self.liste = []

    def add(self, plan):
        if getattr(plan, "supprime", False):
            raise AssertionError("esquisse sur un plan supprime")
        e = Esquisse(plan)
        self.liste.append(e)
        return e

    @property
    def count(self):
        return len(self.liste)


class Corps(object):
    def __init__(self, comp):
        self.name, self.comp = "", comp

    def deleteMe(self):
        self.comp._corps.remove(self)


class ExtrudeInput(object):
    def __init__(self, profil, op):
        self.profil, self.op, self.etendue = profil, op, None
        self.participantBodies = []

    def setSymmetricExtent(self, vi, pleine_longueur):
        if not pleine_longueur:
            raise AssertionError("extrusion symetrique pleine longueur attendue")
        if vi.reel is not None and vi.reel <= 0:
            raise ValueError("longueur nulle")
        self.etendue = vi


class Extrudes(object):
    def __init__(self, comp):
        self.comp, self.liste = comp, []

    def createInput(self, profil, op):
        if op not in ("NewBody", "Intersect", "Cut"):
            raise AssertionError("operation inconnue %r" % op)
        return ExtrudeInput(profil, op)

    def add(self, entree):
        if entree.etendue is None:
            raise AssertionError("etendue non definie")
        if entree.op == "NewBody":
            corps = Corps(self.comp)
            self.comp._corps.append(corps)
            bodies = [corps]
        else:
            if not entree.participantBodies:
                raise AssertionError("intersection/enlevement sans corps participant")
            for c in entree.participantBodies:
                if c not in self.comp._corps:
                    raise AssertionError("corps participant absent du composant")
            bodies = list(entree.participantBodies)
        f = types.SimpleNamespace(bodies=Collection(bodies), entree=entree)
        self.liste.append(f)
        return f


class RevolveInput(object):
    def __init__(self, profil, axe, op):
        self.profil, self.axe, self.op, self.angle = profil, axe, op, None

    def setAngleExtent(self, symetrique, vi):
        self.angle = vi


class Revolves(object):
    def __init__(self, comp):
        self.comp, self.liste = comp, []

    def createInput(self, profil, axe, op):
        if not isinstance(axe, LigneEsquisse):
            raise AssertionError("axe de revolution : ligne d'esquisse attendue")
        return RevolveInput(profil, axe, op)

    def add(self, entree):
        if entree.angle is None:
            raise AssertionError("angle de revolution non defini")
        corps = Corps(self.comp)
        self.comp._corps.append(corps)
        f = types.SimpleNamespace(bodies=Collection([corps]), entree=entree)
        self.liste.append(f)
        return f


class MoveInput(object):
    def __init__(self, coll):
        self.coll, self.translation = coll, None

    def defineAsTranslateXYZ(self, x, y, z, espace_design):
        self.translation = (x, y, z, espace_design)


class Moves(object):
    def __init__(self, disponible=True):
        self.liste, self.disponible = [], disponible

    def createInput2(self, coll):
        if not self.disponible:
            raise RuntimeError("createInput2 indisponible")
        return MoveInput(coll)

    def add(self, entree):
        self.liste.append(entree)
        return entree


class Composant(object):
    def __init__(self, nom="racine", moves_disponible=True):
        self.name = nom
        self.xYConstructionPlane = Plan((0, 0, 1), 0.0, self)
        self.yZConstructionPlane = Plan((1, 0, 0), 0.0, self)
        self.xZConstructionPlane = Plan((0, -1, 0), 0.0, self)  # normale -Y : force la correction de sens
        self.zConstructionAxis = "axe_Z"
        self.constructionPlanes = ConstructionPlanes(self)
        self.sketches = Sketches()
        self._corps = []
        self.features = types.SimpleNamespace(extrudeFeatures=Extrudes(self), moveFeatures=Moves(moves_disponible),
                                              revolveFeatures=Revolves(self))
        self.occurrences = Occurrences(moves_disponible)

    @property
    def bRepBodies(self):
        return Collection(self._corps)


class Occurrences(object):
    def __init__(self, moves_disponible=True):
        self.liste, self.moves_disponible = [], moves_disponible

    def addNewComponent(self, matrice):
        occ = types.SimpleNamespace(component=Composant("nouveau", self.moves_disponible))
        self.liste.append(occ)
        return occ


class Design(object):
    def __init__(self, moves_disponible=True):
        self.userParameters = UserParameters()
        self.rootComponent = Composant("racine", moves_disponible)
        self.designType = None

    @staticmethod
    def cast(o):
        return o


class UI(object):
    def __init__(self):
        self.messages = []

    def messageBox(self, texte):
        self.messages.append(texte)


class Application(object):
    courante = None

    def __init__(self, design):
        self.activeProduct, self.userInterface = design, UI()

    @staticmethod
    def get():
        return Application.courante


def installer(sys_modules, design=None):
    """Installe les faux modules dans ``sys_modules`` ; renvoie (adsk, design, app)."""
    core = types.ModuleType("adsk.core")
    for nom in ("Point3D", "ValueInput", "ObjectCollection", "Matrix3D", "Application"):
        setattr(core, nom, globals()[nom])
    fusion = types.ModuleType("adsk.fusion")
    fusion.Design = Design
    fusion.FeatureOperations = types.SimpleNamespace(NewBodyFeatureOperation="NewBody",
                                                     IntersectFeatureOperation="Intersect",
                                                     CutFeatureOperation="Cut")
    fusion.DesignTypes = types.SimpleNamespace(ParametricDesignType="Parametric")
    adsk = types.ModuleType("adsk")
    adsk.core, adsk.fusion = core, fusion
    sys_modules["adsk"], sys_modules["adsk.core"], sys_modules["adsk.fusion"] = adsk, core, fusion
    design = design or Design()
    app = Application(design)
    Application.courante = app
    return adsk, design, app
