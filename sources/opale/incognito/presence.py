# -*- coding: utf-8 -*-
"""Présence par cellules de charge (pont de Wheatstone).

Les FSR sont écartés (voir ``catalogues.electronique.NOTE_FSR_ECARTE``).

Le filtre passe-bas logiciel a une fréquence de coupure
``fc ≤ f_exc_min / 10``, calculée automatiquement. Un seul filtre
du second ordre à ~1,8 Hz ne peut pas à la fois atténuer 40 dB à
18 Hz et transitoire en 200–300 ms : la décision de présence
emprunte donc un chemin rapide (soustraction de zone + moyenne
courte) plus une temporisation de levée, tandis que le filtre
strict sert à la tare, à la dérive et au diagnostic.

Ce module est le jumeau Python du firmware (``firmware/src/presence.cpp``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Temporisation de levée : 250 ms, dans la plage 200–300 ms demandée.
# Justification : à 8 Hz, deux périodes durent 250 ms ; on ignore ainsi
# un creux vibratoire ou un rebond d'assise, tout en coupant assez tôt
# après une levée réelle (l'AU câblé reste la coupure d'urgence).
TEMPO_LEVEE_S = 0.25
TEMPO_LEVEE_MIN_S = 0.20
TEMPO_LEVEE_MAX_S = 0.30

# Seuils (kg). Une housse 0,5–1 kg + selle reste sous le seuil bas.
SEUIL_PRESENCE_KG = 15.0
SEUIL_ABSENCE_KG = 10.0
HYSTERESIS_KG = SEUIL_PRESENCE_KG - SEUIL_ABSENCE_KG

DERIVE_ZERO_MAX_KG = 2.5
FENETRE_RAPIDE_S = 0.050
POIDS_ADC_HORS_PLAGE_KG = 80.0  # au-delà d'une cellule 50 kg utile + marge

RAPPORT_FC_SUR_FEXC = 10.0


def frequence_coupure_presence_hz(frequence_exc_min_hz: float) -> float:
    """fc ≤ f_exc_min / 10, calculée automatiquement."""
    if frequence_exc_min_hz <= 0:
        raise ValueError("frequence_exc_min_hz doit être > 0.")
    return frequence_exc_min_hz / RAPPORT_FC_SUR_FEXC


def attenuation_filtre_passe_bas_db(
    frequence_hz: float,
    frequence_coupure_hz: float,
    ordre: int = 2,
) -> float:
    """Atténuation d'un Butterworth, en dB (positive = affaiblissement)."""
    if frequence_coupure_hz <= 0 or ordre < 1:
        raise ValueError("Paramètres de filtre invalides.")
    if frequence_hz < 0:
        raise ValueError("frequence_hz doit être ≥ 0.")
    ratio = (frequence_hz / frequence_coupure_hz) ** (2 * ordre)
    module = 1.0 / math.sqrt(1.0 + ratio)
    if module <= 1e-12:
        return 240.0
    return -20.0 * math.log10(module)


def alias_possible_hx711(frequence_signal_hz: float, fs_hz: float = 80.0) -> bool:
    """True si le signal se replie dans [0, fs/2] (HX711 typique 80 SPS)."""
    nyquist = fs_hz / 2.0
    return frequence_signal_hz > nyquist


def frequence_repliee_hz(frequence_signal_hz: float, fs_hz: float) -> float:
    """Fréquence apparente après sous-échantillonnage (repliement)."""
    if fs_hz <= 0:
        raise ValueError("fs_hz doit être > 0.")
    period = fs_hz
    f = abs(frequence_signal_hz) % period
    if f > period / 2.0:
        f = period - f
    return f


def coefficients_butterworth_ordre2(fc_hz: float, fs_hz: float) -> tuple[float, ...]:
    """Biquad Butterworth 2, transformée bilinéaire (b0, b1, b2, a1, a2)."""
    if fc_hz <= 0 or fs_hz <= 0 or fc_hz >= fs_hz / 2.0:
        raise ValueError("fc doit être dans ]0, fs/2[.")
    k = math.tan(math.pi * fc_hz / fs_hz)
    k2 = k * k
    s2 = math.sqrt(2.0)
    norme = 1.0 / (1.0 + s2 * k + k2)
    b0 = k2 * norme
    b1 = 2.0 * b0
    b2 = b0
    a1 = 2.0 * (k2 - 1.0) * norme
    a2 = (1.0 - s2 * k + k2) * norme
    return (b0, b1, b2, a1, a2)


