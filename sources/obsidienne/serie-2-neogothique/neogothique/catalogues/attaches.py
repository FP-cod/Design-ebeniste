# -*- coding: utf-8 -*-
"""Couche 2 - Systemes d'attache d'ebenisterie (zero vis apparente).

Chaque entree decrit un type de jonction :

- ``nom``, ``description``      : designation, principe.
- ``proportions``               : regles de proportion de l'ebenisterie
  traditionnelle, utilisees par ``dimensionner()`` :
    * ``ratio_epaisseur``       : epaisseur tenon / epaisseur de la piece
      (regle du tiers : 1/3) ;
    * ``ratio_longueur``        : longueur tenon / epaisseur piece receveuse
      (1.0 = traversant) ;
    * ``ratio_diametre_max``    : diametre tourillon / epaisseur la plus
      fine (<= 1/2) ;
    * ``ratio_profondeur``      : profondeur de percage / diametre ;
    * ``ratio_cheville``        : diametre cheville / epaisseur tenon ;
    * ``saillie_ratio``         : saillie du tenon clavete / epaisseur clef.
- ``capacite``                  : mode de calcul de resistance indicatif.
- ``demontable``                : la jonction se demonte-t-elle ?
- ``vis_apparente``             : toujours False dans la gamme.
- ``regles``                    : regles declaratives appliquees quand on
  choisit ce type pour une jonction (``jonctions.type_*``).

Sources : pratiques d'ebenisterie / charpenterie traditionnelles (regle du
tiers, chevillage a tire - « drawbore », tenon a clef dit « tusk tenon ») ;
Wood Handbook GTR-282 ch. 7-8 pour l'ordre de grandeur des resistances.
"""

import math

ATTACHES = {
    "tenon_mortaise_borgne": {
        "nom": "Tenon-mortaise borgne colle",
        "description": "Tenon au tiers, longueur 2/3 de la piece receveuse, colle (colle hide "
                       "ou PVA D3) ; invisible.",
        "proportions": {"ratio_epaisseur": 1.0 / 3.0, "ratio_longueur": 2.0 / 3.0, "ratio_largeur": 0.8},
        "capacite": "cisaillement du tenon + collage",
        "demontable": False, "vis_apparente": False,
        "regles": [
            {"id": "borgne_dilatation", "operation": "signaler",
             "explication": "Tenon borgne colle : ne pas l'utiliser en travers du fil d'un plateau large "
                            "sans mortaise oblongue (jeu {tolerances.jeu_mortaise_oblongue} mm)."},
        ],
    },
    "tenon_traversant_cale": {
        "nom": "Tenon traversant a coins (wedged through tenon)",
        "description": "Tenon traversant la platine, deux traits de scie et deux coins de chene "
                       "contrastes chasses au maillet : bout de tenon apparent, decor franc.",
        "proportions": {"ratio_epaisseur": 1.0 / 3.0, "ratio_longueur": 1.0, "ratio_largeur": 0.8,
                        "pente_coin": 1.0 / 8.0},
        "capacite": "cisaillement du tenon ; arrachement repris par les coins",
        "demontable": False, "vis_apparente": False,
        "regles": [
            {"id": "cale_aspect", "operation": "signaler",
             "explication": "Bout de tenon visible sur le dessus : affleurer et chanfreiner "
                            "{bois.chanfrein_aretes} mm."},
        ],
    },
    "tenon_traversant_cheville": {
        "nom": "Tenon traversant cheville a tire (drawbore)",
        "description": "Trou de cheville du tenon decale de quelques dixiemes vers l'epaulement : "
                       "la cheville serre la jonction sans colle ni vis.",
        "proportions": {"ratio_epaisseur": 1.0 / 3.0, "ratio_longueur": 1.0, "ratio_largeur": 0.8,
                        "ratio_cheville": 0.45},
        "capacite": "double cisaillement des chevilles",
        "demontable": False, "vis_apparente": False,
        "regles": [
            {"id": "drawbore_decalage", "cibles": ["jonctions.decalage_drawbore"], "operation": "minimum",
             "valeur": 1.0, "explication": "Chevillage a tire : decalage >= 1 mm (1,5 mm conseille en chene)."},
        ],
    },
    "tenon_traversant_clavete": {
        "nom": "Tenon traversant a clef (tusk tenon, demontable)",
        "description": "Tenon long qui traverse et depasse ; une clef de chene verticale passee dans "
                       "le depassement serre l'assemblage. Demontable, typique des treteaux medievaux.",
        "proportions": {"ratio_epaisseur": 1.0 / 3.0, "ratio_longueur": 1.0, "ratio_largeur": 0.6,
                        "saillie_ratio": 3.0},
        "capacite": "cisaillement du bois en bout de tenon devant la clef",
        "demontable": True, "vis_apparente": False,
        "regles": [
            {"id": "clef_saillie", "cibles": ["jonctions.saillie_tenon_clavete"], "operation": "minimum",
             "valeur": 40.0, "explication": "Tenon a clef : saillie >= 40 mm pour ne pas faire eclater "
                                              "le bout du tenon devant la clef."},
        ],
    },
    "tourillons": {
        "nom": "Tourillons cannelés (hetre ou chene)",
        "description": "Alignement et reprise d'effort moderee ; pour assembler les joues des "
                       "fourreaux et les alaises de platine. Non porteur seul en arrachement.",
        "proportions": {"ratio_diametre_max": 0.5, "ratio_profondeur": 2.5},
        "capacite": "cisaillement du tourillon",
        "demontable": False, "vis_apparente": False,
        "regles": [
            {"id": "tourillon_porteur", "operation": "signaler",
             "explication": "Tourillons choisis pour une jonction porteuse : prevoir au moins 4 tourillons "
                            "de {jonctions.tourillon_diametre} mm et verifier l'arrachement ; preferer un tenon."},
        ],
    },
    "chevillage": {
        "nom": "Chevillage (cheville de chene fendue, section octogonale)",
        "description": "Cheville fendue au merlin puis taillee en octogone, chassee dans un trou rond : "
                       "tient sans colle.",
        "proportions": {"ratio_diametre_max": 0.5},
        "capacite": "double cisaillement",
        "demontable": False, "vis_apparente": False,
        "regles": [],
    },
    "rivet_forge": {
        "nom": "Rivet forge traversant a contre-plaque",
        "description": "Fixation des ferrures sur le bois sans vis : rivet a tete carree, "
                       "contre-plaque et rivure cote cache.",
        "proportions": {"ratio_diametre_max": 0.25},
        "capacite": "cisaillement du rivet + matage du bois",
        "demontable": False, "vis_apparente": False,
        "regles": [],
    },
}

