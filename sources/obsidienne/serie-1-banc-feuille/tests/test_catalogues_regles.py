# -*- coding: utf-8 -*-
import os

import pytest

from equinox import regles
from equinox.catalogues import CATEGORIES, attaches, bois, garnissage, metaux
from equinox.parametres import Parametres

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _toutes_les_entrees():
    for cat in (bois.BOIS, garnissage.GARNISSAGES, metaux.METAUX, attaches.ATTACHES):
        for cle, ent in cat.items():
            yield cle, ent


def test_regles_declaratives_valides():
    p = Parametres()
    for cle, ent in _toutes_les_entrees():
        assert "regles" in ent, cle
        for r in ent["regles"]:
            assert r["calcul"] in regles.CALCULS, (cle, r)
            if r.get("cible"):
                assert p.meta(r["cible"]) is not None, (cle, r["cible"])


def test_bois_proprietes_et_sources():
    for cle, ent in bois.BOIS.items():
        for champ in ("densite", "module_elasticite", "resistance_flexion", "aptitude_cintrage", "source"):
            assert champ in ent, (cle, champ)
        assert 400 < ent["densite"] < 900 and 8000 < ent["module_elasticite"] < 16000
    assert bois.BOIS["frene"]["module_elasticite"] == 12310.0


def test_nom_tissu_krypton_partout():
    assert "tissu_krypton" in garnissage.GARNISSAGES
    assert "Krypton" in garnissage.GARNISSAGES["tissu_krypton"]["nom"]
    for dossier, _, fichiers in os.walk(RACINE):
        if ".pytest_cache" in dossier or "__pycache__" in dossier:
            continue
        for f in fichiers:
            if f.endswith((".py", ".md", ".json")):
                with open(os.path.join(dossier, f), encoding="utf-8") as fh:
                    assert ("kr" + "ylon") not in fh.read().lower(), f


def test_bois_moins_rigide_augmente_sections():
    q, ajust = regles.changer_materiau(Parametres(), "bois", "erable_sycomore")
    assert q.get("bois.section_noeud") > 50.0 and q.get("bois.section_extremite") > 30.0
    assert q.get("jonctions.longueur_insert") == 25.0  # densite < 650
    assert q.get("jonctions.epaisseur_tenon") == round(q.get("bois.section_noeud") / 3.0)
    assert "rigidite" in regles.rapport(ajust)


def test_bois_plus_rigide_conserve_sections():
    q, _ = regles.changer_materiau(Parametres(), "bois", "hetre")
    assert q.get("bois.section_noeud") == 50.0 and q.get("bois.section_extremite") == 30.0


def test_imposes_bloques_sur_demande():
    q, ajust = regles.changer_materiau(Parametres(), "bois", "erable_sycomore", forcer_imposes=False)
    assert q.get("bois.section_noeud") == 50.0
    assert any(a.statut == "bloque_impose" and a.chemin == "bois.section_noeud" for a in ajust)


def test_rayon_cintrage_vapeur():
    p = Parametres({"bois": {"methode_cintrage": "vapeur"}})
    q, ajust = regles.changer_materiau(p, "bois", "erable_sycomore")
    assert q.get("bois.rayon_courbure_min") >= 10.0 * q.get("bois.section_noeud")


def test_lest_et_inox():
    _, ajust = regles.changer_materiau(Parametres(), "lest", "grenaille_acier")
    assert any(a.statut == "alerte" and "mm de tube" in a.raison for a in ajust)
    q, ajust = regles.changer_materiau(Parametres(), "inox", "inox_304")
    assert q.get("inox.diametre_axe_pivot") >= 16.0
    assert any("chlor" in a.raison for a in ajust)


def test_categorie_inconnue():
    with pytest.raises(KeyError):
        regles.changer_materiau(Parametres(), "bois", "balsa")
    assert set(CATEGORIES) == {"bois", "garnissage", "inox", "laiton", "lest"}
