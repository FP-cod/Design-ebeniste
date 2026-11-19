# -*- coding: utf-8 -*-
"""Ancrages Equinox, reutilisables par toutes les typologies.

- ``oeillets_sous_semelles`` : platine inox (epaisseur ``inox.epaisseur_plaque``)
  encastree en feuillure sous la semelle du pied (profondeur
  ``ancrage.profondeur_encastrement``), prise entre le bois et le capuchon
  laiton ; l'oeil (fil ``inox.diametre_oeillet``) sort de ``ancrage.saillie_oeillet``
  au-dela du capuchon, vers l'exterieur, pour une sangle vers un point au sol.
- ``anneau_traverse`` : anneau inox (fil ``inox.diametre_oeillet``, diametre
  interieur ``ancrage.diametre_interieur_anneau``) a mi-hauteur de la face
  d'une traverse, tenu par une tige M8 traversante.
- ``verifier_ancrage`` : effort de retenue vs CMU du catalogue.

Effort de calcul d'un ancrage de retenue :
F = coefficient_dynamique x 0,5 x charge_utilisateur x g (un membre qui tire
violemment sur un seul point, hypothese a valider).
"""

import math

from ..catalogues.attaches import ATTACHES
from ..geometrie import (Composant, Disque, Jonction, TubeSpline, Verification, Boite, add, mul, unitaire)

G = 9.81


def effort_retenue(params):
    """Effort de calcul sur un point de retenue [N]."""
    return params.get("securite.coefficient_dynamique") * 0.5 * params.get("securite.charge_utilisateur") * G


def verifier_ancrage(params, cle_attache, nom):
    cap = ATTACHES[cle_attache]["capacite_service"]
    f = effort_retenue(params)
    r = cap / f
    return Verification("ancrage_" + nom, "ok" if r >= 1.0 else "echec", f, cap, "N",
                        "%s : effort %.0f N vs CMU catalogue %.0f N (%s) - CMU fabricant a confirmer"
                        % (nom, f, cap, ATTACHES[cle_attache]["nom"]))


def _anneau_points(centre, rayon, normale, n=24):
    """Cercle de rayon ``rayon`` centre en ``centre`` dans le plan de normale ``normale``."""
    nz = unitaire(normale)
    ref = (0.0, 0.0, 1.0) if abs(nz[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = unitaire((nz[1] * ref[2] - nz[2] * ref[1], nz[2] * ref[0] - nz[0] * ref[2], nz[0] * ref[1] - nz[1] * ref[0]))
    v = (nz[1] * u[2] - nz[2] * u[1], nz[2] * u[0] - nz[0] * u[2], nz[0] * u[1] - nz[1] * u[0])
    return [add(centre, add(mul(u, rayon * math.cos(2 * math.pi * i / n)), mul(v, rayon * math.sin(2 * math.pi * i / n))))
            for i in range(n)]


def oeillets_sous_semelles(params, pieds, nom_base="oeillet_bas"):
    """Cree un composant d'oeillet par pied.

    :param pieds: liste (nom_pied, (x, y) centre du pied au sol, (dx, dy) direction de sortie de l'oeil)
    :returns: (composants, jonctions, verifications)
    """
    if not params.get("ancrage.oeillets_bas"):
        return [], [], []
    fil = params.get("inox.diametre_oeillet")
    ep = params.get("inox.epaisseur_plaque")
    d_cap = params.get("laiton.diametre_capuchon")
    e_cap = params.get("laiton.epaisseur_capuchon")
    saillie = params.get("ancrage.saillie_oeillet")
    nuance = params.get("inox.nuance")
    comps, jonctions = [], []
    for nom_pied, (x, y), direction in pieds:
        d = unitaire((direction[0], direction[1], 0.0))
        z_plat = e_cap  # platine posee sur le fond du capuchon, dans la feuillure du pied
        platine = Disque("%s_%s_platine" % (nom_base, nom_pied), (x, y, z_plat), d_cap - 2, ep, nuance, "inox")
        r_oeil = fil / 2.0 + 6.0  # oeil di 12 mm mini pour un mousqueton
        c_oeil = add((x, y, z_plat + ep / 2.0), mul(d, d_cap / 2.0 + saillie - r_oeil))
        oeil = TubeSpline("%s_%s_oeil" % (nom_base, nom_pied), _anneau_points(c_oeil, r_oeil, (0, 0, 1)), fil,
                          nuance, ferme=True)
        patte = Boite("%s_%s_patte" % (nom_base, nom_pied), add((x, y, z_plat + ep / 2.0), mul(d, d_cap / 2.0)),
                      abs(d[0]) * (saillie) + abs(d[1]) * fil + 1, abs(d[1]) * (saillie) + abs(d[0]) * fil + 1, ep,
                      nuance, categorie="inox")
        comps.append(Composant("%s_%s" % (nom_base, nom_pied), [platine, patte, oeil],
                               "Oeillet bas encastre sous semelle (%s)" % nom_pied))
        jonctions.append(Jonction("%s_%s_fixation" % (nom_base, nom_pied), "taraudage",
                                  (x, y, z_plat), (nom_pied, "oeillet"),
                                  {"insert": params.get("jonctions.filetage_insert"),
                                   "longueur_insert": params.get("jonctions.longueur_insert"),
                                   "feuillure_profondeur": params.get("ancrage.profondeur_encastrement"),
                                   "vis_platine": "4 x vis inox A4 d4", "note": "vis axiale traverse capuchon+platine"}))
    verifs = [verifier_ancrage(params, params.get("ancrage.attache_oeillet"), "oeillets_bas")]
    return comps, jonctions, verifs


def anneau_traverse(params, centre_face, normale_face, nom="anneau_arriere"):
    """Anneau a mi-hauteur de la face d'une traverse.

    :param centre_face: point (mm) au centre de la face de traverse (mi-hauteur)
    :param normale_face: direction sortante de la face (ex. (-1, 0, 0) pour l'arriere)
    """
    if not params.get("ancrage.anneau_arriere"):
        return [], [], []
    fil = params.get("inox.diametre_oeillet")
    di = params.get("ancrage.diametre_interieur_anneau")
    nuance = params.get("inox.nuance")
    n = unitaire(normale_face)
    r = di / 2.0 + fil / 2.0
    pontet = Boite(nom + "_pontet", add(centre_face, mul(n, 6.0)), 12 if abs(n[0]) > 0.5 else 30, 30 if abs(n[0]) > 0.5 else 12,
                   20, nuance, categorie="inox")
    centre_anneau = add(add(centre_face, mul(n, 12.0)), (0.0, 0.0, -r))
    # anneau pendant dans le plan contenant la normale et Z
    normale_plan = (-n[1], n[0], 0.0)
    anneau = TubeSpline(nom + "_anneau", _anneau_points(centre_anneau, r, normale_plan), fil, nuance, ferme=True)
    comp = Composant(nom, [pontet, anneau], "Anneau d'ancrage arriere a mi-hauteur de traverse")
    j = Jonction(nom + "_tige", "taraudage", centre_face, ("traverse", nom),
                 {"tige": "M8 inox A4 traversante", "ecrou": "borgne + rondelle d24 cote oppose",
                  "percage_tube": "d 9 a travers les 2 parois du tube 40x40 (manchon entretoise d 12 soude)"})
    return [comp], [j], [verifier_ancrage(params, params.get("ancrage.attache_anneau"), nom)]
