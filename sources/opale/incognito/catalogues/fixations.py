# -*- coding: utf-8 -*-
"""Catalogue des fixations et ancrages de la gamme Incognito.

Aucune ferrure n'est visible à l'état fermé : charnières invisibles
(type Soss ou à compas encastré), vérins à l'intérieur du caisson,
ancres métalliques noyées dans un bloc masqué, assemblages bois
(tourillons et mortaises-tenons exclusivement en façade structurelle).

Les règles de recalcul (section minimale, dimensions du bloc d'ancrage)
sont appliquées par ``incognito.regles``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fixation:
    """Élément de quincaillerie ou d'assemblage bois du catalogue."""

    nom: str
    nom_affiche: str
    famille: str
    visible_etat_ferme: bool
    commentaire: str
    cotes_mm: dict[str, float]


# --- Assemblages bois (toujours privilégiés en façade) ----------------------

TOURILLON_10 = Fixation(
    nom="tourillon_10",
    nom_affiche="Tourillon Ø10",
    famille="tourillon",
    visible_etat_ferme=False,
    commentaire="Tourillon hêtre ou chêne Ø10 mm, typique des caissons. Encollé, non apparent.",
    cotes_mm={"diametre": 10.0, "longueur": 40.0, "profondeur_alésage": 22.0},
)

TOURILLON_12 = Fixation(
    nom="tourillon_12",
    nom_affiche="Tourillon Ø12",
    famille="tourillon",
    visible_etat_ferme=False,
    commentaire="Tourillon Ø12 mm pour assemblages plus sollicités (pieds, joues, traverse).",
    cotes_mm={"diametre": 12.0, "longueur": 50.0, "profondeur_alésage": 28.0},
)

MORTAISE_TENON = Fixation(
    nom="mortaise_tenon",
    nom_affiche="Mortaise et tenon",
    famille="mortaise_tenon",
    visible_etat_ferme=False,
    commentaire=(
        "Assemblage d'ébénisterie principal (dossier dans le caisson, "
        "traverse du banc dans les joues, renforts). Aucune vis apparente."
    ),
    cotes_mm={"epaisseur_tenon": 10.0, "longueur_tenon": 30.0, "jeu": 0.1},
)


# --- Ancrages métalliques noyés ---------------------------------------------

INSERT_ANCRE_NOYE = Fixation(
    nom="insert_ancre_noye",
    nom_affiche="Insert d'ancre noyé",
    famille="ancre",
    visible_etat_ferme=False,
    commentaire=(
        "Insert métallique (inox de préférence) noyé dans un bloc d'ancrage "
        "local, lui-même mortaisé et tourillonné dans le rail du banc. "
        "Un cache bois affleurant, éventuellement sous le cuir, masque l'orifice "
        "jusqu'au déploiement. Pas de vis, d'anneau ni de manille visibles "
        "à l'état fermé."
    ),
    cotes_mm={
        "diametre_insert": 12.0,
        "longueur_encastrement": 80.0,
        "epaisseur_cache": 10.0,
    },
)

CACHE_AFFLEURANT = Fixation(
    nom="cache_affleurant",
    nom_affiche="Cache bois affleurant",
    famille="cache",
    visible_etat_ferme=False,
    commentaire=(
        "Cache de même essence, affleuré, éventuellement aimanté ou à faux "
        "tourillon, qui obture l'orifice d'ancre tant que le banc est rangé "
        "et, si on le souhaite, aussi après déploiement jusqu'à l'usage."
    ),
    cotes_mm={"epaisseur": 10.0, "jeu": 0.2},
)


# --- Mécanisme d'ouverture de l'assise-coffre -------------------------------

CHARNIERE_SOSS = Fixation(
    nom="charniere_soss",
    nom_affiche="Charnière invisible type Soss",
    famille="charniere",
    visible_etat_ferme=False,
    commentaire=(
        "Charnière entièrement mortaisée dans le chant du couvercle et le "
        "traversin arrière du caisson. Invisible à l'état fermé. "
        "Prévoir plusieurs points (typiquement 3) pour un couvercle capitonné "
        "lourd, et une épaisseur de bois d'au moins 22 mm. Les mortaises "
        "affaiblissent le traversin : ne pas les combiner avec un ancrage "
        "dans la même section."
    ),
    cotes_mm={
        "longueur_boitier": 118.0,
        "largeur_boitier": 18.0,
        "profondeur_mortaise": 19.0,
        "epaisseur_min_bois": 22.0,
        "nombre_recommande": 3.0,
    },
)

VERIN_COMPAS = Fixation(
    nom="verin_compas",
    nom_affiche="Vérin ou compas de maintien",
    famille="verin",
    visible_etat_ferme=False,
    commentaire=(
        "Vérins à gaz ou compas encastrés à l'intérieur du caisson, "
        "invisibles à l'état fermé, qui maintiennent le couvercle ouvert. "
        "Dimensionnement à reprendre selon la masse réelle du couvercle "
        "capitonné (essai de prototype recommandé)."
    ),
    cotes_mm={"course": 150.0, "longueur_pliee": 200.0},
)


FIXATIONS: dict[str, Fixation] = {
    f.nom: f
    for f in (
        TOURILLON_10,
        TOURILLON_12,
        MORTAISE_TENON,
        INSERT_ANCRE_NOYE,
        CACHE_AFFLEURANT,
        CHARNIERE_SOSS,
        VERIN_COMPAS,
    )
}


def fixation_par_nom(nom: str) -> Fixation:
    """Retourne une fixation par identifiant ASCII."""
    try:
        return FIXATIONS[nom]
    except KeyError as exc:
        connues = ", ".join(sorted(FIXATIONS))
        raise KeyError(f"Fixation inconnue « {nom} ». Catalogue : {connues}.") from exc
