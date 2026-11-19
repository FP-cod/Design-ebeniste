# -*- coding: utf-8 -*-
"""Machine d'états du pilotage (jumeau Python du firmware ESP32).

États : ARRET, ATTENTE_PRESENCE, RAMPE, MARCHE, DEFAUT.

L'arrêt d'urgence physique est *indépendant* de cette machine : un
contact NF + relais de sécurité coupe la puissance des drivers, même
si l'ESP32 est figé ou déconnecté. Cette machine en prend seulement
acte (passage en DEFAUT) lorsque le retour AU est lu.

La perte de présence (après temporisation) et la perte de connexion
(watchdog) coupent les consignes et ramènent à ARRET ou ATTENTE_PRESENCE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class EtatPilotage(IntEnum):
    ARRET = 0
    ATTENTE_PRESENCE = 1
    RAMPE = 2
    MARCHE = 3
    DEFAUT = 4


# Watchdog de connexion : au-delà, consignes à zéro.
WATCHDOG_CONNEXION_S = 1.5
# Durée typique de rampe (s), de 0 à la consigne.
DUREE_RAMPE_DEFAUT_S = 1.5
# Intensité 0–1000 (pourmil).
INTENSITE_MAX = 1000


@dataclass
class Profil:
    nom: str
    vibration: int = 0
    piston: int = 0
    rotation: int = 0
    minuterie_s: float = 0.0  # 0 = pas de minuterie


PROFIL_NEUTRE = Profil("neutre")


@dataclass
class Commandes:
    demarrer: bool = False
    arreter: bool = False
    rearmer: bool = False
    tare: bool = False
    intensite_vibration: int = 0
    intensite_piston: int = 0
    intensite_rotation: int = 0
    minuterie_s: float = 0.0


@dataclass
class EntreesSecurite:
    au_relais_ok: bool = True          # False = AU enclenché ou relais ouvert
    presence: bool = False
    defaut_capteur: bool = False
    connexion_ok: bool = True
    enable_materiel: bool = False      # retour de la chaîne enable (AU ET présence)


@dataclass
class SortiesPilotage:
    consigne_vibration: int = 0
    consigne_piston: int = 0
    consigne_rotation: int = 0
    demande_enable_logiciel: bool = False  # ne remplace pas l'enable matériel
    etat: EtatPilotage = EtatPilotage.ARRET
    code_defaut: str = ""


class MachineEtats:
    """Ordonne les consignes ; ne coupe jamais la puissance à la place de l'AU."""

    def __init__(
        self,
        duree_rampe_s: float = DUREE_RAMPE_DEFAUT_S,
        watchdog_s: float = WATCHDOG_CONNEXION_S,
    ) -> None:
        self.duree_rampe_s = duree_rampe_s
        self.watchdog_s = watchdog_s
        self.etat = EtatPilotage.ARRET
        self.code_defaut = ""
        self._t_rampe_s = 0.0
        self._t_watchdog_s = 0.0
        self._t_minuterie_s = 0.0
        self._minuterie_active_s = 0.0
        self._cible = Commandes()

    def _zero(self) -> SortiesPilotage:
        return SortiesPilotage(etat=self.etat, code_defaut=self.code_defaut)

    def _consignes_rampe(self, cmd: Commandes, progression: float) -> SortiesPilotage:
        p = max(0.0, min(1.0, progression))
        return SortiesPilotage(
            consigne_vibration=int(round(cmd.intensite_vibration * p)),
            consigne_piston=int(round(cmd.intensite_piston * p)),
            consigne_rotation=int(round(cmd.intensite_rotation * p)),
            demande_enable_logiciel=True,
            etat=self.etat,
        )

    def etape(self, dt_s: float, cmd: Commandes, sec: EntreesSecurite) -> SortiesPilotage:
        if not sec.connexion_ok:
            self._t_watchdog_s += dt_s
        else:
            self._t_watchdog_s = 0.0

        perte_connexion = self._t_watchdog_s >= self.watchdog_s
        defaut = (not sec.au_relais_ok) or sec.defaut_capteur

        if defaut and self.etat is not EtatPilotage.DEFAUT:
            self.etat = EtatPilotage.DEFAUT
            self.code_defaut = "au_enclenche" if not sec.au_relais_ok else "capteur"
            self._t_rampe_s = 0.0
            return self._zero()

        if self.etat is EtatPilotage.DEFAUT:
            # Réarmement manuel : AU relâché, capteur OK, et commande de réarmement.
            if cmd.rearmer and sec.au_relais_ok and not sec.defaut_capteur:
                self.etat = EtatPilotage.ARRET
                self.code_defaut = ""
            return self._zero()

        if cmd.arreter:
            self.etat = EtatPilotage.ARRET
            self._t_rampe_s = 0.0
            self._t_minuterie_s = 0.0
            return self._zero()

        if self.etat is EtatPilotage.ARRET:
            if cmd.demarrer and sec.connexion_ok:
                self._cible = cmd
                self._minuterie_active_s = cmd.minuterie_s
                self._t_minuterie_s = 0.0
                self.etat = EtatPilotage.ATTENTE_PRESENCE
            return self._zero()

        if perte_connexion:
            self.etat = EtatPilotage.ARRET
            self._t_rampe_s = 0.0
            return self._zero()

        if self.etat is EtatPilotage.ATTENTE_PRESENCE:
            if sec.presence:
                self.etat = EtatPilotage.RAMPE
                self._t_rampe_s = 0.0
            return self._zero()

        # RAMPE ou MARCHE : la perte de présence coupe (déjà temporisée en amont).
        if not sec.presence:
            self.etat = EtatPilotage.ATTENTE_PRESENCE
            self._t_rampe_s = 0.0
            return self._zero()

        if self._minuterie_active_s > 0:
            self._t_minuterie_s += dt_s
            if self._t_minuterie_s >= self._minuterie_active_s:
                self.etat = EtatPilotage.ARRET
                self._t_rampe_s = 0.0
                self._t_minuterie_s = 0.0
                return self._zero()

        if self.etat is EtatPilotage.RAMPE:
            self._t_rampe_s += dt_s
            if self._t_rampe_s >= self.duree_rampe_s:
                self.etat = EtatPilotage.MARCHE
                return self._consignes_rampe(self._cible, 1.0)
            return self._consignes_rampe(self._cible, self._t_rampe_s / self.duree_rampe_s)

        # MARCHE : les curseurs peuvent bouger en direct.
        self._cible = cmd
        return SortiesPilotage(
            consigne_vibration=cmd.intensite_vibration,
            consigne_piston=cmd.intensite_piston,
            consigne_rotation=cmd.intensite_rotation,
            demande_enable_logiciel=True,
            etat=self.etat,
        )
