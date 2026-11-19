# -*- coding: utf-8 -*-
"""Regles de compatibilite (assortiment, materiaux) et de securite.

``evaluer(params, cotes)`` renvoie une liste de ``Constat`` :

- ``ECHEC``  : configuration a corriger avant fabrication (bloquant) ;
- ``ALERTE`` : a verifier / deconseille (non bloquant) ;
- ``INFO``   : rappel ou choix derive (ex. longueur de rivet retenue).

Les charges de quincaillerie etant des estimations non sourcees, une piece
n'est JAMAIS declaree conforme sur estimation : au mieux ALERTE "a verifier
fournisseur" avec la charge mini a exiger.
"""

import math

from .catalogues import cuirs, fermetures, finitions, quincaillerie as q

EST = q.EST


class Constat(object):
    def __init__(self, niveau, code, message):
        self.niveau, self.code, self.message = niveau, code, message

    def __repr__(self):
        return "%s [%s] %s" % (self.niveau, self.code, self.message)


def effort_requis(p):
    """Charge de rupture mini a exiger de chaque maillon [N]."""
    return p.get("securite.effort_service") * p.get("securite.coefficient_dynamique") * \
        p.get("securite.coefficient_securite")


def accord_metal_teinte(teinte, metal):
    """'conseille' | 'possible' | 'inhabituel'."""
    t = cuirs.TEINTES[teinte]
    if metal in t["quincaillerie_conseillee"]:
        return "conseille"
    if metal in t["quincaillerie_possible"]:
        return "possible"
    return "inhabituel"


def choisir_longueur_rivet(rivet, empilement, surplus_min=0.5, surplus_max=3.0):
    """Plus courte tige qui depasse l'empilement de surplus_min a surplus_max mm, sinon None."""
    for l in sorted(q.RIVETS[rivet]["longueurs_tige"]):
        if empilement + surplus_min <= l <= empilement + surplus_max:
            return l
    return None


def regles_compatibilite(p):
    c = []
    g = p.get
    teinte, matiere, metal = g("finition.teinte"), g("cuir.matiere"), g("finition.quincaillerie")
    if not cuirs.teinte_disponible(matiere, teinte):
        c.append(Constat("ECHEC", "teinte_matiere", "teinte %s indisponible en %s (teintes : %s)"
                         % (teinte, matiere, ", ".join(cuirs.CUIRS[matiere]["teintes"]))))
    doub = g("cuir.doublure_matiere")
    if g("cuir.nb_couches") >= 2 and teinte not in cuirs.DOUBLURES[doub]["teintes"]:
        c.append(Constat("ALERTE", "teinte_doublure", "doublure %s non disponible en %s : doublure contrastee "
                         "(%s)" % (doub, teinte, ", ".join(cuirs.DOUBLURES[doub]["teintes"]))))
    accord = accord_metal_teinte(teinte, metal)
    if accord == "inhabituel":
        c.append(Constat("ALERTE", "accord_metal", "quincaillerie %s inhabituelle avec le cuir %s (conseille : %s)"
                         % (metal, teinte, ", ".join(cuirs.TEINTES[teinte]["quincaillerie_conseillee"]))))
    elif accord == "possible":
        c.append(Constat("INFO", "accord_metal", "%s avec %s : possible (contraste) ; conseille : %s"
                         % (metal, teinte, ", ".join(cuirs.TEINTES[teinte]["quincaillerie_conseillee"]))))
    m = q.METAUX[metal]
    if m["contact_peau"] != "ok":
        c.append(Constat("ALERTE", "contact_peau", "%s : %s - reserver aux pieces sans contact peau prolonge"
                         % (m["nom"], m["contact_peau"])))
    for cat, cle in (("boucle", g("finition.boucle")), ("anneau", g("anneau_d.reference") if g("anneau_d.present") else None)):
        if cle is None:
            continue
        piece = q.TOUTES[cat][cle]
        if q.METAUX[piece["metal"]]["famille"] != m["famille"]:
            c.append(Constat("ALERTE", "quincaillerie_depareillee", "%s en %s alors que la quincaillerie de la "
                             "piece est %s" % (piece["nom"], piece["metal"], metal)))
    tr = finitions.TRANCHES[g("finition.tranche")]
    if matiere not in tr["cuirs"]:
        c.append(Constat("ECHEC", "tranche_matiere", "finition %s impossible sur %s" % (tr["nom"], matiere)))
    fil = finitions.FILS[g("couture.fil")]
    lo, hi = fil["pas_conseille"]
    if not (lo <= g("couture.pas_point") <= hi):
        c.append(Constat("ALERTE", "pas_fil", "pas %.2f mm hors plage conseillee %s pour %s"
                         % (g("couture.pas_point"), fil["pas_conseille"], fil["nom"])))
    if g("cuir.rembourrage") and cuirs.REMBOURRAGES[g("cuir.rembourrage_materiau")]["allergene"]:
        c.append(Constat("INFO", "allergene", "rembourrage %s : allergene %s a signaler au client"
                         % (g("cuir.rembourrage_materiau"), cuirs.REMBOURRAGES[g("cuir.rembourrage_materiau")]["allergene"])))
    return c


