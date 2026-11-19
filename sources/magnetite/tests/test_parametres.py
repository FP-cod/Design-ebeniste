# -*- coding: utf-8 -*-
import json
import os

import pytest

from gamme_cuir.parametres import CHEMIN_DEFAUTS, CHEMIN_JSON, Parametres, charger_schema

from conftest import WORKSPACE


def test_defauts_valides():
    p = Parametres(json_utilisateur=False)
    assert p.valider() == []


def test_chaque_parametre_documente():
    for chemin, m, v in Parametres(json_utilisateur=False).feuilles():
        assert m["role"] and m["justification"], chemin
        assert m["statut"] in ("impose", "a_valider", "derive", "libre"), chemin
        assert "unite" in m, chemin
        if m["unite"] in ("mm", "N", "") and not isinstance(v, (dict, bool)):
            assert "plage" in m, "%s : plage manquante" % chemin
            assert m["plage"][0] <= v <= m["plage"][1], chemin
        if m["unite"] == "texte" and chemin not in ("gamme.nom", "gamme.prefixe_fusion"):
            assert m.get("choix"), "%s : choix manquants" % chemin
            assert v in m["choix"], chemin


def test_sources_pointent_vers_des_fichiers_reels():
    if not os.path.isdir(os.path.join(WORKSPACE, "equinox")):
        pytest.skip("gammes meubles absentes")
    for chemin, m, _ in Parametres(json_utilisateur=False).feuilles():
        if m.get("source"):
            fichier = m["source"].split(" ")[0]
            assert os.path.exists(os.path.join(WORKSPACE, fichier)), (chemin, fichier)


@pytest.mark.parametrize("membre", ["poignet", "cheville", "cou"])
def test_tailles_croissantes_et_plages_contigues(membre):
    p = Parametres(json_utilisateur=False)
    tours = [p.tour(membre, t) for t in ("S", "M", "L", "XL")]
    assert tours == sorted(tours) and len(set(tours)) == 4
    plages = [p.plage_taille(membre, t) for t in ("S", "M", "L", "XL")]
    for (a0, a1), (b0, b1) in zip(plages, plages[1:]):
        assert b0 <= a1, "trou entre les plages %s et %s" % ((a0, a1), (b0, b1))


def test_epaisseurs_et_classes():
    p = Parametres(json_utilisateur=False)
    assert p.get("cuir.classes_epaisseur") == {"fine": [2.0, 2.5], "moyenne": [3.0, 3.5], "forte": [4.0, 5.0]}
    assert p.classe_epaisseur(2.2) == "fine" and p.classe_epaisseur(3.5) == "moyenne"
    assert p.classe_epaisseur(4.5) == "forte" and p.classe_epaisseur(2.8) is None
    assert p.epaisseur_totale() == pytest.approx(3.5 + 4.0 + 1.2)
    assert p.epaisseur_cuir_seul() == pytest.approx(4.7)
    p.set("cuir.epaisseur_exterieure", 2.8)
    assert any(x.niveau == "ALERTE" and "classes" in x.message for x in p.valider())


def test_points_par_cm():
    p = Parametres(json_utilisateur=False)
    assert p.points_par_cm() == pytest.approx(10 / 3.2)


@pytest.mark.parametrize("surcharge,mot", [
    ({"cuir.epaisseur_exterieure": 9.0}, "hors plage"),
    ({"finition.teinte": "rose_fluo"}, "hors choix"),
    ({"ardillon.nb_trous": 4}, "impair"),
    ({"cuir.nb_couches": 2}, "rembourrage"),
    ({"securite.jeu_doigt": 5.0}, "hors plage"),
    ({"cuir.rembourrage": "oui"}, "booleen"),
    ({"anneau_d.largeur_patte": 35.0, "sangles.largeur_menotte_poignet": 30.0}, "patte plus large"),
])
def test_validation_refuse(surcharge, mot):
    erreurs = Parametres(surcharge, json_utilisateur=False).erreurs()
    assert erreurs and any(mot in e.message for e in erreurs), erreurs


def test_cle_inconnue():
    with pytest.raises(KeyError):
        Parametres({"cuir.inexistant": 1}, json_utilisateur=False)
    with pytest.raises(KeyError):
        Parametres(json_utilisateur=False).get("pas_de_point")


def test_surcharges_imbriquees_et_copie():
    p = Parametres({"finition": {"teinte": "noir"}}, json_utilisateur=False)
    q = p.copie()
    q.set("finition.teinte", "tan")
    assert p.get("finition.teinte") == "noir" and q.get("finition.teinte") == "tan"


def test_json_utilisateur_et_aller_retour(tmp_path):
    with open(CHEMIN_JSON, encoding="utf-8") as f:
        assert "surcharges" in json.load(f)
    p = Parametres({"finition.teinte": "havane"}, json_utilisateur=False)
    chemin = tmp_path / "p.json"
    p.vers_json(str(chemin))
    q = Parametres(json.loads(chemin.read_text(encoding="utf-8"))["surcharges"], json_utilisateur=False)
    assert q.get("finition.teinte") == "havane" and q.valider() == []
    assert set(charger_schema(CHEMIN_DEFAUTS)) >= {"tailles", "sangles", "cuir", "couture", "jonctions", "securite"}


def test_parametres_exportables_en_mm():
    p = Parametres(json_utilisateur=False)
    noms = [n for n, *_ in p.parametres_exportables()]
    assert "gc_couture_pas_point" in noms and "gc_tailles_poignet_M" in noms
    assert all(e.endswith(" mm") for _, e, _, _ in p.parametres_exportables())
