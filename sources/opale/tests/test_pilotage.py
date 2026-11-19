# -*- coding: utf-8 -*-
"""Machine d'états du pilotage ESP32 (jumeau Python)."""

from incognito.pilotage import (
    Commandes,
    EntreesSecurite,
    EtatPilotage,
    MachineEtats,
    WATCHDOG_CONNEXION_S,
)


def _tourner(m, n, dt, cmd, sec):
    s = None
    for _ in range(n):
        s = m.etape(dt, cmd, sec)
    return s


def test_cycle_nominal_rampe_marche_et_curseurs():
    m = MachineEtats(duree_rampe_s=1.0)
    dt = 0.05
    cmd = Commandes(demarrer=True, intensite_vibration=800, intensite_piston=400, intensite_rotation=200)
    sec = EntreesSecurite(presence=False, connexion_ok=True)
    s = _tourner(m, 2, dt, cmd, sec)
    assert s.etat is EtatPilotage.ATTENTE_PRESENCE
    assert s.consigne_vibration == 0
    sec = EntreesSecurite(presence=True, connexion_ok=True)
    s = m.etape(dt, cmd, sec)
    assert s.etat is EtatPilotage.RAMPE
    s = _tourner(m, 25, dt, cmd, sec)  # 1,25 s > rampe 1,0 s
    assert s.etat is EtatPilotage.MARCHE
    assert s.consigne_vibration == 800
    assert s.demande_enable_logiciel is True
    # Curseur en marche
    cmd2 = Commandes(intensite_vibration=100, intensite_piston=0, intensite_rotation=0)
    s = m.etape(dt, cmd2, sec)
    assert s.consigne_vibration == 100


def test_perte_presence_et_watchdog_connexion():
    m = MachineEtats(duree_rampe_s=0.2, watchdog_s=WATCHDOG_CONNEXION_S)
    dt = 0.1
    cmd = Commandes(demarrer=True, intensite_vibration=500)
    sec = EntreesSecurite(presence=True, connexion_ok=True)
    _tourner(m, 3, dt, cmd, sec)  # rampe
    _tourner(m, 5, dt, cmd, sec)  # marche
    assert m.etat is EtatPilotage.MARCHE
    # Présence perdue (temporisation déjà appliquée en amont)
    sec_abs = EntreesSecurite(presence=False, connexion_ok=True)
    s = m.etape(dt, cmd, sec_abs)
    assert s.etat is EtatPilotage.ATTENTE_PRESENCE
    assert s.consigne_vibration == 0

    # Reprise puis perte de connexion
    _tourner(m, 8, dt, cmd, EntreesSecurite(presence=True, connexion_ok=True))
    assert m.etat is EtatPilotage.MARCHE
    sec_ko = EntreesSecurite(presence=True, connexion_ok=False)
    n = int(WATCHDOG_CONNEXION_S / dt) + 2
    s = _tourner(m, n, dt, cmd, sec_ko)
    assert s.etat is EtatPilotage.ARRET
    assert s.consigne_vibration == 0


def test_au_independant_defaut_et_rearmement_manuel():
    m = MachineEtats(duree_rampe_s=0.2)
    dt = 0.1
    cmd = Commandes(demarrer=True, intensite_vibration=500)
    _tourner(m, 8, dt, cmd, EntreesSecurite(presence=True, connexion_ok=True, au_relais_ok=True))
    assert m.etat is EtatPilotage.MARCHE
    s = m.etape(dt, cmd, EntreesSecurite(presence=True, connexion_ok=True, au_relais_ok=False))
    assert s.etat is EtatPilotage.DEFAUT
    assert s.consigne_vibration == 0
    assert s.code_defaut == "au_enclenche"
    # Relâcher l'AU ne relance pas tout seul
    s = m.etape(dt, Commandes(), EntreesSecurite(presence=True, connexion_ok=True, au_relais_ok=True))
    assert s.etat is EtatPilotage.DEFAUT
    s = m.etape(dt, Commandes(rearmer=True), EntreesSecurite(presence=True, connexion_ok=True, au_relais_ok=True))
    assert s.etat is EtatPilotage.ARRET
    assert s.consigne_vibration == 0


def test_minuterie_arret():
    m = MachineEtats(duree_rampe_s=0.1)
    dt = 0.1
    cmd_go = Commandes(demarrer=True, intensite_vibration=300, minuterie_s=0.5)
    cmd = Commandes(intensite_vibration=300, minuterie_s=0.5)
    sec = EntreesSecurite(presence=True, connexion_ok=True)
    m.etape(dt, cmd_go, sec)
    s = _tourner(m, 20, dt, cmd, sec)
    assert s.etat is EtatPilotage.ARRET
    assert s.consigne_vibration == 0
