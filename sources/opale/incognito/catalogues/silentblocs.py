# -*- coding: utf-8 -*-
"""Catalogue des silentblocs d'isolation vibratoire (pouf vibrant).

Les raideurs et charges sont des **ordres de grandeur** de plots souples
type isolation d'instrumentation ou de coffret (pas des plots moteur
industriels, trop raides pour un module de quelques kilogrammes).

Sources d'hypothèse : catalogues types Paulstra / Hutchinson / Fabreeka
et plots silicone/Sorbothane pour charges légères. Un choix définitif
exige la fiche constructeur et un essai de transmissibilité.
"""

from __future__ import annotations

from dataclasses import dataclass

from incognito.parametres import GAMME_SYBIAN_ENTREE, GAMME_SYBIAN_HAUT


@dataclass(frozen=True)
class Silentbloc:
    """Plot d'isolation, caractérisé en compression axiale."""

    nom: str
    nom_affiche: str
    materiau: str  # "silicone" ou "caoutchouc"
    gammes: tuple[str, ...]
    raideur_axiale_n_par_mm: float
    raideur_radiale_n_par_mm: float
    charge_nominale_n: float
    deflexion_nominale_mm: float
    hauteur_libre_mm: float
    diametre_mm: float
    filetage_fixation: str
    amortissement_zeta: float
    source: str
    hypotheses: str

    def __post_init__(self) -> None:
        if self.raideur_axiale_n_par_mm <= 0 or self.charge_nominale_n <= 0:
            raise ValueError(f"Silentbloc {self.nom} : raideur et charge doivent être > 0.")
        if not 0.0 < self.amortissement_zeta < 1.0:
            raise ValueError(f"Silentbloc {self.nom} : zeta typique attendu dans (0, 1).")


_HYP = (
    "Raideur approximative à 20 °C, petite oscillation autour de la déflexion "
    "nominale. La raideur réelle dépend de l'amplitude, de la fréquence, de "
    "la température et du fluage. Valeurs à reprendre sur fiche constructeur."
)

SILICONE_TRES_SOUPLE_M6 = Silentbloc(
    nom="silicone_tres_souple_m6",
    nom_affiche="Plot silicone très souple M6 (gamme haut, isolation basse fréquence)",
    materiau="silicone",
    gammes=(GAMME_SYBIAN_HAUT,),
    raideur_axiale_n_par_mm=1.5,
    raideur_radiale_n_par_mm=0.9,
    charge_nominale_n=50.0,
    deflexion_nominale_mm=8.0,
    hauteur_libre_mm=36.0,
    diametre_mm=32.0,
    filetage_fixation="M6",
    amortissement_zeta=0.08,
    source="Ordre de grandeur de plots silicone très souples / plots instrument.",
    hypotheses=_HYP + " Destiné à viser f0 ≈ 6 Hz sous quelques kilogrammes, pour isoler dès ~18 Hz (rapport 3).",
)

SILICONE_SOUPLE_M6 = Silentbloc(
    nom="silicone_souple_m6",
    nom_affiche="Plot silicone souple M6 (gamme haut)",
    materiau="silicone",
    gammes=(GAMME_SYBIAN_HAUT,),
    raideur_axiale_n_par_mm=2.8,
    raideur_radiale_n_par_mm=1.6,
    charge_nominale_n=40.0,
    deflexion_nominale_mm=6.0,
    hauteur_libre_mm=30.0,
    diametre_mm=25.0,
    filetage_fixation="M6",
    amortissement_zeta=0.08,
    source=(
        "Ordre de grandeur de plots silicone souples / plots type Sorbothane "
        "pour charges légères (isolation d'instrumentation)."
    ),
    hypotheses=_HYP + " Zeta faible typique du silicone (isolement meilleur hors résonance, pic plus marqué).",
)

SILICONE_MOYEN_M6 = Silentbloc(
    nom="silicone_moyen_m6",
    nom_affiche="Plot silicone moyen M6 (gamme haut)",
    materiau="silicone",
    gammes=(GAMME_SYBIAN_HAUT,),
    raideur_axiale_n_par_mm=5.0,
    raideur_radiale_n_par_mm=2.8,
    charge_nominale_n=70.0,
    deflexion_nominale_mm=5.0,
    hauteur_libre_mm=28.0,
    diametre_mm=25.0,
    filetage_fixation="M6",
    amortissement_zeta=0.08,
    source="Même famille que silicone_souple_m6, durété supérieure (hypothèse de catalogue).",
    hypotheses=_HYP,
)

CAOUTCHOUC_SOUPLE_M6 = Silentbloc(
    nom="caoutchouc_souple_m6",
    nom_affiche="Plot caoutchouc souple M6 (gamme entrée)",
    materiau="caoutchouc",
    gammes=(GAMME_SYBIAN_ENTREE,),
    raideur_axiale_n_par_mm=8.0,
    raideur_radiale_n_par_mm=4.5,
    charge_nominale_n=80.0,
    deflexion_nominale_mm=4.0,
    hauteur_libre_mm=25.0,
    diametre_mm=25.0,
    filetage_fixation="M6",
    amortissement_zeta=0.12,
    source="Ordre de grandeur de plots NR/NBR cylindriques à faible charge.",
    hypotheses=_HYP + " Zeta un peu plus élevé que le silicone (pic de résonance atténué, isolement HF un peu moindre).",
)

CAOUTCHOUC_MOYEN_M8 = Silentbloc(
    nom="caoutchouc_moyen_m8",
    nom_affiche="Plot caoutchouc moyen M8 (gamme entrée)",
    materiau="caoutchouc",
    gammes=(GAMME_SYBIAN_ENTREE,),
    raideur_axiale_n_par_mm=15.0,
    raideur_radiale_n_par_mm=8.0,
    charge_nominale_n=150.0,
    deflexion_nominale_mm=4.0,
    hauteur_libre_mm=30.0,
    diametre_mm=32.0,
    filetage_fixation="M8",
    amortissement_zeta=0.13,
    source="Ordre de grandeur de plots cylindriques M8 pour petites machines.",
    hypotheses=_HYP,
)

SILENTBLOCS: dict[str, Silentbloc] = {
    s.nom: s
    for s in (
        SILICONE_TRES_SOUPLE_M6,
        SILICONE_SOUPLE_M6,
        SILICONE_MOYEN_M6,
        CAOUTCHOUC_SOUPLE_M6,
        CAOUTCHOUC_MOYEN_M8,
    )
}


def silentbloc_par_nom(nom: str) -> Silentbloc:
    try:
        return SILENTBLOCS[nom]
    except KeyError as exc:
        raise KeyError(
            f"Silentbloc inconnu « {nom} ». Catalogue : {', '.join(sorted(SILENTBLOCS))}."
        ) from exc


def silentblocs_pour_gamme(gamme: str) -> tuple[Silentbloc, ...]:
    """Silentblocs dont la gamme cible correspond (silicone / haut, caoutchouc / entrée)."""
    return tuple(s for s in SILENTBLOCS.values() if gamme in s.gammes)
