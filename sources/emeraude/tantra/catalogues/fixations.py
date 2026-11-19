# -*- coding: utf-8 -*-
"""Catalogue des fixations : assemblages d'ébénisterie, ancrages, ferrures cachées.

Résistances : **valeurs caractéristiques d'ordre de grandeur** (rupture
moyenne d'essais publiés minorée), utilisées par ``tantra.regles`` avec
CS ≥ 3. À confirmer par essais sur les assemblages réels de l'atelier.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fixation:
    nom: str
    nom_affiche: str
    famille: str
    resistance_caracteristique_n: float
    """Résistance caractéristique par unité (cisaillement), 0 si calculée par règle."""
    prix_unitaire_eur: float
    temps_pose_h: float
    visible: bool
    commentaire: str
    cotes_mm: dict = field(default_factory=dict)


TOURILLON_10 = Fixation(
    "tourillon_10", "Tourillon hêtre Ø10 × 40", "tourillon", 2500.0, 0.06, 0.03, False,
    "Encollé (PVAc D3). Cisaillement caractéristique ~2,5 kN en feuillu (ordre de grandeur).",
    {"diametre": 10.0, "longueur": 40.0, "profondeur_alesage": 22.0},
)
TOURILLON_12 = Fixation(
    "tourillon_12", "Tourillon hêtre Ø12 × 50", "tourillon", 3500.0, 0.08, 0.04, False,
    "Pieds, ceintures et blocs d'ancrage.",
    {"diametre": 12.0, "longueur": 50.0, "profondeur_alesage": 28.0},
)
MORTAISE_TENON = Fixation(
    "mortaise_tenon", "Tenon-mortaise encollé", "mortaise_tenon", 0.0, 0.0, 0.3, False,
    "Assemblage principal des traverses. Résistance calculée par regles.cs_tenon "
    "(cisaillement du tenon). Tenon ≈ 1/3 de l'épaisseur de la pièce, épaulements 4 côtés "
    "si possible.",
    {"rapport_epaisseur": 1 / 3, "longueur_mini": 30.0, "jeu": 0.1},
)
ENFOURCHEMENT = Fixation(
    "enfourchement", "Enfourchement (tenon traversant d'angle)", "mortaise_tenon", 0.0, 0.0, 0.4, False,
    "Angles de cadres (plateau-cadre, portique) : deux plans de collage, très résistant en "
    "flexion dans le plan du cadre. Chevillé (tourillon traversant) pour les cadres de contention.",
    {"longueur_mini": 40.0},
)
INSERT_ANCRE_M12 = Fixation(
    "insert_ancre_m12", "Insert d'ancre inox A4 M12 (Ø ext. 16) + anneau à visser", "ancre", 0.0, 19.0, 0.35, False,
    "Insert fileté inox A4 dans bloc de chêne ; arrachement calculé par regles.arrachement_insert_n "
    "(formule EC5 des vis, appliquée par analogie). Anneau à épaulement vissé à l'usage seulement : "
    "rien ne dépasse au repos.",
    {"diametre_insert": 16.0, "longueur_encastrement": 60.0, "filetage": 12.0},
)
ANNEAU_RABATTABLE = Fixation(
    "anneau_rabattable", "Anneau rabattable encastré inox (affleurant)", "ancre", 0.0, 24.0, 0.5, True,
    "Pour le volet Tantra (fonction assumée) : anneau qui se couche dans une cuvette fraisée. "
    "Visible mais affleurant ; se visse dans l'insert M12.",
    {"diametre_cuvette": 50.0, "profondeur_cuvette": 12.0},
)
CACHE_AIMANTE = Fixation(
    "cache_aimante", "Cache affleurant aimanté (même essence / même tissu)", "cache", 0.0, 6.0, 0.3, False,
    "Pastille Ø40 avec aimant néodyme noyé : obture l'insert d'ancre au repos (volet 2).",
    {"diametre": 40.0, "epaisseur": 10.0},
)
CHARNIERE_SOSS = Fixation(
    "charniere_soss", "Charnière invisible type Soss 218", "charniere", 0.0, 22.0, 0.6, False,
    "Mortaisée dans les chants ; invisible fermée. Ne pas la combiner avec un ancrage dans la "
    "même section de bois.",
    {"longueur_boitier": 118.0, "profondeur_mortaise": 19.0, "epaisseur_min_bois": 22.0},
)
AIMANT_FERMETURE = Fixation(
    "aimant_fermeture", "Loqueteau magnétique encastré (néodyme, ~40 N)", "fermeture", 0.0, 4.0, 0.2, False,
    "Maintient les manchettes et bavettes fermées sans aucune pièce visible.",
    {"force_n": 40.0},
)
VERIN_GAZ = Fixation(
    "verin_gaz", "Vérin à gaz 100–250 N", "verin", 0.0, 22.0, 0.4, False,
    "Assistance des pièces lourdes en mouvement ; force à dimensionner sur prototype.",
    {"course": 150.0},
)
SANGLE_ELASTIQUE = Fixation(
    "sangle_elastique", "Sanglage élastique d'assise (Pirelli 60 mm)", "garniture", 0.0, 3.5, 0.15, False,
    "Suspension d'assise classique des sièges tapissés (au mètre).",
    {"largeur": 60.0},
)

FIXATIONS: dict[str, Fixation] = {
    f.nom: f for f in (TOURILLON_10, TOURILLON_12, MORTAISE_TENON, ENFOURCHEMENT, INSERT_ANCRE_M12,
                       ANNEAU_RABATTABLE, CACHE_AIMANTE, CHARNIERE_SOSS, AIMANT_FERMETURE, VERIN_GAZ,
                       SANGLE_ELASTIQUE)
}


def fixation_par_nom(nom: str) -> Fixation:
    try:
        return FIXATIONS[nom]
    except KeyError as exc:
        raise KeyError(f"Fixation inconnue « {nom} ». Catalogue : {', '.join(sorted(FIXATIONS))}.") from exc
