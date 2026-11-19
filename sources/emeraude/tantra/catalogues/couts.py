# -*- coding: utf-8 -*-
"""Catalogue des coûts (ESTIMATIONS datées novembre 2026).

Toutes les valeurs sont des **hypothèses HT** pour un atelier
d'ébénisterie français travaillant en petite série (lots de 5 à 10
pièces, programme CNC amorti sur le lot). Elles servent à comparer les
typologies entre elles et à situer un prix de vente indicatif ; elles ne
remplacent pas des devis fournisseurs. Un prototype unitaire coûte
typiquement 2 à 3 fois plus en main-d'œuvre (``coefficient_prototype``).

Hypothèses principales :

* bois : prix au m³ de bois sec raboté de qualité ébénisterie, avec un
  coefficient de perte (rendement de débit) ;
* contreplaqué cintré : prix du placage collé + amortissement du moule ;
* main-d'œuvre : taux horaire chargé atelier (ébéniste / tapissier) ;
* prix de vente : (matière + MO + quincaillerie + finition) × coefficient
  commercial de vente directe (frais généraux + marge), puis TVA 20 %.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tantra.catalogues.mousses import MOUSSES
from tantra.parametres import ESSENCES, REVETEMENTS

DATE_ESTIMATION = "novembre 2026"


@dataclass(frozen=True)
class CatalogueCouts:
    date: str = DATE_ESTIMATION
    prix_bois_eur_m3: dict = field(default_factory=lambda: {
        "chene": 2400.0, "hetre": 1500.0, "frene": 1700.0, "noyer": 4300.0,
        "lamelle_hetre": 1900.0, "contreplaque_bouleau": 4200.0,
    })
    coefficient_perte_bois: dict = field(default_factory=lambda: {
        "massif": 1.8, "lamelle_colle": 1.25, "contreplaque": 1.35,
    })
    prix_acier_inox_eur_kg: float = 9.0
    prix_acier_eur_kg: float = 3.5
    taux_horaire_ebeniste_eur: float = 58.0
    taux_horaire_tapissier_eur: float = 52.0
    heures_tapisserie_par_m2: float = 1.4
    heures_tapisserie_forfait: float = 1.5
    heures_montage_forfait: float = 2.0
    heures_controle_essai: float = 1.5
    """Contrôle final + essai de charge de série (banc d'essai amorti)."""
    finition_eur_par_kg_bois: float = 1.2
    """Huile-cire dure, abrasifs, teinte éventuelle."""
    emballage_eur: float = 45.0
    amortissement_moule_eur: float = 120.0
    """Part par pièce d'un moule de cintrage amorti sur ~25 pièces."""
    coefficient_commercial: float = 1.45
    tva: float = 0.20
    coefficient_prototype: float = 2.5
    incertitude: float = 0.25
    """Fourchette ± appliquée au prix de vente indicatif."""
    # Temps unitaires (h) en petite série avec CNC : débit, usinage, ponçage, pré-finition.
    temps_role_h: dict = field(default_factory=lambda: {
        "flasque": 1.5, "coque": 2.0, "traverse": 0.4, "pied": 0.6, "ceinture": 0.5,
        "plateau": 1.2, "montant": 0.8, "bloc_ancrage": 0.4, "socle": 0.5, "panneau": 0.5,
        "cache": 0.2, "manchette": 0.7, "bavette": 0.7, "pied_compas": 0.8, "vantail": 1.2,
        "contrefiche": 0.7, "assise": 0.6, "dossier": 0.8, "accoudoir": 1.0, "patin": 1.2,
        "mousse": 0.4, "revetement": 0.0, "repose_genoux": 0.6, "acier": 0.5,
    })


CATALOGUE_COUTS = CatalogueCouts()

MASSE_VOLUMIQUE_ACIER = 7850.0
MASSE_VOLUMIQUE_REVETEMENT = 900.0
"""Masse volumique apparente d'une pièce « revêtement » modélisée en volume mince."""


def masses_volumiques() -> dict[str, float]:
    """Dictionnaire matériau → masse volumique (kg/m³) pour ``geometrie.masse_et_cdg``."""
    d: dict[str, float] = {e.nom: e.masse_volumique_kg_m3 for e in ESSENCES.values()}
    d.update({m.nom: m.masse_volumique_kg_m3 for m in MOUSSES.values()})
    d.update({r.nom: MASSE_VOLUMIQUE_REVETEMENT for r in REVETEMENTS.values()})
    d["acier_inox"] = MASSE_VOLUMIQUE_ACIER
    d["acier"] = MASSE_VOLUMIQUE_ACIER
    return d
