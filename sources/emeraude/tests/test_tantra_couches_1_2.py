# -*- coding: utf-8 -*-
"""Couche 1 (paramètres) et couche 2 (catalogues, chiffrage)."""
import pytest

from tantra import parametres as P
from tantra.catalogues import couts, fixations, mecanismes, mousses
from tantra.fusion_outils import cm_vers_mm, deg_vers_rad, mm_vers_cm, point_mm_vers_cm


def test_conversion_cm_uniquement_dans_fusion_outils():
    assert mm_vers_cm(450) == 45.0
    assert cm_vers_mm(4.5) == 45.0
    assert point_mm_vers_cm((10, 20, 30)) == (1.0, 2.0, 3.0)
    assert deg_vers_rad(180) == pytest.approx(3.14159265)


def test_charges_et_securite():
    c = P.ParametresCharge()
    assert c.charge_service_ancrage_n == 1500
    assert c.coefficient_securite >= 3
    assert c.charge_rupture_visee_ancrage_n == pytest.approx(4500)
    assert c.charge_surface_service_n(2) == pytest.approx(2 * 1100 * 1.5)


def test_parametres_globaux_valides():
    r = P.PARAMETRES_DEFAUT.valider()
    assert all(s.niveau != P.NIVEAU_NON_CONFORME for s in getattr(r, "signalements", r))


def test_anthropometrie_sources_et_ordre():
    a = P.ANTHROPOMETRIE_DEFAUT
    assert "Pheasant" in P.SOURCE_ANTHROPOMETRIE
    for nom in ("hauteur_poplitee", "longueur_fesse_poplite"):
        m = getattr(a, nom)
        assert m.p5 < m.p50 < m.p95


def test_typologies_et_plages():
    assert len([t for t in P.TYPOLOGIES.values() if t.volet == P.VOLET_TANTRA]) >= 3
    t = P.typologie_par_nom("cadre_desserte_genoux")
    t.verifier("hauteur_cadre", 1150)
    with pytest.raises(ValueError):
        t.verifier("hauteur_cadre", 2000)
    with pytest.raises(KeyError):
        P.typologie_par_nom("inconnue")


def test_essences_caracteristiques():
    assert P.LAMELLE_HETRE.fm_k_mpa > P.CHENE.fm_k_mpa
    assert P.essence_par_nom("chene") is P.CHENE


def test_revetements_lavables():
    assert P.CUIR_COGNAC.lavable
    assert not P.revetement_par_nom("bouclette").lavable


def test_parametres_fusion_prefixe_et_noms_ascii():
    d = P.vers_parametres_fusion()
    assert len(d) > 20
    for nom, (val, unite, com) in d.items():
        assert nom.startswith("tan_")
        assert nom.isascii() and nom.replace("_", "").isalnum()
        assert com


def test_catalogues():
    assert fixations.fixation_par_nom("insert_ancre_m12").cotes_mm["longueur_encastrement"] == 60
    assert mousses.mousse_par_nom("mousse_hr55").prix_eur_m3 > 0
    v = mecanismes.verrou_par_nom("goupille_captive_12")
    assert v.resistance_caracteristique_n == pytest.approx(2 * 0.6 * 700 * 3.14159265 * 36, rel=1e-6)
    assert not mecanismes.verrou_par_nom("verrou_came").verrou_de_forme
    with pytest.raises(KeyError):
        mecanismes.axe_par_nom("axe_99")
    mv = couts.masses_volumiques()
    assert mv["chene"] == P.CHENE.masse_volumique_kg_m3 and "mousse_hr35" in mv


def test_catalogue_couts_date():
    assert "2026" in couts.CATALOGUE_COUTS.date
