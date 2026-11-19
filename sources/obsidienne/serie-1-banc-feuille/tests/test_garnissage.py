# -*- coding: utf-8 -*-
"""Revetements : une serie de tests par famille + selection famille/coloris + banc Flore."""

import pytest

from equinox import regles
from equinox.catalogues import garnissage as gc
from equinox.grammaires import banc_flore
from equinox.parametres import Parametres

CHAMPS = ("nom", "famille", "coloris", "coloris_defaut", "epaisseur_matiere", "epaisseur_plage", "abrasion",
          "abrasion_martindale", "cout_m2", "entretien", "epaisseur_rembourrage_recommandee", "methode_fixation",
          "finition_bords", "rayon_bord_min", "regles")


def _changer(cle, couleur=None, params=None):
    p = params or Parametres.pour_typologie("banc_flore", json_utilisateur=False)
    if couleur:
        p.set("garnissage.couleur", couleur)
    return regles.changer_materiau(p, "garnissage", cle)


def _par_chemin(ajust):
    return {a.chemin: a for a in ajust if a.chemin}


def test_structure_de_toutes_les_entrees():
    for cle, ent in gc.GARNISSAGES.items():
        for champ in CHAMPS:
            assert champ in ent, (cle, champ)
        assert 1 <= ent["abrasion"] <= 10 and isinstance(ent["abrasion"], int)
        assert ent["cout_m2"] in gc.CATEGORIES_COUT
        assert ent["coloris_defaut"] in ent["coloris"]
        mini, maxi = ent["epaisseur_plage"]
        assert mini <= ent["epaisseur_matiere"] <= maxi
        assert ent["methode_fixation"] in gc.METHODES_FIXATION and ent["finition_bords"] in gc.FINITIONS_BORDS
        assert not any("prix" in k or k.endswith("_eur") for k in ent)  # pas de prix invente


def test_echelle_abrasion_coherente():
    attendu = {"cuir_vegan": "moyenne", "cuir_classique_pleine_fleur": "elevee", "tissu_krypton": "elevee",
               "cuir_synthetique_hq": "tres_elevee"}
    for cle, qualif in attendu.items():
        mini, maxi = gc.ECHELLE_ABRASION[qualif]
        assert mini <= gc.GARNISSAGES[cle]["abrasion"] <= maxi, cle


def test_cuir_vegan():
    ent = gc.GARNISSAGES["cuir_vegan"]
    assert ent["coloris"] == ["noir", "blanc", "cognac", "vert_olive", "bordeaux"]
    assert ent["epaisseur_plage"] == (1.2, 1.5) and ent["cout_m2"] == "moyen" and "facile" in ent["entretien"]
    assert "veritable" in ent["nom"]
    q, aj = _changer("cuir_vegan")
    assert q.get("garnissage.epaisseur_rembourrage") == 35.0
    assert q.get("dimensions.hauteur_structure") == 700.0 - 35.0 - 18.0
    assert "+ 5 mm" in _par_chemin(aj)["garnissage.epaisseur_rembourrage"].raison


def test_cuir_vegan_rembourrage_relatif_et_non_code_en_dur(monkeypatch):
    ref = gc.GARNISSAGES["cuir_classique_pleine_fleur"]
    monkeypatch.setitem(ref, "epaisseur_rembourrage_recommandee", 32.0)
    q, _ = _changer("cuir_vegan")
    assert q.get("garnissage.epaisseur_rembourrage") == 37.0


def test_cuir_classique_et_alias():
    ent = gc.GARNISSAGES["cuir_classique_pleine_fleur"]
    assert ent["coloris"] == ["noir", "cognac", "havane", "vert_bouteille", "bleu_nuit"]
    assert ent["coloris_defaut"] == "cognac" and ent["cout_m2"] == "eleve" and "patine" in ent["entretien"]
    assert ent["epaisseur_plage"] == (1.5, 2.0)
    assert gc.GARNISSAGES["cuir_pleine_fleur"] is ent and "cuir_pleine_fleur" in gc.GARNISSAGES
    assert "cuir_pleine_fleur" not in list(gc.GARNISSAGES)
    q, _ = _changer("cuir_vegan")
    r, aj = regles.changer_materiau(q, "garnissage", "cuir_pleine_fleur")  # ancienne cle acceptee
    assert r.get("garnissage.materiau") == "cuir_classique_pleine_fleur"
    assert r.get("garnissage.methode_fixation") == "agrafage_sous_plateau"
    assert r.get("garnissage.finition_bords") == "ourlets_cousus"
    assert r.get("garnissage.epaisseur_rembourrage") == 30.0
    assert Parametres({"garnissage": {"materiau": "cuir_pleine_fleur"}}).erreurs() == []


