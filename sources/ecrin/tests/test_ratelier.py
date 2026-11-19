# -*- coding: utf-8 -*-
"""Grammaire de demonstration : ratelier mural modulaire."""
import pytest

from rangement.grammaires import ratelier_mural as RM
from rangement.geometrie import Boite, Cylindre


def _plan(**ov):
    return RM.concevoir(overrides={k.replace("__", "."): v for k, v in ov.items()}, json_utilisateur=False)


def _noms(plan):
    return {pr.nom for pr in plan.primitives()}


def test_defaut_sans_echec():
    plan = _plan()
    assert len(plan.composants) == 12
    assert not plan.echecs()
    assert {v.nom for v in plan.todos()} == {"support_mural_par_module"}       # mur inconnu
    assert {v.nom for v in plan.alertes()} == {"crochet_accidentel"}


def test_masse_et_charges_plausibles():
    plan = _plan()
    _, m = plan.cg_structure()
    assert 15.0 < m < 45.0
    assert plan.repere["charges_service"] > 0


def test_geometrie_coherente():
    plan = _plan()
    (x0, y0, z0), (x1, y1, z1) = plan.boite_englobante()
    assert x1 - x0 == pytest.approx(2 * 600 + 2.0, abs=5.0)        # 2 modules + jeu
    assert z0 >= 900.0 - 1e-6 and z1 <= 900.0 + 960.0 + 1e-6
    assert 0.0 <= y0 and y1 < 300.0
    for pr in plan.primitives():
        assert isinstance(pr, (Boite, Cylindre)) and pr.masse_kg() > 0


def test_ports_npt_par_defaut():
    plan = _plan()
    noms = _noms(plan)
    assert "module_1_port_1_plot" in noms and "module_1_port_1_douille_npt" in noms
    assert "module_2_port_2_ergot_vac_u_lock" in noms
    types_j = {j.type for j in plan.jonctions}
    assert {"douille_npt_1_femelle", "tourillons"} <= types_j


def test_ports_filetes_m8_sans_plot():
    plan = _plan(systemes__port="port_vac_u_lock_m8", ports__montage_arriere="filete_machine")
    noms = _noms(plan)
    assert not any(n.endswith("_plot") or n.endswith("_douille_npt") for n in noms)
    assert "module_1_port_1_ergot_vac_u_lock" in noms
    assert "insert_filete_m8" in {j.type for j in plan.jonctions}
    assert not plan.echecs()


def test_pas_de_port_si_desactive():
    plan = _plan(ports__npt=False)
    assert not any("port_" in n for n in _noms(plan))


def test_echec_si_barre_trop_chargee():
    plan = _plan(charges__charge_lineaire_barre=60.0, systemes__barre="rond_bois_30", modules__module_largeur=1200.0)
    assert {"barre_flexion", "barre_fleche"} <= {v.nom for v in plan.echecs()}


def test_parametre_hors_plage_refuse():
    with pytest.raises(ValueError):
        _plan(charges__charge_lineaire_barre=400.0)


def test_support_mural_verifie_si_capacite_connue():
    plan = _plan(pose__capacite_support_mur=3000.0)
    assert not plan.todos()


def test_nombre_modules():
    assert len(_plan(ratelier__nombre_modules=3).composants) == 18
