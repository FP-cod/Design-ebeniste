# -*- coding: utf-8 -*-
import json

import pytest

from equinox.parametres import OVERRIDES_TYPOLOGIE, Parametres, fusion_profonde


def test_valeurs_imposees_par_fabien():
    p = Parametres()
    attendu = {
        "dimensions.hauteur_assise": 700.0, "dimensions.longueur_plateau": 1150.0,
        "bois.essence": "frene", "bois.section_noeud": 50.0, "bois.section_extremite": 30.0, "bois.angle_splay": 7.0,
        "garnissage.inclinaison_plateau": 2.0, "garnissage.couleur": "cognac",
        "inox.diametre_tube_helice": 12.0, "inox.nombre_tours_helice": 2.0, "inox.crans_verrouillage": 2,
        "inox.diametre_oeillet": 8.0, "inox.epaisseur_plaque": 2.0, "laiton.diametre_capuchon": 40.0,
        "laiton.epaisseur_capuchon": 3.0, "traverse.cote_tube": 40.0, "traverse.lest_min": 15.0,
        "traverse.lest_max": 20.0, "ancrage.oeillets_bas": True, "ancrage.position_anneau": "mi_hauteur_traverse",
        "securite.charge_utilisateur": 120.0,
    }
    for chemin, valeur in attendu.items():
        assert p.get(chemin) == valeur, chemin
        assert p.meta(chemin).statut == "impose", chemin
    # 30 mm reste la valeur de reference (cuir classique) mais devient derivee de la famille
    assert p.get("garnissage.epaisseur_rembourrage") == 30.0
    assert p.meta("garnissage.epaisseur_rembourrage").statut == "derive"
    assert p.get("garnissage.materiau") == "cuir_classique_pleine_fleur"


def test_defauts_valides_et_tout_documente():
    p = Parametres()
    assert p.valider() == []
    for chemin, meta, val in p.feuilles():
        assert meta.role and meta.unite is not None, chemin
        assert meta.statut in ("impose", "a_valider", "derive", "libre")


def test_acces_par_chemin():
    p = Parametres()
    p.set("bois.section_noeud", 55.0)
    assert p["bois.section_noeud"] == 55.0
    assert p.get("inexistant.x", None) is None
    with pytest.raises(KeyError):
        p.get("bois.inexistant")
    with pytest.raises(KeyError):
        p.set("bois.inexistant", 1)


def test_bornes_et_coherences():
    p = Parametres({"bois": {"section_extremite": 60.0}, "traverse": {"lest_nominal": 25.0}})
    chemins = {pb.chemin for pb in p.erreurs()}
    assert "bois.section_extremite" in chemins and "traverse.lest_nominal" in chemins
    p = Parametres({"dimensions": {"hauteur_assise": 2000.0}})
    assert any("hors plage" in pb.message for pb in p.erreurs())
    p = Parametres({"garnissage": {"methode_fixation": "housse_amovible_zip"}})
    assert any("non admise" in pb.message for pb in p.erreurs())


def test_fusion_profonde_et_typologies():
    base = {"a": {"b": 1, "c": 2}}
    assert fusion_profonde(base, {"a": {"c": 3}}) == {"a": {"b": 1, "c": 3}}
    assert base["a"]["c"] == 2
    t = Parametres.pour_typologie("tabouret", json_utilisateur=False)
    assert t.get("dimensions.hauteur_assise") == OVERRIDES_TYPOLOGIE["tabouret"]["dimensions"]["hauteur_assise"]
    assert t.get("bois.section_noeud") == 50.0
    q = Parametres.pour_typologie("banc_flore", overrides={"bois.section_noeud": 52.0}, json_utilisateur=False)
    assert q.get("bois.section_noeud") == 52.0


def test_longueur_bassin_epaules():
    p = Parametres()
    assert p.longueur_plateau_effective() == 1150.0
    p.set("dimensions.mode_longueur", "bassin_epaules")
    assert p.longueur_plateau_effective() == 540.0 + 80.0 + 60.0


def test_json_aller_retour(tmp_path):
    p = Parametres({"bois": {"section_noeud": 51.0}})
    chemin = tmp_path / "p.json"
    p.vers_json(str(chemin))
    q = Parametres.depuis_json(str(chemin))
    assert q.get("bois.section_noeud") == 51.0
    assert json.loads(p.vers_json())["gamme"]["nom"] == "Equinox"


def test_noms_et_export_fusion(adsk_mock):
    p = Parametres()
    assert Parametres.nom_fusion("bois.section_noeud") == "eq_bois_section_noeud"
    exp = {n: (e, u, c) for n, e, u, c in p.parametres_exportables()}
    assert exp["eq_dimensions_hauteur_assise"][0] == "700 mm"
    assert exp["eq_bois_angle_splay"][:2] == ("7 deg", "deg")
    assert exp["eq_traverse_lest_min"][:2] == ("15 kg", "kg")
    assert "eq_garnissage_couleur" not in exp  # textes non exportes
    crees, maj = p.exporter_user_parameters(adsk_mock.design)
    assert len(crees) == len(exp) and maj == []
    assert adsk_mock.params["eq_dimensions_hauteur_assise"].comment.startswith("dimensions.hauteur_assise [impose")
    p.set("dimensions.hauteur_assise", 720.0)
    crees, maj = p.exporter_user_parameters(adsk_mock.design)
    assert crees == [] and "eq_dimensions_hauteur_assise" in maj
    assert adsk_mock.params["eq_dimensions_hauteur_assise"].expression == "720 mm"
