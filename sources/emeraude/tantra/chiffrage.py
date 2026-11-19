# -*- coding: utf-8 -*-
"""Chiffrage indicatif d'une géométrie (ESTIMATIONS nov. 2026, HT puis TTC).

Méthode (petite série, voir ``tantra.catalogues.couts``) :

1. **matière bois** : volume de chaque pièce × prix au m³ × coefficient de perte ;
2. **mousses** : volume × prix au m³ ; **revêtement** : surface × prix au m² × 1,25 (chutes) ;
3. **acier** : masse × prix au kg ;
4. **quincaillerie** : fixations des assemblages + liste ``quincaillerie`` de la géométrie
   (inserts, verrous, axes, vérins) ;
5. **main-d'œuvre** : temps par rôle de pièce + temps de pose par assemblage + forfaits
   (montage, contrôle et essai), tapisserie au m² ; moule de cintrage amorti ;
6. **prix de vente** : coût de revient × coefficient commercial, TVA 20 %, fourchette ± 25 %.

Les montants sont des ordres de grandeur pour comparer les typologies.
"""

from __future__ import annotations

from dataclasses import dataclass

from tantra.catalogues.couts import CATALOGUE_COUTS, CatalogueCouts, MASSE_VOLUMIQUE_ACIER
from tantra.catalogues.fixations import FIXATIONS
from tantra.catalogues.mecanismes import AXES, VERROUS
from tantra.catalogues.mousses import MOUSSES
from tantra.geometrie import GeometrieMeuble
from tantra.parametres import ESSENCES, REVETEMENTS


def prix_unitaire_quincaillerie(nom: str) -> tuple[float, float]:
    """(prix €, temps de pose h) d'un article de quincaillerie du catalogue."""
    if nom in FIXATIONS:
        f = FIXATIONS[nom]
        return f.prix_unitaire_eur, f.temps_pose_h
    if nom in VERROUS:
        v = VERROUS[nom]
        return v.prix_eur, v.temps_pose_h
    if nom in AXES:
        a = AXES[nom]
        return a.prix_eur, a.temps_pose_h
    raise KeyError(f"Article de quincaillerie inconnu « {nom} ».")


@dataclass(frozen=True)
class Chiffrage:
    typologie: str
    date: str
    bois_eur: float
    mousse_eur: float
    revetement_eur: float
    acier_eur: float
    quincaillerie_eur: float
    finition_emballage_eur: float
    moules_eur: float
    heures_ebenisterie: float
    heures_tapisserie: float
    main_oeuvre_eur: float
    cout_revient_ht: float
    prix_vente_ht: float
    prix_vente_ttc: float
    fourchette_ttc: tuple[float, float]
    prix_prototype_ttc: float
    masse_bois_kg: float

    @property
    def matiere_eur(self) -> float:
        return self.bois_eur + self.mousse_eur + self.revetement_eur + self.acier_eur

    def resume(self) -> str:
        return (
            f"{self.typologie} — estimation {self.date} : matière {self.matiere_eur:.0f} €, "
            f"quincaillerie {self.quincaillerie_eur:.0f} €, MO {self.heures_ebenisterie:.1f} h ébénisterie + "
            f"{self.heures_tapisserie:.1f} h tapisserie = {self.main_oeuvre_eur:.0f} €, revient "
            f"{self.cout_revient_ht:.0f} € HT ; prix de vente indicatif {self.prix_vente_ttc:.0f} € TTC "
            f"(fourchette {self.fourchette_ttc[0]:.0f}–{self.fourchette_ttc[1]:.0f} €), "
            f"prototype unitaire ≈ {self.prix_prototype_ttc:.0f} € TTC."
        )


def _arrondir(v: float, pas: float = 10.0) -> float:
    return round(v / pas) * pas


