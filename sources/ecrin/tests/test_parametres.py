# -*- coding: utf-8 -*-
import json
import os

import pytest

from rangement import parametres as P, sources as S
from rangement.parametres import Parametres

from conftest import WORKSPACE


@pytest.mark.parametrize("typo", P.TYPOLOGIES)
def test_defauts_sans_erreur(typo):
    p = Parametres.pour_typologie(typo, json_utilisateur=False)
    assert p.erreurs() == []
    # la seule inconnue est le support mural (TODO, rien n'est invente)
    assert [x.chemin for x in p.valider() if x.niveau == "todo"] == ["pose.capacite_support_mur"]


def test_typologie_inconnue():
    with pytest.raises(KeyError):
        Parametres.pour_typologie("cheval_arcon")


def test_tracabilite_des_statuts():
    p = Parametres()
    for chemin, meta, val in p.feuilles():
        assert meta.statut in P.STATUTS, chemin
        assert meta.role, chemin
        if meta.statut == P.REP:
            assert meta.source and "/" in meta.source, "valeur reprise sans source : %s" % chemin
        if meta.statut == P.VAL:
            assert meta.justification, "valeur a valider sans justification : %s" % chemin
        if meta.statut == P.TODO:
            assert val is None, chemin
    assert len(p.repris()) >= 25 and len(p.a_valider()) >= 20


@pytest.mark.skipif(not os.path.isdir(os.path.join(WORKSPACE, "equinox")), reason="autres gammes absentes")
def test_sources_existent():
    for nom in dir(S):
        val = getattr(S, nom)
        if isinstance(val, str) and val.endswith(".py"):
            assert os.path.exists(os.path.join(WORKSPACE, val)), val


def test_plages_et_choix():
    p = Parametres.pour_typologie("ratelier_mural", {"panneaux.epaisseur_caisson": 5.0, "bois.essence": "teck"},
                                  json_utilisateur=False)
    chemins = {x.chemin for x in p.erreurs()}
    assert {"panneaux.epaisseur_caisson", "bois.essence"} <= chemins


def test_teinte_doit_exister_dans_la_famille():
    p = Parametres.pour_typologie("coffre", {"cuir.famille": "cuir_harnais_noir", "cuir.teinte": "cognac"},
                                  json_utilisateur=False)
    assert any(x.chemin == "cuir.teinte" for x in p.erreurs())
    p.set("cuir.teinte", "brun_fonce")
    assert p.erreurs() == []


def test_finitions_neogothique_reservees_au_chene():
    p = Parametres.pour_typologie("coffre", {"bois.essence": "frene", "bois.finition": "fumage_ammoniac"},
                                  json_utilisateur=False)
    assert any(x.chemin == "bois.finition" for x in p.erreurs())
    p.set("bois.essence", "chene_fume")
    assert p.erreurs() == []


def test_finition_metal_compatible():
    p = Parametres.pour_typologie("coffre", {"quincaillerie.finition_metal": "cire_noire"}, json_utilisateur=False)
    assert any(x.chemin == "quincaillerie.finition_metal" for x in p.erreurs())


def test_module_hauteur_multiple_du_pas():
    p = Parametres.pour_typologie("coffre", {"modules.module_hauteur": 300.0}, json_utilisateur=False)
    assert any(x.chemin == "modules.module_hauteur" and x.niveau == "alerte" for x in p.valider())


def test_overrides_typologie():
    p = Parametres.pour_typologie("armoire_verrouillable", json_utilisateur=False)
    assert p.get("discretion.niveau") == "invisible"
    assert p.get("systemes.serrure") == "serrure_electronique_rfid"
    assert Parametres.pour_typologie("coffre", json_utilisateur=False).get("systemes.porte") == "abattant_compas"


def test_json_defauts_a_jour():
    with open(P.CHEMIN_DEFAUTS, encoding="utf-8") as f:
        assert json.load(f) == P.valeurs_par_defaut(), "relancer outils/generer_docs.py"


def test_json_utilisateur(tmp_path, monkeypatch):
    chemin = tmp_path / "p.json"
    chemin.write_text(json.dumps({"commun": {"bois": {"essence": "noyer"}},
                                  "typologies": {"coffre": {"modules": {"hauteur_coffre": 460.0}}}}), encoding="utf-8")
    monkeypatch.setattr(P, "CHEMIN_JSON", str(chemin))
    p = Parametres.pour_typologie("coffre")
    assert p.get("bois.essence") == "noyer" and p.get("modules.hauteur_coffre") == 460.0
    assert Parametres.pour_typologie("ratelier_mural").get("modules.hauteur_coffre") == 440.0


def test_aller_retour_json():
    p = Parametres.pour_typologie("ratelier_mural", {"ports.pas_ports": 160.0}, json_utilisateur=False)
    q = Parametres.depuis_json(p.vers_json())
    assert q.get("ports.pas_ports") == 160.0


def test_export_noms_fusion():
    p = Parametres.pour_typologie("ratelier_mural", json_utilisateur=False)
    d = {n: (e, u) for n, e, u, c in p.parametres_exportables()}
    assert d["ran_ports_pas_ports"] == ("200 mm", "mm")
    assert d["ran_charges_charge_lineaire_barre"][1] == ""
    assert "ran_pose_capacite_support_mur" not in d          # None non exporte
    assert all(n.startswith("ran_") for n in d)
