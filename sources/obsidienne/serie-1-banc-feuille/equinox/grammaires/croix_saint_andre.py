# -*- coding: utf-8 -*-
"""Grammaire (squelette fonctionnel) : croix de Saint-Andre Equinox « Nervure ».

Deux branches frene lamelle-colle legerement cintrees (nervures de feuille)
se croisent a mi-bois au noeud ; la croix est autoportante grace a une jambe
de force arriere (branche) et a deux semelles au sol dont l'arriere contient
le tube inox 40x40 leste. Anneaux de retenue aux 4 extremites et pres du
noeud (module ``ancrages``), oeillets bas sous les semelles avant.

Repere : la personne se tient en X < 0 face a la croix (plan X ~ 0), la
structure de stabilisation part vers +X. Z = sol.

Points critiques : traction vers l'arriere (la personne tire en se
penchant) -> basculement vers l'avant autour de la ligne des pieds avant ;
c'est le lest arriere + la profondeur de base qui stabilisent.
"""

import math

from ..calculs import G, verifier_flexion_rond
from ..geometrie import (Boite, Composant, Jonction, Plan, TubeCarre, Verification, branche, fuseaux_le_long, lerp,
                         rayon_courbure_min_polyligne, rotation_y)
from ..parametres import Param
from ..regles import capacite_lest_kg_par_m
from . import ancrages
from .commun import preparer, verifs_standard

TYPOLOGIE = "croix_saint_andre"
VAL = "a_valider"

SCHEMA_CROIX = {
    "hauteur": Param(2100.0, "mm", "Hauteur hors tout des branches.", (1600.0, 2500.0), statut=VAL),
    "largeur_haut": Param(1250.0, "mm", "Ecart des extremites hautes (poignets).", (800.0, 1600.0), statut=VAL),
    "largeur_bas": Param(950.0, "mm", "Ecart des extremites basses (chevilles).", (500.0, 1300.0), statut=VAL),
    "inclinaison": Param(6.0, "deg", "Inclinaison de la croix vers l'arriere (la personne s'appuie).", (0.0, 20.0),
                         statut=VAL),
    "fleche_branches": Param(30.0, "mm", "Fleche du cintrage des branches (vers l'exterieur).", (0.0, 120.0), statut=VAL),
    "profondeur_base": Param(750.0, "mm", "Recul du pied de la jambe de force derriere le plan de la croix.",
                             (400.0, 1200.0), statut=VAL),
    "hauteur_attache_jambe": Param(0.0, "mm", "Hauteur d'attache de la jambe de force (0 = au noeud).", (0.0, 2000.0),
                                   statut=VAL),
    "profondeur_plateforme": Param(550.0, "mm", "Plateforme frene (lattes) devant la croix sur laquelle se tient la "
                                   "personne : son poids stabilise et ses tractions deviennent des efforts internes. "
                                   "0 = pas de plateforme.", (0.0, 900.0), statut=VAL),
    "section_branches": Param(60.0, "mm", "Section des branches au noeud (>= section_noeud : grande portee).",
                              (40.0, 100.0), statut=VAL),
}


