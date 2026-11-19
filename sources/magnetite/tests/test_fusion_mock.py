# -*- coding: utf-8 -*-
import importlib
import os
import sys

from gamme_cuir import fusion_outils
from gamme_cuir.grammaires import menottes
from gamme_cuir.parametres import Parametres

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_conversion_cm():
    assert fusion_outils.cm(170) == 17.0 and fusion_outils.cm(3.2) == 0.32


def test_constructeur_menottes(adsk_mock):
    plan = menottes.concevoir(params=Parametres(json_utilisateur=False))
    c = fusion_outils.Constructeur(adsk_mock.design)
    c.construire(plan)
    assert c.erreurs == []
    assert c.nb_corps == len(plan.primitives("plaque")) + len(plan.primitives("cylindre"))
    assert c.nb_percages == len(plan.primitives("percage"))
    assert c.nb_points_couture == plan.cotes["nb_points_couture"]
    # coordonnees en cm : bande ~31 cm
    assert adsk_mock.points and max(abs(p.x) for p in adsk_mock.points) < 40
    assert any(abs(p.x - plan.cotes["longueur_developpee"] / 10.0) < 1e-6 for p in adsk_mock.points)
    ext = adsk_mock.comp.features.extrudeFeatures.addSimple
    ops = [call.args[2] for call in ext.call_args_list]
    assert adsk_mock.fusion.FeatureOperations.CutFeatureOperation in ops
    # rayon des trous d'ardillon : 4,5 mm -> 0,225 cm
    rayons = [call.args[1] for call in adsk_mock.comp.sketches.add.return_value.sketchCurves.sketchCircles
              .addByCenterRadius.call_args_list]
    assert 0.225 in rayons
    # apparences copiees et nommees selon la teinte / le metal
    noms = {call.args[1] for call in adsk_mock.design.appearances.addByCopy.call_args_list}
    assert "GammeCuir - cuir cognac" in noms and "GammeCuir - laiton_massif_cw510l" in noms
    assert adsk_mock.core.Color.create.called


def test_executer_run(adsk_mock):
    res = menottes.run(None)
    assert res is not None
    plan, constructeur = res
    msg = adsk_mock.app.userInterface.messageBox.call_args.args[0]
    assert "construit" in msg and "Echecs : 0" in msg
    assert "gc_couture_pas_point" in adsk_mock.params
    assert (adsk_mock.home / ("gamme_cuir_rapport_%s.txt" % plan.nom)).exists()


def test_executer_sans_design(adsk_mock):
    adsk_mock.fusion.Design.cast.return_value = None
    assert menottes.run(None) is None
    assert "ouvrir un design" in adsk_mock.app.userInterface.messageBox.call_args.args[0]


def test_erreur_attrapee(adsk_mock, monkeypatch):
    monkeypatch.setattr(menottes, "concevoir", lambda: 1 / 0)
    assert fusion_outils.executer(None, menottes.concevoir, "menottes") is None
    assert "erreur" in adsk_mock.app.userInterface.messageBox.call_args.args[0]


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