class Biquad:
    """Filtre d'ordre 2, état interne."""

    def __init__(self, coeffs: tuple[float, ...]) -> None:
        self.b0, self.b1, self.b2, self.a1, self.a2 = coeffs
        self.x1 = self.x2 = 0.0
        self.y1 = self.y2 = 0.0

    def reinitialiser(self, valeur: float = 0.0) -> None:
        self.x1 = self.x2 = valeur
        self.y1 = self.y2 = valeur

    def etape(self, x: float) -> float:
        y = (
            self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2
            - self.a1 * self.y1 - self.a2 * self.y2
        )
        self.x2, self.x1 = self.x1, x
        self.y2, self.y1 = self.y1, y
        return y


@dataclass
class EtatPresence:
    present: bool = False
    poids_soustrait_kg: float = 0.0
    poids_filtre_kg: float = 0.0
    poids_rapide_kg: float = 0.0
    tare_kg: float = 0.0
    defaut: bool = False
    code_defaut: str = ""
    temps_sous_seuil_s: float = 0.0


@dataclass
class ParametresPresence:
    frequence_exc_min_hz: float = 18.0
    fs_hz: float = 500.0  # ADS1220 recommandé
    seuil_presence_kg: float = SEUIL_PRESENCE_KG
    seuil_absence_kg: float = SEUIL_ABSENCE_KG
    tempo_levee_s: float = TEMPO_LEVEE_S
    derive_zero_max_kg: float = DERIVE_ZERO_MAX_KG
    gain_reference: float = 1.0

    def __post_init__(self) -> None:
        if not (TEMPO_LEVEE_MIN_S <= self.tempo_levee_s <= TEMPO_LEVEE_MAX_S):
            raise ValueError(
                f"tempo_levee_s doit être dans [{TEMPO_LEVEE_MIN_S}, {TEMPO_LEVEE_MAX_S}] s."
            )
        if self.seuil_absence_kg >= self.seuil_presence_kg:
            raise ValueError("Hystérésis : seuil_absence < seuil_presence.")

    @property
    def frequence_coupure_hz(self) -> float:
        return frequence_coupure_presence_hz(self.frequence_exc_min_hz)

    @property
    def attenuation_a_fexc_db(self) -> float:
        return attenuation_filtre_passe_bas_db(
            self.frequence_exc_min_hz, self.frequence_coupure_hz, ordre=2
        )


