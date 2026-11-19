# -*- coding: utf-8 -*-
"""Briques communes des cadres transformables (volet 3, Python pur).

Principe de gamme : **le meuble est la structure du cadre**. Aucune pièce
n'est ajoutée ni retirée entre les états MEUBLE (0) et CADRE (1) ; tout est
captif, et chaque liaison qui maintient l'état CADRE porte une **double
sécurité** (deux verrous de forme indépendants, chacun seul à CS ≥ 3, l'un
à enclenchement automatique, tous imperdables).

La résistance d'un verrou est le minimum entre le cisaillement de l'acier
et la portance du bois qui l'entoure (EN 1995-1-1, éq. 8.32, × 0,7 en
travers du fil), car c'est presque toujours le bois qui cède d'abord.
"""

from __future__ import annotations

from math import inf

from tantra.catalogues.mecanismes import Verrou
from tantra.geometrie import Verification
from tantra.parametres import COEFFICIENT_SECURITE_MIN, Essence
from tantra.regles import portance_bois_mpa, verif, verifier_double_verrouillage

ETAT_MEUBLE = "MEUBLE"
ETAT_CADRE = "CADRE"
ETATS = (ETAT_MEUBLE, ETAT_CADRE)
CODE_ETAT = {ETAT_MEUBLE: 0, ETAT_CADRE: 1}


def etat_depuis_code(code: int | str) -> str:
    if isinstance(code, str) and code in ETATS:
        return code
    return ETAT_CADRE if int(code) else ETAT_MEUBLE


def resistance_verrou_dans_bois_n(verrou: Verrou, essence: Essence, epaisseur_paroi_mm: float) -> float:
    """min(cisaillement acier, portance du bois sur chaque plan de cisaillement)."""
    r_bois = (0.7 * portance_bois_mpa(verrou.diametre_mm, essence) * verrou.diametre_mm
              * epaisseur_paroi_mm * max(1, verrou.plans_cisaillement))
    return min(verrou.resistance_caracteristique_n, r_bois)


def verifier_liaison_verrouillee(nom: str, effort_n: float, verrous: list[Verrou], essence: Essence,
                                 epaisseur_paroi_mm: float,
                                 cs: float = COEFFICIENT_SECURITE_MIN) -> list[Verification]:
    """Double verrouillage (règles de gamme) + chaque verrou seul en tenant compte du bois."""
    out = verifier_double_verrouillage(nom, effort_n, verrous, cs)
    for i, v in enumerate([v for v in verrous if v.verrou_de_forme]):
        r = resistance_verrou_dans_bois_n(v, essence, epaisseur_paroi_mm)
        c = r / effort_n if effort_n > 0 else inf
        out.append(verif(f"{nom}_verrou_{i + 1}_bois", c >= cs,
                         f"{nom} — {v.nom_affiche} dans {essence.nom} (paroi {epaisseur_paroi_mm:g} mm) : "
                         f"R ≈ {r / 1000:.1f} kN (min acier / portance bois), CS {c:.1f}."))
    return out


def appui_compas(distance_pivots_mm: float, longueur_contrefiche_mm: float, angle_deg: float) -> float | None:
    """Compas plan : où une contrefiche de longueur ``lc``, articulée à ``AB`` du pivot du
    plateau, rejoint-elle un plateau incliné de ``angle_deg`` ?

    Loi des cosinus : lc² = s² + AB² − 2 s AB cos θ. Retourne la plus grande racine
    ``s`` (distance pivot → appui le long du plateau) ou ``None`` si la contrefiche est
    trop courte (lc < AB sin θ). Sert à la fiche « table basse → cadre incliné ».
    """
    from math import cos, radians, sqrt
    ab, lc, t = distance_pivots_mm, longueur_contrefiche_mm, radians(angle_deg)
    b = -2.0 * ab * cos(t)
    c = ab * ab - lc * lc
    disc = b * b - 4.0 * c
    if disc < 0:
        return None
    s = (-b + sqrt(disc)) / 2.0
    return s if s > 0 else None
