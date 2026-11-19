# -*- coding: utf-8 -*-
"""Moteur de regles materiaux -> geometrie.

Quand un materiau change (essence, garnissage, nuance inox, laiton, lest),
le moteur lit le champ ``regles`` de la nouvelle entree du catalogue,
recalcule les parametres cibles et renvoie la liste des ajustements avec une
explication lisible. Les grandeurs de jonction (tourillons, tenons,
mortaises, inserts) sont ensuite recalculees en cascade a partir des
sections.

Exemple ::

    from equinox.parametres import Parametres
    from equinox import regles
    p = Parametres.pour_typologie("banc_flore")
    p2, ajust = regles.changer_materiau(p, "garnissage", "tissu_krypton")
    print(regles.rapport(ajust))
"""

import math

from .catalogues import CATEGORIES, entree
from .catalogues.bois import BOIS
from .catalogues.metaux import METAUX
from .catalogues.attaches import ATTACHES
from .catalogues import garnissage as _garn

ALERTE = "__alerte__"


class Ajustement(object):
    """Un ajustement de parametre (ou une alerte) issu d'une regle.

    statut : 'applique' | 'modifie_impose' | 'bloque_impose' | 'alerte'
    """

    def __init__(self, chemin, avant, apres, unite, raison, source, statut):
        self.chemin, self.avant, self.apres = chemin, avant, apres
        self.unite, self.raison, self.source, self.statut = unite, raison, source, statut

    def __repr__(self):
        return "<Ajustement %s>" % self

    def __str__(self):
        if self.statut == "alerte":
            return "ALERTE [%s] %s" % (self.source, self.raison)
        u = (" " + self.unite) if self.unite and self.unite not in ("texte", "") else ""
        tag = {"applique": "AJUSTE", "modifie_impose": "AJUSTE (valeur imposee modifiee, a confirmer)",
               "bloque_impose": "BLOQUE (valeur imposee conservee)"}[self.statut]
        return "%s %s : %s%s -> %s%s  [%s] %s" % (tag, self.chemin, _fmt(self.avant), u, _fmt(self.apres), u,
                                                  self.source, self.raison)


def _fmt(v):
    return ("%g" % v) if isinstance(v, float) else str(v)


def _arrondi_sup(v, pas=1.0):
    return math.ceil(v / pas - 1e-9) * pas


# ---------------------------------------------------------------------------
# Calculs elementaires : f(params, entree_catalogue, args) -> (valeur, detail)
# ---------------------------------------------------------------------------
def _section_equivalente(p, ent, args):
    ref = BOIS[args.get("reference", "frene")]
    d0 = float(args.get("valeur_reference"))
    f_rig = (ref["module_elasticite"] / ent["module_elasticite"]) ** 0.25
    f_res = (ref["resistance_flexion"] / ent["resistance_flexion"]) ** (1.0 / 3.0)
    f = max(f_rig, f_res, 1.0)
    d = _arrondi_sup(d0 * f)
    return d, "facteur rigidite %.3f, resistance %.3f sur %g mm (frene)" % (f_rig, f_res, d0)


def _rayon_cintrage(p, ent, args):
    methode = p.get("bois.methode_cintrage")
    actuel = p.get("bois.rayon_courbure_min")
    if methode == "lamelle_colle":
        req = ent["ratio_lamelle"] * p.get("bois.epaisseur_lamelle")
        detail = "lamelle-colle : %g x lamelle %g mm = %g mm" % (ent["ratio_lamelle"], p.get("bois.epaisseur_lamelle"), req)
    elif methode == "vapeur":
        req = ent["ratio_vapeur"] * p.get("bois.section_noeud")
        detail = "vapeur : %g x section %g mm = %g mm" % (ent["ratio_vapeur"], p.get("bois.section_noeud"), req)
    else:
        return (ALERTE, "massif debite : fil tranche dans les courbes, rayon >= 600 mm conseille et sections +20 %")
    req = _arrondi_sup(req, 10.0)
    return max(actuel, req), detail + " (requis), actuel %g mm" % actuel


def _copier(p, ent, args):
    return ent[args["propriete"]], "valeur catalogue '%s'" % args["propriete"]


def _fixer(p, ent, args, cible=None):
    return args["valeur"], "valeur imposee par la regle"


def _alerte(p, ent, args):
    return ALERTE, args["message"]