def chiffrer(geo: GeometrieMeuble, cat: CatalogueCouts = CATALOGUE_COUTS) -> Chiffrage:
    """Chiffre une géométrie (en pratique l'état MEUBLE / SALON / fixe)."""
    bois = mousse = revet = acier = 0.0
    masse_bois = 0.0
    heures_eb = 0.0
    surface_revet = 0.0
    moules = 0.0
    for p in geo.pieces:
        if p.materiau in ESSENCES:
            e = ESSENCES[p.materiau]
            bois += p.volume_m3 * cat.prix_bois_eur_m3[e.nom] * cat.coefficient_perte_bois[e.famille]
            masse_bois += p.volume_m3 * e.masse_volumique_kg_m3
            heures_eb += cat.temps_role_h.get(p.role, 0.5)
            if e.famille == "contreplaque" and p.role in ("coque", "flasque"):
                moules += cat.amortissement_moule_eur
        elif p.materiau in MOUSSES:
            mousse += p.volume_m3 * MOUSSES[p.materiau].prix_eur_m3
            heures_eb += cat.temps_role_h.get("mousse", 0.4) * 0.5
        elif p.materiau in REVETEMENTS:
            revet += p.surface_revetement_m2 * REVETEMENTS[p.materiau].prix_indicatif_eur_m2 * 1.25
            surface_revet += p.surface_revetement_m2
        elif p.materiau in ("acier", "acier_inox"):
            prix_kg = cat.prix_acier_inox_eur_kg if p.materiau == "acier_inox" else cat.prix_acier_eur_kg
            acier += p.volume_m3 * MASSE_VOLUMIQUE_ACIER * prix_kg
            heures_eb += cat.temps_role_h.get("acier", 0.5)
        else:
            raise KeyError(f"Matériau sans prix « {p.materiau} » ({p.nom}).")
    quinc = 0.0
    for a in geo.assemblages:
        prix, temps = prix_unitaire_quincaillerie(a.fixation)
        quinc += prix * a.quantite
        heures_eb += temps * a.quantite
    for nom, qte in geo.quincaillerie:
        prix, temps = prix_unitaire_quincaillerie(nom)
        quinc += prix * qte
        heures_eb += temps * qte
    heures_eb += cat.heures_montage_forfait + cat.heures_controle_essai
    heures_tap = (cat.heures_tapisserie_forfait + cat.heures_tapisserie_par_m2 * surface_revet
                  if surface_revet > 0 else 0.0)
    mo = heures_eb * cat.taux_horaire_ebeniste_eur + heures_tap * cat.taux_horaire_tapissier_eur
    finition = masse_bois * cat.finition_eur_par_kg_bois + cat.emballage_eur
    revient = bois + mousse + revet + acier + quinc + finition + moules + mo
    ht = revient * cat.coefficient_commercial
    ttc = ht * (1.0 + cat.tva)
    mo_proto = mo * cat.coefficient_prototype
    proto_ttc = (revient - mo - moules + mo_proto + moules * 25) * cat.coefficient_commercial * (1.0 + cat.tva)
    return Chiffrage(
        typologie=geo.typologie, date=cat.date,
        bois_eur=_arrondir(bois, 1), mousse_eur=_arrondir(mousse, 1), revetement_eur=_arrondir(revet, 1),
        acier_eur=_arrondir(acier, 1), quincaillerie_eur=_arrondir(quinc, 1),
        finition_emballage_eur=_arrondir(finition, 1), moules_eur=_arrondir(moules, 1),
        heures_ebenisterie=round(heures_eb, 1), heures_tapisserie=round(heures_tap, 1),
        main_oeuvre_eur=_arrondir(mo, 1), cout_revient_ht=_arrondir(revient),
        prix_vente_ht=_arrondir(ht), prix_vente_ttc=_arrondir(ttc),
        fourchette_ttc=(_arrondir(ttc * (1 - cat.incertitude), 50), _arrondir(ttc * (1 + cat.incertitude), 50)),
        prix_prototype_ttc=_arrondir(proto_ttc, 50), masse_bois_kg=round(masse_bois, 1),
    )
