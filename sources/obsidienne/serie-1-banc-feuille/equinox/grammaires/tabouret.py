# -*- coding: utf-8 -*-
"""Grammaire (squelette fonctionnel) : tabouret Equinox « Graine »
(tabouret modulable / tabouret de queening).

Assise garnie en feuille (superellipse), option echancrure avant (queening :
acces au visage de la personne allongee dessous), quatre pieds fuseau
splayes 7 deg relies par une ceinture basse de branches cintrees (noeuds a
``tabouret.hauteur_ceinture``) qui porte quatre anneaux de retenue.
Oeillets bas sous les deux pieds arriere (module ``ancrages``).

Repere : X avant (echancrure cote +X), Y lateral, Z sol.
"""

import math

from ..calculs import G, verifier_flexion_rond
from ..geometrie import Boite, Composant, Jonction, Plan, Verification, branche, fuseaux_le_long, lerp
from ..parametres import Param
from . import ancrages
from .commun import pied_fuseau, plateau_garni, preparer, verifs_standard

TYPOLOGIE = "tabouret"
VAL = "a_valider"

SCHEMA_TABOURET = {
    "longueur_assise": Param(400.0, "mm", "Longueur (X) de l'assise.", (300.0, 600.0), statut=VAL),
    "echancrure": Param(0.0, "mm", "Profondeur de l'echancrure avant de queening (0 = tabouret plein).",
                        (0.0, 200.0), statut=VAL),
    "hauteur_ceinture": Param(160.0, "mm", "Hauteur de la ceinture basse (noeuds) portant les anneaux.",
                              (80.0, 300.0), statut=VAL),
    "retrait_pieds": Param(50.0, "mm", "Retrait des noeuds de pied sous l'assise.", (20.0, 120.0), statut=VAL),
    "fleche_ceinture": Param(18.0, "mm", "Fleche des branches de ceinture (vers l'exterieur).", (0.0, 60.0),
                             statut=VAL),
}


def concevoir(params=None, overrides=None):
    p, ajust = preparer(TYPOLOGIE, SCHEMA_TABOURET, "tabouret", params, overrides)
    g = p.get
    plan = Plan(TYPOLOGIE, p)
    plan.ajustements = ajust
    H = g("dimensions.hauteur_assise")
    L, W = g("tabouret.longueur_assise"), g("dimensions.largeur_plateau")
    r, es = g("garnissage.epaisseur_rembourrage"), g("garnissage.epaisseur_support")
    ess = g("bois.essence")
    plateau_garni(plan, "assise", L, W, H, x0=-L / 2.0, exposant=3.0)
    ech = g("tabouret.echancrure")
    if ech > 0:
        plan.notes.append("Echancrure de queening %g mm cote +X : a decouper dans le support (contour en U, rayon "
                          ">= rayon_bord) ; renfort par la ceinture haute." % ech)
    z_n = H - r - es - 40.0
    rx, ry = L / 2.0 - g("tabouret.retrait_pieds"), W / 2.0 - g("tabouret.retrait_pieds")
    ceinture_haute = [Boite("ceinture_haute_%s" % n, c, dx, dy, 40.0, ess) for n, c, dx, dy in
                      (("X+", (rx, 0, z_n + 20), 35, 2 * ry), ("X-", (-rx, 0, z_n + 20), 35, 2 * ry),
                       ("Y+", (0, ry, z_n + 20), 2 * rx, 35), ("Y-", (0, -ry, z_n + 20), 2 * rx, 35))]
    plan.ajouter(Composant("ceinture_haute", ceinture_haute, "Ceinture haute sous assise"))
    pieds = {}
    for nom, sx, sy in (("AR_G", -1, 1), ("AR_D", -1, -1), ("AV_G", 1, 1), ("AV_D", 1, -1)):
        pieds[nom] = pied_fuseau(plan, "pied_" + nom, (sx * rx, sy * ry, z_n), (sx, sy))
    # ceinture basse en branches : relie les pieds a hauteur_ceinture
    zc = g("tabouret.hauteur_ceinture")
    pts_c = {}
    for nom, info in plan.repere["pieds"].items():
        a, b = info["noeud"], info["pied"]
        t = (a[2] - zc) / (a[2] - b[2])
        pts_c[nom] = lerp(a, b, t)
    tour = ["pied_AR_G", "pied_AV_G", "pied_AV_D", "pied_AR_D"]
    prims = []
    for i in range(4):
        a, b = pts_c[tour[i]], pts_c[tour[(i + 1) % 4]]
        mil = lerp(a, b, 0.5)
        dirx = (mil[0], mil[1], 0.0)
        pts = branche(a, b, g("tabouret.fleche_ceinture"), dirx, n=5)
        prims += fuseaux_le_long("ceinture_basse_%d" % i, pts, g("bois.section_extremite"), g("bois.section_extremite"), ess)
        c, j, v = ancrages.anneau_traverse(p, lerp(a, b, 0.5), (mil[0] or 1e-6, mil[1], 0.0), "anneau_ceinture_%d" % i)
        for comp in c:
            plan.ajouter(comp)
        plan.jonctions += j
        plan.verifications += v
    plan.ajouter(Composant("ceinture_basse", prims, "Ceinture basse en branches (porte les anneaux)"))
    for nom, pt in pts_c.items():
        plan.jonctions.append(Jonction("noeud_ceinture_" + nom, "tourillons", pt, (nom, "ceinture_basse"),
                                       {"nombre": 2, "diametre": g("jonctions.diametre_tourillon")}))
    c, j, v = ancrages.oeillets_sous_semelles(p, [("AR_G", pieds["AR_G"][:2], (-1, 0.5)), ("AR_D", pieds["AR_D"][:2], (-1, -0.5))])
    for comp in c:
        plan.ajouter(comp)
    plan.jonctions += j
    plan.verifications += v
    u = g("securite.charge_utilisateur")
    f_lat = g("securite.coefficient_horizontal_lat") * u * G
    forces = [("lateral_Y", (0.0, f_lat), H + 250.0), ("bascule_X", (f_lat, 0.0), H + 250.0),
              ("bascule_-X", (-f_lat, 0.0), H + 250.0)]
    verifs_standard(plan, [(u, (0.0, 0.0, H + 250.0))], forces, hauteur_pied=z_n)
    # ceinture haute : la charge passe par les pieds, verif de la ceinture basse sous traction d'anneau
    f_ret = ancrages.effort_retenue(p)
    l = math.hypot(pts_c["pied_AR_G"][0] - pts_c["pied_AV_G"][0], pts_c["pied_AR_G"][1] - pts_c["pied_AV_G"][1])
    plan.verifications.append(verifier_flexion_rond("ceinture_basse_flexion", f_ret * l / 4.0, g("bois.section_extremite"),
                                                    ess, g("securite.securite_bois")))
    plan.notes.append("Squelette : choisir tabouret plein ou de queening (echancrure), et la hauteur 440 a valider.")
    return plan


def run(context):
    from ..fusion_outils import executer
    return executer(context, concevoir, TYPOLOGIE)


def stop(context):
    pass
