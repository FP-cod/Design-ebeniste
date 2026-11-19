# -*- coding: utf-8 -*-
from neogothique.catalogues import BOIS, GARNISSAGE, METAUX, FINITIONS, PIVOTS, ATTACHES, COMPOSANTS, CATEGORIES, SELECTIONS
from neogothique.catalogues.attaches import dimensionner, JONCTIONS_ADMISES
from neogothique.parametres import Parametres
from neogothique import regles


def test_bois_champs_et_sources():
    for cle, e in BOIS.items():
        for champ in ("densite_kg_m3", "module_elasticite_mpa", "resistance_flexion_mpa",
                      "resistance_flexion_calcul_mpa", "compression_perp_mpa", "retrait_tangentiel_coef", "regles"):
            assert champ in e, (cle, champ)
        assert e["sources"]
        assert 500 < e["densite_kg_m3"] < 900
        assert e["resistance_flexion_calcul_mpa"] < e["resistance_flexion_mpa"]
    assert {"chene", "noyer", "chene_fume"} <= set(BOIS)


def test_garnissage_champs():
    for cle, e in GARNISSAGE.items():
        assert 1 <= e["resistance_abrasion"] <= 10
        assert "noir" in e["coloris"]
        assert e["cout_categorie"] in ("bas", "moyen", "eleve", "tres_eleve")
        assert e["entretien"] and e["usages"] and "regles" in e
        lo, hi = e["epaisseur_plage_mm"]
        assert lo <= e["epaisseur_mm"] <= hi


def test_metaux_laiton_moins_resistant():
    assert METAUX["laiton_mat"]["limite_elastique_mpa"] < METAUX["fer_forge_mat"]["limite_elastique_mpa"]
    for cle, f in FINITIONS.items():
        assert set(f["metaux"]) <= set(METAUX)
        assert 1 <= f["protection_corrosion"] <= 10
    assert METAUX["fer_forge_mat"]["finition_defaut"] in FINITIONS


def test_pivots_trois_options():
    assert set(PIVOTS) == {"axe_vertical_chape", "rotule", "charniere_basculante"}


def test_attaches_zero_vis():
    for cle, e in ATTACHES.items():
        assert e["vis_apparente"] is False
    for jonction, types_ in JONCTIONS_ADMISES.items():
        assert set(types_) <= set(ATTACHES)


def test_dimensionner_regle_du_tiers():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    d = dimensionner("tenon_traversant_cale", 63, 50, 63, p)
    assert d["tenon_epaisseur"] == 21 and d["tenon_longueur"] == 50
    t = dimensionner("tourillons", 22, 22, None, p)
    assert t["diametre"] <= 11 and t["profondeur"] == 2.5 * t["diametre"]
    k = dimensionner("tenon_traversant_clavete", 60, 90, 70, p)
    assert k["saillie"] >= 40 and k["clef_epaisseur"] >= 10


def test_regles_syntaxe_et_cibles():
    assert regles.verifier_catalogues() == []


def test_selections_couvrent_les_categories():
    assert set(SELECTIONS.values()) == set(CATEGORIES)
    p = Parametres()
    for chemin in SELECTIONS:
        assert p.meta(chemin) is not None, chemin


def test_composants_pilotes_par_parametres_existants():
    p = Parametres()
    for cle, comp in COMPOSANTS.items():
        for chemin in comp["pilote_par"]:
            assert p.meta(chemin) is not None, (cle, chemin)