def regles_securite(p, cotes=None):
    c = []
    g = p.get
    cotes = cotes or {}
    contention = g("produit.usage") == "contention"
    ferm = g("finition.fermeture")
    w = p.largeur_bande()
    if g("securite.jeu_doigt") < 15.0:
        c.append(Constat("ECHEC", "jeu_doigt", "jeu %.0f mm < 15 mm : risque de garrot" % g("securite.jeu_doigt")))
    if ferm == "scratch":
        c.append(Constat("ECHEC" if contention else "ALERTE", "scratch",
                         "scratch deconseille pour une contention serieuse (s'ouvre sous traction)" if contention
                         else "scratch : jeu leger uniquement"))
    if ferm == "boucle_ardillon_cadenas":
        if not q.BOUCLES[g("finition.boucle")].get("verrouillable"):
            c.append(Constat("ECHEC", "cadenas_boucle", "fermeture a cadenas : choisir une boucle verrouillable"))
        if not g("securite.deverrouillage_rapide"):
            c.append(Constat("ECHEC", "cadenas_sans_secours", "cadenas sans attache de deverrouillage rapide en aval"))
        c.append(Constat("ALERTE", "cadenas_cle", "cadenas : cle (et double) a portee, ciseaux de securite a proximite"))
    if not g("securite.deverrouillage_rapide"):
        c.append(Constat("ALERTE", "deverrouillage", "attache de deverrouillage rapide (mousqueton panique) "
                         "recommandee entre l'anneau et le point d'ancrage"))
    r_ext = g("extremites.rayon_ratio") * w
    if r_ext < g("securite.rayon_mini_extremite"):
        c.append(Constat("ECHEC", "coin_vif", "rayon d'extremite %.1f mm < %.1f mm" % (r_ext, g("securite.rayon_mini_extremite"))))
    if finitions.TRANCHES[g("finition.tranche")]["arete_vive"]:
        c.append(Constat("ECHEC", "arete_vive", "tranche %s : arete vive interdite sur un accessoire porte"
                         % g("finition.tranche")))
    if g("extremites.rayon_tranche") < 0.5:
        c.append(Constat("ALERTE", "rayon_tranche", "abat-carre < 0,5 mm : arete encore vive"))
    if contention and w < 40.0:
        c.append(Constat("ALERTE", "largeur_contention", "bande %.0f mm < 40 mm en contention : pression concentree" % w))
    if g("jonctions.rivet") == "rivet_cuivre_contre_rivet":
        c.append(Constat("ALERTE", "rivet_cote_peau", "contre-rivet : le placer cote exterieur ou sous rabat, "
                         "jamais nu cote peau"))
    # rigidite : cuir epais sur petit tour
    rayon_membre = p.tour() / (2 * math.pi)
    if rayon_membre / g("cuir.epaisseur_exterieure") < 6.0:
        c.append(Constat("ALERTE", "cintrage", "rayon du membre %.0f mm < 6 x epaisseur (%.1f mm) : cuir trop "
                         "raide, risque de fleur qui craque (regle d'atelier estimee)"
                         % (rayon_membre, g("cuir.epaisseur_exterieure"))))
    # quincaillerie : dimensions
    b = q.BOUCLES[g("finition.boucle")]
    if b["passage"] < w + g("tolerances.jeu_passage_boucle"):
        c.append(Constat("ECHEC", "passage_boucle", "boucle passage %.0f mm < bande %.0f + jeu" % (b["passage"], w)))
    elif b["passage"] - w > 6.0:
        c.append(Constat("ALERTE", "boucle_trop_large", "boucle %.0f mm pour une bande de %.0f mm : la bande flotte"
                         % (b["passage"], w)))
    if g("ardillon.diametre_trou") < b["ardillon_diametre"] + g("tolerances.jeu_trou_ardillon"):
        c.append(Constat("ECHEC", "trou_ardillon", "trou %.1f mm < ardillon %.1f + jeu %.1f"
                         % (g("ardillon.diametre_trou"), b["ardillon_diametre"], g("tolerances.jeu_trou_ardillon"))))
    if g("anneau_d.present"):
        a = q.ANNEAUX[g("anneau_d.reference")]
        if a["passage"] < g("anneau_d.largeur_patte") + g("tolerances.jeu_passage_boucle"):
            c.append(Constat("ECHEC", "passage_anneau", "anneau passage %.0f < patte %.0f + jeu"
                             % (a["passage"], g("anneau_d.largeur_patte"))))
        dispo = g("anneau_d.longueur_patte") / 2.0 - a["fil"] - 4.0
        if g("anneau_d.entraxe_rivets_patte") + g("jonctions.diametre_trou_rivet") > dispo:
            c.append(Constat("ECHEC", "patte_courte", "patte : %.1f mm disponibles pour deux rivets (entraxe %.0f + "
                             "trou)" % (dispo, g("anneau_d.entraxe_rivets_patte"))))
    # longueurs de rivets
    e_cs = p.epaisseur_cuir_seul()
    empilements = {}
    if g("jonctions.fixation_repli") in ("rivets", "rivets_et_couture"):
        empilements["repli_boucle"] = 2 * e_cs
    if g("anneau_d.present"):
        empilements["patte_anneau"] = e_cs + 2 * g("cuir.epaisseur_exterieure")
    for ou, emp in empilements.items():
        l = choisir_longueur_rivet(g("jonctions.rivet"), emp)
        cotes["rivet_%s_longueur" % ou] = l
        if l is None:
            c.append(Constat("ECHEC", "rivet_longueur", "%s : aucune tige de %s pour un empilement de %.1f mm "
                             "(longueurs %s)" % (ou, g("jonctions.rivet"), emp, q.RIVETS[g("jonctions.rivet")]["longueurs_tige"])))
        else:
            c.append(Constat("INFO", "rivet_longueur", "%s : empilement %.1f mm -> tige %g mm" % (ou, emp, l)))
    # resistance
    f = effort_requis(p)
    cotes["effort_requis_n"] = f
    sigma = cuirs.CUIRS[g("cuir.matiere")]["resistance_traction_mpa"]
    if sigma:
        sections = {"bande_au_trou": (w - g("ardillon.diametre_trou")) * g("cuir.epaisseur_exterieure")}
        if g("anneau_d.present"):
            sections["patte_double"] = 2 * g("anneau_d.largeur_patte") * g("cuir.epaisseur_exterieure")
        for nom, s in sections.items():
            r = s * sigma
            cotes["resistance_%s_n" % nom] = r
            if r < f:
                c.append(Constat("ECHEC", "resistance_cuir", "%s : %.0f N < %.0f N requis (cuir %g MPa, ordre de "
                                 "grandeur repris de Neogothique)" % (nom, r, f, sigma)))
    else:
        c.append(Constat("ALERTE", "resistance_cuir", "resistance du cuir %s non sourcee : essai de traction "
                         "a faire" % g("cuir.matiere")))
    maillons = [("boucle", q.BOUCLES[g("finition.boucle")])]
    if g("anneau_d.present"):
        maillons.append(("anneau", q.ANNEAUX[g("anneau_d.reference")]))
        rv = q.RIVETS[g("jonctions.rivet")]
        if g("anneau_d.fixation_patte") == "rivets":
            maillons.append(("2 rivets de patte", dict(rv, charge_rupture_n=2 * rv["charge_rupture_n"])))
        else:
            c.append(Constat("ALERTE", "essai_patte", "patte cousue + rivetee : capacite combinee non calculable, "
                             "essai de traction >= %.0f N a faire sur prototype" % f))
    if g("securite.deverrouillage_rapide"):
        maillons.append(("mousqueton", q.MOUSQUETONS["mousqueton_panique_inox"]))
    for role, piece in maillons:
        ch = piece["charge_rupture_n"]
        if ch is None:
            continue
        if piece["statut_charge"] == EST:
            niveau_txt = "probablement insuffisant" if ch < f else "plausible"
            c.append(Constat("ALERTE", "charge_estimee", "%s (%s) : %.0f N estime (%s) - exiger du fournisseur une "
                             "rupture >= %.0f N" % (role, piece["nom"], ch, niveau_txt, f)))
        elif ch < f:
            c.append(Constat("ECHEC", "charge", "%s : %.0f N < %.0f N" % (role, ch, f)))
    # reglage vs plage de taille
    if "tour_mini_reglable" in cotes:
        lo, hi = p.plage_taille()
        if cotes["tour_mini_reglable"] > lo or cotes["tour_maxi_reglable"] < hi:
            c.append(Constat("ALERTE", "plage_reglage", "trous : tours %.0f-%.0f mm, plage de taille %.0f-%.0f mm"
                             % (cotes["tour_mini_reglable"], cotes["tour_maxi_reglable"], lo, hi)))
    c.append(Constat("INFO", "usage", "aucune suspension par les menottes ; surveiller la circulation "
                     "(couleur, fourmillements, froid) ; ciseaux de securite a portee"))
    return c


def evaluer(p, cotes=None):
    return regles_compatibilite(p) + regles_securite(p, cotes)
