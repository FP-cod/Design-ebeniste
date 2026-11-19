# -*- coding: utf-8 -*-
"""Tests hors Fusion des cadres de contention modulaires."""

import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import cadres.cadre_modulaire as cm
from cadres.cadre_modulaire import (
    calculer_cadre,
    efforts_hypotheses,
    matrice_compatibilite,
    contrainte_travée_simple,
    positions_ports,
    TYPOLOGIES,
    ABOUTISSANTS_MATRICE,
    ANCRAGES_MEUBLES_MATRICE,
)
from catalogues.jonctions_cadre import cotes_tenon, JONCTIONS
from common.params_globaux import Parametres, G


def test_module_sans_import_adsk():
    src = Path(cm.__file__).read_text(encoding="utf-8")
    tete, _, _ = src.partition("def construire_fusion")
    for ligne in tete.splitlines():
        s = ligne.strip()
        if s.startswith("import adsk") or s.startswith("from adsk"):
            raise AssertionError("import adsk au niveau module : %s" % ligne)


def test_efforts_chiffres_hypotheses():
    e = efforts_hypotheses()
    assert e["masse_kg"] == 120.0
    assert e["k_dyn"] == 2.0
    assert e["cs_ancrage"] == 3.0
    assert e["poids_N"] == pytest.approx(120.0 * G)
    # F_ret = k_dyn × 0,5 × m × g = 1177,2 N
    assert e["F_retenue_N"] == pytest.approx(1177.2)
    # F_susp = k_dyn × m × g = 2354,4 N
    assert e["F_suspension_N"] == pytest.approx(2354.4)
    # Poussée nominale validée 400 N × k_dyn 2 = 800 N (CS 3 → 2400 N)
    assert e["poussee_service_N"] == 400.0
    assert e["F_poussee_dyn_N"] == 800.0
    assert e["F_retenue_calcul_CS3_N"] == pytest.approx(1177.2 * 3)
    assert e["F_suspension_calcul_CS3_N"] == pytest.approx(2354.4 * 3)
    assert e["F_poussee_calcul_CS3_N"] == 2400.0
    assert "hypothèse" in e["hypotheses"].lower() or "hypothes" in e["hypotheses"].lower() or "Hypoth" in e["hypotheses"]


def test_trois_typologies_et_ports():
    for typ in TYPOLOGIES:
        p = Parametres()
        p.set("cadre_modulaire.typologie", typ)
        res = calculer_cadre(p)
        assert res["typologie"] == typ
        assert res["modification_meuble"] is False
        assert len(res["ports"]) >= 1
        assert any("vac_u_lock" in pr for pr in res["ports"])
        noms = {s["nom"] for s in res["solides"]}
        assert any("plot" in n for n in noms)
        # Vérif flexion présente.
        assert any(v["nom"].startswith("flexion") for v in res["verifications"])


def test_support_batiment_todo():
    p = Parametres()
    assert p.get("cadre_modulaire.capacite_support_mur") is None
    assert p.get("cadre_modulaire.capacite_support_plafond") is None
    assert p.get("cadre_modulaire.entraxe_solives") is None
    assert p.meta("cadre_modulaire.capacite_support_plafond").statut == "todo"
    p.set("cadre_modulaire.typologie", "poutre_suspendue")
    res = calculer_cadre(p)
    by = {v["nom"]: v for v in res["verifications"]}
    assert by["support_plafond_connu"]["ok"] is False
    assert res["todos"]
    p2 = Parametres()
    p2.set("cadre_modulaire.typologie", "cadre_mural")
    res2 = calculer_cadre(p2)
    by2 = {v["nom"]: v for v in res2["verifications"]}
    assert by2["support_mur_connu"]["ok"] is False


def test_tenon_regle_equinox():
    # section 80 → tenon 80/3, mortaise 0,8×80
    c = cotes_tenon(80.0, 80.0)
    assert c["tenon_epaisseur_mm"] == pytest.approx(80.0 / 3.0)
    assert c["mortaise_profondeur_mm"] == pytest.approx(64.0)
    for cle in ("tenon_mortaise", "queue_d_aronde", "tenon_clavete", "raccord_metallique"):
        assert cle in JONCTIONS
    assert JONCTIONS["tenon_mortaise"]["demontable"] is False
    assert JONCTIONS["tenon_clavete"]["demontable"] is True
    assert JONCTIONS["raccord_metallique"]["demontable"] is True
    # Queue d'aronde : pas de CMU inventée.
    assert JONCTIONS["queue_d_aronde"]["capacite_service_N"] is None


def test_flexion_formule():
    r = contrainte_travée_simple(2354.4, 1800.0, 80.0, 80.0)
    # M = F L / 4 ; W = b h² / 6 ; σ = M/W ≈ 12,4 MPa < 14
    assert r["M_Nmm"] == pytest.approx(2354.4 * 1800.0 / 4.0)
    assert r["sigma_mpa"] == pytest.approx(r["M_Nmm"] / r["W_mm3"])
    assert r["sigma_mpa"] < 14.0


def test_matrice_complete():
    m = matrice_compatibilite()
    for typ in TYPOLOGIES:
        for a in ABOUTISSANTS_MATRICE:
            c = m["aboutissants"][typ][a]
            assert c["statut"] in m["statuts"]
            assert c["note"]
        for g in ANCRAGES_MEUBLES_MATRICE:
            c = m["meubles"][typ][g]
            assert c["statut"] in m["statuts"]
            assert c["note"]
    # Décisions clés du brief.
    assert m["aboutissants"]["cadre_sol"]["sex_machine_mecanique"]["statut"] == "compatible"
    assert m["aboutissants"]["poutre_suspendue"]["sex_machine_mecanique"]["statut"] == "incompatible"
    assert m["aboutissants"]["poutre_suspendue"]["collecteur_urine"]["statut"] == "incompatible"
    # Incognito : discrétion limitante, pouf non ciblé.
    inc = m["meubles"]["cadre_sol"]["incognito"]["note"].lower()
    assert "pouf" in inc and "visible" in inc


def test_positions_ports_dans_la_membrure():
    xs = positions_ports(1200.0, 200.0, 80.0)
    assert xs
    assert min(xs) >= 80.0 - 1e-9
    assert max(xs) <= 1200.0 - 80.0 + 1e-9
