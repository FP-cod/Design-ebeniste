# -*- coding: utf-8 -*-
"""Fixtures pytest : racine du projet dans sys.path + mock de l'API Fusion (repris d'Equinox)."""

import os
import sys
import types
from unittest import mock

import pytest

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

WORKSPACE = os.environ.get("GAMME_CUIR_WORKSPACE", "/workspace")


class PointFactice(object):
    """Remplace adsk.core.Point3D : garde les coordonnees (en cm)."""

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __repr__(self):
        return "P(%g, %g, %g)" % (self.x, self.y, self.z)


def _configurer_composant(comp):
    sketch = comp.sketches.add.return_value
    sketch.profiles.count = 2
    sketch.profiles.item.return_value.profileLoops.count = 2
    sketch.sketchCurves.count = 0
    feat = comp.features.extrudeFeatures
    feat.addSimple.return_value.bodies.item.return_value.edges.count = 12


@pytest.fixture
def adsk_mock(monkeypatch, tmp_path):
    """Installe un faux paquet ``adsk`` (core, fusion) ; HOME redirige (rapport ecrit dans tmp)."""
    monkeypatch.setenv("HOME", str(tmp_path))
    points = []
    core = mock.MagicMock(name="adsk.core")
    fusion = mock.MagicMock(name="adsk.fusion")

    def creer_point(x, y, z):
        p = PointFactice(x, y, z)
        points.append(p)
        return p
    core.Point3D.create.side_effect = creer_point
    core.ValueInput.createByReal.side_effect = lambda v: ("reel_cm", v)
    core.ValueInput.createByString.side_effect = lambda s: ("expr", s)

    design = mock.MagicMock(name="design")
    params_existants = {}

    def ajouter(nom, valeur, unite, commentaire):
        param = mock.MagicMock(name=nom)
        param.expression = valeur[1]
        param.unit = unite
        param.comment = commentaire
        params_existants[nom] = param
        return param
    design.userParameters.itemByName.side_effect = lambda nom: params_existants.get(nom)
    design.userParameters.add.side_effect = ajouter
    design.appearances.itemByName.return_value = None  # force la copie depuis la bibliotheque
    racine = design.rootComponent
    comp = racine.occurrences.addNewComponent.return_value.component
    comp.occurrences.addNewComponent.return_value.component = comp  # meme mock a tous les niveaux
    _configurer_composant(comp)
    _configurer_composant(racine)

    app = core.Application.get.return_value
    app.materialLibraries.itemByName.return_value.appearances.count = 3
    props = mock.MagicMock(name="appearanceProperties")
    props.count = 1
    for a in (app.materialLibraries.itemByName.return_value.appearances.itemByName.return_value,):
        a.appearanceProperties = props
    design.appearances.addByCopy.return_value.appearanceProperties = props
    fusion.Design.cast.return_value = design
    paquet = types.ModuleType("adsk")
    paquet.core, paquet.fusion = core, fusion
    anciens = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
    sys.modules.update({"adsk": paquet, "adsk.core": core, "adsk.fusion": fusion})
    try:
        yield types.SimpleNamespace(core=core, fusion=fusion, design=design, app=app, comp=comp, points=points,
                                    params=params_existants, home=tmp_path)
    finally:
        for k, v in anciens.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
