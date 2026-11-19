# -*- coding: utf-8 -*-
import pytest

from neogothique.parametres import Parametres, ErreurParametres
from neogothique.grammaires import entrave as E
from neogothique import regles


def calc(**ov):
    return E.calculer_entrave(Parametres.pour_typologie("entrave", {k.replace("__", "."): v for k, v in ov.items()},
                                                        json_utilisateur=False))


def test_calcul_par_defaut():
    r = calc()
    assert r.hauteur == 300.0 and r.cran == 0
    assert r.cotes["positions"] == 7 and r.cotes["debattement"] == 150.0
    assert r.cotes["course_crans"] == r.cotes["debattement"]
    assert r.cotes["pignon_dents"] == 16 and r.cotes["pignon_d_primitif"] == 48.0
    pl = r.solide("platine")
    assert pl.boite_englobante()[1][2] == pytest.approx(300.0)
    assert pl.boite_englobante()[1][0] - pl.boite_englobante()[0][0] == pytest.approx(800.0)


@pytest.mark.parametrize("cran", range(7))
def test_hauteur_pilotee_par_cran(cran):
    r = calc(cremaillere__cran_courant=cran)
    assert r.hauteur == 300.0 + 25.0 * cran
    zb = r.cotes["z_dessous_platine"]
    c = r.solide("coulisseau_AV_D").boite_englobante()
    assert c[1][2] == pytest.approx(zb)
    # le coulisseau reste dans le fourreau et au-dessus du fond de logement
    f = r.solide("fourreau_AV_D").boite_englobante()
    assert c[0][2] < f[1][2] and c[0][2] >= r.cotes["z_bas_coulisseau_min"] - 1e-6
    # le point de contact pignon/cremaillere est sur la denture a chaque cran
    assert c[0][2] + 10 <= r.cotes["z_arbre"] <= c[1][2] - 10
    # le pene du loquet tombe sur un trou de cran a chaque position
    bar = r.solide("cremaillere_calage_AV_D").boite_englobante()
    rel = r.cotes["z_loquet"] - bar[0][2]
    assert min(abs(rel - t) for t in r.cotes["trous_crans"]) < 1e-6


def test_cran_hors_plage():
    with pytest.raises(ErreurParametres):
        calc(cremaillere__cran_courant=7)
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    with pytest.raises(E.ErreurGeometrie):
        E.calculer_entrave(p, cran=9, strict=False)


def test_engrenement_coherent():
    r = calc()
    c = r.cotes
    assert c["x_arbre"] + c["pignon_d_primitif"] / 2.0 == pytest.approx(c["x_ligne_primitive"])
    pig = r.solide("pignon_AV_D").boite_englobante()
    fou = r.solide("fourreau_AV_D").boite_englobante()
    assert pig[1][0] < fou[0][0]                         # pignon hors du fourreau
    assert c["z_arbre"] + c["pignon_d_tete"] / 2 < c["z_dessous_platine_min"]
    assert c["course_par_tour"] == pytest.approx(150.796, rel=1e-3)


def test_section_octogonale():
    r = calc(entrave__pied__section="octogonal")
    assert r.cotes["coulisseau"] < calc().cotes["coulisseau"]
    f = r.solide("fourreau_AV_D")
    assert len(f.directions) == 4 and f.alesage is not None          # octogone = 4 tranches moulurees
    assert len(f.section_a(150.0)) == 8                                # section octogonale dans le fut
    r2 = calc(entrave__pied__section="octogonal", entrave__pied__cote=120.0)
    assert r2.cotes["coulisseau"] >= 58


def test_pied_trop_fin():
    with pytest.raises(E.ErreurGeometrie):
        calc(entrave__pied__section="octogonal", entrave__pied__cote=100.0,
             entrave__fourreau__paroi_diagonale_min=25.0)


def test_jonctions_regle_du_tiers_et_zero_vis():
    r = calc()
    j = {x["nom_jonction"]: x for x in r.jonctions}
    jc = j["coulisseau -> platine"]
    assert jc["tenon_epaisseur"] == pytest.approx(r.cotes["coulisseau"] / 3.0, abs=1.0)
    assert jc["tenon_longueur"] == r.cotes["e"]  # traversant
    assert j["fourreau -> semelle"]["tenon_epaisseur"] <= r.params.get("entrave.fourreau.paroi")
    assert j["demi-fourreaux (joues rainurees)"]["diametre"] <= r.params.get("entrave.fourreau.paroi") / 2
    for x in r.jonctions:
        assert "vis" not in x["type"]
    assert r.cotes["jeu_mortaise_oblongue"] >= r.cotes["dilatation_platine"]


