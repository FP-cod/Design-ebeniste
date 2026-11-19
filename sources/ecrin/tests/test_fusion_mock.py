# -*- coding: utf-8 -*-
"""Construction Fusion simulee (faux paquet adsk, cf. conftest)."""
import importlib
import os
import sys

import pytest

from rangement import fusion_outils as FO
from rangement.grammaires import ratelier_mural as RM


def test_cm():
    assert FO.cm(25.4) == pytest.approx(2.54)


def test_constructeur_un_corps_par_primitive(adsk_mock):
    plan = RM.concevoir(json_utilisateur=False)
    c = FO.Constructeur(adsk_mock.design)
    c.construire(plan)
    assert not c.erreurs
    assert c.nb_corps == len(list(plan.primitives())) > 0
    # coordonnees passees a Fusion en cm : un ratelier de < 2 m de haut reste sous 200 cm
    assert adsk_mock.points and max(abs(v) for p in adsk_mock.points for v in (p.x, p.y, p.z)) < 200.0
    feats = adsk_mock.comp.features.extrudeFeatures
    assert feats.createInput.return_value.setSymmetricExtent.called


def test_plan_decale_respecte_le_signe_de_la_normale(adsk_mock):
    c = FO.Constructeur(adsk_mock.design)
    comp = adsk_mock.comp
    comp.xZConstructionPlane.geometry.normal.y = -1.0
    c.plan_decale(comp, "y", 50.0)
    arg = comp.constructionPlanes.createInput.return_value.setByOffset.call_args[0][1]
    assert arg == ("reel_cm", pytest.approx(-5.0))


def test_executer_cree_parametres_et_rapport(adsk_mock, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    res = FO.executer(None, lambda: RM.concevoir(json_utilisateur=False), "test")
    assert res is not None
    msg = adsk_mock.app.userInterface.messageBox.call_args[0][0]
    assert "construit" in msg
    assert "ran_ports_pas_ports" in adsk_mock.params
    assert (tmp_path / "rangement_rapport_ratelier_mural.txt").exists()


def test_executer_sans_design(adsk_mock):
    adsk_mock.fusion.Design.cast.return_value = None
    assert FO.executer(None, RM.concevoir, "test") is None
    assert "ouvrir un design" in adsk_mock.app.userInterface.messageBox.call_args[0][0]


def test_rapport_texte():
    txt = FO.rapport_texte(RM.concevoir(json_utilisateur=False))
    assert "Verifications" in txt and "Jonctions" in txt and "TODO" in txt.upper()


def test_script_fusion_enveloppe(adsk_mock, monkeypatch, tmp_path):
    racine = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dossier = os.path.join(racine, "scripts_fusion", "RangementRatelierMural")
    assert os.path.exists(os.path.join(dossier, "RangementRatelierMural.manifest"))
    monkeypatch.setenv("HOME", str(tmp_path))
    sys.path.insert(0, dossier)
    try:
        mod = importlib.import_module("RangementRatelierMural")
        mod.run(None)
    finally:
        sys.path.remove(dossier)
        sys.modules.pop("RangementRatelierMural", None)
    assert "construit" in adsk_mock.app.userInterface.messageBox.call_args[0][0]
