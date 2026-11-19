# -*- coding: utf-8 -*-
"""Grammaire — canapé deux places à ancrages escamotés (volet 2, camouflable).

État SALON : un canapé de facture classique (dossier droit, accoudoirs
pleins, galettes, pieds fuseaux), sans aucun élément technique visible.
État RÉVÉLÉ : les deux manchettes d'accoudoir sont soulevées (charnières
Soss invisibles à l'avant), la bavette de ceinture est rabattue vers
l'avant ; quatre inserts M12 sont accessibles, deux autres sous les
galettes. Les anneaux à épaulement sont rangés hors du meuble.

Ne duplique pas la banquette Incognito (coffre à vérins) : ici aucun
volume n'est ouvert, seules des pièces tapissées pivotent.
"""

from __future__ import annotations

from dataclasses import dataclass

from tantra.chiffrage import chiffrer
from tantra.geometrie import CasStabilite, GeometrieMeuble
from tantra.grammaires._salon import (
    CODE_ETAT, ETAT_REVELE, ETAT_SALON, ETATS, ParametresSalon, construire_salon, etat_depuis_code,
    verifier_discretion, verifs_communes,
)
from tantra.grammaires._siege import (COEFFICIENT_STABILITE_ACCIDENTEL_MIN, essais_communs,
                                      verif_traction_exterieure, verifs_stabilite)
from tantra.parametres import CAMO_CANAPE as TYPO, PARAMETRES_DEFAUT, PREFIXE_FUSION, ParametresGlobaux

PREFIXE = "canape"


@dataclass(frozen=True)
class ParametresCanape:
    largeur: float = 1750.0
    profondeur: float = 900.0
    hauteur_assise: float = 440.0
    hauteur_dossier: float = 860.0
    hauteur_accoudoir: float = 620.0
    largeur_accoudoir: float = 170.0
    nombre_galettes: int = 2
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def salon(self) -> ParametresSalon:
        return ParametresSalon(self.largeur, self.profondeur, self.hauteur_assise, self.hauteur_dossier,
                               self.hauteur_accoudoir, largeur_accoudoir=self.largeur_accoudoir,
                               nombre_galettes=self.nombre_galettes)


def calculer(p: ParametresCanape | None = None, etat: str | int = ETAT_SALON) -> GeometrieMeuble:
    p = p or ParametresCanape()
    etat = etat_depuis_code(etat)
    g = p.globaux
    for nom in ("largeur", "profondeur", "hauteur_assise", "hauteur_dossier", "hauteur_accoudoir"):
        TYPO.verifier(nom, getattr(p, nom))
    s = p.salon()
    c = construire_salon(s, g, etat, PREFIXE)
    v = verifier_discretion(c, etat)
    v += verifs_communes(s, g, c, etat, PREFIXE)
    ch = g.charges
    w = ch.poids_personne_n
    xm, L = p.largeur / 2, p.largeur
    cas = [
        CasStabilite("deux_assis_pousse_dossier", ((w, L * 0.3, 300.0), (w, L * 0.7, 300.0)),
                     (ch.effort_horizontal_exterieur_n, "+y", p.hauteur_dossier), 1.5,
                     "Deux personnes assises, poussée de 300 N vers l'arrière en haut du dossier."),
        CasStabilite("assis_sur_accoudoir", ((w * ch.facteur_dynamique, 40.0, p.profondeur / 2),),
                     None, COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
                     "Une personne assise brusquement sur l'accoudoir gauche (porte-à-faux latéral)."),
        CasStabilite("bord_avant", ((w * ch.facteur_dynamique, xm, 20.0),),
                     (ch.effort_horizontal_exterieur_n, "-y", p.hauteur_assise), 1.5,
                     "Personne sur le bord avant (état RÉVÉLÉ, ancrages avant), poussée vers l'avant."),
    ]
    v_stab, infos = verifs_stabilite(list(c.pieces), cas)
    v += v_stab
    v.append(verif_traction_exterieure(c.infos["z_traverse_accoudoir"] + 60.0, infos["masse_kg"],
                                       p.profondeur / 2, ch.charge_service_ancrage_n))
    v += essais_communs(PREFIXE)
    n = len(c.ancrages)
    return GeometrieMeuble(TYPO.nom, etat, tuple(c.pieces), tuple(c.assemblages), tuple(c.ancrages), tuple(v),
                           {**c.infos, **infos, "code_etat": CODE_ETAT[etat]},
                           quincaillerie=(("insert_ancre_m12", n), ("anneau_rabattable", n),
                                          ("cache_aimante", 2)))


def calculer_etats(p: ParametresCanape | None = None) -> dict[str, GeometrieMeuble]:
    return {e: calculer(p, e) for e in ETATS}


def vers_parametres_fusion_canape(p: ParametresCanape | None = None) -> dict:
    p = p or ParametresCanape()
    P = f"{PREFIXE_FUSION}canape_"
    return {
        f"{P}etat": (0, "", "0 = SALON, 1 = RÉVÉLÉ."),
        f"{P}largeur_accoudoir": (p.largeur_accoudoir, "mm", "Largeur d'un accoudoir."),
        f"{P}angle_manchette": (p.salon().angle_manchette, "deg", "Ouverture des manchettes à l'état RÉVÉLÉ."),
    }


def chiffrage(p: ParametresCanape | None = None):
    return chiffrer(calculer(p, ETAT_SALON))
