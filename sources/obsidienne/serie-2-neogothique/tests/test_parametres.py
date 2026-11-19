# -*- coding: utf-8 -*-
import json
import re

import pytest

from neogothique.parametres import Parametres, ErreurParametres, fusion_profonde, tableau_markdown


def test_defauts_valides(params):
    assert [p for p in params.valider() if p.niveau == "erreur"] == []


def test_override_typologie_noyer():
    assert Parametres().get("bois.essence") == "chene"
    assert Parametres.pour_typologie("entrave", json_utilisateur=False).get("bois.essence") == "noyer"


def test_fusion_profonde_ne_mute_pas():
    base = {"a": {"b": 1, "c": 2}}
    res = fusion_profonde(base, {"a": {"b": 5}})
    assert res == {"a": {"b": 5, "c": 2}} and base["a"]["b"] == 1


def test_acces_par_chemin_et_overrides_pointes(params):
    q = Parametres.pour_typologie("entrave", {"cremaillere.pas": 30.0, "entrave": {"pied": {"section": "octogonal"}}},
                                  json_utilisateur=False)
    assert q.get("cremaillere.pas") == 30.0
    assert q.get("entrave.pied.section") == "octogonal"
    assert q.get("entrave.pied.cote") == 100.0  # fusion profonde : voisins conserves
    with pytest.raises(KeyError):
        params.get("inexistant.chemin")
    with pytest.raises(KeyError):
        params.set("inexistant.chemin", 1)


def test_hauteur_cran(params):
    assert params.hauteur_cran(0) == 300.0
    assert params.hauteur_cran(6) == 450.0
    assert params.nombre_positions() == 7
    assert params.debattement() == 150.0


def test_convention_crans_incoherente():
    q = Parametres.pour_typologie("entrave", {"cremaillere.nombre_crans": 6}, json_utilisateur=False)
    assert any(p.chemin == "cremaillere.nombre_crans" and p.niveau == "erreur" for p in q.valider())
    # 6 intervalles de 25 mm en convention 'intervalles' -> coherent
    q.set("cremaillere.convention", "intervalles")
    assert not [p for p in q.valider() if p.niveau == "erreur"]
    assert q.nombre_positions() == 7


def test_bornes_et_choix():
    q = Parametres.pour_typologie("entrave", {"entrave.platine.epaisseur": 10.0, "entrave.pied.section": "rond"},
                                  json_utilisateur=False)
    chemins = {p.chemin for p in q.valider() if p.niveau == "erreur"}
    assert {"entrave.platine.epaisseur", "entrave.pied.section"} <= chemins
    with pytest.raises(ErreurParametres):
        q.verifier()


def test_coherences_ebenisterie():
    q = Parametres.pour_typologie("entrave", {"jonctions.tourillon_diametre": 12.0, "jonctions.ratio_tenon": 0.45},
                                  json_utilisateur=False)
    pbs = q.valider()
    assert any(p.chemin == "jonctions.tourillon_diametre" and p.niveau == "erreur" for p in pbs)
    assert any(p.chemin == "jonctions.ratio_tenon" and p.niveau == "alerte" for p in pbs)


def test_coherences_materiaux():
    q = Parametres.pour_typologie("entrave", {"ferrures.finition": "laiton_patine_vieilli",
                                              "garnissage.cuir_manilles": "cuir_harnais_noir",
                                              "bois.finition": "fumage_ammoniac"}, json_utilisateur=False)
    chemins = {p.chemin for p in q.valider() if p.niveau == "erreur"}
    assert "ferrures.finition" in chemins          # finition laiton sur fer
    assert "bois.finition" in chemins              # fumage sur noyer
    assert "garnissage.coloris" not in chemins     # noir dispo en harnais


def test_hauteurs_incoherentes():
    q = Parametres.pour_typologie("entrave", {"cremaillere.hauteur_mini": 460.0}, json_utilisateur=False)
    assert any(p.chemin == "cremaillere.hauteur_mini" for p in q.erreurs())


def test_pene_et_course():
    q = Parametres.pour_typologie("entrave", {"loquet.course": 15.0}, json_utilisateur=False)
    assert any(p.chemin == "loquet.course" for p in q.erreurs())


def test_noms_fusion_valides(params):
    lignes = params.parametres_exportables()
    assert len(lignes) > 60
    for nom, expr, unite, com in lignes:
        assert re.match(r"^[A-Za-z][A-Za-z0-9_]*$", nom), nom
        assert nom.startswith("neo_")
        assert len(com) <= 250
    noms = [l[0] for l in lignes]
    assert len(noms) == len(set(noms))
    d = {l[0]: l for l in lignes}
    assert d["neo_cremaillere_pas"][1] == "25 mm"
    assert d["neo_cremaillere_cran_courant"][2] == ""
    assert Parametres.nom_fusion("1.a b", "") == "p1_a_b"


def test_json_aller_retour(params, tmp_path):
    f = tmp_path / "p.json"
    params.vers_json(str(f))
    q = Parametres.depuis_json(str(f))
    assert q.valeurs == params.valeurs
    assert json.loads(f.read_text(encoding="utf-8"))["bois"]["essence"] == "noyer"


def test_chaque_parametre_documente():
    p = Parametres()
    for chemin, meta, val in p.feuilles():
        assert meta.role and len(meta.role) > 8, chemin
        assert meta.unite is not None
        assert meta.utilise_par, chemin
    assert tableau_markdown(p).count("\n") == len(list(p.feuilles())) + 1