def test_tissu_krypton():
    ent = gc.GARNISSAGES["tissu_krypton"]
    assert "Krypton" in ent["nom"] and "velours cotele renforce" in ent["nom"]
    assert ent["coloris"] == ["noir", "gris_anthracite", "bordeaux", "bleu_marine"]
    assert ent["epaisseur_plage"] == (2.0, 3.0) and ent["cout_m2"] == "bas_moyen" and "lavable" in ent["entretien"]
    q, aj = _changer("tissu_krypton")
    assert q.get("garnissage.epaisseur_rembourrage") == 40.0
    assert q.get("garnissage.methode_fixation") == "agrafage_ou_scratch"
    assert q.get("garnissage.couleur") == "noir"  # cognac indisponible -> coloris par defaut, signale
    assert _par_chemin(aj)["garnissage.couleur"].statut == "modifie_impose"
    assert _par_chemin(aj)["dimensions.hauteur_structure"].apres == 642.0
    alertes = [a.raison for a in aj if a.statut == "alerte"]
    assert any("pas de couture apparente" in m for m in alertes)  # banc Flore : coutures sur courbes
    assert any(m.startswith("Recommandation") for m in alertes)


def test_tissu_krypton_sans_courbes_cousues():
    p = Parametres.pour_typologie("tabouret", json_utilisateur=False)
    assert p.get("garnissage.coutures_sur_courbes") is False
    _, aj = _changer("tissu_krypton", params=p)
    assert not any("couture apparente" in a.raison for a in aj if a.statut == "alerte")


def test_cuir_synthetique_hq():
    ent = gc.GARNISSAGES["cuir_synthetique_hq"]
    assert ent["coloris"] == ["noir", "cognac", "gris"] and ent["epaisseur_plage"] == (1.0, 1.2)
    assert ent["abrasion"] >= 9 and ent["cout_m2"] == "moyen" and "desinfectant" in ent["desinfection"]
    assert ent["compatible_toutes_geometries"] is True
    q, aj = _changer("cuir_synthetique_hq")
    assert q.get("garnissage.methode_fixation") == "collage_et_agrafage"
    assert q.get("garnissage.epaisseur_rembourrage") == 30.0
    assert "dimensions.hauteur_structure" not in _par_chemin(aj)  # rembourrage inchange
    assert gc.GARNISSAGES["cuir_synthetique_pu"] is ent  # ancienne cle


def test_validation_coloris_par_famille():
    p = Parametres({"garnissage": {"materiau": "tissu_krypton", "couleur": "cognac"}})
    pbs = [x for x in p.erreurs() if x.chemin == "garnissage.couleur"]
    assert pbs and "gris_anthracite" in pbs[0].message
    assert Parametres({"garnissage": {"materiau": "tissu_krypton", "couleur": "bleu_marine"}}).erreurs() == []
    assert any(x.chemin == "garnissage.materiau" for x in Parametres({"garnissage": {"materiau": "lin"}}).erreurs())
    with pytest.raises(ValueError):
        banc_flore.concevoir(overrides={"garnissage.materiau": "cuir_vegan", "garnissage.couleur": "gris"})


@pytest.mark.parametrize("cle,couleur,rembourrage", [
    ("cuir_classique_pleine_fleur", "cognac", 30.0), ("cuir_vegan", "vert_olive", 35.0),
    ("tissu_krypton", "gris_anthracite", 40.0), ("cuir_synthetique_hq", "gris", 30.0)])
def test_banc_flore_assise_constante(cle, couleur, rembourrage):
    plan = banc_flore.concevoir(overrides={"garnissage.materiau": cle, "garnissage.couleur": couleur})
    p = plan.params
    assert p.get("garnissage.epaisseur_rembourrage") == rembourrage
    hs = 700.0 - rembourrage - 18.0
    assert p.get("dimensions.hauteur_structure") == hs
    mousse = plan.composant("plateau").primitives[1]
    assert abs(max(z for _, _, z in mousse.points_3d(True)) - 700.0) < 1e-6
    ref = banc_flore.concevoir().repere["pieds"]["AR_G"]["noeud"]
    noeud = plan.repere["pieds"]["AR_G"]["noeud"]
    assert abs((ref[2] - noeud[2]) - (rembourrage - 30.0)) < 0.01  # (x cos 2 deg) la structure descend du surplus de mousse
    if rembourrage != 30.0:
        aj = [a for a in plan.ajustements if a.chemin == "dimensions.hauteur_structure"]
        assert aj and aj[0].avant == 652.0 and aj[0].apres == hs and "assise maintenue" in aj[0].raison