#: Types admis pour chaque jonction de l'Entrave (valide les parametres).
JONCTIONS_ADMISES = {
    "coulisseau_platine": ["tenon_traversant_cale", "tenon_traversant_cheville", "tenon_mortaise_borgne"],
    "fourreau_semelle": ["tenon_traversant_cheville", "tenon_traversant_cale", "tenon_mortaise_borgne"],
    "traverse_semelle": ["tenon_traversant_clavete", "tenon_traversant_cheville"],
    "joues_fourreau": ["tourillons", "chevillage"],
}


def _arrondi(v, pas=1.0, sens="bas"):
    f = math.floor if sens == "bas" else math.ceil
    return f(v / pas + (1e-9 if sens == "bas" else -1e-9)) * pas


def dimensionner(cle, epaisseur_piece, epaisseur_receveuse, largeur_piece=None, params=None):
    """Dimensionne une jonction d'apres les proportions du catalogue.

    :param cle: cle de ``ATTACHES``.
    :param epaisseur_piece: epaisseur (mm) de la piece qui porte le tenon
        (ou piece la plus fine pour un tourillon).
    :param epaisseur_receveuse: epaisseur (mm) de la piece mortaisee.
    :param largeur_piece: largeur (mm) de la piece tenonnee (defaut = epaisseur).
    :param params: objet ``Parametres`` (diametres de cheville/tourillon,
        decalage drawbore, saillie...). Optionnel.
    :return: dict des cotes (mm) avec la cle ``type``.
    """
    ent = ATTACHES[cle]
    pr = ent["proportions"]
    largeur_piece = largeur_piece or epaisseur_piece
    g = (lambda c, d: params.get(c, d)) if params is not None else (lambda c, d: d)
    res = {"type": cle, "nom": ent["nom"]}
    if "ratio_epaisseur" in pr:
        ratio = g("jonctions.ratio_tenon", pr["ratio_epaisseur"])
        ep = _arrondi(epaisseur_piece * ratio, 1.0, "haut")
        res.update({
            "tenon_epaisseur": ep,
            "tenon_largeur": _arrondi(largeur_piece * pr.get("ratio_largeur", 0.8), 1.0),
            "tenon_longueur": _arrondi(epaisseur_receveuse * pr["ratio_longueur"], 1.0),
            "mortaise_epaisseur": ep + g("tolerances.jeu_mortaise", 0.2),
            "epaulement": (epaisseur_piece - ep) / 2.0,
        })
        if "ratio_cheville" in pr:
            dch = min(g("jonctions.cheville_diametre", 10.0), _arrondi(ep * 0.5, 1.0))
            res["cheville_diametre"] = dch
            res["decalage_drawbore"] = g("jonctions.decalage_drawbore", 1.5)
            res["nombre_chevilles"] = 2 if largeur_piece >= 60 else 1
        if "pente_coin" in pr:
            res["coins"] = 2
            res["pente_coin"] = pr["pente_coin"]
        if "saillie_ratio" in pr:
            ep_clef = max(10.0, _arrondi(ep * 0.6, 1.0))
            res["clef_epaisseur"] = ep_clef
            res["saillie"] = max(g("jonctions.saillie_tenon_clavete", 45.0), pr["saillie_ratio"] * ep_clef)
    else:
        dmax = _arrondi(epaisseur_piece * pr.get("ratio_diametre_max", 0.5), 1.0)
        d = min(g("jonctions.tourillon_diametre", 10.0), dmax) if cle == "tourillons" else dmax
        res.update({"diametre": d, "diametre_max": dmax,
                    "profondeur": d * pr.get("ratio_profondeur", 2.5)})
    return res


def capacite_cheville_n(diametre, fv_mpa=7.0, cisaillements=2):
    """Capacite indicative (N) d'une cheville de chene en cisaillement.

    ``fv_mpa`` : resistance au cisaillement transversal du bois de cheville
    (ordre de grandeur, chene fendu de fil). Valeur caracteristique, sans
    coefficient de securite.
    """
    return cisaillements * math.pi * diametre ** 2 / 4.0 * fv_mpa