def concevoir(params=None, overrides=None):
    p, ajust = preparer(TYPOLOGIE, SCHEMA_CROIX, "croix", params, overrides)
    g = p.get
    plan = Plan(TYPOLOGIE, p)
    plan.ajustements = ajust
    ess, nuance = g("bois.essence"), g("inox.nuance")
    H, wh, wb = g("croix.hauteur"), g("croix.largeur_haut"), g("croix.largeur_bas")
    inc = g("croix.inclinaison")
    d_b, d_ext = g("croix.section_branches"), g("bois.section_extremite") + 10
    z_noeud = H * wb / (wb + wh)

    def pt(y, z):  # plan de la croix incline vers +X (arriere) autour de l'axe Y au sol
        return rotation_y((0.0, y, z), (0.0, 0.0, 0.0), -inc)

    noeud = pt(0.0, z_noeud)
    branches = []
    for nom, y0, y1 in (("branche_1", -wb / 2, wh / 2), ("branche_2", wb / 2, -wh / 2)):
        a, b = pt(y0, 0.0), pt(y1, H)
        pts = branche(a, b, g("croix.fleche_branches"), (0.0, 1.0 if y1 > 0 else -1.0, 0.0), n=9)
        # fuseau : extremite -> noeud -> extremite
        demi = len(pts) // 2
        prims = (fuseaux_le_long(nom + "_bas", pts[:demi + 1], d_ext, d_b, ess)
                 + fuseaux_le_long(nom + "_haut", pts[demi:], d_b, d_ext, ess))
        plan.ajouter(Composant(nom, prims, "Branche nervure frene lamelle-colle %g->%g" % (d_ext, d_b)))
        branches.append(pts)
        rc = rayon_courbure_min_polyligne(pts)
        plan.verifications.append(Verification("courbure_" + nom, "ok" if rc >= g("bois.rayon_courbure_min") else "echec",
                                               rc, g("bois.rayon_courbure_min"), "mm", "rayon mini %.0f mm" % rc))
    plan.jonctions.append(Jonction("noeud_mi_bois", "mi_bois", noeud, ("branche_1", "branche_2"),
                                   {"type": "entaille a mi-bois collee", "renfort": "platines inox %g mm x2 + 4 inserts %s"
                                    % (g("inox.epaisseur_plaque"), g("jonctions.filetage_insert"))}))
    # jambe de force + semelles
    z_att = g("croix.hauteur_attache_jambe") or z_noeud
    attache = pt(0.0, z_att)
    D = g("croix.profondeur_base")
    pied_ar = (D, 0.0, 0.0)
    pts_j = branche(attache, (pied_ar[0], 0.0, 40.0), 40.0, (1.0, 0.0, 1.0), n=7)
    plan.ajouter(Composant("jambe_de_force", fuseaux_le_long("jambe", pts_j, g("bois.section_noeud"), d_ext, ess),
                           "Jambe de force arriere (branche)"))
    st, ct, ep = g("bois.section_traverse"), g("traverse.cote_tube"), g("traverse.epaisseur_paroi")
    pieds_av = [branches[0][0], branches[1][0]]
    plan.ajouter(Composant("semelle_avant", [Boite("semelle_avant", (0.0, 0.0, st / 2.0), st, wb + 120, st, ess)],
                           "Semelle avant"))
    l_ar = D
    kgpm = capacite_lest_kg_par_m(p)
    m_lest = min(g("traverse.lest_nominal"), kgpm * (l_ar - 2 * st) / 1000.0)
    plan.ajouter(Composant("semelle_arriere", [
        Boite("semelle_arriere_enveloppe", (D / 2.0, 0.0, st / 2.0), l_ar, st, st, ess),
        TubeCarre("semelle_arriere_tube", (st, 0.0, st / 2.0), (D - st / 2.0, 0.0, st / 2.0), ct, ep, nuance),
        Boite("semelle_arriere_lest", ((D + st / 2.0) / 2.0, 0.0, st / 2.0), m_lest / kgpm * 1000.0, ct - 2 * ep, ct - 2 * ep,
              g("traverse.materiau_lest"), categorie="lest"),
    ], "Semelle arriere lestee %.1f kg" % m_lest))
    plan.verifications.append(Verification("lest_integrable", "ok" if m_lest >= g("traverse.lest_min") else "alerte", m_lest,
                                           g("traverse.lest_min"), "kg", "lest logeable dans la semelle arriere : %.1f kg" % m_lest))
    plan.points_appui += [(-st / 2.0, -(wb + 120) / 2.0), (-st / 2.0, (wb + 120) / 2.0), (D, -st / 2.0), (D, st / 2.0)]
    Pf = g("croix.profondeur_plateforme")
    masses_u = []
    if Pf > 0:
        lattes = [Boite("plateforme_latte_%d" % i, (-Pf / 2.0, y, 25.0), Pf, 70.0, 22.0, ess)
                  for i, y in enumerate([-(wb + 120) / 2.0 + 35 + k * ((wb + 50) / 6.0) for k in range(7)])]
        lattes.append(Boite("plateforme_semelle", (-Pf + st / 2.0, 0.0, st / 4.0), st, wb + 120, st / 2.0, ess))
        plan.ajouter(Composant("plateforme", lattes, "Plateforme a lattes frene (la personne s'y tient)"))
        plan.points_appui += [(-Pf, -(wb + 120) / 2.0), (-Pf, (wb + 120) / 2.0)]
        masses_u = [(g("securite.charge_utilisateur"), (-Pf * 0.45, 0.0, 1000.0))]
        plan.notes.append("Plateforme %g mm : la personne s'y tient, ses tractions sur les anneaux sont internes ; "
                          "seuls les efforts du partenaire sont externes." % Pf)
    plan.jonctions.append(Jonction("jambe_attache", "tenon_barillet", attache, ("jambe_de_force", "noeud"),
                                   {"boulon": "M10 traversant + barillet", "demontable": True}))
    # ancrages : anneaux aux extremites et pres du noeud, oeillets sous semelle avant
    points_anneaux = [("poignet_G", branches[0][-2]), ("poignet_D", branches[1][-2]), ("cheville_G", branches[1][1]),
                      ("cheville_D", branches[0][1]), ("taille_G", lerp(noeud, branches[0][-1], 0.15)),
                      ("taille_D", lerp(noeud, branches[1][-1], 0.15))]
    for nom, pt_ in points_anneaux:
        c, j, v = ancrages.anneau_traverse(p, (pt_[0] - d_b / 2.0, pt_[1], pt_[2]), (-1.0, 0.0, 0.0), "anneau_" + nom)
        for comp in c:
            plan.ajouter(comp)
        plan.jonctions += j
        plan.verifications += v
    c, j, v = ancrages.oeillets_sous_semelles(p, [("AV_G", (0.0, (wb + 120) / 2.0 - 30), (-1.0, 0.0)),
                                                  ("AV_D", (0.0, -(wb + 120) / 2.0 + 30), (-1.0, 0.0))])
    for comp in c:
        plan.ajouter(comp)
    plan.jonctions += j
    # mecanique : sans plateforme, la traction de la personne est externe (poignets) ;
    # avec plateforme, on garde la poussee du partenaire dans le dos et un effort lateral.
    f = g("securite.coefficient_horizontal_long") * g("securite.charge_utilisateur") * G
    forces = [("traction_vers_avant", (-f, 0.0), H * 0.9 if Pf <= 0 else H * 0.5),
              ("poussee_dos", (f * 0.6, 0.0), H * 0.6),
              ("lateral", (0.0, g("securite.coefficient_horizontal_lat") * g("securite.charge_utilisateur") * G), H * 0.75)]
    verifs_standard(plan, masses_u, forces, position_lest=(D / 2.0, 0.0))
    f_ret = ancrages.effort_retenue(p)
    bras = math.hypot(branches[0][-2][1] - noeud[1], branches[0][-2][2] - noeud[2])
    v = verifier_flexion_rond("branche_flexion_noeud", f_ret * bras, d_b, ess, g("securite.securite_bois"))
    plan.verifications.append(v)
    if v.niveau != "ok":
        d_req = d_b * (v.valeur / v.limite) ** (1 / 3.0)
        plan.notes.append("Branches : d %.0f mm requis au noeud pour %.0f N au poignet (ou section ovale lamelle-colle "
                          "%.0f x %.0f, plus profonde que large)" % (d_req, f_ret, d_req * 1.1, d_req * 0.8))
    if plan.stabilite["lest_additionnel_kg"] > 0:
        plan.notes.append("Croix : +%.1f kg de lest ou base plus profonde, ou fixation murale/sol."
                          % plan.stabilite["lest_additionnel_kg"])
    plan.notes.append("Squelette : branches cintrees a verifier en lamelle-colle (rayon), anneaux a positionner "
                      "selon la morphologie (poignets a hauteur bras leves).")
    return plan


def run(context):
    from ..fusion_outils import executer
    return executer(context, concevoir, TYPOLOGIE)


def stop(context):
    pass
