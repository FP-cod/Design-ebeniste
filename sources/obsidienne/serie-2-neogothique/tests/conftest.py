# -*- coding: utf-8 -*-
import os
import sys

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fake_adsk  # noqa: E402


@pytest.fixture
def adsk_mock(monkeypatch):
    """Installe un faux adsk dans sys.modules le temps du test."""
    modules = dict(sys.modules)
    adsk, design, app = fake_adsk.installer(modules)
    for nom in ("adsk", "adsk.core", "adsk.fusion"):
        monkeypatch.setitem(sys.modules, nom, modules[nom])
    return adsk, design, app


@pytest.fixture
def params():
    from neogothique.parametres import Parametres
    return Parametres.pour_typologie("entrave", json_utilisateur=False)
