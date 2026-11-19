# -*- coding: utf-8 -*-
"""Catalogue des mécanismes de transformation (volet 3) et de révélation (volet 2).

* **Axes traversants** : axe inox A4 traversant deux joues (double cisaillement),
  bagues bronze ou POM, arrêt par circlips + rondelle.
* **Verrous** : doigts d'indexage à ressort (type GN 617 / Kipp K0338),
  verrous à came excentrique, goupilles captives à bille (type GN 113) sur câble.

Résistances caractéristiques de cisaillement d'un doigt / d'une goupille :
R = 0,6 × f_u × π d² / 4 par plan, avec f_u = 700 MPa (inox A4-70) ; les
doigts du commerce à corps acier ont souvent une capacité inférieure
annoncée par le fabricant : retenir la plus faible des deux.
Prix : indicatifs nov. 2026, HT, à l'unité, petites séries.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

FU_INOX_A4_70_MPA = 700.0
"""Résistance ultime à la traction de l'inox A4-70 (EN ISO 3506-1)."""


def resistance_cisaillement_broche_n(diametre_mm: float, plans: int = 1,
                                     fu_mpa: float = FU_INOX_A4_70_MPA) -> float:
    """Résistance caractéristique en cisaillement d'une broche pleine : n × 0,6 f_u A."""
    if diametre_mm <= 0 or plans < 1:
        raise ValueError("Diamètre > 0 et plans ≥ 1 requis.")
    return plans * 0.6 * fu_mpa * pi * diametre_mm**2 / 4.0


@dataclass(frozen=True)
class Verrou:
    nom: str
    nom_affiche: str
    type: str
    """'indexage', 'came' ou 'goupille'."""
    diametre_mm: float
    plans_cisaillement: int
    force_ressort_n: float
    """Force de rappel du ressort (0 si pas de ressort)."""
    verrou_de_forme: bool
    """True : tient par obstacle (pas par frottement)."""
    imperdable: bool
    prix_eur: float
    temps_pose_h: float
    commentaire: str

    @property
    def resistance_caracteristique_n(self) -> float:
        return resistance_cisaillement_broche_n(self.diametre_mm, self.plans_cisaillement)


DOIGT_INDEXAGE_12 = Verrou(
    "doigt_indexage_12", "Doigt d'indexage à ressort Ø12, bouton à cran de repos", "indexage",
    12.0, 1, 25.0, True, True, 32.0, 0.8,
    "Verrou primaire : s'enclenche seul (ressort) quand la pièce atteint la position ; "
    "cran de repos pour la manœuvre. Plongeur inox ; cisaillement simple.",
)
DOIGT_INDEXAGE_16 = Verrou(
    "doigt_indexage_16", "Doigt d'indexage à ressort Ø16", "indexage",
    16.0, 1, 40.0, True, True, 45.0, 0.8,
    "Variante renforcée pour les montants télescopiques.",
)
GOUPILLE_CAPTIVE_12 = Verrou(
    "goupille_captive_12", "Goupille à bille Ø12 inox sur câble", "goupille",
    12.0, 2, 0.0, True, True, 14.0, 0.4,
    "Verrou secondaire : traverse deux joues (double cisaillement) ; câble inox fixé au "
    "meuble (imperdable). Ne s'engage qu'à la main : sert de témoin visuel de verrouillage.",
)
GOUPILLE_CAPTIVE_10 = Verrou(
    "goupille_captive_10", "Goupille à bille Ø10 inox sur câble", "goupille",
    10.0, 2, 0.0, True, True, 12.0, 0.4, "Idem Ø10.",
)
VERROU_CAME = Verrou(
    "verrou_came", "Verrou à came excentrique à levier (auto-bloquant)", "came",
    10.0, 1, 0.0, False, True, 18.0, 0.7,
    "Serrage par came ; tient par frottement + angle d'auto-blocage. N'est **pas** un verrou "
    "de forme : utilisable comme anti-jeu ou comme second verrou seulement s'il est complété "
    "par une butée de forme.",
)

VERROUS: dict[str, Verrou] = {
    v.nom: v for v in (DOIGT_INDEXAGE_12, DOIGT_INDEXAGE_16, GOUPILLE_CAPTIVE_12,
                       GOUPILLE_CAPTIVE_10, VERROU_CAME)
}


@dataclass(frozen=True)
class AxeTraversant:
    nom: str
    nom_affiche: str
    diametre_mm: float
    prix_eur: float
    temps_pose_h: float
    commentaire: str

    @property
    def resistance_caracteristique_n(self) -> float:
        """Cisaillement de l'axe en double cisaillement."""
        return resistance_cisaillement_broche_n(self.diametre_mm, 2)


AXE_16 = AxeTraversant("axe_16", "Axe inox A4 Ø16, bagues POM, circlips", 16.0, 22.0, 0.8,
                       "Charnière à axe traversant : joues en chêne de part et d'autre.")
AXE_20 = AxeTraversant("axe_20", "Axe inox A4 Ø20, bagues bronze, circlips", 20.0, 34.0, 0.9,
                       "Pivots principaux chargés (plateau-cadre).")

AXES: dict[str, AxeTraversant] = {a.nom: a for a in (AXE_16, AXE_20)}


def verrou_par_nom(nom: str) -> Verrou:
    try:
        return VERROUS[nom]
    except KeyError as exc:
        raise KeyError(f"Verrou inconnu « {nom} ». Catalogue : {', '.join(sorted(VERROUS))}.") from exc


def axe_par_nom(nom: str) -> AxeTraversant:
    try:
        return AXES[nom]
    except KeyError as exc:
        raise KeyError(f"Axe inconnu « {nom} ». Catalogue : {', '.join(sorted(AXES))}.") from exc
