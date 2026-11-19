# -*- coding: utf-8 -*-
"""Présence Wheatstone : filtre, aliasing, simulation poids + vibration."""

import pytest

from incognito.presence import (
    TEMPO_LEVEE_S,
    alias_possible_hx711,
    attenuation_filtre_passe_bas_db,
    frequence_coupure_presence_hz,
    frequence_repliee_hz,
    DetecteurPresence,
    ParametresPresence,
    simuler_presence,
)


def test_fc_automatique_et_attenuation():
    fc = frequence_coupure_presence_hz(18.0)
    assert fc == pytest.approx(1.8)
    att = attenuation_filtre_passe_bas_db(18.0, fc, ordre=2)
    assert att == pytest.approx(40.0, abs=0.1)
    with pytest.raises(ValueError):
        frequence_coupure_presence_hz(0.0)


def test_aliasing_hx711_vs_ads1220():
    # HX711 80 SPS : une raie à 30 Hz est sous Nyquist ; à 50 Hz elle se replie.
    assert alias_possible_hx711(30.0, 80.0) is False
    assert alias_possible_hx711(50.0, 80.0) is True
    assert frequence_repliee_hz(50.0, 80.0) == pytest.approx(30.0)
    # ADS1220 à 500 SPS : 8–60 Hz sans repliement.
    assert alias_possible_hx711(60.0, 500.0) is False


def test_simulation_pas_de_fausse_coupure_puis_levee_dans_le_delai():
    """70 kg + vibration 18 Hz et 8 Hz : pas de fausse coupure ; levée ~250 ms."""
    params = ParametresPresence(frequence_exc_min_hz=18.0, fs_hz=500.0)
    levee = 2.0
    # Mode commun ~40 N sur les deux voies, 8 % de résidu après soustraction.
    etats_18 = simuler_presence(
        70.0, duree_s=3.0, params=params,
        vibration_centrale_n=40.0, vibration_reference_n=40.0,
        frequence_vibration_hz=18.0, levee_a_s=levee, residu_relatif=0.08,
    )
    dt = 1.0 / params.fs_hz
    avant = [e for i, e in enumerate(etats_18) if 0.3 <= i * dt < levee]
    assert avant, "préchauffage insuffisant"
    assert all(e.present and not e.defaut for e in avant)

    defauts_levee = None
    for i, e in enumerate(etats_18):
        t = i * dt
        if t >= levee and not e.present:
            defauts_levee = t - levee
            break
    assert defauts_levee is not None, "levée non détectée"
    assert 0.20 <= defauts_levee <= 0.40, f"levée en {defauts_levee:.3f} s, attendu 0,20–0,40 s"
    assert abs(defauts_levee - TEMPO_LEVEE_S) <= 0.12

    # Même scénario à 8 Hz (isolation moins bonne, soustraction indispensable).
    etats_8 = simuler_presence(
        70.0, duree_s=3.0, params=params,
        vibration_centrale_n=80.0, vibration_reference_n=80.0,
        frequence_vibration_hz=8.0, levee_a_s=levee, residu_relatif=0.08,
    )
    avant_8 = [e for i, e in enumerate(etats_8) if 0.3 <= i * dt < levee]
    assert all(e.present and not e.defaut for e in avant_8)
    t_off = next(i * dt - levee for i, e in enumerate(etats_8) if i * dt >= levee and not e.present)
    assert 0.20 <= t_off <= 0.40


def test_derive_zero_et_hors_plage():
    params = ParametresPresence(fs_hz=200.0)
    det = DetecteurPresence(params)
    det.tare_auto(0.0)
    # Dérive humide de 4 kg à vide.
    for _ in range(int(params.fs_hz)):
        e = det.etape(4.0, 0.0)
    assert e.defaut and e.code_defaut == "derive_zero"
    assert e.present is False

    det2 = DetecteurPresence(params)
    det2.tare_auto(0.0)
    e2 = det2.etape(120.0, 0.0)
    assert e2.defaut and e2.code_defaut == "capteur_hors_plage"


def test_tempo_hors_plage_rejetee():
    with pytest.raises(ValueError):
        ParametresPresence(tempo_levee_s=0.5)
