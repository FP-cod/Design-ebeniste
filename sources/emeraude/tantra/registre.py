# -*- coding: utf-8 -*-
"""Registre des typologies : point d'entrée unique pour les tests, les scripts
Fusion et la documentation.

``geometrie(nom, etat)`` renvoie la ``GeometrieMeuble`` d'une typologie
dans un état donné (code entier 0/1 ou nom d'état) ; ``etats(nom)`` liste
les états ; ``parametres_fusion(nom)`` donne les paramètres utilisateur
propres à la typologie, y compris ``tan_<clé>_etat`` pour les meubles à
deux états.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Callable

from tantra.chiffrage import Chiffrage
from tantra.geometrie import GeometrieMeuble
from tantra.grammaires import (
    cadre_desserte_genoux,
    camo_canape,
    camo_fauteuil,
    tantra_banquette_deux_niveaux,
    tantra_chaise_double_courbe,
    tantra_fauteuil_lombaire,
    tantra_siege_repose_genoux,
)
from tantra.parametres import PREFIXE_FUSION, VOLET_CADRE, VOLET_CAMOUFLABLE, VOLET_TANTRA


@dataclass(frozen=True)
class EntreeRegistre:
    nom: str
    volet: str
    module: ModuleType
    cle_fusion: str
    """Clé courte des paramètres Fusion : ``tan_<cle>_...``."""
    etats: tuple[str, ...]
    fonction_fusion: Callable[[], dict]
    deux_etats: bool

    def geometrie(self, etat: int | str | None = None) -> GeometrieMeuble:
        if not self.deux_etats:
            return self.module.calculer()
        return self.module.calculer(None, self.etats[0] if etat is None else etat)

    def chiffrage(self) -> Chiffrage:
        return self.module.chiffrage()


def _e(nom, volet, module, cle, fusion, deux_etats=False) -> EntreeRegistre:
    etats = tuple(module.calculer_etats().keys())
    return EntreeRegistre(nom, volet, module, cle, etats, fusion, deux_etats)


REGISTRE: dict[str, EntreeRegistre] = {e.nom: e for e in (
    _e("tantra_chaise_double_courbe", VOLET_TANTRA, tantra_chaise_double_courbe, "chaise",
       tantra_chaise_double_courbe.vers_parametres_fusion_chaise),
    _e("tantra_fauteuil_lombaire", VOLET_TANTRA, tantra_fauteuil_lombaire, "lombaire",
       tantra_fauteuil_lombaire.vers_parametres_fusion_fauteuil),
    _e("tantra_banquette_deux_niveaux", VOLET_TANTRA, tantra_banquette_deux_niveaux, "banquette2n",
       tantra_banquette_deux_niveaux.vers_parametres_fusion_banquette),
    _e("tantra_siege_repose_genoux", VOLET_TANTRA, tantra_siege_repose_genoux, "siege",
       tantra_siege_repose_genoux.vers_parametres_fusion_siege),
    _e("camo_canape", VOLET_CAMOUFLABLE, camo_canape, "canape", camo_canape.vers_parametres_fusion_canape, True),
    _e("camo_fauteuil", VOLET_CAMOUFLABLE, camo_fauteuil, "bergere",
       camo_fauteuil.vers_parametres_fusion_fauteuil, True),
    _e("cadre_desserte_genoux", VOLET_CADRE, cadre_desserte_genoux, "desserte",
       cadre_desserte_genoux.vers_parametres_fusion_desserte, True),
)}

TYPOLOGIES_EN_FICHE = {
    "cadre_table_inclinee": "Étudiée (docs/cadre_table_inclinee.md) ; grammaire non livrée : la stabilité "
                            "impose une fixation murale et la géométrie du compas un plateau de 2 m.",
}


def entree(nom: str) -> EntreeRegistre:
    try:
        return REGISTRE[nom]
    except KeyError as exc:
        raise KeyError(f"Typologie inconnue « {nom} ». Registre : {', '.join(REGISTRE)}.") from exc


def etats(nom: str) -> tuple[str, ...]:
    return entree(nom).etats


def geometrie(nom: str, etat: int | str | None = None) -> GeometrieMeuble:
    return entree(nom).geometrie(etat)


def nom_parametre_etat(nom: str) -> str | None:
    e = entree(nom)
    return f"{PREFIXE_FUSION}{e.cle_fusion}_etat" if e.deux_etats else None


def parametres_fusion(nom: str) -> dict:
    return entree(nom).fonction_fusion()


def tableau_chiffrages() -> list[tuple[str, str, float, tuple[float, float], float]]:
    """(typologie, volet, prix TTC, fourchette, prototype) pour toutes les typologies."""
    out = []
    for e in REGISTRE.values():
        c = e.chiffrage()
        out.append((e.nom, e.volet, c.prix_vente_ttc, c.fourchette_ttc, c.prix_prototype_ttc))
    return out
