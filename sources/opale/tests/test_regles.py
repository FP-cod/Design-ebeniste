# -*- coding: utf-8 -*-
"""Tests des règles de recalcul d'ancrage."""

import pytest

from incognito.catalogues.essences import CHENE, MERISIER, essence_par_nom
from incognito.parametres import CHARGES_DEFAUT
from incognito.regles import (
    epaisseur_rail_insuffisante,
    paroi_bois_minimale_mm,
    recaler_bloc_ancrage,
    section_bois_minimale_mm2,
)


def test_section_minimale_formule():
    # 1500 N × 3 / 14 MPa = 321.428... mm²
    section = section_bois_minimale_mm2(CHENE, CHARGES_DEFAUT)
    assert section == pytest.approx(1500.0 * 3.0 / 14.0)


def test_paroi_minimale_chene():
    paroi = paroi_bois_minimale_mm(CHENE, CHARGES_DEFAUT, longueur_encastrement_mm=80.0, nombre_plans=2)
    assert paroi == pytest.approx(1500.0 * 3.0 / (2.0 * 80.0 * 2.0))


def test_recalage_bloc_conforme_et_plus_epais_pour_merisier():
    chene = recaler_bloc_ancrage(CHENE)
    merisier = recaler_bloc_ancrage(MERISIER)
    assert chene.conforme_modele_simplifie
    assert merisier.conforme_modele_simplifie
    assert merisier.geometrie.epaisseur_bloc_mm >= chene.geometrie.epaisseur_bloc_mm
    assert chene.geometrie.epaisseur_recouvrement_mm >= 10.0
    assert any(a.code == "epaisseur_bloc" for a in chene.ajustements)
    assert any(s.code == "essai_charge_reel" for s in chene.rapport.signalements)


def test_rail_28_mm_insuffisant():
    assert epaisseur_rail_insuffisante(28.0, CHENE) is True
    # Un « rail » énorme théoriquement suffisant
    assert epaisseur_rail_insuffisante(200.0, CHENE) is False


def test_recalage_refuse_cs_trop_bas():
    from incognito.parametres import ParametresCharge
    with pytest.raises(ValueError):
        recaler_bloc_ancrage(essence_par_nom("chene"), ParametresCharge(coefficient_securite=2.0))


def test_force_centrifuge_et_transmissibilite():
    from incognito.regles import force_centrifuge_n, transmissibilite, frequence_propre_hz
    # 0,045 kg, 12 mm, 4500 tr/min
    f = force_centrifuge_n(0.045, 12.0, 4500.0)
    assert f == pytest.approx(0.045 * 0.012 * (2 * 3.1415926535 * 4500 / 60) ** 2, rel=1e-3)
    t_res = transmissibilite(1.0, 0.1)
    assert t_res > 1  # pic autour de la résonance
    t_iso = transmissibilite(3.0, 0.1)
    assert t_iso < 0.3
    assert frequence_propre_hz(6000.0, 4.0) == pytest.approx(6.16, abs=0.2)


def test_recalage_change_avec_la_gamme():
    from incognito.regles import recaler_module_vibrant
    h = recaler_module_vibrant("haut", 0.5)
    e = recaler_module_vibrant("entree", 0.5)
    assert h.gamme != e.gamme
    assert h.choix_silentblocs.silentbloc.nom != e.choix_silentblocs.silentbloc.nom
    assert h.choix_silentblocs.isole_ideal or h.choix_silentblocs.isole_au_minimum


def test_analyse_masses_serie_vs_parallele():
    from incognito.regles import (
        analyser_masses_empilement,
        encombrement_vertical_haut,
        ARCHITECTURE_PARALLELE,
        ARCHITECTURE_SERIE,
    )
    par = analyser_masses_empilement(0.75, architecture=ARCHITECTURE_PARALLELE)
    ser = analyser_masses_empilement(0.75, architecture=ARCHITECTURE_SERIE)
    assert par.hors_capacite_15hz_8mm is False
    assert ser.hors_capacite_15hz_8mm is True
    assert ser.masse_mobile_vibration_kg > par.masse_mobile_vibration_kg
    enc_p = encombrement_vertical_haut(ARCHITECTURE_PARALLELE, 430, 90, 15, 18, 18, 36)
    enc_s = encombrement_vertical_haut(ARCHITECTURE_SERIE, 430, 90, 15, 18, 18, 36)
    assert enc_p.rentre is True
    assert enc_s.rentre is False



def test_treillis_petg_trop_raide_pour_isolateur():
    from incognito.regles import comparer_treillis_et_silentbloc
    c = comparer_treillis_et_silentbloc()
    assert c.remplissage == 0.40
    assert c.rapport_raideur_flexion > 1000
    assert c.f0_treillis_flexion_hz > 60.0
    assert c.f0_silentbloc_hz == pytest.approx(6.0, abs=0.2)
    assert c.transmissibilite_treillis_flexion > 0.9
    assert c.transmissibilite_silentbloc < 0.2
    assert c.treillis_adapte_isolation_solidienne is False
    # PLA encore plus raide
    pla = comparer_treillis_et_silentbloc(materiau="PLA")
    assert pla.f0_treillis_flexion_hz >= c.f0_treillis_flexion_hz
