# -*- coding: utf-8 -*-
"""Primitives geometriques, composants, jonctions, verifications et Plan.

Logique pure (aucun import adsk), en mm. Repere des rateliers et meubles :
X le long du mur (gauche -> droite), Y perpendiculaire au mur (0 = nu du mur,
positif vers la piece), Z vertical (0 = sol).

Meme organisation que ``equinox.geometrie`` (Composant / Jonction /
Verification / Plan), reduite aux primitives utiles au rangement : boites
(panneaux, tasseaux, plots) et cylindres d'axe X, Y ou Z (barres, tiges,
douilles, ergots), pleins ou tubulaires.
"""

import math

AXES = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


class Primitive(object):
    nom, materiau, densite = "", "", 0.0

    def volume_mm3(self):
        raise NotImplementedError

    def centroide(self):
        raise NotImplementedError

    def masse_kg(self):
        return self.volume_mm3() * 1e-9 * self.densite

    def boite_englobante(self):
        raise NotImplementedError


class Boite(Primitive):
    """Parallelepipede aligne sur les axes : ``centre``, cotes ``dx, dy, dz``."""

    def __init__(self, nom, centre, dx, dy, dz, materiau, densite):
        self.nom, self.centre = nom, tuple(float(v) for v in centre)
        self.dx, self.dy, self.dz = float(dx), float(dy), float(dz)
        self.materiau, self.densite = materiau, float(densite)

    def volume_mm3(self):
        return self.dx * self.dy * self.dz

    def centroide(self):
        return self.centre

    def boite_englobante(self):
        c = self.centre
        d = (self.dx / 2.0, self.dy / 2.0, self.dz / 2.0)
        return (c[0] - d[0], c[1] - d[1], c[2] - d[2]), (c[0] + d[0], c[1] + d[1], c[2] + d[2])


class Cylindre(Primitive):
    """Cylindre d'axe ``axe`` ('x' | 'y' | 'z') : ``base`` = centre de la face
    de depart, extrusion de ``longueur`` dans le sens +axe. ``paroi`` : tube."""

    def __init__(self, nom, base, axe, diametre, longueur, materiau, densite, paroi=None):
        if axe not in AXES:
            raise ValueError("axe %r inconnu" % axe)
        self.nom, self.base, self.axe = nom, tuple(float(v) for v in base), axe
        self.diametre, self.longueur, self.paroi = float(diametre), float(longueur), paroi
        self.materiau, self.densite = materiau, float(densite)

    def aire_section(self):
        r = self.diametre / 2.0
        if self.paroi:
            return math.pi * (r ** 2 - (r - self.paroi) ** 2)
        return math.pi * r ** 2

    def volume_mm3(self):
        return self.aire_section() * self.longueur

    def centre(self):
        return add(self.base, mul(AXES[self.axe], self.longueur / 2.0))

    centroide = centre

    def fin(self):
        return add(self.base, mul(AXES[self.axe], self.longueur))

    def boite_englobante(self):
        r = self.diametre / 2.0
        lo, hi = list(self.base), list(self.fin())
        i = "xyz".index(self.axe)
        mini = [min(lo[k], hi[k]) if k == i else lo[k] - r for k in range(3)]
        maxi = [max(lo[k], hi[k]) if k == i else lo[k] + r for k in range(3)]
        return tuple(mini), tuple(maxi)


class Composant(object):
    """Composant Fusion : un nom, des primitives, un role lisible."""

    def __init__(self, nom, primitives, role=""):
        self.nom, self.primitives, self.role = nom, list(primitives), role

    def masse_kg(self):
        return sum(p.masse_kg() for p in self.primitives)


class Jonction(object):
    """Jonction nommee et calculee (tourillons, insert, douille NPT...)."""

    def __init__(self, nom, type_, position, pieces, details):
        self.nom, self.type, self.position, self.pieces, self.details = nom, type_, tuple(position), pieces, details

    def __repr__(self):
        return "Jonction(%s, %s)" % (self.nom, self.type)


class Verification(object):
    """Resultat de verification : niveau 'ok' | 'alerte' | 'echec' | 'todo'."""

    def __init__(self, nom, niveau, valeur, limite, unite, detail):
        self.nom, self.niveau, self.valeur, self.limite = nom, niveau, valeur, limite
        self.unite, self.detail = unite, detail

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau.upper(), self.nom, self.detail)

    __str__ = __repr__


class Plan(object):
    """Resultat d'une grammaire : tout ce qu'il faut pour construire et verifier."""

    def __init__(self, nom, params):
        self.nom, self.params = nom, params
        self.composants, self.jonctions, self.verifications = [], [], []
        self.notes, self.repere = [], {}

    def ajouter(self, composant):
        self.composants.append(composant)
        return composant

    def composant(self, nom):
        for c in self.composants:
            if c.nom == nom:
                return c
        raise KeyError(nom)

    def primitives(self):
        for c in self.composants:
            for p in c.primitives:
                yield p

    def masse_structure(self):
        return sum(c.masse_kg() for c in self.composants)

    def cg_structure(self):
        m_tot, acc = 0.0, (0.0, 0.0, 0.0)
        for p in self.primitives():
            m = p.masse_kg()
            acc = add(acc, mul(p.centroide(), m))
            m_tot += m
        return mul(acc, 1.0 / m_tot), m_tot

    def boite_englobante(self):
        bs = [p.boite_englobante() for p in self.primitives()]
        return (tuple(min(b[0][k] for b in bs) for k in range(3)), tuple(max(b[1][k] for b in bs) for k in range(3)))

    def par_niveau(self, niveau):
        return [v for v in self.verifications if v.niveau == niveau]

    def echecs(self):
        return self.par_niveau("echec")

    def alertes(self):
        return self.par_niveau("alerte")

    def todos(self):
        return self.par_niveau("todo")
