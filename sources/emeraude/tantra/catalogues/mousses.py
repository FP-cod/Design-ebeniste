# -*- coding: utf-8 -*-
"""Catalogue des mousses et garnitures.

Densités et portances : ordres de grandeur fabricants (mousses HR
« haute résilience » de garnissage). Prix indicatifs nov. 2026, bloc
découpé, HT, petites séries — hypothèses à remplacer par devis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mousse:
    nom: str
    nom_affiche: str
    masse_volumique_kg_m3: float
    portance_kpa: float
    """Indentation (ILD/CLD) indicative à 40 %."""
    prix_eur_m3: float
    usage: str


HR35 = Mousse("mousse_hr35", "Mousse HR 35 kg/m³", 35.0, 3.0, 380.0,
              "Dossiers, appuis peu chargés.")
HR45 = Mousse("mousse_hr45", "Mousse HR 45 kg/m³ ferme", 45.0, 4.5, 480.0,
              "Assises et surfaces de soutien tantriques (ferme : on doit sentir la forme du "
              "profil, pas s'y enfoncer).")
HR55_GENOUX = Mousse("mousse_hr55", "Mousse HR 55 kg/m³ très ferme", 55.0, 6.0, 560.0,
                     "Repose-genoux et cales : charge concentrée.")
MEMOIRE = Mousse("mousse_memoire", "Mousse viscoélastique (couche de confort 20 mm)", 55.0, 1.5, 700.0,
                 "Couche supérieure facultative ; chaleur et lenteur de reprise : déconseillée "
                 "pour les surfaces où l'on bouge.")
OUATE = Mousse("ouate_polyester", "Ouate polyester 200 g/m²", 20.0, 0.5, 250.0,
               "Enveloppe de ouatinage sous revêtement.")

MOUSSES: dict[str, Mousse] = {m.nom: m for m in (HR35, HR45, HR55_GENOUX, MEMOIRE, OUATE)}


def mousse_par_nom(nom: str) -> Mousse:
    try:
        return MOUSSES[nom]
    except KeyError as exc:
        raise KeyError(f"Mousse inconnue « {nom} ». Catalogue : {', '.join(sorted(MOUSSES))}.") from exc
