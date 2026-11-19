# -*- coding: utf-8 -*-
"""Jonctions d'ebenisterie et regles de dimensionnement.

Les regles sont REPRISES des autres gammes (sources citees) :

- tourillons : diametre <= 0,5 x epaisseur du panneau (Neogothique,
  ``ratio_diametre_max``), arrondi au diametre standard inferieur (Equinox :
  6/8/10/12/14) ; longueur = 5 d (Equinox) ; alesage cote chant = 2,5 d
  (Neogothique, ``ratio_profondeur``) ; au moins 2 par jonction (Equinox) ;
- tenon-mortaise : epaisseur de tenon = 1/3 de la piece tenonnee, profondeur
  de mortaise = 0,8 x piece receveuse (Equinox, repris par Aboutissants) ;
- barillet M8 : a >= 2,5 d du bout (Equinox) ;
- tasseau biseaute (« french cleat ») : propose pour la pose murale
  modulaire, sans source -> À VALIDER.
"""

import math

from .. import sources as S

DIAMETRES_TOURILLON = [6, 8, 10, 12, 14]          # Equinox attaches.tourillon_hetre
RATIO_DIAMETRE_TOURILLON = 0.5                     # Neogothique attaches.tourillons
RATIO_LONGUEUR_TOURILLON = 5.0                     # Equinox (L >= 5 d)
RATIO_ALESAGE_TOURILLON = 2.5                      # Neogothique (profondeur = 2,5 d)
FRACTION_TENON = 1.0 / 3.0                         # Equinox regle du tiers
FRACTION_MORTAISE = 0.8                            # Equinox 0,8 x section
ANGLE_TASSEAU_BISEAUTE = 45.0                      # À VALIDER

JONCTIONS = {
    "tourillons": {
        "nom": "Tourillons canneles (hetre ou chene), colles", "demontable": False, "capacite_service": 1500.0,
        "regle": "d = plus grand standard <= 0,5 e ; L = 5 d ; alesage chant 2,5 d ; >= 2 par jonction",
        "source": S.EQ_ATT + " (tourillon_hetre, 1500 N) ; " + S.NEO_ATT + " (tourillons : ratios 0,5 / 2,5) ; "
                  + S.INC_FIX + " (TOURILLON_10 : caissons)",
        "compromis": "Invisible, economique, ideal pour caissons ; non porteur seul en arrachement (Neogothique).",
        "a_valider": False,
    },
    "tenon_mortaise": {
        "nom": "Tenon-mortaise colle (+ cheville)", "demontable": False, "capacite_service": 3000.0,
        "regle": "tenon = 1/3 de la piece tenonnee ; mortaise = 0,8 x piece receveuse",
        "source": S.EQ_ATT + " (tenon_mortaise, 3000 N) ; " + S.ABO_JC,
        "compromis": "La plus solide des jonctions collees ; pour cadres de portes, montants, consoles de barre.",
        "a_valider": False,
    },
    "tenon_clavete": {
        "nom": "Tenon traversant a clef (demontable)", "demontable": True, "capacite_service": None,
        "regle": "meme fraction de tenon que le tenon-mortaise ; clef demontable",
        "source": S.NEO_ATT + " (tenon_traversant_clavete) ; " + S.ABO_JC,
        "compromis": "Demontable sans metal, decoratif ; capacite non chiffree (essai).", "a_valider": True,
    },
    "queue_d_aronde": {
        "nom": "Queues d'aronde (tiroirs, coffres)", "demontable": False, "capacite_service": None,
        "regle": "pente 1:6 sur feuillu (hypothese d'atelier Aboutissants)",
        "source": S.ABO_JC + " (queue_d_aronde)",
        "compromis": "Reference pour les angles de tiroir et de coffre ; capacite non chiffree.", "a_valider": True,
    },
    "vis_barillet_m8": {
        "nom": "Boulon + ecrou barillet M8 (demontable)", "demontable": True, "capacite_service": 4000.0,
        "regle": "barillet d 10 a >= 2,5 d du bout",
        "source": S.EQ_ATT + " (vis_barillet_m8)",
        "compromis": "Demontage pour transport / demenagement ; tete visible sauf bouchon affleurant.",
        "a_valider": False,
    },
    "tasseau_biseaute": {
        "nom": "Tasseau biseaute a 45 deg (french cleat) mur / panneau", "demontable": True, "capacite_service": None,
        "regle": "deux tasseaux d'epaisseur egale, biseau 45 deg ; cale basse de meme epaisseur ; "
                 "capacite limitee par la fixation au mur (support inconnu)",
        "source": S.A_VALIDER + " (absent des autres gammes) ; support mural : " + S.ABO_PARAM +
                  " (cadre_modulaire.capacite_support_mur = TODO)",
        "compromis": "Modules decrochables et repositionnables ; demande un releve du mur.", "a_valider": True,
    },
}


def diametre_tourillon(epaisseur):
    """Plus grand diametre standard <= 0,5 x epaisseur (Equinox + Neogothique)."""
    lim = RATIO_DIAMETRE_TOURILLON * float(epaisseur)
    ok = [d for d in DIAMETRES_TOURILLON if d <= lim + 1e-9]
    return float(ok[-1] if ok else DIAMETRES_TOURILLON[0])


def cotes_tourillon(epaisseur):
    d = diametre_tourillon(epaisseur)
    return {"diametre": d, "longueur": RATIO_LONGUEUR_TOURILLON * d,
            "alesage_chant": RATIO_ALESAGE_TOURILLON * d,
            "alesage_face_max": max(0.0, float(epaisseur) - 5.0),
            "regle": "d <= 0,5 e (Neogothique) ; L = 5 d (Equinox) ; chant 2,5 d (Neogothique)"}


def cotes_tenon(section_tenonnee, section_receveuse):
    """Epaisseur de tenon (tiers) et profondeur de mortaise (0,8) - Equinox."""
    ep = math.floor(float(section_tenonnee) * FRACTION_TENON * 2.0 + 1e-9) / 2.0   # arrondi au 0,5 mm
    prof = float(section_receveuse) * FRACTION_MORTAISE
    return {"epaisseur_tenon": ep, "profondeur_mortaise": prof, "longueur_tenon": prof - 2.0,
            "regle": "tiers / 0,8 (Equinox attaches.tenon_mortaise), longueur = mortaise - 2 mm de fond de colle"}


def distance_barillet(diametre_barillet=10.0):
    """Distance mini barillet / bout de piece : 2,5 x d du barillet (Equinox)."""
    return 2.5 * float(diametre_barillet)
