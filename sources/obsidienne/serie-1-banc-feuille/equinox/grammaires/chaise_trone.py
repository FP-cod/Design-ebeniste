# -*- coding: utf-8 -*-
"""Grammaire (squelette fonctionnel) : chaise / trone Equinox « Eventail ».

Assise garnie, quatre pieds fuseau, dossier en eventail de nervures (une
nervure centrale + nervures secondaires partant d'un noeud bas, comme les
veines d'une feuille) coiffees d'une branche haute, accoudoirs fins en
branche. Anneaux : bouts d'accoudoirs (poignets), pieds avant (chevilles),
haut du dossier. Oeillets bas sous les pieds arriere.

Repere : X vers l'avant de l'assise, dossier en X < 0.
"""

import math

from ..calculs import G, verifier_flexion_rond
from ..geometrie import Composant, Jonction, Plan, branche, fuseaux_le_long, lerp, rotation_y
from ..parametres import Param
from . import ancrages
from .commun import pied_fuseau, plateau_garni, preparer, verifs_standard

TYPOLOGIE = "chaise_trone"
VAL = "a_valider"

SCHEMA_CHAISE = {
    "profondeur_assise": Param(460.0, "mm", "Profondeur d'assise.", (380.0, 600.0), statut=VAL),
    "hauteur_dossier": Param(1250.0, "mm", "Hauteur du haut du dossier (trone) au sol.", (800.0, 1800.0), statut=VAL),
    "inclinaison_dossier": Param(12.0, "deg", "Inclinaison du dossier vers l'arriere.", (0.0, 30.0), statut=VAL),
    "nervures": Param(5, "", "Nombre de nervures du dossier (impair).", (3, 9), statut=VAL),
    "recul_pieds_arriere": Param(220.0, "mm", "Recul supplementaire des pieds arriere (pieds 'sabre') contre le "
                                 "basculement arriere du trone.", (0.0, 400.0), statut=VAL),
    "hauteur_accoudoirs": Param(670.0, "mm", "Hauteur des accoudoirs au sol.", (550.0, 800.0), statut=VAL),
}


