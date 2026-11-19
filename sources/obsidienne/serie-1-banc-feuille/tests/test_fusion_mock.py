# -*- coding: utf-8 -*-
import importlib
import os
import sys

from equinox import fusion_outils
from equinox.grammaires import banc_flore, croix_saint_andre

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_conversion_cm():
    assert fusion_outils.cm(700) == 70.0 and fusion_outils.cm(12) == 1.2


def test_constructeur_banc_flore(adsk_mock):
    plan = banc_flore.concevoir()
    c = fusion_outils.Constructeur(adsk_mock.design)
    c.construire(plan)
    assert c.erreurs == []
    nb_prims = sum(len(x.primitives) for x in plan.composants)
    assert c.nb_corps == nb_prims
    # toutes les coordonnees passees a Point3D sont en cm (banc < 1,5 m -> < 150)
    assert adsk_mock.points and max(abs(p.x) for p in adsk_mock.points) < 150
    assert any(abs(p.z - 70.0) < 0.5 for p in adsk_mock.points)  # 700 mm -> 70 cm
    # rayon du balayage d'helice : 6 mm -> 0,6 cm
    rayons = [call.args[1] for call in adsk_mock.comp.sketches.add.return_value.sketchCurves.sketchCircles.addByCenterRadius.call_args_list]
    assert 0.6 in rayons
    assert adsk_mock.comp.features.sweepFeatures.add.called
    assert adsk_mock.comp.features.loftFeatures.add.called
    assert adsk_mock.comp.features.moveFeatures.add.called  # inclinaison 2 deg


def test_executer_run(adsk_mock):
    res = banc_flore.run(None)
    assert res is not None
    plan, constructeur = res
    ui = adsk_mock.app.userInterface
    assert ui.messageBox.called and "banc_flore construit" in ui.messageBox.call_args.args[0]
    assert "eq_dimensions_hauteur_assise" in adsk_mock.params


def test_executer_sans_design(adsk_mock):
    adsk_mock.fusion.Design.cast.return_value = None
    assert croix_saint_andre.run(None) is None
    assert "ouvrir un design" in adsk_mock.app.userInterface.messageBox.call_args.args[0]


def test_scripts_fusion_enveloppes(adsk_mock):
    dossier = os.path.join(RACINE, "scripts_fusion")
    for nom in sorted(os.listdir(dossier)):
        assert os.path.exists(os.path.join(dossier, nom, nom + ".manifest"))
        sys.path.insert(0, os.path.join(dossier, nom))
        try:
            mod = importlib.import_module(nom)
            mod.run(None)
        finally:
            sys.path.pop(0)
        msg = adsk_mock.app.userInterface.messageBox.call_args.args[0]
        assert "construit" in msg, (nom, msg[:300])
