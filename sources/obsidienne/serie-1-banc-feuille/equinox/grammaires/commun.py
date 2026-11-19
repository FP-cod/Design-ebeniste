# -*- coding: utf-8 -*-
"""Briques de grammaire partagees par les typologies Equinox.

- ``pied_fuseau`` : pied frene splaye, galbe branche, capuchon laiton ;
- ``plateau_garni`` : support contreplaque + mousse, contour feuille ;
- ``verifs_standard`` : stabilite, glissement, flambement des pieds.
"""

import math

from ..calculs import (G, stabilite, verifier_flambement_rond, verifier_glissement, verifier_stabilite)
from ..geometrie import (Composant, Disque, Fuseau, Jonction, PlaqueContour, branche, contour_superellipse,
                         rayon_courbure_min_polyligne, Verification)
from ..parametres import Parametres
from ..regles import appliquer_materiaux_actifs


def preparer(typologie, schema_specifique, racine, params=None, overrides=None):
    """Parametres de typologie + schema specifique + overrides + regles materiaux."""
    p = params.copie() if params is not None else Parametres.pour_typologie(typologie)
    if p.meta(racine + "." + next(iter(schema_specifique))) is None:
        p.etendre(racine, schema_specifique)
    if overrides:
        p.fusionner(overrides)
    erreurs = p.erreurs()
    if erreurs:
        raise ValueError("Parametres invalides : %s" % erreurs)
    return appliquer_materiaux_actifs(p)


def pied_fuseau(plan, nom, noeud, direction_splay, cambrure=12.0, d_haut=None, d_bas=None, decalage_pied=(0.0, 0.0)):
    """Ajoute un pied (composant + capuchon + jonction) ; renvoie la position au sol (x, y).

    :param noeud: point haut du pied (jonction)
    :param direction_splay: (dx, dy) direction horizontale d'ecartement
    :param decalage_pied: (dx, dy) recul supplementaire du pied (pied 'sabre')
    """
    p = plan.params
    g = p.get
    e_cap = g("laiton.epaisseur_capuchon")
    h = noeud[2] - e_cap
    t = math.tan(math.radians(g("bois.angle_splay")))
    n = math.hypot(*direction_splay) or 1.0
    dx, dy = direction_splay[0] / n, direction_splay[1] / n
    pied = (noeud[0] + dx * h * t + decalage_pied[0], noeud[1] + dy * h * t + decalage_pied[1], e_cap)
    axe = branche(noeud, pied, cambrure, (dx, dy, 0.0), n=7)
    d0 = d_haut or g("bois.section_noeud")
    d1 = d_bas or g("bois.section_extremite")
    prims = [Fuseau("%s_%d" % (nom, i + 1), axe[i], axe[i + 1],
                    d0 + (d1 - d0) * i / 6.0, d0 + (d1 - d0) * (i + 1) / 6.0, g("bois.essence")) for i in range(6)]
    plan.ajouter(Composant(nom, prims, "Pied frene %g->%g, splay %g deg" % (d0, d1, g("bois.angle_splay"))))
    plan.ajouter(Composant("capuchon_" + nom, [Disque("capuchon_" + nom, (pied[0], pied[1], 0.0),
                                                       g("laiton.diametre_capuchon"), e_cap, g("laiton.nuance"),
                                                       "laiton")], "Embout laiton"))
    plan.jonctions.append(Jonction("mortaise_" + nom, "tenon_mortaise", noeud, (nom, "ceinture"),
                                   {"tenon": g("jonctions.epaisseur_tenon"), "profondeur": g("jonctions.profondeur_mortaise"),
                                    "tourillon": g("jonctions.diametre_tourillon")}))
    plan.points_appui.append((pied[0], pied[1]))
    plan.repere.setdefault("pieds", {})[nom] = {"noeud": noeud, "pied": pied, "axe": axe}
    rc = rayon_courbure_min_polyligne(axe)
    if rc < g("bois.rayon_courbure_min"):
        plan.verifications.append(Verification("courbure_" + nom, "echec", rc, g("bois.rayon_courbure_min"), "mm",
                                               "galbe trop serre"))
    return pied


def plateau_garni(plan, nom, longueur, largeur, z_haut, x0=0.0, y0=0.0, exposant=4.0, angle=0.0, pivot=None):
    p = plan.params
    g = p.get
    r, es = g("garnissage.epaisseur_rembourrage"), g("garnissage.epaisseur_support")
    contour = contour_superellipse(longueur, largeur, exposant, x0=x0, y0=y0)
    pivot = pivot or (x0, y0, z_haut)
    plan.ajouter(Composant(nom, [
        PlaqueContour(nom + "_support", contour, z_haut - r - es, es, "contreplaque_bouleau", angle, pivot, "bois"),
        PlaqueContour(nom + "_garnissage", contour, z_haut - r, r, "mousse_hr", angle, pivot, "garnissage"),
    ], "%s %s %s, rembourrage %g mm, fixation %s" % (nom, g("garnissage.materiau"), g("garnissage.couleur"), r,
                                                     g("garnissage.methode_fixation"))))
    return contour


def verifs_standard(plan, masses_utilisateur, forces, position_lest=None, hauteur_pied=None, n_pieds=4):
    """Stabilite + glissement + flambement des pieds (cas standard)."""
    p = plan.params
    g = p.get
    cg_s, m_s = plan.cg_structure()
    masses = [(m_s, cg_s)] + list(masses_utilisateur)
    st = stabilite(masses, forces, plan.points_appui, position_lest, g("securite.securite_renversement"))
    plan.stabilite = st
    plan.verifications += verifier_stabilite(st, g("securite.securite_renversement"))
    f_max = max(math.hypot(*f[1]) for f in forces) if forces else 0.0
    plan.verifications.append(verifier_glissement(f_max, st["masse_totale"], g("securite.frottement_sol")))
    if hauteur_pied:
        u = sum(m for m, _ in masses_utilisateur)
        n = (u * g("securite.coefficient_dynamique") + m_s) * G / n_pieds * 1.3
        plan.verifications.append(verifier_flambement_rond("pied_flambement", n, g("bois.section_extremite"), hauteur_pied,
                                                           g("bois.essence"), 2.0, g("securite.securite_bois")))
    return st
