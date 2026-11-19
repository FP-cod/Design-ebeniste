# -*- coding: utf-8 -*-
"""Catalogue des mousses et coussins du pouf vibrant.

Le coussin amovible de façade est un coussin de salon standard (tissu
de la gamme). Sous le coussin, la selle et son revêtement sont
lavables et non poreux (cuir ou silicone médical). Le carter de la
gamme entrée est en mousse dense, autour des pièces tournantes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mousse:
    """Mousse de garnissage ou de carter."""

    nom: str
    nom_affiche: str
    usage: str
    masse_volumique_kg_m3: float
    epaisseur_typique_mm: float
    poreuse: bool
    lavable_surface: bool
    commentaire: str


MOUSSE_COUSSIN_SALON = Mousse(
    nom="mousse_coussin_salon",
    nom_affiche="Mousse de coussin de salon (HR)",
    usage="coussin_amovible_facade",
    masse_volumique_kg_m3=35.0,
    epaisseur_typique_mm=90.0,
    poreuse=True,
    lavable_surface=False,
    commentaire=(
        "Coussin amovible d'apparence salon, recouvert du tissu de façade "
        "(velours, lin, etc.). Il masque complètement la selle à l'état pouf. "
        "Il n'est pas le contact d'usage du module."
    ),
)

MOUSSE_DENSES_CARTER = Mousse(
    nom="mousse_dense_carter",
    nom_affiche="Mousse dense de carter (gamme entrée)",
    usage="carter_balourd",
    masse_volumique_kg_m3=80.0,
    epaisseur_typique_mm=20.0,
    poreuse=True,
    lavable_surface=False,
    commentaire=(
        "Enveloppe acoustique et de sécurité autour du carter fermé du "
        "moteur à balourd. Elle n'autorise aucun accès aux pièces tournantes. "
        "Elle n'est pas un isolateur primaire (rôle des silentblocs)."
    ),
)

REVETEMENT_SELLE_SILICONE = Mousse(
    nom="revetement_selle_silicone",
    nom_affiche="Revêtement de selle silicone non poreux",
    usage="selle_lavable",
    masse_volumique_kg_m3=1100.0,
    epaisseur_typique_mm=3.0,
    poreuse=False,
    lavable_surface=True,
    commentaire=(
        "Peau de selle lavable, non poreuse, sous le coussin amovible. "
        "Silicone platine ou équivalent médical. Compatible nettoyage "
        "savon doux / jouet cleaner ; lubrifiant à l'eau recommandé."
    ),
)

REVETEMENT_SELLE_CUIR = Mousse(
    nom="revetement_selle_cuir",
    nom_affiche="Revêtement de selle cuir (intérieur caché)",
    usage="selle_lavable",
    masse_volumique_kg_m3=900.0,
    epaisseur_typique_mm=2.0,
    poreuse=False,
    lavable_surface=True,
    commentaire=(
        "Alternative cuir (cognac ou noir du catalogue), uniquement sur la "
        "selle, invisible à l'état pouf. Moins idéal hygiéniquement que le "
        "silicone (entretien, coutures). Non poreux s'il est fini correctement."
    ),
)


MOUSSES: dict[str, Mousse] = {
    m.nom: m
    for m in (
        MOUSSE_COUSSIN_SALON,
        MOUSSE_DENSES_CARTER,
        REVETEMENT_SELLE_SILICONE,
        REVETEMENT_SELLE_CUIR,
    )
}


def mousse_par_nom(nom: str) -> Mousse:
    try:
        return MOUSSES[nom]
    except KeyError as exc:
        raise KeyError(
            f"Mousse inconnue « {nom} ». Catalogue : {', '.join(sorted(MOUSSES))}."
        ) from exc
