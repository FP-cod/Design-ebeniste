# -*- coding: utf-8 -*-
"""La documentation couvre tous les parametres et tous les systemes."""
import io
import os

from rangement import parametres as P
from rangement.catalogues import systemes
from rangement.grammaires import ratelier_mural

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _readme():
    with io.open(os.path.join(RACINE, "README.md"), encoding="utf-8") as f:
        return f.read()


def test_readme_documente_chaque_parametre():
    texte = _readme()
    manquants = [c for c, _ in P._iter_schema(P.SCHEMA) if "`%s`" % c not in texte]
    manquants += ["ratelier." + c for c, _ in P._iter_schema(ratelier_mural.SCHEMA_RATELIER)
                  if "`ratelier.%s`" % c not in texte]
    assert not manquants, "relancer outils/generer_docs.py : %s" % manquants


def test_readme_compromis_chaque_systeme():
    texte = _readme()
    assert not [k for k in systemes.SYSTEMES if "`%s`" % k not in texte]


def test_chaque_parametre_a_role_et_unite():
    for chemin, m in P._iter_schema(P.SCHEMA):
        assert m.role and m.unite is not None, chemin
        if m.statut == "repris":
            assert m.source, chemin
        if m.statut in ("a_valider", "todo"):
            assert m.justification or m.source, chemin