def concevoir(params=None, overrides=None):
    p, ajust = preparer(TYPOLOGIE, SCHEMA_CHAISE, "chaise", params, overrides)
    g = p.get
    plan = Plan(TYPOLOGIE, p)
    plan.ajustements = ajust
    H, P, W = g("dimensions.hauteur_assise"), g("chaise.profondeur_assise"), g("dimensions.largeur_plateau")
    r, es = g("garnissage.epaisseur_rembourrage"), g("garnissage.epaisseur_support")
    ess, d_n, d_e = g("bois.essence"), g("bois.section_noeud"), g("bois.section_extremite")
    inc = g("garnissage.inclinaison_plateau")
    plateau_garni(plan, "assise", P, W, H, x0=-P / 2.0, exposant=3.5, angle=-inc, pivot=(P / 2.0, 0.0, H))
    z_n = H - r - es - 30.0
    rx, ry = P / 2.0 - 50.0, W / 2.0 - 40.0
    pieds = {}
    for nom, sx, sy in (("AR_G", -1, 1), ("AR_D", -1, -1), ("AV_G", 1, 1), ("AV_D", 1, -1)):
        recul = (-g("chaise.recul_pieds_arriere"), 0.0) if sx < 0 else (0.0, 0.0)
        pieds[nom] = pied_fuseau(plan, "pied_" + nom, (sx * rx, sy * ry, z_n), (sx, sy), cambrure=8.0,
                                 decalage_pied=recul)
    # dossier en eventail
    n = int(g("chaise.nervures"))
    base = (-rx, 0.0, z_n + 20.0)
    Hd, incd = g("chaise.hauteur_dossier"), g("chaise.inclinaison_dossier")
    sommets = []
    for i in range(n):
        u = (i / float(n - 1)) * 2 - 1
        top = rotation_y((-rx, u * (W / 2.0 + 60.0), Hd - 60.0 * u * u), base, -incd)
        sommets.append(top)
        pts = branche(lerp(base, top, 0.0), top, 25.0 * u, (0.0, 1.0, 0.0), n=5)
        d0 = d_n if i == n // 2 else (d_n + d_e) / 2.0
        plan.ajouter(Composant("nervure_%d" % i, fuseaux_le_long("nervure_%d" % i, pts, d0, d_e, ess), "Nervure de dossier"))
        plan.jonctions.append(Jonction("nervure_%d_pied" % i, "tenon_mortaise", base, ("nervure_%d" % i, "traverse_dossier"),
                                       {"tenon": g("jonctions.epaisseur_tenon")}))
    plan.ajouter(Composant("branche_haute", fuseaux_le_long("branche_haute", branche(sommets[0], sommets[-1], 60.0, (0, 0, 1), n=7),
                                                            d_e, d_e, ess), "Branche haute du dossier"))
    # accoudoirs
    za = g("chaise.hauteur_accoudoirs")
    for cote, s in (("G", 1), ("D", -1)):
        a = (-rx, s * (ry + 20.0), za)
        b = (rx + 40.0, s * (ry + 50.0), za - 10.0)
        pts = branche(a, b, 20.0, (0.0, s, 1.0), n=5)
        plan.ajouter(Composant("accoudoir_" + cote, fuseaux_le_long("accoudoir_" + cote, pts, d_n * 0.8, d_e, ess), "Accoudoir branche"))
        c, j, v = ancrages.anneau_traverse(p, b, (0.0, s, 0.0), "anneau_poignet_" + cote)
        for comp in c:
            plan.ajouter(comp)
        plan.jonctions += j
        plan.verifications += v
        plan.verifications.append(verifier_flexion_rond("accoudoir_%s_flexion" % cote, ancrages.effort_retenue(p) * 150.0,
                                                        d_e, ess, g("securite.securite_bois")))
    for cote in ("G", "D"):
        info = plan.repere["pieds"]["pied_AV_" + cote]
        c, j, v = ancrages.anneau_traverse(p, lerp(info["noeud"], info["pied"], 0.8), (1.0, 0.0, 0.0), "anneau_cheville_" + cote)
        for comp in c:
            plan.ajouter(comp)
        plan.jonctions += j
    c, j, v = ancrages.oeillets_sous_semelles(p, [("AR_G", pieds["AR_G"][:2], (-1, 0.5)), ("AR_D", pieds["AR_D"][:2], (-1, -0.5))])
    for comp in c:
        plan.ajouter(comp)
    plan.jonctions += j
    plan.verifications += v
    u = g("securite.charge_utilisateur")
    f = g("securite.coefficient_horizontal_long") * u * G
    forces = [("appui_dossier", (-f, 0.0), Hd * 0.8), ("lateral", (0.0, g("securite.coefficient_horizontal_lat") * u * G), H + 300),
              ("vers_avant", (f * 0.5, 0.0), H + 200)]
    verifs_standard(plan, [(u, (-P * 0.1, 0.0, H + 200.0))], forces, position_lest=(-rx - g("chaise.recul_pieds_arriere") * 0.5, 0.0), hauteur_pied=z_n)
    if plan.stabilite["lest_additionnel_kg"] > 0:
        plan.notes.append("Trone : +%.1f kg de lest bas a l'arriere requis ; alternatives : augmenter "
                          "chaise.recul_pieds_arriere, reduire l'inclinaison du dossier, ou ancrer au sol (oeillets bas)."
                          % plan.stabilite["lest_additionnel_kg"])
    plan.notes.append("Squelette : eventail de nervures a affiner en dessin ; assise inclinee de %g deg vers l'arriere." % inc)
    return plan


def run(context):
    from ..fusion_outils import executer
    return executer(context, concevoir, TYPOLOGIE)


def stop(context):
    pass
