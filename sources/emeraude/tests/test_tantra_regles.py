# -*- coding: utf-8 -*-
"""Règles de recalcul (couche 2)."""
import pytest

from tantra import regles as R
from tantra.catalogues.mecanismes import (AXE_16, DOIGT_INDEXAGE_12, DOIGT_INDEXAGE_16, GOUPILLE_CAPTIVE_10,
                                          GOUPILLE_CAPTIVE_12, VERROU_CAME)
from tantra.parametres import CHENE, LAMELLE_HETRE, NIVEAU_NON_CONFORME, ParametresCharge
from tantra.grammaires._cadre import resistance_verrou_dans_bois_n, verifier_liaison_verrouillee, etat_depuis_code
from tantra.grammaires import _salon


def test_arrachement_insert_croit_avec_densite():
    assert R.arrachement_insert_n(16, 60, 730) > R.arrachement_insert_n(16, 60, 550) > 0


def test_bloc_ancrage_cs3():
    b = R.recaler_bloc_ancrage(CHENE)
    assert b.epaisseur_mm >= 50 and b.largeur_mm >= 80
    with pytest.raises(ValueError):
        R.recaler_bloc_ancrage(CHENE, ParametresCharge(coefficient_securite=2.0))


def test_piece_loge_insert():
    ok, _ = R.piece_loge_insert(60, 70, CHENE)
    assert ok
    ok, txt = R.piece_loge_insert(160, 50, CHENE)
    assert not ok and "besoin 60" in txt
    ok, _ = R.piece_loge_insert(50, 60, CHENE, recouvrement_mm=10)
    assert not ok


def test_flexion_et_fleche():
    s1 = R.contrainte_flexion_mpa(1000, 50, 100, 1000, "centree")
    assert s1 == pytest.approx(1000 * 1000 / 4 / (50 * 100**2 / 6))
    assert R.cs_flexion(1000, 50, 100, 1000, CHENE, "centree") == pytest.approx(40 / s1)
    assert R.fleche_mm(1000, 50, 100, 1000, CHENE, "console") > R.fleche_mm(1000, 50, 100, 1000, CHENE, "centree")


def test_tenon_et_tourillons():
    assert R.cs_tenon(1000, 20, 60, CHENE) > R.cs_tenon(2000, 20, 60, CHENE)
    from tantra.catalogues.fixations import fixation_par_nom
    assert R.nombre_tourillons(4500, fixation_par_nom("tourillon_10")) >= 2


def test_cintrage():
    assert R.rayon_cintrage_minimal_mm(1.5) == pytest.approx(150)


def test_axe_traversant_mode():
    cs, mode = R.cs_axe_traversant(3000, AXE_16, CHENE, 20, 2)
    assert cs > 0 and mode in ("cisaillement de l'axe", "portance du bois des joues")


def test_double_verrouillage_exige_deux_verrous_de_forme():
    v = R.verifier_double_verrouillage("x", 1500, [DOIGT_INDEXAGE_16, VERROU_CAME])
    assert not v[0].ok
    v = R.verifier_double_verrouillage("x", 1500, [DOIGT_INDEXAGE_16, GOUPILLE_CAPTIVE_12])
    assert all(x.ok for x in v)


def test_double_verrouillage_auto_enclenchement():
    v = R.verifier_double_verrouillage("x", 1500, [GOUPILLE_CAPTIVE_12, GOUPILLE_CAPTIVE_10])
    assert not [x for x in v if x.code == "x_auto_enclenchement"][0].ok


def test_verrou_dans_bois_limite_par_portance():
    r = resistance_verrou_dans_bois_n(DOIGT_INDEXAGE_12, CHENE, 10)
    assert r < DOIGT_INDEXAGE_12.resistance_caracteristique_n
    v = verifier_liaison_verrouillee("y", 1500, [DOIGT_INDEXAGE_12, GOUPILLE_CAPTIVE_10], CHENE, 3)
    assert any(not x.ok for x in v)


def test_deverrouillage_sous_charge():
    assert R.verifier_deverrouillage_sous_charge("t", 1500, DOIGT_INDEXAGE_16).ok
    assert not R.verifier_deverrouillage_sous_charge("t", 50, GOUPILLE_CAPTIVE_12).ok


@pytest.mark.parametrize("jeu,ok", [(5, True), (8, True), (12, False), (24, False), (25, True), (40, True)])
def test_pincement(jeu, ok):
    assert R.verifier_pincement("z", jeu).ok is ok


def test_effort_manoeuvre_et_telescope():
    assert R.effort_manoeuvre_n(10, 150, 300) == pytest.approx(10 * 9.81 / 2)
    assert R.effort_manoeuvre_n(10, 150, 300, assistance_nmm=1e9) == 0
    with pytest.raises(ValueError):
        R.effort_manoeuvre_n(1, 1, 0)
    assert R.recouvrement_telescope_ok(210, 70) and not R.recouvrement_telescope_ok(200, 70)


def test_etats():
    assert etat_depuis_code(1) == "CADRE" and etat_depuis_code("MEUBLE") == "MEUBLE"
    assert _salon.etat_depuis_code(0) == "SALON" and _salon.etat_depuis_code(1) == "REVELE"


def test_appui_compas():
    from tantra.grammaires._cadre import appui_compas
    assert appui_compas(940, 900, 78) is None          # contrefiche trop courte
    s = appui_compas(940, 940, 78)
    assert s == pytest.approx(2 * 940 * 0.2079, rel=1e-3)
    assert appui_compas(1000, 1000, 90) == pytest.approx(0, abs=1e-6) or appui_compas(1000, 1000, 90) is None