def _tourillon(p, ent, args):
    std = ATTACHES["tourillon_hetre"]["diametres"]
    cible = p.get("bois.section_noeud") / 5.0
    d = min(std, key=lambda x: (abs(x - cible), -x))
    return float(d), "section_noeud / 5 = %.1f -> standard %d" % (cible, d)


def _longueur_tourillon(p, ent, args):
    d = p.get("jonctions.diametre_tourillon")
    return float(5 * d), "5 x d"


def _tenon(p, ent, args):
    return float(round(p.get("bois.section_noeud") / 3.0)), "section_noeud / 3"


def _mortaise(p, ent, args):
    return float(round(0.8 * p.get("bois.section_noeud"))), "0,8 x section_noeud"


def _longueur_insert(p, ent, args):
    dens = BOIS[p.get("bois.essence")]["densite"]
    return (20.0 if dens >= 650 else 25.0), "densite %g kg/m3" % dens


def _section_metal_equivalente(p, ent, args):
    ref = METAUX[args["reference"]]
    d = _arrondi_sup(args["valeur_reference"] * (ref["limite_elastique"] / ent["limite_elastique"]) ** (1.0 / 3.0))
    return max(d, args["valeur_reference"]), "Re %g -> %g MPa" % (ref["limite_elastique"], ent["limite_elastique"])


def _coloris_disponible(p, ent, args):
    couleur = p.get("garnissage.couleur")
    if couleur in ent["coloris"]:
        return couleur, "coloris disponible"
    return ent["coloris_defaut"], "%r indisponible (coloris : %s)" % (couleur, ", ".join(ent["coloris"]))


def _rembourrage_relatif(p, ent, args):
    ref = _garn.rembourrage_recommande(args["reference"])
    return ref + args["ecart"], "rembourrage %s %g mm %+g mm" % (args["reference"], ref, args["ecart"])


def _alerte_si(p, ent, args):
    if p.get(args["parametre"], None) == args["valeur"]:
        return ALERTE, args["message"]
    return None, None


def _hauteur_structure(p, ent, args):
    h, r, s = (p.get("dimensions.hauteur_assise"), p.get("garnissage.epaisseur_rembourrage"),
               p.get("garnissage.epaisseur_support"))
    return h - r - s, "assise maintenue a %g mm : %g - %g (rembourrage) - %g (support)" % (h, h, r, s)


def capacite_lest_kg_par_m(p, materiau=None):
    """Masse de lest logeable par metre de tube carre [kg/m]."""
    ent = METAUX[materiau or p.get("traverse.materiau_lest")]
    interieur = p.get("traverse.cote_tube") - 2 * p.get("traverse.epaisseur_paroi")
    return interieur ** 2 * 1e-6 * ent["densite"] * ent.get("taux_remplissage", 1.0)


def _capacite_lest(p, ent, args):
    kgpm = capacite_lest_kg_par_m(p)
    l_req = p.get("traverse.lest_nominal") / kgpm * 1000.0
    return ALERTE, ("lest %s : %.2f kg/m dans tube %gx%g ; %g kg exigent %.0f mm de tube rempli"
                    % (p.get("traverse.materiau_lest"), kgpm, p.get("traverse.cote_tube"), p.get("traverse.cote_tube"),
                       p.get("traverse.lest_nominal"), l_req))


CALCULS = {
    "section_equivalente": _section_equivalente,
    "rayon_cintrage": _rayon_cintrage,
    "copier": _copier,
    "fixer": _fixer,
    "alerte": _alerte,
    "tourillon": _tourillon,
    "longueur_tourillon": _longueur_tourillon,
    "tenon": _tenon,
    "mortaise": _mortaise,
    "longueur_insert": _longueur_insert,
    "section_metal_equivalente": _section_metal_equivalente,
    "capacite_lest": _capacite_lest,
    "coloris_disponible": _coloris_disponible,
    "rembourrage_relatif": _rembourrage_relatif,
    "alerte_si": _alerte_si,
    "hauteur_structure": _hauteur_structure,
}

#: Regles de jonction recalculees en cascade apres tout changement.
REGLES_JONCTIONS = (ATTACHES["tourillon_hetre"]["regles"] + ATTACHES["tenon_mortaise"]["regles"]
                    + ATTACHES["insert_filete_m8"]["regles"])

