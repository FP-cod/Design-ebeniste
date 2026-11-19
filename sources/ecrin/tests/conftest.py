# -*- coding: utf-8 -*-
"""Fixtures pytest : racine du projet dans sys.path + mock de l'API Fusion
(meme principe que equinox/tests/conftest.py)."""

import os
import sys
import types
from unittest import mock

import pytest

# Ne pas ecrire de __pycache__ dans les depots des autres gammes importes par les tests de reprise.
sys.dont_write_bytecode = True

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

#: Dossier contenant les autres gammes (pour les tests de reprise ; ignores s'il manque).
WORKSPACE = os.environ.get("RANGEMENT_WORKSPACE") or os.path.dirname(RACINE)


class PointFactice(object):
    """Remplace adsk.core.Point3D : garde les coordonnees (en cm)."""

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __repr__(self):
        return "P(%g, %g, %g)" % (self.x, self.y, self.z)


def _configurer_composant(comp):
    sketch = comp.sketches.add.return_value
    sketch.modelToSketchSpace.side_effect = lambda p: p
    sketch.profiles.count = 2
    sketch.profiles.item.return_value.profileLoops.count = 2
    comp.features.extrudeFeatures.add.return_value.bodies.item.return_value.edges.count = 12


@pytest.fixture
def adsk_mock():
    """Installe un faux paquet ``adsk`` (core, fusion) dans sys.modules."""
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

    def item_by_name(nom):
        return params_existants.get(nom)

    def ajouter(nom, valeur, unite, commentaire):
        param = mock.MagicMock(name=nom)
        param.expression, param.unit, param.comment = valeur[1], unite, commentaire
        params_existants[nom] = param
        return param
    design.userParameters.itemByName.side_effect = item_by_name
    design.userParameters.add.side_effect = ajouter
    racine = design.rootComponent
    comp = racine.occurrences.addNewComponent.return_value.component
    comp.occurrences.addNewComponent.return_value.component = comp  # meme mock a tous les niveaux
    _configurer_composant(comp)
    _configurer_composant(racine)

    app = core.Application.get.return_value
    fusion.Design.cast.return_value = design
    paquet = types.ModuleType("adsk")
    paquet.core, paquet.fusion = core, fusion
    anciens = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
    sys.modules.update({"adsk": paquet, "adsk.core": core, "adsk.fusion": fusion})
    try:
        yield types.SimpleNamespace(core=core, fusion=fusion, design=design, app=app, comp=comp, points=points,
                                    params=params_existants)
    finally:
        for k, v in anciens.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