def test_verifications_presentes_et_signalees():
    r = calc()
    ids = {v.ident for v in r.verifications}
    for i in ("renversement_x", "renversement_y", "glissement", "flexion_platine", "fleche_platine",
              "cisaillement_pene", "matage_cran", "dent_lewis", "torsion_arbre", "recouvrement", "axe_pivot"):
        assert i in ids
    assert r.verification("flexion_platine").ok
    assert r.verification("cisaillement_pene").ok
    # sans ancrage ni lest, 500 N x 1,5 a ~56 cm fait basculer l'Entrave : signale
    assert r.verification("renversement_y").niveau == "alerte"
    assert "UNIQUEMENT ancre" in r.verification("renversement_y").detail
    assert r.verification("recouvrement").niveau == "alerte"
    assert r.cotes["hauteur_mini_pour_recouvrement"] == 315.0


def test_sans_ancrage_insuffisant():
    r = calc(ancrage__anneaux_sol=False)
    assert r.verification("renversement_y").niveau == "insuffisant"
    assert r.insuffisances()


def test_lest_suffisant():
    r = calc(ancrage__anneaux_sol=False, ancrage__lest=80.0)
    assert r.verification("renversement_x").ok


def test_recouvrement_ok_si_hauteur_mini_relevee():
    r = calc(cremaillere__hauteur_mini=325.0, cremaillere__nombre_crans=6)
    assert r.verification("recouvrement").ok


def test_laiton_sans_regles_insuffisant_puis_corrige():
    p = Parametres.pour_typologie("entrave", {"ferrures.metal": "laiton_mat",
                                              "ferrures.finition": "laiton_brosse_vernis_mat"}, json_utilisateur=False)
    v = E.calculer_entrave(p).verification("axe_pivot")
    # axe de 18 mm en laiton : passe encore mais sous la marge exigee des ferrures affinees
    assert v.niveau == "alerte" and v.marge < p.get("charges.marge_mini_ferrures")
    q, _ = regles.changer_materiau(Parametres.pour_typologie("entrave", json_utilisateur=False),
                                   "ferrures.metal", "laiton_mat")
    v2 = E.calculer_entrave(q).verification("axe_pivot")
    assert v2.niveau == "ok" and v2.marge >= q.get("charges.marge_mini_ferrures")


def test_trois_pivots():
    for piv, piece in (("axe_vertical_chape", "chape"), ("rotule", "coquille_rotule"),
                       ("charniere_basculante", "noeud_charniere")):
        r = calc(entrave__manilles__pivot_cou=piv)
        assert any(s.piece == piece for s in r.solides), piv


def test_manilles_ecartement():
    r = calc(entrave__manilles__ecartement_poignets=650.0)
    g, d = r.solide("manille_poignet_G"), r.solide("manille_poignet_D")
    assert d.centre[0] - g.centre[0] == pytest.approx(650.0)
    assert r.solide("manille_cou").centre[0] == 0.0
    assert any(s.piece == "fermoir_ouverture_rapide" for s in r.solides)


def test_mode_synchro():
    assert any(s.nom == "arbre_longitudinal" for s in calc().solides)
    assert not any(s.nom == "arbre_longitudinal" for s in calc(synchro__mode="deux_cotes").solides)


def test_noms_uniques_et_masses():
    r = calc()
    noms = [s.nom for s in r.solides]
    assert len(noms) == len(set(noms))
    assert 30 < r.masses["total"] < 80
    assert r.masses["mobile"] > 10
    q, _ = regles.changer_materiau(r.params, "bois.essence", "chene")
    assert E.calculer_entrave(q).masses["par_materiau"]["bois"] > r.masses["par_materiau"]["bois"]


def test_parametres_derives_lies():
    r = calc()
    d = {l[0]: l for l in r.parametres_derives}
    assert d["neo_hauteur_platine"][1] == "neo_cremaillere_hauteur_mini + neo_course_courante"
    assert d["neo_course_courante"][1] == "neo_cremaillere_cran_courant * neo_cremaillere_pas"


def test_rapport_texte():
    txt = E.rapport_texte(calc())
    assert "Cran 0 / 6" in txt and "Verifications" in txt