#: Grandeurs geometriques derivees recalculees en cascade (assise constante).
REGLES_DERIVEES = [{"cible": "dimensions.hauteur_structure", "calcul": "hauteur_structure",
                    "raison": "hauteur de structure recalculee pour garder la hauteur d'assise"}]


# ---------------------------------------------------------------------------
# Moteur
# ---------------------------------------------------------------------------
def appliquer_regles(params, regles, ent, source, forcer_imposes=True):
    """Applique une liste de regles sur ``params`` (modifie en place)."""
    ajustements = []
    for regle in regles:
        calcul = CALCULS[regle["calcul"]]
        args = regle.get("args", {})
        cible = regle.get("cible")
        if regle["calcul"] == "fixer" and "si_parmi" in args and params.get(cible) not in args["si_parmi"]:
            continue
        valeur, detail = calcul(params, ent, args)
        if valeur is None and detail is None:  # regle conditionnelle non declenchee
            continue
        if valeur == ALERTE:
            ajustements.append(Ajustement(None, None, None, "", detail, source, "alerte"))
            continue
        avant = params.get(cible)
        if avant == valeur:
            continue
        meta = params.meta(cible)
        unite = meta.unite if meta else ""
        raison = "%s (%s)" % (regle.get("raison", ""), detail)
        if meta is not None and meta.statut == "impose":
            if not forcer_imposes:
                ajustements.append(Ajustement(cible, avant, valeur, unite, raison, source, "bloque_impose"))
                continue
            statut = "modifie_impose"
        else:
            statut = "applique"
        params.set(cible, valeur)
        ajustements.append(Ajustement(cible, avant, valeur, unite, raison, source, statut))
    return ajustements


def recalculer_jonctions(params):
    """Cascade : jonctions derivees des sections et de la densite, puis
    hauteur de structure derivee du rembourrage."""
    ent = BOIS[params.get("bois.essence")]
    return (appliquer_regles(params, REGLES_JONCTIONS, ent, "jonctions")
            + appliquer_regles(params, REGLES_DERIVEES, ent, "geometrie"))


def changer_materiau(params, categorie, cle, forcer_imposes=True):
    """Change le materiau d'une categorie et recalcule la geometrie.

    :param params: ``Parametres`` (non modifie, une copie est renvoyee)
    :param categorie: 'bois' | 'garnissage' | 'inox' | 'laiton' | 'lest'
    :param cle: cle dans le catalogue correspondant
    :param forcer_imposes: si False, les valeurs imposees ne sont pas
        modifiees (ajustement 'bloque_impose' signale a la place)
    :returns: (nouveaux_params, liste d'``Ajustement``)
    """
    chemin, _ = CATEGORIES[categorie]
    ent = entree(categorie, cle)
    if categorie == "garnissage":
        cle = _garn.resoudre(cle)  # ancienne cle -> cle canonique
    p = params.copie()
    avant = p.get(chemin)
    ajust = []
    if avant != cle:
        p.set(chemin, cle)
        ajust.append(Ajustement(chemin, avant, cle, "texte", "changement de materiau demande", categorie, "applique"))
    ajust += appliquer_regles(p, ent.get("regles", []), ent, "%s:%s" % (categorie, cle), forcer_imposes)
    ajust += recalculer_jonctions(p)
    for pb in p.erreurs():
        ajust.append(Ajustement(None, None, None, "", "validation : %s" % pb, "validation", "alerte"))
    return p, ajust


def appliquer_materiaux_actifs(params, forcer_imposes=False):
    """Met ``params`` en coherence avec ses materiaux actuels (copie renvoyee).

    Utilise au lancement d'une grammaire. Par defaut, ne touche pas aux
    valeurs imposees (signalees 'bloque_impose' si une regle les contredit).
    """
    p = params.copie()
    ajust = []
    for categorie, (chemin, _) in sorted(CATEGORIES.items()):
        cle = p.get(chemin)
        ent = entree(categorie, cle)
        ajust += appliquer_regles(p, ent.get("regles", []), ent, "%s:%s" % (categorie, cle), forcer_imposes)
    ajust += recalculer_jonctions(p)
    return p, ajust


def rapport(ajustements):
    """Texte lisible, une ligne par ajustement."""
    if not ajustements:
        return "Aucun ajustement."
    return "\n".join("- %s" % a for a in ajustements)