class DetecteurPresence:
    """Double zone (centrale − référence) + tare + hystérésis + défauts."""

    def __init__(self, params: ParametresPresence | None = None) -> None:
        self.params = params or ParametresPresence()
        self.filtre = Biquad(
            coefficients_butterworth_ordre2(
                self.params.frequence_coupure_hz, self.params.fs_hz
            )
        )
        n_rapide = max(1, int(round(FENETRE_RAPIDE_S * self.params.fs_hz)))
        self._fenetre: list[float] = []
        self._n_rapide = n_rapide
        self.etat = EtatPresence()
        self._tare_faite = False

    def tare_auto(self, poids_brut_kg: float) -> None:
        """Tare selle vide (housse éventuellement en place, sous le seuil)."""
        self.etat.tare_kg = poids_brut_kg
        self.filtre.reinitialiser(0.0)
        self._fenetre.clear()
        self.etat.poids_filtre_kg = 0.0
        self.etat.poids_rapide_kg = 0.0
        self._tare_faite = True
        self.etat.defaut = False
        self.etat.code_defaut = ""

    def etape(
        self,
        zone_centrale_kg: float,
        zone_reference_kg: float = 0.0,
        dt_s: float | None = None,
    ) -> EtatPresence:
        p = self.params
        dt = 1.0 / p.fs_hz if dt_s is None else dt_s
        if not self._tare_faite:
            # Tare automatique à la première mesure (selle vide attendue).
            self.tare_auto(zone_centrale_kg - p.gain_reference * zone_reference_kg)

        if abs(zone_centrale_kg) > POIDS_ADC_HORS_PLAGE_KG:
            self.etat.defaut = True
            self.etat.code_defaut = "capteur_hors_plage"
            self.etat.present = False
            return self.etat

        soustrait = (
            zone_centrale_kg - p.gain_reference * zone_reference_kg - self.etat.tare_kg
        )
        self.etat.poids_soustrait_kg = soustrait
        self.etat.poids_filtre_kg = self.filtre.etape(soustrait)

        self._fenetre.append(soustrait)
        if len(self._fenetre) > self._n_rapide:
            self._fenetre.pop(0)
        rapide = sum(self._fenetre) / len(self._fenetre)
        self.etat.poids_rapide_kg = rapide

        # Dérive du zéro (humidité, fluage de jauge) sur le filtre strict,
        # uniquement en l'absence de présence.
        if (
            not self.etat.present
            and abs(self.etat.poids_filtre_kg) > p.derive_zero_max_kg
            and len(self._fenetre) >= self._n_rapide
        ):
            self.etat.defaut = True
            self.etat.code_defaut = "derive_zero"
            self.etat.present = False
            return self.etat

        if self.etat.present:
            if rapide < p.seuil_absence_kg:
                self.etat.temps_sous_seuil_s += dt
                if self.etat.temps_sous_seuil_s >= p.tempo_levee_s:
                    self.etat.present = False
                    self.etat.temps_sous_seuil_s = 0.0
            else:
                self.etat.temps_sous_seuil_s = 0.0
        else:
            self.etat.temps_sous_seuil_s = 0.0
            if rapide >= p.seuil_presence_kg:
                self.etat.present = True

        return self.etat


def simuler_presence(
    poids_usager_kg,
    duree_s: float,
    params: ParametresPresence | None = None,
    vibration_centrale_n: float = 0.0,
    vibration_reference_n: float = 0.0,
    frequence_vibration_hz: float = 18.0,
    levee_a_s: float | None = None,
    residu_relatif: float = 0.08,
) -> list[EtatPresence]:
    """Simule une série temporelle (poids + vibration) et renvoie les états.

    ``poids_usager_kg`` peut être un flottant constant ou un appelable t → kg.
    La vibration de référence est soustraite ; un résidu relatif (défaut
    de gain) reste sur la voie centrale.
    """
    params = params or ParametresPresence()
    det = DetecteurPresence(params)
    dt = 1.0 / params.fs_hz
    n = int(round(duree_s * params.fs_hz))
    # Tare à vide, avant l'usager.
    det.tare_auto(0.0)
    etats: list[EtatPresence] = []
    g = 9.81
    for i in range(n):
        t = i * dt
        if callable(poids_usager_kg):
            m = float(poids_usager_kg(t))
        else:
            m = float(poids_usager_kg)
        if levee_a_s is not None and t >= levee_a_s:
            m = 0.0
        omega = 2.0 * math.pi * frequence_vibration_hz
        osc_c = (vibration_centrale_n / g) * math.sin(omega * t)
        osc_r = (vibration_reference_n / g) * math.sin(omega * t)
        # Résidu de soustraction (désaccord de gain).
        centrale = m + osc_c
        reference = osc_r
        # On injecte le résidu sur la centrale après le modèle physique.
        centrale = m + osc_c * (1.0 + residu_relatif)
        # La référence voit le mode commun (sans le poids usager).
        reference = osc_r
        # Copie : l'état renvoyé doit être figé pour l'historique.
        e = det.etape(centrale, reference, dt_s=dt)
        etats.append(EtatPresence(
            present=e.present,
            poids_soustrait_kg=e.poids_soustrait_kg,
            poids_filtre_kg=e.poids_filtre_kg,
            poids_rapide_kg=e.poids_rapide_kg,
            tare_kg=e.tare_kg,
            defaut=e.defaut,
            code_defaut=e.code_defaut,
            temps_sous_seuil_s=e.temps_sous_seuil_s,
        ))
    return etats
