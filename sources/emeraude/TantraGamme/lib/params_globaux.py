# -*- coding: utf-8 -*-
"""Couche 1 — Paramètres globaux de la gamme Tantra.

Ce module ne dépend PAS de ``adsk`` : il est importable et testable en pur
Python (``python -m unittest``), puis réutilisé tel quel dans Fusion 360.

Conventions
-----------
* Toutes les longueurs sont en **millimètres (mm)**, les angles en **degrés**,
  les masses en **kg**, les forces en **newtons (N)**, les contraintes en
  **MPa (= N/mm²)**, les prix en **euros HT**.
* L'API Fusion travaille en **centimètres** en interne : utiliser
  :func:`mm_vers_cm` avant de passer une valeur à ``adsk.core.ValueInput``
  (ou passer une chaîne "450 mm" via ``createByString``).
* Chaque paramètre est documenté : unité, plage admissible, rôle.
* Les prix sont des **ordres de grandeur France 2026, HT, à valider par devis**.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Utilitaires d'unités
# ---------------------------------------------------------------------------
G = 9.81  # m/s² — accélération de la pesanteur


def mm_vers_cm(valeur_mm: float) -> float:
    """Convertit des mm en cm (unité interne de l'API Fusion 360)."""
    return valeur_mm / 10.0


def kg_vers_N(masse_kg: float) -> float:
    """Convertit une masse (kg) en poids (N)."""
    return masse_kg * G


# ---------------------------------------------------------------------------
# (a1) Anthropométrie de référence
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Anthropometrie:
    """Dimensions anthropométriques de référence (adultes, mm).

    Sources d'ordre de grandeur : tables ergonomiques type NF EN ISO 7250 /
    données françaises adultes (5e centile femme -> 95e centile homme).
    Une gamme FIXE ne se règle pas : on dimensionne pour couvrir la plage
    P5 femme – P95 homme et on documente les compromis.
    """

    stature_p5: float = 1530.0
    """mm — stature 5e centile (femme). Plage 1500–1560. Borne basse de confort."""
    stature_p95: float = 1880.0
    """mm — stature 95e centile (homme). Plage 1850–1920. Fixe les longueurs."""
    hauteur_poplitee_p5: float = 380.0
    """mm — creux du genou au sol, P5. Plage 360–400. Hauteur d'assise max confortable."""
    hauteur_poplitee_p95: float = 490.0
    """mm — idem P95. Plage 470–510."""
    profondeur_assise_p5: float = 440.0
    """mm — fesse-creux poplité P5. Plage 420–460. Profondeur d'assise MAX utile."""
    profondeur_assise_p95: float = 530.0
    """mm — fesse-creux poplité P95. Plage 510–550."""
    largeur_hanches_p95: float = 430.0
    """mm — largeur hanches assis P95. Plage 410–460. Largeur d'assise MIN (1 personne)."""
    hauteur_lombaire_bas: float = 170.0
    """mm — centre lombaire (L3–L4) au-dessus de l'assise, petit gabarit. Plage 150–190."""
    hauteur_lombaire_haut: float = 250.0
    """mm — centre lombaire au-dessus de l'assise, grand gabarit. Plage 230–270."""
    hauteur_omoplates: float = 450.0
    """mm — pointe des omoplates au-dessus de l'assise (moyenne). Plage 400–500."""
    largeur_epaules_p95: float = 500.0
    """mm — largeur bi-deltoïdienne P95. Plage 480–520. Largeur utile couchage dos."""

    def plage_lombaire(self) -> Tuple[float, float]:
        """Plage (mm) de hauteur du centre de l'appui lombaire au-dessus de l'assise."""
        return (self.hauteur_lombaire_bas, self.hauteur_lombaire_haut)


# ---------------------------------------------------------------------------
# (a2) Charges de conception
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ChargesConception:
    """Hypothèses de charge. Mobilier d'usage dynamique à DEUX personnes.

    Les normes mobilier (EN 12520, EN 1728) testent ~1300–2000 N statiques
    sur l'assise ; un usage à deux, avec mouvements, justifie des valeurs
    nettement supérieures.
    """

    masse_occupant_kg: float = 120.0
    """kg — masse de conception par occupant. Plage 100–150."""
    nb_occupants: int = 2
    """— nombre d'occupants simultanés. Plage 1–2."""
    coef_dynamique: float = 2.0
    """— majoration dynamique (mouvements, chocs). Plage 1.5–2.5."""
    coef_repartition: float = 2.0
    """— part de charge concentrée : 2.0 = toute la charge sur la moitié des pieds. Plage 1–2."""
    coef_securite_flambement: float = 3.0
    """— marge sur la charge critique d'Euler des pieds. Plage 2.5–4."""
    effort_lateral_ratio: float = 0.15
    """— effort horizontal / effort vertical (balancement, contreventement). Plage 0.10–0.25."""
    fleche_relative_max: float = 300.0
    """— flèche admissible des traverses/lattes = portée / cette valeur. Plage 200–400."""

    def charge_verticale_N(self) -> float:
        """Charge verticale de conception totale (N), dynamique incluse."""
        return kg_vers_N(self.masse_occupant_kg * self.nb_occupants) * self.coef_dynamique

    def charge_laterale_N(self) -> float:
        """Effort horizontal de conception (N) pour le contreventement."""
        return self.charge_verticale_N() * self.effort_lateral_ratio


# ---------------------------------------------------------------------------
# (a3) Essences de bois
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Essence:
    """Bois massif. Propriétés mécaniques assimilées EN 338 (valeurs prudentes)."""

    nom: str
    masse_volumique: float
    """kg/m³ à 12 % d'humidité. Plage 550–800."""
    prix_m3_bas: float
    """€/m³ HT — avivés séchés qualité ébénisterie, bas de fourchette."""
    prix_m3_haut: float
    """€/m³ HT — haut de fourchette (qualité choisie, petites quantités)."""
    E0_mean: float
    """MPa — module d'élasticité moyen // fil. Plage 10000–14000."""
    fc0k: float
    """MPa — résistance caractéristique compression // fil. Plage 20–30."""
    fmk: float
    """MPa — résistance caractéristique flexion. Plage 28–45."""
    fvk: float
    """MPa — résistance caractéristique cisaillement. Plage 3.5–4.5."""
    retrait_tangentiel_pct: float
    """% — retrait tangentiel total (anhydre). Guide les jeux des panneaux."""
    commentaire: str = ""

    @property
    def prix_m3_moyen(self) -> float:
        """€/m³ HT — milieu de fourchette."""
        return (self.prix_m3_bas + self.prix_m3_haut) / 2.0


ESSENCES: Dict[str, Essence] = {
    "chene": Essence(
        nom="Chêne européen (Quercus robur/petraea)", masse_volumique=700,
        prix_m3_bas=1800, prix_m3_haut=3000, E0_mean=11000, fc0k=24, fmk=30,
        fvk=3.9, retrait_tangentiel_pct=9.0,
        commentaire="Classe ~D30. Référence de la gamme : solide, classique, tanins (tache au fer).",
    ),
    "frene": Essence(
        nom="Frêne européen (Fraxinus excelsior)", masse_volumique=690,
        prix_m3_bas=1300, prix_m3_haut=2000, E0_mean=12500, fc0k=26, fmk=38,
        fvk=4.0, retrait_tangentiel_pct=8.0,
        commentaire="Classe ~D35-D40. Le plus résilient aux chocs, idéal pièces cintrées; teinte claire.",
    ),
    "noyer": Essence(
        nom="Noyer (européen ou noir d'Amérique)", masse_volumique=640,
        prix_m3_bas=3500, prix_m3_haut=6000, E0_mean=11000, fc0k=23, fmk=30,
        fvk=3.8, retrait_tangentiel_pct=7.0,
        commentaire="Assimilé D30 (prudent). Haut de gamme, stable, sections à garder généreuses.",
    ),
}


# ---------------------------------------------------------------------------
# (a4) Garnissage : mousses et revêtements, finitions
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Mousse:
    """Mousse de garnissage."""

    nom: str
    densite: float
    """kg/m³. Plage 30–80. Durabilité ≈ densité."""
    portance_kpa: float
    """kPa — portance (indentation 40 %). Plage 2–8. Ferme > 5."""
    prix_m3: float
    """€/m³ HT — ordre de grandeur, découpe incluse."""
    usage: str = ""


MOUSSES: Dict[str, Mousse] = {
    "HR35": Mousse("Haute résilience 35 kg/m³", 35, 3.5, 320, "Dossiers, appuis lombaires."),
    "HR45": Mousse("Haute résilience 45 kg/m³", 45, 4.5, 450, "Assises, plans de soutien (référence)."),
    "HR55F": Mousse("Haute résilience 55 kg/m³ extra-ferme", 55, 7.0, 600, "Cales fessières, arêtes porteuses."),
    "VISCO50": Mousse("Viscoélastique 50 kg/m³", 50, 2.0, 900, "Surcouche confort 20–30 mm (lente, chaude)."),
    "LATEX65": Mousse("Latex naturel 65 kg/m³", 65, 4.0, 1300, "Option premium, très résilient, respirant."),
}


@dataclass(frozen=True)
class Revetement:
    """Revêtement de garnissage."""

    nom: str
    prix_m2_bas: float
    """€/m² HT — bas de fourchette."""
    prix_m2_haut: float
    """€/m² HT — haut de fourchette."""
    coef_chute: float
    """— surface achetée / surface utile. Cuir 1.3–1.5 (peaux), tissu 1.15–1.25."""
    nettoyabilite: int
    """1 (faible) à 5 (excellente) — critère majeur pour cet usage."""
    commentaire: str = ""


REVETEMENTS: Dict[str, Revetement] = {
    "cuir_pigmente": Revetement("Cuir pleine fleur pigmenté (protégé)", 55, 90, 1.4, 5,
                                "Recommandé : patine, nettoyable, résiste aux huiles de massage si verni."),
    "cuir_aniline": Revetement("Cuir aniline / semi-aniline", 80, 140, 1.45, 2,
                               "Superbe mais tache (huiles, fluides) : déconseillé en assise."),
    "simili_pu": Revetement("Simili PU/vinyle haut de gamme (grade médical)", 25, 45, 1.2, 5,
                            "Imperméable, désinfectable, moins noble ; option économique."),
    "velours_deperlant": Revetement("Velours traité déperlant", 40, 75, 1.2, 3,
                                    "Chaleureux ; prévoir housses amovibles."),
}


@dataclass(frozen=True)
class Finition:
    """Finition du bois apparent."""

    nom: str
    prix_m2: float
    """€/m² HT — produits seuls (la main d'œuvre est dans les heures)."""
    nettoyabilite: int
    """1 à 5."""


FINITIONS: Dict[str, Finition] = {
    "huile_cire": Finition("Huile-cire dure", 8, 3),
    "vernis_pu_mat": Finition("Vernis PU bi-composant mat", 14, 5),
    "huile_teck": Finition("Huile simple", 5, 2),
}


# ---------------------------------------------------------------------------
# (a5) Tarifs et coefficients économiques
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Tarifs:
    """Hypothèses économiques (HT, France, 2026). À recaler sur devis réels."""

    taux_ebeniste_bas: float = 45.0
    """€/h HT — atelier artisanal, bas de fourchette. Plage 40–55."""
    taux_ebeniste_haut: float = 70.0
    """€/h HT — atelier haut de gamme. Plage 60–85."""
    taux_tapissier_bas: float = 40.0
    """€/h HT. Plage 35–50."""
    taux_tapissier_haut: float = 60.0
    """€/h HT. Plage 55–75."""
    coef_dechet_droit: float = 1.5
    """— volume brut acheté / volume net, pièces droites. Plage 1.3–1.7."""
    coef_dechet_cintre: float = 2.2
    """— idem, pièces chantournées dans la masse. Plage 1.8–2.6."""
    coef_frais_generaux: float = 1.0
    """— multiplicateur optionnel (frais d'atelier, marge). 1.0 = coût de revient direct."""


# ---------------------------------------------------------------------------
# (a6) Règles ergonomiques globales (bornes partagées par les typologies)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Ergonomie:
    """Bornes ergonomiques de la gamme (mm, degrés)."""

    angle_assise_dossier_min: float = 100.0
    """deg — angle intérieur assise/dossier min. Plage 95–105."""
    angle_assise_dossier_max: float = 125.0
    """deg — max (posture semi-allongée). Plage 115–135."""
    inclinaison_assise_max: float = 15.0
    """deg — basculement arrière de l'assise. Plage 0–20."""
    rayon_arete_min: float = 6.0
    """mm — rayon mini des arêtes bois apparentes (contact peau). Plage 4–15."""
    epaisseur_garnissage_assise: float = 80.0
    """mm — mousse d'assise totale. Plage 60–120."""
    epaisseur_garnissage_dossier: float = 50.0
    """mm — mousse de dossier/lombaire. Plage 30–70."""
    diametre_boudin_lombaire: float = 160.0
    """mm — diamètre équivalent de l'appui lombaire. Plage 120–200."""
    hauteur_cale_fessiere: float = 90.0
    """mm — surélévation du bassin par la cale. Plage 60–150."""
    angle_cale_fessiere: float = 18.0
    """deg — pente de la cale. Plage 10–30."""
    largeur_assise_duo: float = 700.0
    """mm — largeur utile pour deux personnes face à face. Plage 650–800."""


# ---------------------------------------------------------------------------
# Jeu de paramètres complet
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParametresGlobaux:
    """Agrégat de la couche 1, passé aux scripts de typologie."""

    anthropo: Anthropometrie = field(default_factory=Anthropometrie)
    charges: ChargesConception = field(default_factory=ChargesConception)
    tarifs: Tarifs = field(default_factory=Tarifs)
    ergonomie: Ergonomie = field(default_factory=Ergonomie)
    essence_defaut: str = "chene"
    """Clé de ``ESSENCES``. Essence de référence de la gamme."""
    mousse_assise: str = "HR45"
    """Clé de ``MOUSSES`` pour les assises."""
    revetement_defaut: str = "cuir_pigmente"
    """Clé de ``REVETEMENTS``."""
    finition_defaut: str = "vernis_pu_mat"
    """Clé de ``FINITIONS``."""

    def essence(self) -> Essence:
        """Essence de référence (objet)."""
        return ESSENCES[self.essence_defaut]


PARAMS = ParametresGlobaux()
"""Instance par défaut, importée par les scripts de typologie."""


def parametres_fusion(p: ParametresGlobaux = PARAMS) -> Dict[str, Tuple[float, str, str]]:
    """Liste à plat des paramètres dimensionnels à créer comme *User Parameters* Fusion.

    Retourne ``{nom: (valeur, unité_fusion, commentaire)}``. Les noms respectent
    la syntaxe Fusion (lettres, chiffres, '_', pas d'accent).
    """
    a, e = p.anthropo, p.ergonomie
    return {
        "TG_poplitee_p5": (a.hauteur_poplitee_p5, "mm", "Hauteur poplitée P5"),
        "TG_poplitee_p95": (a.hauteur_poplitee_p95, "mm", "Hauteur poplitée P95"),
        "TG_prof_assise_p5": (a.profondeur_assise_p5, "mm", "Profondeur d'assise max utile"),
        "TG_larg_hanches_p95": (a.largeur_hanches_p95, "mm", "Largeur hanches assis P95"),
        "TG_lombaire_bas": (a.hauteur_lombaire_bas, "mm", "Centre lombaire bas / assise"),
        "TG_lombaire_haut": (a.hauteur_lombaire_haut, "mm", "Centre lombaire haut / assise"),
        "TG_stature_p95": (a.stature_p95, "mm", "Stature P95"),
        "TG_ang_assise_dos_min": (e.angle_assise_dossier_min, "deg", "Angle assise/dossier min"),
        "TG_ang_assise_dos_max": (e.angle_assise_dossier_max, "deg", "Angle assise/dossier max"),
        "TG_incl_assise_max": (e.inclinaison_assise_max, "deg", "Bascule assise max"),
        "TG_rayon_arete": (e.rayon_arete_min, "mm", "Rayon mini arêtes"),
        "TG_ep_garn_assise": (e.epaisseur_garnissage_assise, "mm", "Mousse assise"),
        "TG_ep_garn_dossier": (e.epaisseur_garnissage_dossier, "mm", "Mousse dossier"),
        "TG_d_boudin_lomb": (e.diametre_boudin_lombaire, "mm", "Diamètre appui lombaire"),
        "TG_h_cale": (e.hauteur_cale_fessiere, "mm", "Hauteur cale fessière"),
        "TG_ang_cale": (e.angle_cale_fessiere, "deg", "Pente cale fessière"),
        "TG_larg_duo": (e.largeur_assise_duo, "mm", "Largeur assise duo"),
    }


def resume(p: ParametresGlobaux = PARAMS) -> dict:
    """Dictionnaire sérialisable de tous les paramètres (journal, export JSON)."""
    return {
        "anthropo": asdict(p.anthropo),
        "charges": asdict(p.charges),
        "tarifs": asdict(p.tarifs),
        "ergonomie": asdict(p.ergonomie),
        "essence_defaut": p.essence_defaut,
        "charge_verticale_N": round(p.charges.charge_verticale_N(), 1),
    }
